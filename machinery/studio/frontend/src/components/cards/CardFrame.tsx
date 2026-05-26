import { FileText, Layers3, PenSquare } from 'lucide-react'
import { useEditorStore } from '@/store/useEditorStore'
import PoemEditor from '@/components/editor/PoemEditor'

interface Props {
  projectId: string
}

export default function CardFrame({ projectId }: Props) {
  const { activePoem, activeSection } = useEditorStore()

  if (!activePoem) {
    return (
      <div className="flex h-full items-center justify-center bg-canvas px-8">
        <div className="w-full max-w-xl rounded-[2rem] border border-border bg-surface/90 p-8">
          <div className="inline-flex rounded-full border border-accent/30 bg-accent/10 p-3 text-accent">
            <PenSquare className="h-5 w-5" />
          </div>
          <h2 className="mt-5 text-2xl text-text-primary">
            {activeSection ? activeSection.label : 'Select a section to start authoring'}
          </h2>
          <p className="mt-3 text-sm leading-6 text-text-secondary">
            {activeSection
              ? 'Choose an existing poem from the selected section or create a new one from the cards rail.'
              : 'The cards rail is now section-first. Pick a section, then open or create poems inside it.'}
          </p>

          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            <div className="rounded-2xl border border-border bg-canvas px-4 py-4">
              <div className="inline-flex rounded-full bg-card p-2 text-text-muted">
                <FileText className="h-4 w-4" />
              </div>
              <p className="mt-3 text-sm text-text-primary">Section-first browsing</p>
              <p className="mt-1 text-xs leading-5 text-text-muted">
                Open a section to reveal its poem cards, warnings, canonical status, and order.
              </p>
            </div>

            <div className="rounded-2xl border border-border bg-canvas px-4 py-4">
              <div className="inline-flex rounded-full bg-card p-2 text-text-muted">
                <Layers3 className="h-4 w-4" />
              </div>
              <p className="mt-3 text-sm text-text-primary">Metadata stays visible</p>
              <p className="mt-1 text-xs leading-5 text-text-muted">
                The right panel shows section or poem metadata so you can browse structure without opening the graph.
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <div className="shrink-0 border-b border-accent/25 bg-accent/5 px-5 py-3">
        <div className="flex items-center gap-2 text-[11px] uppercase tracking-[0.18em] text-text-muted">
          <span>{activeSection?.label ?? activePoem.section_id}</span>
          <span>•</span>
          <span>{activePoem.filename}</span>
        </div>

        <div className="mt-2 flex flex-wrap items-center gap-2">
          <h2 className="text-lg text-text-primary">{activePoem.frontmatter.title}</h2>
          <span className="rounded-full border border-border px-2 py-0.5 text-[11px] uppercase tracking-[0.14em] text-text-muted">
            {activePoem.frontmatter.type}
          </span>
          <span className="rounded-full border border-border px-2 py-0.5 text-[11px] text-text-muted">
            {activePoem.line_count} lines
          </span>
          {activePoem.frontmatter.order != null && (
            <span className="rounded-full border border-border px-2 py-0.5 text-[11px] text-text-muted">
              order {activePoem.frontmatter.order}
            </span>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-hidden">
        <PoemEditor projectId={projectId} />
      </div>
    </div>
  )
}
