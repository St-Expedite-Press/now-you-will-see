import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useProjectStore } from '@/store/useProjectStore'

export default function ProjectSelect() {
  const navigate = useNavigate()
  const { workspace, loading, error, loadWorkspace } = useProjectStore()

  useEffect(() => {
    loadWorkspace()
  }, [loadWorkspace])

  return (
    <div className="min-h-screen bg-canvas p-8">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-lg font-mono text-text-primary">⬡ Texgraph Studio</h1>
          <span className="text-text-muted text-xs">{workspace?.workspace_path}</span>
        </div>

        {loading && <p className="text-text-muted text-sm">Loading workspace…</p>}
        {error && <p className="text-red-400 text-sm">{error}</p>}

        <div className="grid grid-cols-1 gap-4">
          {workspace?.projects.map((p) => (
            <button
              key={p.id}
              onClick={() => navigate(`/projects/${p.id}`)}
              className="text-left border border-border bg-panel rounded-lg p-5 hover:border-accent transition-colors"
            >
              <div className="flex items-center justify-between">
                <span className="text-text-primary font-mono font-bold">{p.id}</span>
                <span className="text-text-muted text-xs">{p.path}</span>
              </div>
              {p.description && (
                <p className="text-text-secondary text-sm mt-1">{p.description}</p>
              )}
            </button>
          ))}

          {/* New project card */}
          <div className="border border-dashed border-border rounded-lg p-5">
            <p className="text-text-muted text-sm mb-3">New Project</p>
            <div className="flex gap-3">
              <button
                onClick={() => navigate('/projects/new')}
                className="text-sm text-text-secondary hover:text-text-primary border border-border rounded px-3 py-1.5 transition-colors"
              >
                ⊞ Configure manually
              </button>
              <button
                onClick={() => navigate('/projects/new?wizard=1')}
                className="text-sm text-agent-text hover:text-white border border-agent rounded px-3 py-1.5 transition-colors"
              >
                ⬡ Set up with Agent
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
