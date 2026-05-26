import type { PoemSummary } from '@/types/poem'

interface Props {
  poem: PoemSummary
  isActive: boolean
  isSelected?: boolean
  onClick: () => void
}

export default function CardChip({ poem, isActive, isSelected = false, onClick }: Props) {
  return (
    <button
      onClick={onClick}
      className={`w-full rounded-xl border px-3 py-2 text-left transition ${
        isActive
          ? 'border-accent/40 bg-accent/10 text-accent shadow-[0_0_0_1px_rgba(64,145,108,0.12)]'
          : isSelected
            ? 'border-border/80 bg-card text-text-primary'
            : 'border-transparent bg-transparent text-text-secondary hover:border-border/80 hover:bg-card hover:text-text-primary'
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <span className="block truncate text-sm font-medium">{poem.title}</span>
          <div className="mt-1 text-[11px] text-text-muted">
            {poem.type} • {poem.line_count}L
            {poem.order != null && ` • #${poem.order}`}
          </div>
        </div>

        <div className="ml-2 flex shrink-0 items-center gap-1.5 text-[10px]">
          {poem.is_canonical && (
            <span className="rounded-full border border-accent/30 bg-accent/10 px-1.5 py-0.5 text-accent">
              canon
            </span>
          )}
          {poem.has_warning && <span className="text-amber-400">⚠</span>}
          {poem.version_count > 1 && (
            <span className="rounded-full border border-border px-1.5 py-0.5 text-text-muted">
              v{poem.version_count}
            </span>
          )}
        </div>
      </div>

      {poem.has_warning && poem.warning_message && (
        <p className="mt-2 text-[11px] text-amber-300">{poem.warning_message}</p>
      )}
    </button>
  )
}
