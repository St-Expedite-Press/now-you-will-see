import { Info, Layers3, ScrollText } from 'lucide-react'
import { useEditorStore } from '@/store/useEditorStore'
import VersionList from '@/components/cards/VersionList'

interface Props {
  projectId: string
}

export default function PropertiesPanel({ projectId }: Props) {
  const { activePoem, activeSection } = useEditorStore()
  const hasTitlePage = Boolean(activeSection && 'has_title_page' in activeSection && activeSection.has_title_page)

  if (!activeSection && !activePoem) {
    return (
      <aside className="w-72 border-l border-border bg-panel px-4 py-5">
        <div className="rounded-2xl border border-dashed border-border px-4 py-6 text-sm text-text-muted">
          Browse a section or poem to inspect metadata.
        </div>
      </aside>
    )
  }

  const poemFields: [string, string | number | undefined][] = activePoem
    ? [
        ['type', activePoem.frontmatter.type],
        ['order', activePoem.frontmatter.order],
        ['lines', activePoem.line_count],
        ['subtitle', activePoem.frontmatter.subtitle || '—'],
        ['epigraph', summarize(activePoem.frontmatter.epigraph)],
        ['dedication', activePoem.frontmatter.dedication || '—'],
        ['cycle', activePoem.frontmatter.cycle || '—'],
        ['cycle part', activePoem.frontmatter.cycle_part],
      ]
    : []

  return (
    <aside className="w-72 border-l border-border bg-panel flex flex-col overflow-hidden">
      <div className="border-b border-border px-4 py-4">
        <p className="text-[11px] uppercase tracking-[0.24em] text-text-muted">Inspector</p>
        <h3 className="mt-2 text-sm text-text-primary">
          {activePoem ? activePoem.frontmatter.title : activeSection?.label}
        </h3>
        <p className="mt-1 text-xs text-text-muted">
          {activePoem ? activePoem.filename : activeSection?.id}
        </p>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4">
        {activeSection && (
          <section className="rounded-2xl border border-border bg-surface/80 p-4">
            <div className="flex items-start gap-3">
              <div className="inline-flex rounded-full bg-card p-2 text-text-muted">
                <Layers3 className="h-4 w-4" />
              </div>
              <div>
                <p className="text-sm text-text-primary">Section</p>
                <p className="mt-1 text-xs text-text-muted">{activeSection.label}</p>
              </div>
            </div>

            <dl className="mt-4 space-y-2 text-xs">
              <MetaRow label="directory" value={activeSection.id} />
              <MetaRow label="order" value={activeSection.order} />
              <MetaRow label="poems" value={activeSection.poem_count} />
              <MetaRow label="cycle section" value={activeSection.section_is_cycle ? 'yes' : 'no'} />
              {'has_title_page' in activeSection && (
                <MetaRow label="title page" value={hasTitlePage ? 'present' : 'none'} />
              )}
            </dl>
          </section>
        )}

        {activePoem ? (
          <>
            <section className="mt-4 rounded-2xl border border-border bg-surface/80 p-4">
              <div className="flex items-start gap-3">
                <div className="inline-flex rounded-full bg-card p-2 text-text-muted">
                  <ScrollText className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-sm text-text-primary">Poem metadata</p>
                  <p className="mt-1 text-xs text-text-muted">
                    Structured frontmatter from the active file
                  </p>
                </div>
              </div>

              <dl className="mt-4 space-y-2 text-xs">
                {poemFields.map(([label, value]) => (
                  <MetaRow key={label} label={label} value={value ?? '—'} />
                ))}
              </dl>
            </section>

            {activeSection && (
              <section className="mt-4 rounded-2xl border border-border bg-surface/80 p-4">
                <div className="flex items-start gap-3">
                  <div className="inline-flex rounded-full bg-card p-2 text-text-muted">
                    <Info className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-sm text-text-primary">Versions</p>
                    <p className="mt-1 text-xs text-text-muted">
                      Promote a different canonical draft without leaving the card editor.
                    </p>
                  </div>
                </div>

                <div className="mt-4">
                  <VersionList projectId={projectId} sectionId={activeSection.id} slug={activePoem.slug} />
                </div>
              </section>
            )}
          </>
        ) : (
          <section className="mt-4 rounded-2xl border border-dashed border-border px-4 py-5 text-sm text-text-muted">
            Select a poem in this section to open the editor and inspect frontmatter.
          </section>
        )}
      </div>
    </aside>
  )
}

function MetaRow({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex items-start justify-between gap-3">
      <dt className="shrink-0 text-text-muted">{label}</dt>
      <dd className="text-right font-mono text-text-secondary">{String(value)}</dd>
    </div>
  )
}

function summarize(value: string | undefined): string {
  if (!value) return '—'
  return value.length > 60 ? `${value.slice(0, 57)}...` : value
}
