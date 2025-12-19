"""Database migrations."""

import sqlite3
from typing import Any


def get_schema_version(conn: sqlite3.Connection) -> int:
    """Get current schema version."""
    try:
        cursor = conn.execute("SELECT MAX(version) FROM schema_version")
        row = cursor.fetchone()
        return row[0] if row and row[0] is not None else 0
    except sqlite3.OperationalError:
        return 0


MIGRATIONS: list[str] = [
    # Version 1: Initial schema
    """
    CREATE TABLE IF NOT EXISTS schema_version (
        version INTEGER PRIMARY KEY,
        applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS scenarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code_type TEXT NOT NULL CHECK (code_type IN ('github', 'local', 'empty')),
        code_ref TEXT,
        prompt TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scenario_id INTEGER NOT NULL REFERENCES scenarios(id),
        harness TEXT NOT NULL,
        provider TEXT NOT NULL,
        model TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'queued'
            CHECK (status IN ('queued', 'running', 'completed', 'failed', 'timeout')),
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        started_at TEXT,
        finished_at TEXT,
        duration_ms INTEGER,
        lines_added INTEGER,
        lines_removed INTEGER,
        files_changed INTEGER,
        tokens_used INTEGER,
        cost_usd REAL,
        harness_metrics TEXT,
        annotations TEXT,
        timeout_seconds INTEGER
    );
    
    CREATE INDEX IF NOT EXISTS idx_results_scenario ON results(scenario_id);
    CREATE INDEX IF NOT EXISTS idx_results_status ON results(status);
    """,
    # Version 2: Add timeout_seconds column (if it doesn't exist)
    """
    -- SQLite doesn't support IF NOT EXISTS for ALTER TABLE ADD COLUMN
    -- So we'll check if the column exists first
    -- This will fail silently if column already exists, which is fine
    -- We'll catch the error and continue
    """,
    # Version 3: Add driver column
    """
    -- Add driver column to results table
    """,
    # Version 4: Add updated_at column
    """
    -- Add updated_at column to results table
    """,
    # Version 5: Add datasets table and dataset_scenarios join table
    """
    CREATE TABLE IF NOT EXISTS datasets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS dataset_scenarios (
        dataset_id INTEGER NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
        scenario_id INTEGER NOT NULL REFERENCES scenarios(id) ON DELETE CASCADE,
        PRIMARY KEY (dataset_id, scenario_id)
    );
    
    CREATE INDEX IF NOT EXISTS idx_dataset_scenarios_dataset ON dataset_scenarios(dataset_id);
    CREATE INDEX IF NOT EXISTS idx_dataset_scenarios_scenario ON dataset_scenarios(scenario_id);
    """,
    # Version 6: Add error_message column and update status constraint
    """
    -- Add error_message column and update status constraint
    """,
    # Version 7: Add notes and quality columns
    """
    -- Add notes and quality columns to results table
    """,
    # Version 8: Add LLM judges and judgements tables
    """
    -- Add LLM scenario judges and judgements tables
    """,
    # Version 9: Add tasks table (durable queue for worker execution)
    """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_type TEXT NOT NULL CHECK (task_type IN ('agent_run', 'judge_result', 'train_judge')),
        status TEXT NOT NULL DEFAULT 'queued'
            CHECK (status IN ('queued', 'running', 'completed', 'failed')),
        priority INTEGER NOT NULL DEFAULT 0,

        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        started_at TEXT,
        finished_at TEXT,
        error_message TEXT,
        worker_id TEXT,

        -- agent_run fields (NULL for other task types)
        result_id INTEGER REFERENCES results(id) ON DELETE CASCADE,
        scenario_id INTEGER REFERENCES scenarios(id) ON DELETE CASCADE,
        executor_spec TEXT,
        timeout_seconds INTEGER,
        driver TEXT,

        -- judge_result fields (NULL for other task types)
        judge_id INTEGER REFERENCES llm_scenario_judges(id) ON DELETE CASCADE,
        target_result_id INTEGER REFERENCES results(id) ON DELETE CASCADE,
        judge_provider TEXT,
        judge_model TEXT
    );

    CREATE INDEX IF NOT EXISTS idx_tasks_poll
        ON tasks(status, priority DESC, created_at ASC);
    CREATE INDEX IF NOT EXISTS idx_tasks_result_id
        ON tasks(result_id);
    CREATE INDEX IF NOT EXISTS idx_tasks_target_result_id
        ON tasks(target_result_id);
    CREATE INDEX IF NOT EXISTS idx_tasks_type
        ON tasks(task_type);
    """,
    # Version 10: Add judge provider/model columns to LLM judges
    """
    -- Add judge_provider and judge_model columns to llm_scenario_judges
    """,
    # Version 11: Remove test_sample_ids column from llm_scenario_judges (table rebuild)
    """
    -- Remove test_sample_ids column from llm_scenario_judges (handled in Python)
    """,
    # Version 12: Add alignment_result_ids to tasks (handled in Python)
    """
    -- Add alignment_result_ids column to tasks (handled in Python)
    """,
    # Version 13: Add task cancellation + PID tracking (table rebuild for CHECK constraint)
    """
    -- Add cancelled status, pid, cancel_requested_at to tasks (handled in Python)
    """,
    # Version 14: Add commit_scenario_drafts table and draft_id to tasks
    """
    CREATE TABLE IF NOT EXISTS commit_scenario_drafts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER REFERENCES tasks(id),
        
        -- Source commit
        owner TEXT NOT NULL,
        repo TEXT NOT NULL,
        commit_sha TEXT NOT NULL,
        parent_sha TEXT NOT NULL,
        commit_message TEXT NOT NULL,
        commit_author TEXT,
        pr_number INTEGER,
        pr_title TEXT,
        pr_body TEXT,
        diff TEXT NOT NULL,
        
        -- Generated content
        generated_prompt TEXT,
        generated_judge_guidance TEXT,
        generated_summary TEXT,
        
        -- Status
        status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'ready', 'saved', 'failed')),
        error_message TEXT,
        
        -- Final references (after save)
        scenario_id INTEGER REFERENCES scenarios(id),
        judge_id INTEGER REFERENCES llm_scenario_judges(id),
        
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX IF NOT EXISTS idx_commit_drafts_task_id ON commit_scenario_drafts(task_id);
    CREATE INDEX IF NOT EXISTS idx_commit_drafts_status ON commit_scenario_drafts(status);
    """,
    # Version 15: Add archived column to scenarios table
    """
    -- Add archived column to scenarios table (handled in Python)
    """,
]


