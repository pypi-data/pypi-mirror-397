import { useNavigate } from 'react-router-dom'
import { Card, Button } from './ui'
import {
  CellData,
  MatrixRow,
  MatrixQualityBadge,
  MatrixCellContent,
  ScenarioRowTitle,
  formatDuration,
  MatrixLegend,
  RunMissingButton,
} from './AnalyticsMatrix'
import { getExecutorDisplayName } from '../lib/modelNames'

interface QualityMatrixViewProps {
  matrix: MatrixRow[]
  visibleExecutors: string[]
  agg: {
    global: { quality: { avg: number | null; count: number }; duration: { avg: number | null; count: number } }
    byScenario: Record<number, { quality: { avg: number | null; count: number }; duration: { avg: number | null; count: number } }>
    byExecutor: Record<string, { quality: { avg: number | null; count: number }; duration: { avg: number | null; count: number } }>
  }
  stats: { completed: number; failed: number; running: number; pendingJudges: number }
  missingRuns: {
    byRow: Record<number, Array<{ scenarioId: number; executor: string }>>
    byColumn: Record<string, Array<{ scenarioId: number; executor: string }>>
    all: Array<{ scenarioId: number; executor: string }>
  }
  judgeByScenario: Map<number, number>
  judgingResultIds: Set<number>
  batchRunning: Set<string>
  
  // Actions
  runAllJudges: () => void
  handleStartRun: (scenarioId: number, executor: string) => void
  isStartingRun: (scenarioId: number, executor: string) => boolean
  handleRunRowMissing: (scenarioId: number) => void
  handleRunColumnMissing: (executor: string) => void
  handleRunAllMissing: () => void
  
  // Optional customization
  showJudgeAllButton?: boolean
  /** Full-page mode: no card wrapper, fills parent height */
  fullPage?: boolean
  /** Hide the header (title + action buttons) when in full-page mode with external header */
  hideHeader?: boolean
}

