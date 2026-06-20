import { useEffect } from 'react'
import { Star } from 'lucide-react'
import { poemsApi } from '@/api/poems'
import { useEditorStore } from '@/store/useEditorStore'
import { useGraphStore } from '@/store/useGraphStore'
import { useVersionStore } from '@/store/useVersionStore'
import type { VersionEntry } from '@/types/version'

interface Props {
  projectId: string
  sectionId: string
  slug: string
}

export default function VersionList({ projectId, sectionId, slug }: Props) {
  const { versionsBySlug, loadVersions, setCanonical } = useVersionStore()
  const { activePoem, setActivePoem } = useEditorStore()
  const { loadPoems } = useGraphStore()
  const versionData = versionsBySlug[`${sectionId}::${slug}`]

  useEffect(() => {
    void loadVersions(projectId, sectionId, slug)
  }, [projectId, sectionId, slug, loadVersions])

  async function handleSetCanonical(file: string) {
    await setCanonical(projectId, sectionId, slug, file)
    await loadPoems(projectId, sectionId, true)

    if (activePoem?.section_id === sectionId && activePoem.slug === slug) {
      const detail = await poemsApi.get(projectId, sectionId, slug)
      setActivePoem(detail)
    }
  }

  if (!versionData) return <p className="text-text-muted text-xs">Loading…</p>

  return (
    <div className="flex flex-col gap-2">
      {versionData.versions.map((version: VersionEntry) => (
        <div
          key={version.file}
          className={`flex items-center justify-between gap-3 rounded-xl border px-3 py-2 text-xs ${
            version.is_canonical
              ? 'border-accent/30 bg-accent/10'
              : 'border-border bg-card'
          }`}
        >
          <div className="min-w-0">
            <p className="truncate font-mono text-text-secondary">{version.label || version.file}</p>
            <p className="mt-1 text-[11px] text-text-muted">{version.file}</p>
          </div>

          <div className="flex shrink-0 items-center gap-2">
            <span className="text-text-muted">{version.lines}L</span>
            {version.is_canonical ? (
              <span className="inline-flex items-center gap-1 rounded-full border border-accent/25 px-2 py-1 text-[11px] text-accent">
                <Star className="h-3 w-3 fill-current" />
                Canon
              </span>
            ) : (
              <button
                type="button"
                onClick={() => void handleSetCanonical(version.file)}
                className="text-text-muted transition hover:text-accent"
                title="Set as canonical"
              >
                <Star className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