def migrate(conn: sqlite3.Connection) -> None:
    """Apply pending migrations.

    Important: a migration version is recorded in `schema_version` only if the
    migration executes successfully.
    """

    def _table_columns(table: str) -> list[str]:
        return [row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]

    def _add_column_if_missing(*, table: str, column: str, ddl: str) -> None:
        cols = _table_columns(table)
        if column not in cols:
            conn.execute(ddl)

    current = get_schema_version(conn)

    for version, sql in enumerate(MIGRATIONS, start=1):
        if version <= current:
            continue

        # Apply migration `version`.
        if version == 2:
            _add_column_if_missing(
                table="results",
                column="timeout_seconds",
                ddl="ALTER TABLE results ADD COLUMN timeout_seconds INTEGER",
            )
        elif version == 3:
            _add_column_if_missing(
                table="results",
                column="driver",
                ddl="ALTER TABLE results ADD COLUMN driver TEXT DEFAULT 'local'",
            )
        elif version == 4:
            _add_column_if_missing(
                table="results",
                column="updated_at",
                ddl="ALTER TABLE results ADD COLUMN updated_at TEXT",
            )
        elif version == 6:
            # Version 6: add error_message + expand status constraint to include infra_failure.
            _add_column_if_missing(
                table="results",
                column="error_message",
                ddl="ALTER TABLE results ADD COLUMN error_message TEXT",
            )

            # Rebuild results table to update CHECK constraint.
            conn.execute(
                """
                CREATE TABLE results_new (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  scenario_id INTEGER NOT NULL REFERENCES scenarios(id),
                  harness TEXT NOT NULL,
                  provider TEXT NOT NULL,
                  model TEXT NOT NULL,
                  status TEXT NOT NULL DEFAULT 'queued'
                    CHECK (status IN ('queued','running','completed','failed','timeout','infra_failure')),
                  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  started_at TEXT,
                  finished_at TEXT,
                  duration_ms INTEGER,
                  lines_added INTEGER,
                  lines_removed INTEGER,
                  files_changed INTEGER,
                  tokens_used INTEGER,
                  cost_usd REAL,
                  harness_metrics TEXT,
                  annotations TEXT,
                  timeout_seconds INTEGER,
                  driver TEXT DEFAULT 'local',
                  updated_at TEXT,
                  error_message TEXT
                )
                """
            )
            conn.execute("INSERT INTO results_new SELECT * FROM results")
            conn.execute("DROP TABLE results")
            conn.execute("ALTER TABLE results_new RENAME TO results")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_results_scenario ON results(scenario_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_results_status ON results(status)")
        elif version == 7:
            _add_column_if_missing(
                table="results",
                column="notes",
                ddl="ALTER TABLE results ADD COLUMN notes TEXT",
            )
            _add_column_if_missing(
                table="results",
                column="quality",
                ddl="ALTER TABLE results ADD COLUMN quality INTEGER CHECK (quality IS NULL OR (quality >= 1 AND quality <= 4))",
            )
        elif version == 8:
            # This migration's SQL is implemented in code (historical), so create tables idempotently here.
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS llm_scenario_judges (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  scenario_id INTEGER NOT NULL REFERENCES scenarios(id) ON DELETE CASCADE,
                  guidance TEXT NOT NULL,
                  training_sample_ids TEXT NOT NULL,
                  test_sample_ids TEXT NOT NULL,
                  alignment_score REAL,
                  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS judgements (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  result_id INTEGER NOT NULL REFERENCES results(id) ON DELETE CASCADE,
                  judge_id INTEGER NOT NULL REFERENCES llm_scenario_judges(id) ON DELETE CASCADE,
                  notes TEXT,
                  quality INTEGER CHECK (quality IS NULL OR (quality >= 1 AND quality <= 4)),
                  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  UNIQUE(result_id, judge_id)
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_judges_scenario ON llm_scenario_judges(scenario_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_judgements_result ON judgements(result_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_judgements_judge ON judgements(judge_id)")
        elif version == 10:
            # Version 10: add judge_provider/judge_model columns (if missing).
            cols = _table_columns("llm_scenario_judges")
            if "judge_provider" not in cols:
                conn.execute(
                    "ALTER TABLE llm_scenario_judges ADD COLUMN judge_provider TEXT NOT NULL DEFAULT 'anthropic'"
                )
            if "judge_model" not in cols:
                conn.execute(
                    "ALTER TABLE llm_scenario_judges ADD COLUMN judge_model TEXT NOT NULL DEFAULT 'claude-sonnet-4-20250514'"
                )
        elif version == 11:
            # Version 11: remove test_sample_ids from llm_scenario_judges (table rebuild).
            cols = _table_columns("llm_scenario_judges")
            if "test_sample_ids" in cols:
                conn.execute(
                    """
                    CREATE TABLE llm_scenario_judges_new (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      scenario_id INTEGER NOT NULL REFERENCES scenarios(id) ON DELETE CASCADE,
                      guidance TEXT NOT NULL,
                      training_sample_ids TEXT NOT NULL,
                      alignment_score REAL,
                      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                      judge_provider TEXT NOT NULL DEFAULT 'anthropic',
                      judge_model TEXT NOT NULL DEFAULT 'claude-sonnet-4-20250514'
                    )
                    """
                )
                conn.execute(
                    """
                    INSERT INTO llm_scenario_judges_new
                      (id, scenario_id, guidance, training_sample_ids, alignment_score, created_at, judge_provider, judge_model)
                    SELECT
                      id, scenario_id, guidance, training_sample_ids, alignment_score, created_at, judge_provider, judge_model
                    FROM llm_scenario_judges
                    """
                )
                conn.execute("DROP TABLE llm_scenario_judges")
                conn.execute("ALTER TABLE llm_scenario_judges_new RENAME TO llm_scenario_judges")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_judges_scenario ON llm_scenario_judges(scenario_id)")
        elif version == 12:
            # Version 12: add alignment_result_ids to tasks (if missing).
            _add_column_if_missing(
                table="tasks",
                column="alignment_result_ids",
                ddl="ALTER TABLE tasks ADD COLUMN alignment_result_ids TEXT",
            )
        elif version == 13:
            # Version 13: rebuild tasks table to:
            # - expand status CHECK to include 'cancelled'
            # - add pid + cancel_requested_at columns
            cols = _table_columns("tasks")
            
            # Check if we need to rebuild (if pid column is missing)
            if "pid" not in cols:
                conn.execute(
                    """
                    CREATE TABLE tasks_new (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      task_type TEXT NOT NULL CHECK (task_type IN ('agent_run', 'judge_result', 'train_judge', 'generate_scenario_from_commit')),
                      status TEXT NOT NULL DEFAULT 'queued'
                        CHECK (status IN ('queued', 'running', 'completed', 'failed', 'cancelled')),
                      priority INTEGER NOT NULL DEFAULT 0,

                      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                      started_at TEXT,
                      finished_at TEXT,
                      error_message TEXT,
                      worker_id TEXT,
                      pid INTEGER,
                      cancel_requested_at TEXT,

                      -- agent_run fields (NULL for other task types)
                      result_id INTEGER REFERENCES results(id) ON DELETE CASCADE,
                      scenario_id INTEGER REFERENCES scenarios(id) ON DELETE CASCADE,
                      executor_spec TEXT,
                      timeout_seconds INTEGER,
                      driver TEXT,

                      -- judge_result fields (NULL for other task types)
                      judge_id INTEGER REFERENCES llm_scenario_judges(id) ON DELETE CASCADE,
                      target_result_id INTEGER REFERENCES results(id) ON DELETE CASCADE,
                      judge_provider TEXT,
                      judge_model TEXT,

                      -- train_judge fields
                      alignment_result_ids TEXT,
                      
                      -- generate_scenario_from_commit fields
                      draft_id INTEGER
                    )
                    """
                )
                
                # Copy existing rows - build column list dynamically based on what exists
                base_cols = [
                    "id", "task_type", "status", "priority",
                    "created_at", "started_at", "finished_at", "error_message", "worker_id",
                    "result_id", "scenario_id", "executor_spec", "timeout_seconds", "driver",
                    "judge_id", "target_result_id", "judge_provider", "judge_model"
                ]
                existing_cols = [c for c in base_cols if c in cols]
                
                # Add optional columns that may exist
                if "alignment_result_ids" in cols:
                    existing_cols.append("alignment_result_ids")
                
                cols_str = ", ".join(existing_cols)
                conn.execute(f"INSERT INTO tasks_new ({cols_str}) SELECT {cols_str} FROM tasks")
                
                conn.execute("DROP TABLE tasks")
                conn.execute("ALTER TABLE tasks_new RENAME TO tasks")

                # Recreate indexes
                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_tasks_poll
                      ON tasks(status, priority DESC, created_at ASC)
                    """
                )
                conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_result_id ON tasks(result_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_target_result_id ON tasks(target_result_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_type ON tasks(task_type)")
        elif version == 14:
            # Version 14: add draft_id column to tasks table (if not already added)
            _add_column_if_missing(
                table="tasks",
                column="draft_id",
                ddl="ALTER TABLE tasks ADD COLUMN draft_id INTEGER",
            )
            # Also execute the SQL to create commit_scenario_drafts table
            conn.executescript(sql)
        elif version == 15:
            # Version 15: add archived column to scenarios table
            _add_column_if_missing(
                table="scenarios",
                column="archived",
                ddl="ALTER TABLE scenarios ADD COLUMN archived INTEGER NOT NULL DEFAULT 0",
            )
        else:
            conn.executescript(sql)

        # Record migration version only after success.
        conn.execute("INSERT INTO schema_version (version) VALUES (?)", (version,))
        conn.commit()
