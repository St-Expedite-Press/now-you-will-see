import { ArrowLeft, ArrowRight, FileText, Plus } from 'lucide-react'
import { useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useProjectStore } from '@/store/useProjectStore'

export default function ProjectSelect() {
  const navigate = useNavigate()
  const { workspace, loading, error, loadWorkspace } = useProjectStore()

  useEffect(() => {
    loadWorkspace()
  }, [loadWorkspace])

  return (
    <main className="min-h-screen bg-[#0b0b0a] px-5 py-6 text-[#ebe7de]">
      <div className="mx-auto max-w-5xl">
        <header className="flex flex-wrap items-start justify-between gap-4 border-b border-[#343129] pb-6">
          <div>
            <Link to="/" className="inline-flex items-center gap-2 text-xs text-[#8f887b] hover:text-[#ebe7de]">
              <ArrowLeft className="h-3.5 w-3.5" />
              Studio entry
            </Link>
            <h1 className="mt-3 text-2xl font-medium text-[#ebe7de]">Continue Project</h1>
            <p className="mt-1 break-all text-xs text-[#8f887b]">{workspace?.workspace_path}</p>
          </div>
          <Link
            to="/projects/new"
            className="inline-flex items-center gap-2 rounded-md border border-[#343129] px-3 py-2 text-xs text-[#b8b0a1] transition hover:border-[#676050] hover:text-[#ebe7de]"
          >
            <Plus className="h-3.5 w-3.5" />
            Create Project
          </Link>
        </header>

        <section className="py-8">
          {loading && <p className="text-sm text-[#8f887b]">Loading workspace...</p>}
          {error && (
            <p className="border-l border-red-400/50 pl-3 text-sm text-red-100">
              {error}
            </p>
          )}

          {workspace && workspace.projects.length === 0 && (
            <div className="border-y border-[#343129] py-6">
              <p className="text-sm text-[#ebe7de]">No projects are registered.</p>
              <Link
                to="/projects/new"
                className="mt-4 inline-flex items-center gap-2 rounded-md border border-[#8fb996]/50 px-3 py-2 text-xs font-medium text-[#8fb996]"
              >
                <Plus className="h-3.5 w-3.5" />
                Create Project
              </Link>
            </div>
          )}

          {workspace && workspace.projects.length > 0 && (
            <div className="border-y border-[#343129]">
              {workspace.projects.map((project) => (
                <button
                  key={project.id}
                  type="button"
                  onClick={() => navigate(`/projects/${project.id}`)}
                  className="group grid w-full grid-cols-[2.5rem_minmax(0,1fr)_auto] items-center gap-4 border-b border-[#343129] px-1 py-5 text-left transition last:border-b-0 hover:bg-[#11100e]"
                >
                  <span className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-[#343129] text-[#8fb996] transition group-hover:border-[#8fb996]/60">
                    <FileText className="h-5 w-5" />
                  </span>
                  <span className="min-w-0">
                    <span className="block truncate text-sm font-medium text-[#ebe7de]">{project.id}</span>
                    <span className="mt-1 block truncate text-xs text-[#8f887b]">{project.path}</span>
                    {project.description && (
                      <span className="mt-1 block text-xs leading-5 text-[#b8b0a1]">{project.description}</span>
                    )}
                  </span>
                  <ArrowRight className="h-4 w-4 text-[#8f887b] transition group-hover:translate-x-1 group-hover:text-[#8fb996]" />
                </button>
              ))}
            </div>
          )}

          <div className="mt-8 border-l border-[#343129] pl-4">
            <p className="text-sm text-[#8f887b]">New Project</p>
            <Link
              to="/projects/new"
              className="mt-3 inline-flex items-center gap-2 rounded-md border border-[#343129] px-3 py-2 text-xs text-[#b8b0a1] transition hover:border-[#676050] hover:text-[#ebe7de]"
            >
              <Plus className="h-3.5 w-3.5" />
              Create Project
            </Link>
          </div>
        </section>
      </div>
    </main>
  )
}
