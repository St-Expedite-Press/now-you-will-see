import { ArrowLeft, CheckCircle2, FileText, FolderTree, Plus } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { projectsApi } from '@/api/projects'
import { useProjectStore } from '@/store/useProjectStore'

const steps = ['Identity', 'Metadata', 'Output targets', 'Preview']
const stageDirs = ['ingest', 'transcribe', 'proof', 'typeset', 'covers', 'front-end', 'final']

export default function ProjectConfig() {
  const navigate = useNavigate()
  const { workspace, loadWorkspace } = useProjectStore()
  const [form, setForm] = useState({
    id: '',
    path: '',
    description: '',
    title: '',
    author: '',
    subtitle: '',
    year: '',
    publisher: '',
    isbn: '',
    publicationType: 'poetry_collection',
    outputTargets: 'print_pdf',
    initialStage: 'ingest',
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    loadWorkspace()
  }, [loadWorkspace])

  const effectivePath = form.path || (form.id ? `projects/${form.id}/typeset` : 'projects/<project-id>/typeset')
  const valid = Boolean(form.id && form.title && form.author)

  const collectionPreview = useMemo(() => {
    return [
      `title: "${form.title || 'Collection Title'}"`,
      `author: "${form.author || 'Author Name'}"`,
      form.subtitle ? `subtitle: "${form.subtitle}"` : 'subtitle: ""',
      form.year ? `year: ${form.year}` : 'year: null',
      `publisher: "${form.publisher || ''}"`,
      `isbn: "${form.isbn || ''}"`,
      'content_dir: content',
      'output_dir: output',
      'lualatex_path: lualatex',
      'draft_mode: false',
    ].join('\n')
  }, [form])

  const set = (key: keyof typeof form) => (
    event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => setForm((current) => ({ ...current, [key]: event.target.value }))

  const handleCreate = async () => {
    if (!valid) return
    setSaving(true)
    setError('')
    try {
      const body = {
        id: form.id,
        path: effectivePath,
        description: form.description,
        meta: {
          title: form.title,
          author: form.author,
          subtitle: form.subtitle,
          year: form.year ? parseInt(form.year, 10) : undefined,
          publisher: form.publisher,
          isbn: form.isbn,
          content_dir: 'content',
          output_dir: 'output',
          lualatex_path: 'lualatex',
          draft_mode: false,
        },
      }
      const project = await projectsApi.create(body)
      navigate(`/projects/${project.id}`)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setSaving(false)
    }
  }

  return (
    <main className="flex min-h-screen flex-col bg-[#0b0b0a] text-[#ebe7de]">
      <header className="border-b border-[#343129] px-5 py-6">
        <div className="mx-auto flex max-w-6xl flex-wrap items-start justify-between gap-4">
          <div>
            <Link to="/" className="inline-flex items-center gap-2 text-xs text-[#8f887b] hover:text-[#ebe7de]">
              <ArrowLeft className="h-3.5 w-3.5" />
              Studio entry
            </Link>
            <div className="mt-4 flex items-center gap-3">
              <span className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-[#343129] text-[#8fb996]">
                <Plus className="h-5 w-5" />
              </span>
              <div>
                <h1 className="text-2xl font-medium">Create Project</h1>
                <p className="mt-1 text-xs text-[#8f887b]">{workspace?.workspace_path ?? 'Workspace not loaded'}</p>
              </div>
            </div>
          </div>
          <Link
            to="/"
            className="inline-flex items-center gap-2 rounded-md border border-[#343129] px-3 py-2 text-xs text-[#b8b0a1] transition hover:border-[#676050] hover:text-[#ebe7de]"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Cancel
          </Link>
        </div>
      </header>

      <div className="mx-auto w-full max-w-6xl flex-1 px-5 py-7">
        <div className="flex flex-wrap gap-x-6 gap-y-2 border-b border-[#343129] pb-5">
          {steps.map((step, index) => (
            <div key={step} className="flex items-center gap-2 text-xs">
              <span className="font-mono text-[#8fb996]">{String(index + 1).padStart(2, '0')}</span>
              <span className="text-[#b8b0a1]">{step}</span>
            </div>
          ))}
        </div>

        <div className="grid gap-8 pt-7 lg:grid-cols-[minmax(0,1fr)_22rem]">
          <section className="min-w-0">
            <div className="grid gap-x-5 gap-y-5 md:grid-cols-2">
              <Field label="Project ID" value={form.id} onChange={set('id')} placeholder="my-collection" required />
              <Field label="Path" value={form.path} onChange={set('path')} placeholder={effectivePath} />
              <Field label="Title" value={form.title} onChange={set('title')} placeholder="Collection Title" required />
              <Field label="Author/editor" value={form.author} onChange={set('author')} placeholder="Author Name" required />
              <Field label="Subtitle" value={form.subtitle} onChange={set('subtitle')} />
              <Field label="Year" value={form.year} onChange={set('year')} placeholder="2026" />
              <Field label="Publisher" value={form.publisher} onChange={set('publisher')} />
              <Field label="ISBN" value={form.isbn} onChange={set('isbn')} />
            </div>

            <label className="mt-5 flex flex-col gap-2">
              <span className="text-[11px] uppercase tracking-[0.16em] text-[#8f887b]">Description</span>
              <textarea
                value={form.description}
                onChange={set('description')}
                rows={4}
                className="min-h-28 rounded-md border border-[#343129] bg-[#11100e] px-3 py-3 text-sm leading-6 text-[#ebe7de] outline-none transition placeholder:text-[#6f695e] focus:border-[#8fb996]/70"
              />
            </label>

            <div className="mt-6 grid gap-5 md:grid-cols-3">
              <Select label="Publication type" value={form.publicationType} onChange={set('publicationType')}>
                <option value="poetry_collection">poetry_collection</option>
                <option value="critical_edition">critical_edition</option>
                <option value="chapbook">chapbook</option>
                <option value="prose_collection">prose_collection</option>
              </Select>
              <Select label="Output target" value={form.outputTargets} onChange={set('outputTargets')}>
                <option value="print_pdf">print_pdf</option>
                <option value="proof_pdf">proof_pdf</option>
                <option value="epub_later">epub_later</option>
                <option value="web_later">web_later</option>
              </Select>
              <Select label="Initial stage" value={form.initialStage} onChange={set('initialStage')}>
                <option value="ingest">ingest</option>
                <option value="typeset">typeset</option>
                <option value="proof">proof</option>
              </Select>
            </div>

            {error && (
              <p className="mt-5 border-l border-red-400/50 pl-3 text-sm text-red-100">
                {error}
              </p>
            )}
          </section>

          <aside className="space-y-6 border-l border-[#343129] pl-5">
            <section>
              <div className="flex items-center gap-2 text-sm font-medium">
                <FolderTree className="h-4 w-4 text-[#8fb996]" />
                Project body
              </div>
              <div className="mt-3 font-mono text-[11px] leading-5 text-[#b8b0a1]">
                <div>{effectivePath.replace(/\/typeset$/, '')}/</div>
                {stageDirs.map((stage) => (
                  <div key={stage} className="pl-3">{stage}/</div>
                ))}
              </div>
            </section>

            <section className="border-t border-[#343129] pt-5">
              <div className="flex items-center gap-2 text-sm font-medium">
                <CheckCircle2 className="h-4 w-4 text-[#8fb996]" />
                Workspace entry
              </div>
              <pre className="mt-3 whitespace-pre-wrap font-mono text-[11px] leading-5 text-[#b8b0a1]">
{`id: ${form.id || '<project-id>'}
path: ${effectivePath}
description: "${form.description || ''}"`}
              </pre>
            </section>

            <section className="border-t border-[#343129] pt-5">
              <div className="flex items-center gap-2 text-sm font-medium">
                <FileText className="h-4 w-4 text-[#8fb996]" />
                collection.yaml
              </div>
              <pre className="mt-3 max-h-56 overflow-y-auto whitespace-pre-wrap font-mono text-[11px] leading-5 text-[#b8b0a1]">
                {collectionPreview}
              </pre>
            </section>
          </aside>
        </div>
      </div>

      <footer className="border-t border-[#343129] px-5 py-4">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3">
          <Link to="/" className="inline-flex items-center gap-2 rounded-md border border-[#343129] px-3 py-2 text-xs text-[#b8b0a1] transition hover:border-[#676050] hover:text-[#ebe7de]">
            <ArrowLeft className="h-3.5 w-3.5" />
            Back to entry
          </Link>
          <button
            type="button"
            onClick={handleCreate}
            disabled={saving || !valid}
            className="inline-flex items-center gap-2 rounded-md border border-[#8fb996]/50 px-3 py-2 text-xs font-medium text-[#8fb996] transition hover:bg-[#8fb996]/10 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Plus className="h-3.5 w-3.5" />
            {saving ? 'Creating' : 'Create Project'}
          </button>
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
  required = false,
}: {
  label: string
  value: string
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void
  placeholder?: string
  required?: boolean
}) {
  return (
    <label className="flex flex-col gap-2">
      <span className="text-[11px] uppercase tracking-[0.16em] text-[#8f887b]">
        {label}{required ? ' *' : ''}
      </span>
      <input
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="rounded-md border border-[#343129] bg-[#11100e] px-3 py-2.5 text-sm text-[#ebe7de] outline-none transition placeholder:text-[#6f695e] focus:border-[#8fb996]/70"
      />
    </label>
  )
}

function Select({
  label,
  value,
  onChange,
  children,
}: {
  label: string
  value: string
  onChange: (event: React.ChangeEvent<HTMLSelectElement>) => void
  children: React.ReactNode
}) {
  return (
    <label className="flex flex-col gap-2">
      <span className="text-[11px] uppercase tracking-[0.16em] text-[#8f887b]">{label}</span>
      <select
        value={value}
        onChange={onChange}
        className="rounded-md border border-[#343129] bg-[#11100e] px-3 py-2.5 text-sm text-[#ebe7de] outline-none transition focus:border-[#8fb996]/70"
      >
        {children}
      </select>
    </label>
  )
}
