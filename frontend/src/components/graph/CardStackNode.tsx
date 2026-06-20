import { Handle, Position } from '@xyflow/react'
import { AlertTriangle, Layers3, Star } from 'lucide-react'
import { useEditorStore } from '@/store/useEditorStore'
import { useGraphStore } from '@/store/useGraphStore'

interface Props {
  data: {
    poemTitle: string
    poemSlug: string
    poemType: string
    lineCount: number
    versionCount: number
    hasWarning: boolean
    warningMessage: string
    isCanonical: boolean
    sectionLabel: string
    sectionId: string
    projectId: string
    sectionSelected: boolean
    poemSelected: boolean
  }
}

export default function CardStackNode({ data }: Props) {
  const { setPendingSelect, setActiveView } = useEditorStore()
  const { selectPoem, selectSection } = useGraphStore()

  const handleOpen = () => {
    selectSection(data.sectionId)
    selectPoem(data.poemSlug)
    setPendingSelect({ sectionId: data.sectionId, poemSlug: data.poemSlug })
    setActiveView('cards')
  }

  const stackShadow =
    data.versionCount > 1
      ? '3px 3px 0 rgba(31,31,31,0.9), 7px 7px 0 rgba(20,20,20,0.85)'
      : undefined

  return (
    <div
      className={`min-w-[156px] rounded-2xl border px-3 py-3 transition ${
        data.poemSelected
          ? 'border-accent/50 bg-accent/10'
          : data.sectionSelected
            ? 'border-border/90 bg-card'
            : 'border-border/60 bg-surface/90 hover:border-accent/35'
      }`}
      style={{ boxShadow: stackShadow }}
      onClick={handleOpen}
      role="button"
      tabIndex={0}
      onKeyDown={(event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault()
          handleOpen()
        }
      }}
    >
      <Handle type="target" position={Position.Top} style={{ opacity: 0 }} />

      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="truncate text-sm text-text-primary">{data.poemTitle}</p>
          <p className="mt-1 truncate text-[11px] text-text-muted">{data.sectionLabel}</p>
        </div>

        <div className="flex shrink-0 items-center gap-1.5">
          {data.hasWarning && <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />}
          {data.isCanonical && <Star className="h-3.5 w-3.5 fill-accent text-accent" />}
        </div>
      </div>

      <div className="mt-3 flex items-center gap-2 text-[11px] text-text-muted">
        <span>{data.poemType}</span>
        <span>•</span>
        <span>{data.lineCount}L</span>
      </div>

      <div className="mt-3 flex items-center justify-between gap-3">
        <span className="inline-flex items-center gap-1 rounded-full border border-border px-2 py-1 text-[10px] uppercase tracking-[0.14em] text-text-muted">
          <Layers3 className="h-3 w-3" />
          {data.versionCount} version{data.versionCount === 1 ? '' : 's'}
        </span>

        <span className="text-[10px] uppercase tracking-[0.14em] text-accent">Open</span>
      </div>

      {data.hasWarning && data.warningMessage && (
        <p className="mt-3 max-w-[14rem] text-[11px] leading-4 text-amber-300">{data.warningMessage}</p>
      )}

      <Handle type="source" position={Position.Bottom} style={{ opacity: 0 }} />
    </div>
  )
}
