"""Worker process that executes durable tasks from the SQLite queue."""

from __future__ import annotations

import logging
import os
import signal
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from typing import Callable

from ..db import get_db, get_result, get_scenario, get_llm_scenario_judge
from ..models.executor import ExecutorSpec
from .judge import JudgeExecutor, evaluate_alignment_score
from .queue import (
    Task,
    TaskStatus,
    TaskType,
    cancel_task,
    claim_next_task,
    get_task,
    set_task_pid,
    update_task_cancelled,
    update_task_completed,
    update_task_failed,
)
from .runner import Runner

logger = logging.getLogger(__name__)


def _configure_worker_logging() -> None:
    # Respect VIBELAB_LOG_LEVEL if present. Default to INFO.
    level_name = os.environ.get("VIBELAB_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


@dataclass
class Worker:
    worker_id: str
    poll_interval_s: float = 0.5
    execution_mode: str = "subprocess"  # "subprocess" (default) or "inline" (tests)

    # Dependency injection points (for tests)
    runner_factory: Callable[[], Runner] = Runner
    judge_executor_factory: Callable[[], JudgeExecutor] = JudgeExecutor

    _running: bool = False

    def start(self) -> None:
        _configure_worker_logging()
        self._running = True

        def _handle_signal(signum: int, frame: object) -> None:  # noqa: ARG001
            logger.info("Worker %s shutting down (signal=%s)", self.worker_id, signum)
            self._running = False

        signal.signal(signal.SIGINT, _handle_signal)
        signal.signal(signal.SIGTERM, _handle_signal)

        logger.info("Worker %s started", self.worker_id)
        while self._running:
            did_work = self._tick()
            if not did_work:
                time.sleep(self.poll_interval_s)
        logger.info("Worker %s stopped", self.worker_id)

    def _tick(self) -> bool:
        for db in get_db():
            task = claim_next_task(db, self.worker_id)
            if not task:
                return False

            logger.info("Claimed task %s (%s)", task.id, task.task_type.value)
            try:
                if self.execution_mode == "inline":
                    self._execute_task_inline(task)
                    for db2 in get_db():
                        update_task_completed(db2, task.id)
                        break
                    logger.info("Completed task %s", task.id)
                else:
                    outcome = self._execute_task_subprocess(task)
                    for db2 in get_db():
                        if outcome.cancelled:
                            update_task_cancelled(db2, task.id, error_message="cancelled")
                        elif outcome.success:
                            update_task_completed(db2, task.id)
                        else:
                            update_task_failed(db2, task.id, error_message=outcome.error_message or "task failed")
                        break
                    if outcome.cancelled:
                        logger.info("Cancelled task %s", task.id)
                    elif outcome.success:
                        logger.info("Completed task %s", task.id)
                    else:
                        logger.info("Failed task %s", task.id)
            except Exception as e:
                logger.exception("Task %s failed", task.id)
                for db2 in get_db():
                    update_task_failed(db2, task.id, error_message=str(e))
                    break

            return True

        return False

    def _execute_task_inline(self, task: Task) -> None:
        if task.task_type == TaskType.AGENT_RUN:
            self._execute_agent_run(task)
            return
        if task.task_type == TaskType.JUDGE_RESULT:
            self._execute_judge_result(task)
            return
        if task.task_type == TaskType.TRAIN_JUDGE:
            self._execute_train_judge(task)
            return
        if task.task_type == TaskType.GENERATE_SCENARIO_FROM_COMMIT:
            from .task_executor import execute_task
            execute_task(task)
            return
        raise ValueError(f"Unknown task_type: {task.task_type}")

    @dataclass(frozen=True)
    class _TaskOutcome:
        success: bool
        cancelled: bool
        error_message: str | None

    def _execute_task_subprocess(self, task: Task) -> _TaskOutcome:
        """Execute task in a child process and return outcome.

        Returns:
          _TaskOutcome(success, cancelled, error_message)
        """
        # If a cancellation was requested before we even start, honor it.
        for db in get_db():
            current = get_task(db, task.id)
            break
        if current and current.status == TaskStatus.RUNNING and current.cancel_requested_at is not None:
            return Worker._TaskOutcome(success=False, cancelled=True, error_message="cancelled")

        proc = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "vibelab.engine.task_executor",
                "--task-id",
                str(task.id),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,  # new process group => cancel can killpg(pid)
        )

        for db in get_db():
            set_task_pid(db, task.id, pid=proc.pid)
            break

        stderr = ""
        try:
            _, stderr = proc.communicate()
        finally:
            for db in get_db():
                # Best-effort: clear pid once process is done.
                set_task_pid(db, task.id, pid=None)
                break

        rc = proc.returncode or 0

        # Re-read to see if cancellation was requested while running.
        for db in get_db():
            current = get_task(db, task.id)
            break

        cancel_requested = current.cancel_requested_at is not None if current else False
        cancelled = cancel_requested and rc != 0

        if cancelled:
            return Worker._TaskOutcome(success=False, cancelled=True, error_message="cancelled")

        if rc == 0:
            return Worker._TaskOutcome(success=True, cancelled=False, error_message=None)

        # Non-zero failure.
        msg = (stderr or "").strip()
        if len(msg) > 2000:
            msg = msg[:2000] + "…"
        return Worker._TaskOutcome(
            success=False,
            cancelled=False,
            error_message=msg or f"task exited with code {rc}",
        )

    def _execute_agent_run(self, task: Task) -> None:
        if task.result_id is None or task.scenario_id is None or not task.executor_spec:
            raise ValueError("agent_run task missing required fields")
        timeout_seconds = int(task.timeout_seconds or 1800)
        driver_id = task.driver or "local"
        executor_spec = ExecutorSpec.parse(task.executor_spec)

        scenario = None
        for db in get_db():
            scenario = get_scenario(db, task.scenario_id)
            break
        if scenario is None:
            raise ValueError(f"Scenario {task.scenario_id} not found")

        runner = self.runner_factory()
        # Runner handles result status + streaming logs.
        runner.run(
            scenario=scenario,
            executor_spec=executor_spec,
            timeout_seconds=timeout_seconds,
            driver_id=driver_id,
            result_id=task.result_id,
        )

    def _execute_judge_result(self, task: Task) -> None:
        if task.judge_id is None or task.target_result_id is None:
            raise ValueError("judge_result task missing required fields")

        judge = None
        result = None
        for db in get_db():
            judge = get_llm_scenario_judge(db, task.judge_id)
            result = get_result(db, task.target_result_id)
            break
        if judge is None:
            raise ValueError(f"Judge {task.judge_id} not found")
        if result is None:
            raise ValueError(f"Result {task.target_result_id} not found")

        executor = self.judge_executor_factory()
        executor.execute_judge(judge, result)

    def _execute_train_judge(self, task: Task) -> None:
        if task.judge_id is None:
            raise ValueError("train_judge task missing judge_id")

        judge = None
        for db in get_db():
            judge = get_llm_scenario_judge(db, task.judge_id)
            break
        if judge is None:
            raise ValueError(f"Judge {task.judge_id} not found")

        evaluate_alignment_score(judge, result_ids=task.alignment_result_ids)


def run_worker(worker_id: str | None = None) -> None:
    wid = worker_id or f"worker-{uuid.uuid4().hex[:8]}"
    Worker(worker_id=wid).start()