export function QualityMatrixView({
  matrix,
  visibleExecutors,
  agg,
  stats,
  missingRuns,
  judgeByScenario,
  judgingResultIds,
  batchRunning,
  runAllJudges,
  handleStartRun,
  isStartingRun,
  handleRunRowMissing,
  handleRunColumnMissing,
  handleRunAllMissing,
  showJudgeAllButton = true,
  fullPage = false,
  hideHeader = false,
}: QualityMatrixViewProps) {
  const navigate = useNavigate()

  const handleCellClick = (cell: CellData, e: React.MouseEvent) => {
    e.stopPropagation()
    if (cell.result_ids?.length === 1) navigate(`/result/${cell.result_ids[0]}`)
    else if (cell.result_ids && cell.result_ids.length > 1) navigate(`/compare?ids=${cell.result_ids.join(',')}`)
  }

  const handleRowCompare = (row: MatrixRow) => {
    const ids = Object.values(row.cells).flatMap(c => c.result_ids || [])
    if (ids.length > 0) navigate(`/compare?ids=${ids.join(',')}&scenario=${row.scenario_id}`)
  }

  const onStartRun = (scenarioId: number, executor: string, e: React.MouseEvent) => {
    e.stopPropagation()
    handleStartRun(scenarioId, executor)
  }

  // Header with title and action buttons
  const headerContent = !hideHeader && (
    <div className="flex items-center justify-between px-4 py-2 bg-surface-2 border-b border-border">
      <div className="font-medium text-text-primary">
        Quality Matrix
        <span className="ml-2 text-sm font-normal text-text-tertiary">
          {matrix.length} scenarios × {visibleExecutors.length} executors
        </span>
      </div>
      <div className="flex items-center gap-2">
        {showJudgeAllButton && stats.pendingJudges > 0 && (
          <Button
            size="sm"
            variant="secondary"
            onClick={runAllJudges}
            disabled={judgingResultIds.size === stats.pendingJudges}
          >
            {judgingResultIds.size > 0
              ? `⚖️ ${judgingResultIds.size}/${stats.pendingJudges} judging...`
              : `⚖️ Judge All (${stats.pendingJudges})`}
          </Button>
        )}
        {missingRuns.all.length > 0 && (
          <Button
            size="sm"
            variant="secondary"
            onClick={handleRunAllMissing}
            disabled={batchRunning.size > 0}
          >
            {batchRunning.size > 0
              ? `Running ${batchRunning.size}...`
              : `▶ Run All Missing (${missingRuns.all.length})`}
          </Button>
        )}
      </div>
    </div>
  )

  // Matrix table content
  const matrixTable = (
    <table className="w-full text-sm border-separate border-spacing-0">
      <thead className="sticky top-0 z-20">
        <tr className="bg-surface-2">
          {/* Left sticky header - Scenario column */}
          <th className="sticky left-0 z-30 bg-surface-2 text-left px-4 py-2 font-medium text-text-tertiary w-[200px] min-w-[200px] border-b border-border">
            Scenario
          </th>
          {/* Executor columns */}
          {visibleExecutors.map((exec) => {
            const displayName = getExecutorDisplayName(exec)
            const eq = agg.byExecutor[exec]
            const colMissing = missingRuns.byColumn[exec]?.length || 0
            return (
              <th key={exec} className="px-2 py-2 text-center font-medium min-w-[90px] bg-surface-2 border-b border-border">
                <div className="text-xs text-text-primary truncate" title={exec}>
                  {displayName}
                </div>
                <div className="mt-1">
                  <MatrixQualityBadge value={eq?.quality.avg} size="sm" />
                </div>
                {eq?.duration.avg != null && (
                  <div className="text-[9px] text-text-tertiary mt-0.5">
                    {formatDuration(eq.duration.avg)}
                  </div>
                )}
                {colMissing > 0 && (
                  <div className="mt-1">
                    <RunMissingButton
                      count={colMissing}
                      onClick={() => handleRunColumnMissing(exec)}
                      isRunning={batchRunning.size > 0}
                    />
                  </div>
                )}
              </th>
            )
          })}
          {/* Right sticky header - Scenario Avg column */}
          <th className="sticky right-0 z-30 px-3 py-2 text-center font-medium text-text-tertiary bg-surface-2 min-w-[80px] border-b border-border border-l border-l-border">
            <div className="text-[10px] uppercase tracking-wide">Scenario</div>
            <div className="text-[10px]">Avg</div>
          </th>
        </tr>
      </thead>
      <tbody>
        {matrix.map((row) => {
          const hasResults = Object.values(row.cells).some(
            (c) => c.result_ids && c.result_ids.length > 0
          )
          const sq = agg.byScenario[row.scenario_id]
          const rowMissing = missingRuns.byRow[row.scenario_id]?.length || 0
          const hasJudge = judgeByScenario.has(row.scenario_id)

          return (
            <tr
              key={row.scenario_id}
              className="hover:bg-surface-2/50 transition-colors"
            >
              {/* Left sticky - Scenario cell */}
              <td className="sticky left-0 z-10 bg-surface px-4 py-3 border-b border-border-muted">
                <div className="flex items-start gap-2">
                  <div className="flex-1 min-w-0">
                    <ScenarioRowTitle
                      scenarioId={row.scenario_id}
                      prompt={row.scenario_prompt}
                      hasResults={hasResults}
                      onCompare={() => handleRowCompare(row)}
                    />
                  </div>
                  {rowMissing > 0 && (
                    <div className="flex items-center gap-1 shrink-0">
                      <RunMissingButton
                        count={rowMissing}
                        onClick={() => handleRunRowMissing(row.scenario_id)}
                        isRunning={batchRunning.size > 0}
                      />
                      {hasJudge && (
                        <span className="text-[9px] text-status-info" title="Judge will auto-run">
                          ⚖️
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </td>
              {/* Data cells */}
              {visibleExecutors.map((exec) => {
                const cell = row.cells[exec] || {
                  status: 'pending',
                  total: 0,
                  completed: 0,
                  failed: 0,
                  timeout: 0,
                  running: 0,
                  queued: 0,
                  result_ids: [],
                }
                return (
                  <td key={exec} className="px-2 py-2 text-center border-b border-border-muted">
                    <MatrixCellContent
                      cell={cell}
                      onCellClick={(e) => handleCellClick(cell, e)}
                      onRunClick={(e) => onStartRun(row.scenario_id, exec, e)}
                      isStartingRun={
                        isStartingRun(row.scenario_id, exec) ||
                        batchRunning.has(`${row.scenario_id}:${exec}`)
                      }
                    />
                  </td>
                )
              })}
              {/* Right sticky - Scenario Avg cell */}
              <td className="sticky right-0 z-10 px-3 py-2 text-center bg-surface border-b border-border-muted border-l border-l-border">
                <MatrixQualityBadge value={sq?.quality.avg} count={sq?.quality.count} size="sm" />
                {sq?.duration.avg != null && (
                  <div className="text-[9px] text-text-tertiary mt-0.5">
                    {formatDuration(sq.duration.avg)}
                  </div>
                )}
              </td>
            </tr>
          )
        })}
      </tbody>
      {/* Sticky footer */}
      <tfoot className="sticky bottom-0 z-20">
        <tr className="bg-surface-2">
          {/* Left sticky footer - Executor Avg label */}
          <td className="sticky left-0 z-30 bg-surface-2 px-4 py-2 font-medium text-text-secondary text-xs border-t border-border">
            Executor Avg
          </td>
          {/* Executor avg cells */}
          {visibleExecutors.map((exec) => {
            const eq = agg.byExecutor[exec]
            return (
              <td key={exec} className="px-2 py-2 text-center bg-surface-2 border-t border-border">
                <MatrixQualityBadge value={eq?.quality.avg} count={eq?.quality.count} size="sm" />
                {eq?.duration.avg != null && (
                  <div className="text-[9px] text-text-tertiary mt-0.5">
                    {formatDuration(eq.duration.avg)}
                  </div>
                )}
              </td>
            )
          })}
          {/* Right sticky footer - Global avg */}
          <td className="sticky right-0 z-30 px-3 py-2 text-center bg-surface-2 border-t border-border border-l border-l-border">
            <div className="text-[9px] text-text-tertiary uppercase mb-0.5">Global</div>
            <MatrixQualityBadge
              value={agg.global.quality.avg}
              count={agg.global.quality.count}
              size="sm"
            />
            {agg.global.duration.avg != null && (
              <div className="text-[9px] text-text-tertiary mt-0.5">
                {formatDuration(agg.global.duration.avg)}
              </div>
            )}
          </td>
        </tr>
      </tfoot>
    </table>
  )

  // Full-page mode: no card wrapper, fills parent
  if (fullPage) {
    return (
      <div className="h-full flex flex-col border-t border-border">
        {headerContent}
        <div className="flex-1 overflow-auto">
          {matrixTable}
        </div>
      </div>
    )
  }

  // Standard card mode
  return (
    <>
      <Card>
        {!hideHeader && (
          <Card.Header className="flex items-center justify-between">
            <Card.Title>
              Quality Matrix
              <span className="ml-2 text-sm font-normal text-text-tertiary">
                {matrix.length} scenarios × {visibleExecutors.length} executors
              </span>
            </Card.Title>
            <div className="flex items-center gap-2">
              {showJudgeAllButton && stats.pendingJudges > 0 && (
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={runAllJudges}
                  disabled={judgingResultIds.size === stats.pendingJudges}
                >
                  {judgingResultIds.size > 0
                    ? `⚖️ ${judgingResultIds.size}/${stats.pendingJudges} judging...`
                    : `⚖️ Judge All (${stats.pendingJudges})`}
                </Button>
              )}
              {missingRuns.all.length > 0 && (
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={handleRunAllMissing}
                  disabled={batchRunning.size > 0}
                >
                  {batchRunning.size > 0
                    ? `Running ${batchRunning.size}...`
                    : `▶ Run All Missing (${missingRuns.all.length})`}
                </Button>
              )}
            </div>
          </Card.Header>
        )}
        <Card.Content className="p-0 overflow-auto">
          {matrixTable}
        </Card.Content>
      </Card>

      <MatrixLegend />
    </>
  )
}
