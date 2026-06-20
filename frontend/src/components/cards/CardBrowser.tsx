import { useEffect, useState } from 'react'
import { ChevronRight, FilePlus2, FolderPlus, Layers3, Search, Sparkles } from 'lucide-react'
import { poemsApi } from '@/api/poems'
import { sectionsApi } from '@/api/sections'
import { useEditorStore } from '@/store/useEditorStore'
import { useGraphStore } from '@/store/useGraphStore'
import { useProjectStore } from '@/store/useProjectStore'
import type { PoemType } from '@/types/poem'
import type { SectionDetail, SectionSummary } from '@/types/section'
import CardChip from './CardChip'

interface Props {
  projectId: string
}

interface PoemFormState {
  title: string
  type: PoemType
  order: string
}

interface SectionFormState {
  label: string
  id: string
  order: string
  section_is_cycle: boolean
  title_page_title: string
  title_page_epigraph: string
  title_page_epigraph_author: string
}

const DEFAULT_POEM_FORM: PoemFormState = {
  title: '',
  type: 'poem',
  order: '',
}

const DEFAULT_SECTION_FORM: SectionFormState = {
  label: '',
  id: '',
  order: '',
  section_is_cycle: false,
  title_page_title: '',
  title_page_epigraph: '',
  title_page_epigraph_author: '',
}

const POEM_TYPE_OPTIONS: { value: PoemType; label: string }[] = [
  { value: 'poem', label: 'Poem' },
  { value: 'prose', label: 'Prose' },
  { value: 'poem-cycle', label: 'Poem cycle' },
  { value: 'poem-screenplay', label: 'Screenplay' },
]

