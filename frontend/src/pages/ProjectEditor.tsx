import { useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useProjectStore } from '@/store/useProjectStore'
import TopBar from '@/components/layout/TopBar'
import CardBrowser from '@/components/cards/CardBrowser'
import CardFrame from '@/components/cards/CardFrame'
import PropertiesPanel from '@/components/properties/PropertiesPanel'
import GraphCanvas from '@/components/graph/GraphCanvas'
import BuildPanel from '@/components/build/BuildPanel'
import CoverStudio from '@/pages/CoverStudio'
import AuditDashboard from '@/pages/AuditDashboard'
import AgentPanel from '@/components/agent/AgentPanel'
import { useAgentStore } from '@/store/useAgentStore'
import { useEditorStore } from '@/store/useEditorStore'

export type { ViewMode } from '@/store/useEditorStore'

export default function ProjectEditor() {
  const { projectId } = useParams<{ projectId: string }>()
  const { loadProject, activeProject, loading, error } = useProjectStore()
  const { isOpen: agentOpen } = useAgentStore()
  const { activeView: view, setActiveView: setView } = useEditorStore()

  useEffect(() => {
    if (projectId) loadProject(projectId)
  }, [projectId, loadProject])

  if (loading || (projectId && activeProject?.id !== projectId && !error)) {
    return (
      <div className="min-h-screen bg-canvas flex items-center justify-center text-text-muted text-sm">
        Loading project...
      </div>
    )
  }

  if (error || !activeProject || activeProject.id !== projectId) {
    return (
      <div className="min-h-screen bg-canvas flex items-center justify-center px-6">
        <div className="max-w-lg rounded-3xl border border-border bg-surface px-6 py-8 text-center">
          <p className="text-lg text-text-primary">Project unavailable</p>
          <p className="mt-3 text-sm leading-6 text-text-muted">
            {error ?? 'The requested project could not be loaded from the current workspace.'}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col bg-canvas overflow-hidden">
      <TopBar view={view} onViewChange={setView} projectId={projectId!} />

      <div className="flex-1 flex overflow-hidden relative">
        {view === 'cards' && (
          <>
            <CardBrowser projectId={projectId!} />
            <div className="flex-1 overflow-hidden">
              <CardFrame projectId={projectId!} />
            </div>
            <PropertiesPanel projectId={projectId!} />
          </>
        )}

        {view === 'graph' && <GraphCanvas projectId={projectId!} />}

        {view === 'build' && <BuildPanel projectId={projectId!} />}

        {view === 'covers' && <CoverStudio projectId={projectId!} />}

        {view === 'audit' && <AuditDashboard projectId={projectId!} />}

        {agentOpen && (
          <div className="absolute right-0 top-0 bottom-0 w-80 border-l border-border z-10">
            <AgentPanel projectId={projectId!} />
          </div>
        )}
      </div>
    </div>
  )
}
