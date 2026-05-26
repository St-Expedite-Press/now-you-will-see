import { useState, useEffect } from 'react'
import { api } from '@/api/client'
import type { MergedRenderConfig } from '@/types/renderConfig'

interface Props {
  projectId: string
  sectionId?: string
}

export default function RenderConfigPanel({ projectId, sectionId }: Props) {
  const [config, setConfig] = useState<MergedRenderConfig | null>(null)
  const [expanded, setExpanded] = useState(false)

  useEffect(() => {
    const url = `/projects/${projectId}/render-config/merged${sectionId ? `?section_id=${sectionId}` : ''}`
    api.get<MergedRenderConfig>(url).then((r) => setConfig(r.data)).catch(() => {})
  }, [projectId, sectionId])

  if (!expanded) {
    return (
      <button
        onClick={() => setExpanded(true)}
        className="absolute top-3 right-3 text-xs text-text-muted border border-border rounded px-2 py-1 bg-surface hover:text-text-primary transition-colors"
      >
        ⚙ Render Config
      </button>
    )
  }

  return (
    <div className="absolute top-3 right-3 w-56 bg-panel border border-border rounded-lg p-3 text-xs font-mono">
      <div className="flex items-center justify-between mb-2">
        <span className="text-text-secondary">Render Config</span>
        <button onClick={() => setExpanded(false)} className="text-text-muted hover:text-text-primary">✕</button>
      </div>

      {config?.resolved && Object.entries(config.resolved).filter(([, v]) => v != null).map(([k, v]) => (
        <div key={k} className="flex gap-2 text-[11px] mb-0.5">
          <span className="text-text-muted w-24 shrink-0">{k}</span>
          <span className="text-text-secondary">{String(v)}</span>
        </div>
      ))}

      {(!config || Object.values(config.resolved).every((v) => v == null)) && (
        <p className="text-text-muted text-[11px]">No custom config — using LaTeX defaults</p>
      )}
    </div>
  )
}