export default function CardBrowser({ projectId }: Props) {
  const {
    projectId: graphProjectId,
    sections,
    poemsBySectionId,
    loadingSections,
    loadingPoemsBySectionId,
    error,
    selectedSectionId,
    selectedPoemSlug,
    loadSections,
    loadPoems,
    setPoems,
    resetProjectData,
    selectSection,
    selectPoem,
  } = useGraphStore()
  const {
    activeSection,
    activePoem,
    setActivePoem,
    setActiveSection,
    pendingSelect,
    setPendingSelect,
  } = useEditorStore()
  const { loadProject } = useProjectStore()

  const [query, setQuery] = useState('')
  const [showPoemForm, setShowPoemForm] = useState(false)
  const [showSectionForm, setShowSectionForm] = useState(false)
  const [poemForm, setPoemForm] = useState<PoemFormState>(DEFAULT_POEM_FORM)
  const [sectionForm, setSectionForm] = useState<SectionFormState>(DEFAULT_SECTION_FORM)
  const [sectionIdEdited, setSectionIdEdited] = useState(false)
  const [submittingPoem, setSubmittingPoem] = useState(false)
  const [submittingSection, setSubmittingSection] = useState(false)
  const [poemError, setPoemError] = useState<string | null>(null)
  const [sectionError, setSectionError] = useState<string | null>(null)
  const sectionIdValidation = validateSectionId(sectionForm.id)
  const activeSectionHasTitlePage = Boolean(
    activeSection && 'has_title_page' in activeSection && activeSection.has_title_page
  )

  useEffect(() => {
    let cancelled = false

    void (async () => {
      if (graphProjectId === projectId && sections.length > 0) {
        const restoredSectionId = activeSection?.id ?? selectedSectionId ?? sections[0]?.id
        const restoredSection = sections.find((section) => section.id === restoredSectionId) ?? sections[0]

        if (!restoredSection) {
          return
        }

        selectSection(restoredSection.id)
        if (!activeSection || activeSection.id !== restoredSection.id || !('has_title_page' in activeSection)) {
          const sectionDetail = await loadSectionRecord(projectId, restoredSection)
          if (cancelled) {
            return
          }
          setActiveSection(sectionDetail)
        }
        await loadPoems(projectId, restoredSection.id)
        return
      }

      resetProjectData()
      setActiveSection(null)
      setActivePoem(null)

      const loadedSections = await loadSections(projectId)
      if (cancelled || loadedSections.length === 0) {
        return
      }

      const firstSection = await loadSectionRecord(projectId, loadedSections[0])
      if (cancelled) {
        return
      }
      selectSection(firstSection.id)
      setActiveSection(firstSection)
      await loadPoems(projectId, firstSection.id)
    })()

    return () => {
      cancelled = true
    }
  }, [projectId, loadPoems, loadSections, resetProjectData, selectSection, setActivePoem, setActiveSection])

  useEffect(() => {
    if (!pendingSelect || sections.length === 0) return

    let cancelled = false

    void (async () => {
      const nextSection = sections.find((section) => section.id === pendingSelect.sectionId)
      if (!nextSection) {
        setPendingSelect(null)
        return
      }

      const sectionDetail = await loadSectionRecord(projectId, nextSection)
      if (cancelled) return

      selectSection(nextSection.id)
      setActiveSection(sectionDetail)
      const poems = await loadPoems(projectId, nextSection.id)
      if (cancelled) return

      const nextPoem = poems.find((poem) => poem.slug === pendingSelect.poemSlug)
      if (!nextPoem) {
        selectPoem(null)
        setActivePoem(null)
        setPendingSelect(null)
        return
      }

      const detail = await poemsApi.get(projectId, nextSection.id, nextPoem.slug)
      if (cancelled) return

      selectPoem(detail.slug)
      setActivePoem(detail)
      setPendingSelect(null)
    })()

    return () => {
      cancelled = true
    }
  }, [
    pendingSelect,
    projectId,
    graphProjectId,
    sections,
    activeSection,
    selectedSectionId,
    loadPoems,
    selectPoem,
    selectSection,
    setActivePoem,
    setActiveSection,
    setPendingSelect,
  ])

  const activeSectionId = activeSection?.id ?? selectedSectionId

  const filteredSections = sections.filter((section) => {
    const normalizedQuery = query.trim().toLowerCase()
    if (!normalizedQuery) return true

    const loadedPoems = poemsBySectionId[section.id] ?? []
    return (
      section.label.toLowerCase().includes(normalizedQuery) ||
      section.id.toLowerCase().includes(normalizedQuery) ||
      loadedPoems.some((poem) => poem.title.toLowerCase().includes(normalizedQuery))
    )
  })

  async function handleSelectSection(section: SectionSummary) {
    const sectionDetail = await loadSectionRecord(projectId, section)
    selectSection(section.id)
    selectPoem(null)
    setActiveSection(sectionDetail)
    if (activePoem?.section_id !== section.id) {
      setActivePoem(null)
    }
    setShowPoemForm(false)
    setPoemError(null)
    await loadPoems(projectId, section.id)
  }

  async function handleSelectPoem(section: SectionSummary, slug: string) {
    const detail = await poemsApi.get(projectId, section.id, slug)
    const sectionDetail =
      activeSection?.id === section.id && 'has_title_page' in activeSection
        ? activeSection
        : await loadSectionRecord(projectId, section)
    selectSection(section.id)
    selectPoem(slug)
    setActiveSection(sectionDetail)
    setActivePoem(detail)
  }

  async function openPoemForm() {
    if (!activeSectionId) return
    const poems = await loadPoems(projectId, activeSectionId)
    setPoemForm({
      title: '',
      type: 'poem',
      order: String(nextPoemOrder(poems)),
    })
    setPoemError(null)
    setShowSectionForm(false)
    setShowPoemForm((current) => !current)
  }

  function openSectionForm() {
    setSectionForm({
      ...DEFAULT_SECTION_FORM,
      order: String(nextSectionOrder(sections)),
    })
    setSectionIdEdited(false)
    setSectionError(null)
    setShowPoemForm(false)
    setShowSectionForm((current) => !current)
  }

  async function handleCreatePoem(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!activeSection) {
      setPoemError('Select a section before creating a poem.')
      return
    }

    const title = poemForm.title.trim()
    if (!title) {
      setPoemError('Title is required.')
      return
    }

    setSubmittingPoem(true)
    setPoemError(null)

    try {
      const detail = await poemsApi.create(projectId, activeSection.id, {
        title,
        type: poemForm.type,
        order: poemForm.order.trim() ? Number(poemForm.order) : undefined,
      })

      await loadProject(projectId)
      const refreshedSections = await loadSections(projectId)
      const refreshedSection = refreshedSections.find((section) => section.id === activeSection.id) ?? activeSection
      const refreshedPoems = await loadPoems(projectId, activeSection.id, true)

      setActiveSection(refreshedSection)
      selectSection(refreshedSection.id)
      selectPoem(detail.slug)
      setActivePoem(detail)
      setPoemForm({
        title: '',
        type: 'poem',
        order: String(nextPoemOrder(refreshedPoems)),
      })
      setShowPoemForm(false)
    } catch (error) {
      setPoemError(error instanceof Error ? error.message : String(error))
    } finally {
      setSubmittingPoem(false)
    }
  }

  async function handleCreateSection(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()

    const label = sectionForm.label.trim()
    const id = sectionForm.id.trim()
    if (!label) {
      setSectionError('Section label is required.')
      return
    }
    if (!id) {
      setSectionError('Section id is required.')
      return
    }
    if (sectionIdValidation) {
      setSectionError(sectionIdValidation)
      return
    }

    setSubmittingSection(true)
    setSectionError(null)

    try {
      const created = await sectionsApi.create(projectId, {
        id,
        label,
        order: sectionForm.order.trim() ? Number(sectionForm.order) : nextSectionOrder(sections),
        section_is_cycle: sectionForm.section_is_cycle,
        title_page_title: sectionForm.title_page_title.trim(),
        title_page_epigraph: sectionForm.title_page_epigraph.trim(),
        title_page_epigraph_author: sectionForm.title_page_epigraph_author.trim(),
      })

      await loadProject(projectId)
      const refreshedSections = await loadSections(projectId)
      const createdSection =
        refreshedSections.find((section) => section.id === created.id) ??
        ({
          id: created.id,
          dir_name: created.dir_name,
          label: created.label,
          order: created.order,
          poem_count: created.poem_count,
          section_is_cycle: created.section_is_cycle,
        } satisfies SectionSummary)

      selectSection(createdSection.id)
      selectPoem(null)
      setActiveSection(createdSection)
      setActivePoem(null)
      setPoems(createdSection.id, [])
      setSectionForm({
        ...DEFAULT_SECTION_FORM,
        order: String(nextSectionOrder(refreshedSections)),
      })
      setSectionIdEdited(false)
      setShowSectionForm(false)
    } catch (error) {
      setSectionError(error instanceof Error ? error.message : String(error))
    } finally {
      setSubmittingSection(false)
    }
  }

  function handleSectionLabelChange(label: string) {
    setSectionError(null)
    setSectionForm((current) => ({
      ...current,
      label,
      id: sectionIdEdited ? current.id : slugToSectionId(label),
    }))
  }

  return (
    <aside className="w-[22rem] border-r border-border bg-panel flex flex-col overflow-hidden">
      <div className="border-b border-border px-4 py-3">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-[11px] uppercase tracking-[0.28em] text-text-muted">Cards</p>
            <p className="mt-1 text-sm text-text-primary">Sections and poems</p>
          </div>
          <div className="flex items-center gap-2 text-[11px] text-text-muted">
            <span>{sections.length} sections</span>
            <span>•</span>
            <span>{sections.reduce((total, section) => total + section.poem_count, 0)} poems</span>
          </div>
        </div>

        <div className="mt-3 flex items-center gap-2 rounded-xl border border-border bg-canvas px-3 py-2">
          <Search className="h-4 w-4 text-text-muted" />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Filter sections or loaded poems"
            className="w-full bg-transparent text-sm text-text-primary outline-none placeholder:text-text-muted"
          />
        </div>

        <div className="mt-3 flex gap-2">
          <button
            type="button"
            onClick={() => void openPoemForm()}
            disabled={!activeSection}
            className="flex-1 rounded-xl border border-accent/40 bg-accent/10 px-3 py-2 text-xs font-medium text-accent transition hover:bg-accent/15 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <span className="inline-flex items-center gap-2">
              <FilePlus2 className="h-3.5 w-3.5" />
              New poem
            </span>
          </button>
          <button
            type="button"
            onClick={openSectionForm}
            className="rounded-xl border border-border bg-surface px-3 py-2 text-xs font-medium text-text-secondary transition hover:text-text-primary"
          >
            <span className="inline-flex items-center gap-2">
              <FolderPlus className="h-3.5 w-3.5" />
              Section
            </span>
          </button>
        </div>

        {showPoemForm && activeSection && (
          <form onSubmit={handleCreatePoem} className="mt-3 rounded-2xl border border-accent/25 bg-accent/5 p-3">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-sm text-text-primary">New poem in {activeSection.label}</p>
                <p className="text-[11px] text-text-muted">{activeSection.id}</p>
              </div>
              <button
                type="button"
                onClick={() => setShowPoemForm(false)}
                className="text-xs text-text-muted transition hover:text-text-primary"
              >
                Close
              </button>
            </div>

            <div className="mt-3 space-y-3">
              <label className="block">
                <span className="mb-1 block text-[11px] uppercase tracking-[0.18em] text-text-muted">Title</span>
                <input
                  value={poemForm.title}
                  onChange={(event) => setPoemForm((current) => ({ ...current, title: event.target.value }))}
                  placeholder="New poem title"
                  className="w-full rounded-lg border border-border bg-canvas px-3 py-2 text-sm text-text-primary outline-none transition focus:border-accent/50"
                />
              </label>

              <div className="grid grid-cols-2 gap-3">
                <label className="block">
                  <span className="mb-1 block text-[11px] uppercase tracking-[0.18em] text-text-muted">Type</span>
                  <select
                    value={poemForm.type}
                    onChange={(event) => setPoemForm((current) => ({ ...current, type: event.target.value as PoemType }))}
                    className="w-full rounded-lg border border-border bg-canvas px-3 py-2 text-sm text-text-primary outline-none transition focus:border-accent/50"
                  >
                    {POEM_TYPE_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="block">
                  <span className="mb-1 block text-[11px] uppercase tracking-[0.18em] text-text-muted">Order</span>
                  <input
                    type="number"
                    value={poemForm.order}
                    onChange={(event) => setPoemForm((current) => ({ ...current, order: event.target.value }))}
                    className="w-full rounded-lg border border-border bg-canvas px-3 py-2 text-sm text-text-primary outline-none transition focus:border-accent/50"
                  />
                </label>
              </div>

              {poemError && <p className="text-xs text-red-300">{poemError}</p>}

              <div className="flex items-center justify-between gap-3">
                <p className="text-[11px] text-text-muted">
                  Creates a new Markdown file using the backend poem scaffold.
                </p>
                <button
                  type="submit"
                  disabled={submittingPoem}
                  className="rounded-lg bg-accent px-3 py-2 text-xs font-medium text-white transition hover:bg-accent-hover disabled:opacity-50"
                >
                  {submittingPoem ? 'Creating…' : 'Create poem'}
                </button>
              </div>
            </div>
          </form>
        )}

        {showSectionForm && (
          <form onSubmit={handleCreateSection} className="mt-3 rounded-2xl border border-border bg-surface p-3">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-sm text-text-primary">New section</p>
                <p className="text-[11px] text-text-muted">Creates `NN_id` and optional `_title.md`.</p>
              </div>
              <button
                type="button"
                onClick={() => setShowSectionForm(false)}
                className="text-xs text-text-muted transition hover:text-text-primary"
              >
                Close
              </button>
            </div>

            <div className="mt-3 space-y-3">
              <label className="block">
                <span className="mb-1 block text-[11px] uppercase tracking-[0.18em] text-text-muted">Label</span>
                <input
                  value={sectionForm.label}
                  onChange={(event) => handleSectionLabelChange(event.target.value)}
                  placeholder="III. New section"
                  className="w-full rounded-lg border border-border bg-canvas px-3 py-2 text-sm text-text-primary outline-none transition focus:border-accent/50"
                />
              </label>

              <div className="grid grid-cols-2 gap-3">
                <label className="block">
                  <span className="mb-1 block text-[11px] uppercase tracking-[0.18em] text-text-muted">Id</span>
                  <input
                    value={sectionForm.id}
                    onChange={(event) => {
                      setSectionIdEdited(true)
                      setSectionError(null)
                      setSectionForm((current) => ({ ...current, id: event.target.value }))
                    }}
                    placeholder="new_section"
                    className="w-full rounded-lg border border-border bg-canvas px-3 py-2 text-sm text-text-primary outline-none transition focus:border-accent/50"
                  />
                  <span className="mt-1 block text-[11px] text-text-muted">
                    Use lowercase letters, numbers, hyphens, and underscores.
                  </span>
                </label>

                <label className="block">
                  <span className="mb-1 block text-[11px] uppercase tracking-[0.18em] text-text-muted">Order</span>
                  <input
                    type="number"
                    value={sectionForm.order}
                    onChange={(event) => setSectionForm((current) => ({ ...current, order: event.target.value }))}
                    className="w-full rounded-lg border border-border bg-canvas px-3 py-2 text-sm text-text-primary outline-none transition focus:border-accent/50"
                  />
                </label>
              </div>

              <label className="flex items-center gap-2 text-sm text-text-secondary">
                <input
                  type="checkbox"
                  checked={sectionForm.section_is_cycle}
                  onChange={(event) =>
                    setSectionForm((current) => ({ ...current, section_is_cycle: event.target.checked }))
                  }
                  className="h-4 w-4 rounded border-border bg-canvas"
                />
                Mark section as a cycle container
              </label>

              <label className="block">
                <span className="mb-1 block text-[11px] uppercase tracking-[0.18em] text-text-muted">
                  Title page title
                </span>
                <input
                  value={sectionForm.title_page_title}
                  onChange={(event) =>
                    setSectionForm((current) => ({ ...current, title_page_title: event.target.value }))
                  }
                  placeholder="Optional title page"
                  className="w-full rounded-lg border border-border bg-canvas px-3 py-2 text-sm text-text-primary outline-none transition focus:border-accent/50"
                />
              </label>

              {sectionForm.title_page_title && (
                <div className="grid grid-cols-1 gap-3">
                  <label className="block">
                    <span className="mb-1 block text-[11px] uppercase tracking-[0.18em] text-text-muted">
                      Title page epigraph
                    </span>
                    <textarea
                      value={sectionForm.title_page_epigraph}
                      onChange={(event) =>
                        setSectionForm((current) => ({ ...current, title_page_epigraph: event.target.value }))
                      }
                      rows={3}
                      className="w-full rounded-lg border border-border bg-canvas px-3 py-2 text-sm text-text-primary outline-none transition focus:border-accent/50"
                    />
                  </label>

                  <label className="block">
                    <span className="mb-1 block text-[11px] uppercase tracking-[0.18em] text-text-muted">
                      Epigraph author
                    </span>
                    <input
                      value={sectionForm.title_page_epigraph_author}
                      onChange={(event) =>
                        setSectionForm((current) => ({
                          ...current,
                          title_page_epigraph_author: event.target.value,
                        }))
                      }
                      className="w-full rounded-lg border border-border bg-canvas px-3 py-2 text-sm text-text-primary outline-none transition focus:border-accent/50"
                    />
                  </label>
                </div>
              )}

              {(sectionError || sectionIdValidation) && (
                <p className="text-xs text-red-300">{sectionError ?? sectionIdValidation}</p>
              )}

              <div className="flex items-center justify-between gap-3">
                <p className="text-[11px] text-text-muted">
                  The backend will create the directory as `{sectionForm.order || 'NN'}_{sectionForm.id || 'id'}`.
                </p>
                <button
                  type="submit"
                  disabled={submittingSection || Boolean(sectionIdValidation)}
                  className="rounded-lg bg-accent px-3 py-2 text-xs font-medium text-white transition hover:bg-accent-hover disabled:opacity-50"
                >
                  {submittingSection ? 'Creating…' : 'Create section'}
                </button>
              </div>
            </div>
          </form>
        )}
      </div>

      <div className="flex-1 overflow-y-auto px-3 py-3">
        {error && (
          <div className="mb-3 rounded-xl border border-red-500/25 bg-red-500/10 px-3 py-2 text-xs text-red-200">
            {error}
          </div>
        )}

        {loadingSections && sections.length === 0 && (
          <div className="rounded-2xl border border-border bg-surface px-4 py-6 text-sm text-text-muted">
            Loading sections…
          </div>
        )}

        {!loadingSections && filteredSections.length === 0 && (
          <div className="rounded-2xl border border-border bg-surface px-4 py-6 text-sm text-text-muted">
            No sections match the current filter.
          </div>
        )}

        <div className="space-y-2">
          {filteredSections.map((section) => {
            const isSelected = section.id === activeSectionId
            const poems = poemsBySectionId[section.id] ?? []
            const filteredPoems = query.trim()
              ? poems.filter((poem) => poem.title.toLowerCase().includes(query.trim().toLowerCase()))
              : poems

            return (
              <div
                key={section.id}
                className={`rounded-2xl border transition ${
                  isSelected
                    ? 'border-accent/40 bg-accent/5'
                    : 'border-border bg-surface/80 hover:border-border/80'
                }`}
              >
                <button
                  type="button"
                  onClick={() => void handleSelectSection(section)}
                  className="flex w-full items-start justify-between gap-3 px-4 py-3 text-left"
                >
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="rounded-full border border-border px-2 py-0.5 text-[10px] uppercase tracking-[0.16em] text-text-muted">
                        {section.order}
                      </span>
                      {section.section_is_cycle && (
                        <span className="inline-flex items-center gap-1 rounded-full bg-card px-2 py-0.5 text-[10px] uppercase tracking-[0.14em] text-text-muted">
                          <Layers3 className="h-3 w-3" />
                          Cycle
                        </span>
                      )}
                    </div>
                    <p className="mt-2 truncate text-sm text-text-primary">{section.label}</p>
                    <p className="mt-1 truncate text-[11px] text-text-muted">{section.id}</p>
                  </div>

                  <div className="flex shrink-0 items-center gap-3">
                    <div className="text-right text-[11px] text-text-muted">
                      <p>{section.poem_count} poems</p>
                      <p>{isSelected ? 'Open' : 'Browse'}</p>
                    </div>
                    <ChevronRight
                      className={`h-4 w-4 text-text-muted transition ${isSelected ? 'rotate-90 text-accent' : ''}`}
                    />
                  </div>
                </button>

                {isSelected && (
                  <div className="border-t border-border/80 px-3 py-3">
                    <div className="mb-3 flex items-center justify-between gap-3 rounded-xl border border-border bg-canvas px-3 py-2">
                      <div>
                        <p className="text-xs text-text-primary">Selected section</p>
                        <p className="text-[11px] text-text-muted">
                          {poems.length} loaded poems
                          {query.trim() && poems.length !== filteredPoems.length
                            ? ` • ${filteredPoems.length} shown`
                            : ''}
                        </p>
                        {activeSectionHasTitlePage && (
                          <p className="mt-1 text-[11px] text-text-muted">Section title page present</p>
                        )}
                      </div>
                      <button
                        type="button"
                        onClick={() => void openPoemForm()}
                        className="rounded-lg border border-accent/35 px-2.5 py-1.5 text-[11px] font-medium text-accent transition hover:bg-accent/10"
                      >
                        Add poem
                      </button>
                    </div>

                    {loadingPoemsBySectionId[section.id] && poems.length === 0 && (
                      <p className="px-2 py-3 text-xs text-text-muted">Loading poems…</p>
                    )}

                    {!loadingPoemsBySectionId[section.id] && filteredPoems.length === 0 && (
                      <div className="rounded-xl border border-dashed border-border px-3 py-4 text-xs text-text-muted">
                        {query.trim()
                          ? 'No loaded poems match the current filter.'
                          : 'No poems in this section yet. Create one to start authoring.'}
                      </div>
                    )}

                    <div className="space-y-1">
                      {filteredPoems.map((poem) => (
                        <CardChip
                          key={poem.slug}
                          poem={poem}
                          isActive={activePoem?.section_id === section.id && activePoem?.slug === poem.slug}
                          isSelected={selectedSectionId === section.id && selectedPoemSlug === poem.slug}
                          onClick={() => void handleSelectPoem(section, poem.slug)}
                        />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {!activeSection && sections.length > 0 && (
          <div className="mt-3 rounded-2xl border border-dashed border-border px-4 py-5 text-sm text-text-muted">
            Select a section to browse its cards or start a new poem.
          </div>
        )}

        {sections.length === 0 && !loadingSections && (
          <div className="mt-3 rounded-2xl border border-dashed border-border bg-surface px-4 py-6">
            <div className="flex items-start gap-3">
              <Sparkles className="mt-0.5 h-4 w-4 text-accent" />
              <div>
                <p className="text-sm text-text-primary">This project has no sections yet.</p>
                <p className="mt-1 text-xs text-text-muted">
                  Create the first section, then add poems inside it from the cards rail.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </aside>
  )
}

function nextPoemOrder(poems: { order?: number }[]): number {
  const existing = poems
    .map((poem) => poem.order)
    .filter((order): order is number => typeof order === 'number')

  return (existing.length ? Math.max(...existing) : 0) + 1
}

function nextSectionOrder(sections: SectionSummary[]): number {
  const orders = sections.map((section) => section.order)
  return (orders.length ? Math.max(...orders) : 0) + 1
}

function slugToSectionId(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
}

function validateSectionId(value: string): string | null {
  const id = value.trim()
  if (!id) {
    return null
  }
  if (!/^[a-z0-9][a-z0-9_-]*$/.test(id)) {
    return 'Section id must start with a lowercase letter or number and use only lowercase letters, numbers, hyphens, and underscores.'
  }
  return null
}

async function loadSectionRecord(projectId: string, section: SectionSummary): Promise<SectionSummary | SectionDetail> {
  try {
    return await sectionsApi.get(projectId, section.id)
  } catch {
    return section
  }
}
