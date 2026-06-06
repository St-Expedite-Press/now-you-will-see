import { BookOpenText, Bot, Boxes, FileSearch, Hammer, Palette, PanelLeftClose, PanelLeftOpen } from 'lucide-react'
import type { ViewMode } from '@/store/useEditorStore'
import { useAgentStore } from '@/store/useAgentStore'
import { useEditorStore } from '@/store/useEditorStore'
import { useProjectStore } from '@/store/useProjectStore'

interface Props {
  view: ViewMode
  onViewChange: (v: ViewMode) => void
  projectId: string
}

const VIEWS: { id: ViewMode; label: string; icon: typeof BookOpenText }[] = [
  { id: 'cards', label: 'Cards', icon: BookOpenText },
  { id: 'graph', label: 'Graph', icon: Boxes },
  { id: 'build', label: 'Build', icon: Hammer },
  { id: 'covers', label: 'Covers', icon: Palette },
  { id: 'audit', label: 'Audit', icon: FileSearch },
]

export default function TopBar({ view, onViewChange, projectId }: Props) {
  const { activeProject } = useProjectStore()
  const { activeSection, activePoem } = useEditorStore()
  const { isOpen, setOpen } = useAgentStore()

  return (
    <header className="shrink-0 border-b border-border bg-surface px-4 py-3">
      <div className="flex items-center gap-4">
        <div className="mr-2 min-w-0">
          <div className="flex items-center gap-2">
            <span className="inline-flex rounded-full border border-accent/30 bg-accent/10 p-2 text-accent">
              <BookOpenText className="h-4 w-4" />
            </span>
            <div className="min-w-0">
              <p className="truncate text-sm text-text-primary">
                {activeProject?.meta.title ?? projectId}
              </p>
              <p className="truncate text-[11px] uppercase tracking-[0.18em] text-text-muted">
                Texgraph Studio
              </p>
            </div>
          </div>
        </div>

        <div className="flex rounded-2xl border border-border bg-canvas p-1">
          {VIEWS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              type="button"
              onClick={() => onViewChange(id)}
              className={`inline-flex items-center gap-2 rounded-xl px-3 py-2 text-xs font-medium transition ${
                view === id
                  ? 'bg-accent/15 text-accent'
                  : 'text-text-muted hover:text-text-primary'
              }`}
            >
              <Icon className="h-3.5 w-3.5" />
              {label}
            </button>
          ))}
        </div>

        <div className="min-w-0 flex-1">
          <div className="truncate text-sm text-text-secondary">
            {activeSection ? activeSection.label : 'No section selected'}
            {activePoem ? (
              <span className="text-text-muted"> • {activePoem.frontmatter.title}</span>
            ) : null}
          </div>
          <div className="mt-1 flex flex-wrap items-center gap-2 text-[11px] text-text-muted">
            {activeProject && <span>{activeProject.section_count} sections</span>}
            {activeProject && <span>•</span>}
            {activeProject && <span>{activeProject.poem_count} poems</span>}
            {activeSection && <span>•</span>}
            {activeSection && <span>{activeSection.id}</span>}
          </div>
        </div>

        <button
          type="button"
          onClick={() => setOpen(!isOpen)}
          className={`inline-flex items-center gap-2 rounded-xl border px-3 py-2 text-xs font-medium transition ${
            isOpen
              ? 'border-agent/35 bg-agent-surface text-agent-text'
              : 'border-border text-text-secondary hover:text-agent-text'
          }`}
        >
          {isOpen ? <PanelLeftClose className="h-3.5 w-3.5" /> : <PanelLeftOpen className="h-3.5 w-3.5" />}
          <Bot className="h-3.5 w-3.5" />
          Agent
        </button>
      </div>
    </header>
  )
}
