import { ArrowLeft, Bot } from 'lucide-react'
import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { projectsApi } from '@/api/projects'

export default function ProjectConfig() {
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const wizardMode = params.get('wizard') === '1'

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
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const set = (key: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [key]: e.target.value }))

  const handleCreate = async () => {
    setSaving(true)
    setError('')
    try {
      const body = {
        id: form.id,
        path: form.path || `projects/${form.id}/typeset`,
        description: form.description,
        meta: {
          title: form.title,
          author: form.author,
          subtitle: form.subtitle,
          year: form.year ? parseInt(form.year) : undefined,
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
      setError(String(e))
    } finally {
      setSaving(false)
    }
  }

  if (wizardMode) {
    return (
      <div className="min-h-screen bg-canvas px-6 py-10">
        <div className="mx-auto max-w-2xl">
          <div className="rounded-[2rem] border border-agent/35 bg-agent-surface p-8">
            <div className="inline-flex rounded-full border border-agent/35 bg-agent/10 p-3 text-agent-text">
              <Bot className="h-5 w-5" />
            </div>
            <h1 className="mt-5 text-2xl text-text-primary">Project wizard is not available in this frontend path</h1>
            <p className="mt-3 text-sm leading-6 text-text-secondary">
              The wizard route no longer renders blank, but the tested Studio path is still the manual project form.
              Use the standard config flow below until the wizard UI is wired back in.
            </p>

            <div className="mt-6 flex flex-wrap gap-3">
              <button
                type="button"
                onClick={() => navigate('/projects/new')}
                className="inline-flex items-center gap-2 rounded-xl bg-accent px-4 py-2 text-sm font-medium text-white transition hover:bg-accent-hover"
              >
                <ArrowLeft className="h-4 w-4" />
                Open manual setup
              </button>
              <button
                type="button"
                onClick={() => navigate('/projects')}
                className="rounded-xl border border-border px-4 py-2 text-sm text-text-secondary transition hover:text-text-primary"
              >
                Back to projects
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const Field = ({ label, k, placeholder }: { label: string; k: string; placeholder?: string }) => (
    <div className="flex flex-col gap-1">
      <label className="text-text-muted text-xs uppercase tracking-wide">{label}</label>
      <input
        value={(form as Record<string, string>)[k]}
        onChange={set(k)}
        placeholder={placeholder}
        className="bg-card border border-border rounded px-3 py-1.5 text-sm text-text-primary font-mono focus:outline-none focus:border-accent"
      />
    </div>
  )

  return (
    <div className="min-h-screen bg-canvas p-8">
      <div className="max-w-2xl mx-auto">
        <div className="text-text-muted text-xs mb-6">Projects › New Project › Configure</div>
        <h1 className="text-lg font-mono text-text-primary mb-8">Configure New Project</h1>

        <div className="flex flex-col gap-4 mb-8">
          <Field label="Project ID" k="id" placeholder="my-collection" />
          <Field label="Title" k="title" placeholder="Collection Title" />
          <Field label="Author" k="author" placeholder="Author Name" />
          <Field label="Subtitle" k="subtitle" />
          <Field label="Year" k="year" placeholder="2025" />
          <Field label="Publisher" k="publisher" />
          <Field label="ISBN" k="isbn" />
          <Field label="Path (relative to workspace root)" k="path" placeholder="projects/my-collection/typeset" />
          <Field label="Description" k="description" />
        </div>

        {error && <p className="text-red-400 text-sm mb-4">{error}</p>}

        <div className="border border-agent/40 bg-agent-surface rounded-lg p-4 mb-6">
          <p className="text-agent-text text-sm">
            ⬡ Prefer the conversational approach?{' '}
            <button
              onClick={() => navigate('/projects/new?wizard=1')}
              className="underline hover:text-white"
            >
              Set up this project with the AI Agent instead
            </button>
          </p>
        </div>

        <div className="flex gap-3 justify-end">
          <button
            onClick={() => navigate('/projects')}
            className="px-4 py-2 text-sm text-text-secondary border border-border rounded hover:text-text-primary transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleCreate}
            disabled={saving || !form.id || !form.title || !form.author}
            className="px-4 py-2 text-sm bg-accent hover:bg-accent-hover text-white rounded disabled:opacity-50 transition-colors"
          >
            {saving ? 'Creating…' : 'Create →'}
          </button>
        </div>
      </div>
    </div>
  )
}
