import { ArrowRight, ArrowUpRight, FileInput, FolderOpen, Home, Plus } from 'lucide-react'
import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useProjectStore } from '@/store/useProjectStore'

const commands = [
  {
    label: 'Ingest Documents',
    detail: 'Attach sources to an existing project.',
    to: '/ingest',
    icon: FileInput,
  },
  {
    label: 'Create Project',
    detail: 'Name the work and prepare its folders.',
    to: '/projects/new',
    icon: Plus,
  },
  {
    label: 'Continue Project',
    detail: 'Open a registered project.',
    to: '/projects',
    icon: FolderOpen,
  },
]

export default function StudioHome() {
  const { workspace, loading, error, loadWorkspace } = useProjectStore()

  useEffect(() => {
    loadWorkspace()
  }, [loadWorkspace])

  return (
    <main className="min-h-screen bg-[#0b0b0a] px-5 py-6 text-[#ebe7de]">
      <div className="mx-auto flex min-h-[calc(100vh-3rem)] max-w-5xl flex-col">
        <header className="flex flex-wrap items-start justify-between gap-4 border-b border-[#343129] pb-6">
          <div>
            <p className="text-[11px] uppercase tracking-[0.18em] text-[#8f887b]">Texgraph Studio</p>
            <h1 className="mt-3 text-2xl font-medium tracking-normal">Project desk</h1>
          </div>
          <a
            href="https://stexpedite.press"
            className="inline-flex items-center gap-2 rounded-md border border-[#343129] px-3 py-2 text-xs text-[#b8b0a1] transition hover:border-[#676050] hover:text-[#ebe7de]"
          >
            <Home className="h-3.5 w-3.5" />
            Return Home
            <ArrowUpRight className="h-3.5 w-3.5" />
          </a>
        </header>

        <section className="grid flex-1 gap-10 py-8 lg:grid-cols-[minmax(0,1fr)_18rem]">
          <div className="content-start border-y border-[#343129]">
            {commands.map(({ label, detail, to, icon: Icon }) => (
              <Link
                key={label}
                to={to}
                className="group grid grid-cols-[2.75rem_minmax(0,1fr)_auto] items-center gap-4 border-b border-[#343129] px-1 py-6 transition last:border-b-0 hover:bg-[#11100e]"
              >
                <span className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-[#343129] text-[#8fb996] transition group-hover:border-[#8fb996]/60">
                  <Icon className="h-5 w-5" />
                </span>
                <span className="min-w-0">
                  <span className="block text-base font-medium text-[#ebe7de]">{label}</span>
                  <span className="mt-1 block text-xs leading-5 text-[#8f887b]">{detail}</span>
                </span>
                <ArrowRight className="h-4 w-4 text-[#8f887b] transition group-hover:translate-x-1 group-hover:text-[#8fb996]" />
              </Link>
            ))}
          </div>

          <aside className="self-start border-l border-[#343129] pl-5">
            <h2 className="text-sm font-medium">Workspace</h2>
            {loading && <p className="mt-3 text-xs text-[#8f887b]">Loading workspace...</p>}
            {error && (
              <p className="mt-3 border-l border-red-400/50 pl-3 text-xs leading-5 text-red-100">
                {error}
              </p>
            )}
            {workspace && (
              <dl className="mt-3 space-y-3 text-xs">
                <div>
                  <dt className="text-[#8f887b]">Path</dt>
                  <dd className="mt-1 break-all font-mono text-[#c9c1b2]">{workspace.workspace_path}</dd>
                </div>
                <div className="flex items-center justify-between border-t border-[#343129] pt-3">
                  <dt className="text-[#8f887b]">Projects</dt>
                  <dd className="text-[#ebe7de]">{workspace.projects.length}</dd>
                </div>
                <div className="flex items-center justify-between border-t border-[#343129] pt-3">
                  <dt className="text-[#8f887b]">Default</dt>
                  <dd className="max-w-[10rem] truncate text-[#ebe7de]">{workspace.default_project ?? 'None'}</dd>
                </div>
              </dl>
            )}
          </aside>
        </section>
      </div>
    </main>
  )
}
