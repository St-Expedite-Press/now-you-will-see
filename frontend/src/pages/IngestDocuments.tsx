import { ArrowLeft, CheckCircle2, FileInput, Info, Loader2, Search, ShieldAlert } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { projectsApi } from '@/api/projects'
import type { ProjectDetail } from '@/types/project'

type IntakeMode = 'local' | 'archive' | 'manual'
type GateStatus = 'not_started' | 'pending' | 'blocked' | 'ready'

const stageItems = ['Source candidates', 'Registered sources', 'Gate checklist']

const gateLabels: Record<GateStatus, string> = {
  not_started: 'Not started',
  pending: 'Pending',
  blocked: 'Blocked',
  ready: 'Ready',
}

export default function IngestDocuments() {
  const { projectId } = useParams<{ projectId: string }>()
  const [project, setProject] = useState<ProjectDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [mode, setMode] = useState<IntakeMode>('local')
  const [gateStatus, setGateStatus] = useState<GateStatus>('not_started')
  const [form, setForm] = useState({
    author: '',
    year: '',
    title: '',
    source: 'upload',
    extension: 'pdf',
    rights: 'unknown',
    accessConfirmed: false,
    notes: '',
  })

  useEffect(() => {
    let cancelled = false
    async function load() {
      if (!projectId) return
      setLoading(true)
      setError('')
      try {
        const detail = await projectsApi.get(projectId)
        if (!cancelled) setProject(detail)
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e))
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    void load()
    return () => {
      cancelled = true
    }
  }, [projectId])

  const stableName = useMemo(() => {
    const author = form.author || 'author'
    const year = form.year || 'year'
    const title = form.title || 'title'
    const source = form.source || 'source'
    const ext = form.extension || 'pdf'
    return `${slug(author)}_${year}_${slug(title)}_${slug(source)}.${ext.replace(/^\./, '')}`
  }, [form])

  const set = (key: keyof typeof form) => (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const value = event.target instanceof HTMLInputElement && event.target.type === 'checkbox'
      ? event.target.checked
      : event.target.value
    setForm((current) => ({ ...current, [key]: value }))
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0b0b0a] px-5 py-6 text-[#8f887b]">
        <Loader2 className="h-4 w-4 animate-spin" />
      </div>
    )
  }

  if (error || !project) {
    return (
      <div className="min-h-screen bg-[#0b0b0a] px-5 py-6 text-[#ebe7de]">
        <div className="mx-auto max-w-xl border-l border-red-400/50 pl-4">
          <p className="text-sm">Project unavailable</p>
          <p className="mt-2 text-xs leading-5 text-[#8f887b]">{error || 'The project could not be loaded.'}</p>
          <Link to="/ingest" className="mt-4 inline-flex items-center gap-2 text-xs text-[#8fb996]">
            <ArrowLeft className="h-3.5 w-3.5" />
            Choose another project
          </Link>
        </div>
      </div>
    )
  }

  return (
    <main className="flex min-h-screen flex-col bg-[#0b0b0a] text-[#ebe7de]">
      <header className="border-b border-[#343129] px-5 py-6">
        <div className="mx-auto flex max-w-6xl flex-wrap items-start justify-between gap-5">
          <div>
            <Link to="/ingest" className="inline-flex items-center gap-2 text-xs text-[#8f887b] hover:text-[#ebe7de]">
              <ArrowLeft className="h-3.5 w-3.5" />
              Choose project
            </Link>
            <div className="mt-4 flex items-center gap-3">
              <span className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-[#343129] text-[#8fb996]">
                <FileInput className="h-4 w-4" />
              </span>
              <div>
                <h1 className="text-2xl font-medium">{project.meta.title || project.id}</h1>
                <p className="mt-1 text-xs uppercase tracking-[0.16em] text-[#8f887b]">Sources module</p>
              </div>
            </div>
          </div>
          <div className="flex max-w-full flex-wrap items-center gap-2">
            {(['not_started', 'pending', 'blocked', 'ready'] as GateStatus[]).map((status) => (
              <button
                key={status}
                type="button"
                onClick={() => setGateStatus(status)}
                className={`rounded-md border px-2.5 py-1.5 text-[11px] uppercase tracking-[0.12em] transition ${
                  gateStatus === status
                    ? 'border-[#8fb996]/60 text-[#8fb996]'
                    : 'border-[#343129] text-[#8f887b] hover:border-[#676050] hover:text-[#ebe7de]'
                }`}
              >
                {gateLabels[status]}
              </button>
            ))}
          </div>
        </div>
      </header>

      <div className="mx-auto w-full max-w-6xl flex-1 px-5 py-7">
        <div className="flex flex-wrap items-center gap-x-6 gap-y-3 border-b border-[#343129] pb-5">
          {stageItems.map((item, index) => (
            <div key={item} className="flex items-center gap-2 text-xs">
              <span className="font-mono text-[#8fb996]">{String(index + 1).padStart(2, '0')}</span>
              <span className="text-[#b8b0a1]">{item}</span>
            </div>
          ))}
          <div className="flex items-center gap-2 text-xs text-[#d6a657]">
            <ShieldAlert className="h-3.5 w-3.5" />
            Wireframe only
          </div>
        </div>

        <div className="grid gap-8 pt-7 lg:grid-cols-[minmax(0,1fr)_22rem]">
          <section className="min-w-0">
            <div className="flex flex-wrap gap-2">
              {([
                ['local', 'Local file'],
                ['archive', 'Internet Archive'],
                ['manual', 'Manual record'],
              ] as Array<[IntakeMode, string]>).map(([value, label]) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => setMode(value)}
                  className={`rounded-md border px-3 py-2 text-xs font-medium transition ${
                    mode === value
                      ? 'border-[#8fb996]/60 text-[#8fb996]'
                      : 'border-[#343129] text-[#8f887b] hover:border-[#676050] hover:text-[#ebe7de]'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>

            <div className="mt-6 grid gap-x-5 gap-y-5 md:grid-cols-2">
              <Field label="Author slug" value={form.author} onChange={set('author')} placeholder="gould-fletcher" />
              <Field label="Publication year" value={form.year} onChange={set('year')} placeholder="1922" />
              <Field label="Title slug" value={form.title} onChange={set('title')} placeholder="preludes-and-symphonies" />
              <Field label="Source slug" value={form.source} onChange={set('source')} placeholder="upload" />
              <Field label="Extension" value={form.extension} onChange={set('extension')} placeholder="pdf" />
              <label className="flex flex-col gap-2">
                <span className="text-[11px] uppercase tracking-[0.16em] text-[#8f887b]">Rights status</span>
                <select
                  value={form.rights}
                  onChange={set('rights')}
                  className="rounded-md border border-[#343129] bg-[#11100e] px-3 py-2.5 text-sm text-[#ebe7de] outline-none transition focus:border-[#8fb996]/70"
                >
                  <option value="unknown">unknown</option>
                  <option value="public_domain">public_domain</option>
                  <option value="licensed">licensed</option>
                  <option value="restricted">restricted</option>
                </select>
              </label>
            </div>

            <label className="mt-5 flex items-center gap-2 text-sm text-[#b8b0a1]">
              <input
                type="checkbox"
                checked={form.accessConfirmed}
                onChange={set('accessConfirmed')}
                className="h-4 w-4 accent-[#8fb996]"
              />
              Access confirmed
            </label>

            <label className="mt-5 flex flex-col gap-2">
              <span className="text-[11px] uppercase tracking-[0.16em] text-[#8f887b]">Notes</span>
              <textarea
                value={form.notes}
                onChange={set('notes')}
                rows={5}
                className="rounded-md border border-[#343129] bg-[#11100e] px-3 py-3 text-sm leading-6 text-[#ebe7de] outline-none transition focus:border-[#8fb996]/70"
              />
            </label>

            <div className="mt-6 border-l border-[#8fb996]/50 pl-4">
              <p className="text-[11px] uppercase tracking-[0.16em] text-[#8f887b]">Stable filename preview</p>
              <p className="mt-2 break-all font-mono text-sm text-[#8fb996]">{stableName}</p>
            </div>
          </section>

          <PreviewPanel
            project={project}
            gateStatus={gateStatus}
            mode={mode}
            stableName={stableName}
            rights={form.rights}
            accessConfirmed={form.accessConfirmed}
          />
        </div>
      </div>

      <footer className="border-t border-[#343129] px-5 py-4">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3">
          <Link to="/" className="inline-flex items-center gap-2 rounded-md border border-[#343129] px-3 py-2 text-xs text-[#b8b0a1] transition hover:border-[#676050] hover:text-[#ebe7de]">
            <ArrowLeft className="h-3.5 w-3.5" />
            Back to entry
          </Link>
          <div className="flex flex-wrap gap-2">
            <button type="button" disabled className="rounded-md border border-[#343129] px-3 py-2 text-xs text-[#8f887b] opacity-60">
              Save candidate
            </button>
            <button type="button" disabled className="rounded-md border border-[#343129] px-3 py-2 text-xs text-[#8f887b] opacity-60">
              Register source
            </button>
            <button type="button" disabled className="rounded-md border border-[#343129] px-3 py-2 text-xs text-[#8f887b] opacity-60">
              Verify transcription
            </button>
          </div>
        </div>
      </footer>
    </main>
  )
}

function Field({
  label,
  value,
  onChange,
  placeholder,
}: {
  label: string
  value: string
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void
  placeholder?: string
}) {
  return (
    <label className="flex flex-col gap-2">
      <span className="text-[11px] uppercase tracking-[0.16em] text-[#8f887b]">{label}</span>
      <input
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="rounded-md border border-[#343129] bg-[#11100e] px-3 py-2.5 text-sm text-[#ebe7de] outline-none transition placeholder:text-[#6f695e] focus:border-[#8fb996]/70"
      />
    </label>
  )
}

function PreviewPanel({
  project,
  gateStatus,
  mode,
  stableName,
  rights,
  accessConfirmed,
}: {
  project: ProjectDetail
  gateStatus: GateStatus
  mode: IntakeMode
  stableName: string
  rights: string
  accessConfirmed: boolean
}) {
  return (
    <aside className="space-y-6 border-l border-[#343129] pl-5">
      <section>
        <div className="flex items-center gap-2 text-sm font-medium">
          <Info className="h-4 w-4 text-[#8fb996]" />
          Gate status
        </div>
        <p className="mt-3 text-xl font-medium text-[#ebe7de]">{gateLabels[gateStatus]}</p>
        <p className="mt-2 text-xs leading-5 text-[#8f887b]">
          No files are moved. No gate is approved.
        </p>
      </section>

      <section className="border-t border-[#343129] pt-5">
        <div className="flex items-center gap-2 text-sm font-medium">
          <Search className="h-4 w-4 text-[#8fb996]" />
          PDF inspection
        </div>
        <div className="mt-3 grid grid-cols-2 gap-2">
          {[1, 2, 3, 4].map((item) => (
            <div key={item} className="aspect-[3/4] rounded-md border border-dashed border-[#343129] bg-[#11100e]" />
          ))}
        </div>
      </section>

      <section className="border-t border-[#343129] pt-5">
        <div className="flex items-center gap-2 text-sm font-medium">
          <CheckCircle2 className="h-4 w-4 text-[#8fb996]" />
          Provenance preview
        </div>
        <pre className="mt-3 whitespace-pre-wrap font-mono text-[11px] leading-5 text-[#b8b0a1]">
{`project_id: ${project.id}
mode: ${mode}
stable_name: ${stableName}
rights: ${rights}
access_confirmed: ${accessConfirmed}
status: candidate`}
        </pre>
      </section>
    </aside>
  )
}

function slug(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '') || 'untitled'
}
