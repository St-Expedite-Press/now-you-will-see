import { create } from 'zustand'
import { sectionsApi } from '@/api/sections'
import { poemsApi } from '@/api/poems'
import type { SectionSummary } from '@/types/section'
import type { PoemSummary } from '@/types/poem'

interface GraphStore {
  projectId: string | null
  sections: SectionSummary[]
  poemsBySectionId: Record<string, PoemSummary[]>
  loadingSections: boolean
  loadingPoemsBySectionId: Record<string, boolean>
  error: string | null
  selectedSectionId: string | null
  selectedPoemSlug: string | null
  showVariants: boolean
  loadSections: (projectId: string) => Promise<SectionSummary[]>
  loadPoems: (projectId: string, sectionId: string, force?: boolean) => Promise<PoemSummary[]>
  setSections: (sections: SectionSummary[]) => void
  setPoems: (sectionId: string, poems: PoemSummary[]) => void
  resetProjectData: () => void
  selectSection: (id: string | null) => void
  selectPoem: (slug: string | null) => void
  toggleVariants: () => void
}

export const useGraphStore = create<GraphStore>((set, get) => ({
  projectId: null,
  sections: [],
  poemsBySectionId: {},
  loadingSections: false,
  loadingPoemsBySectionId: {},
  error: null,
  selectedSectionId: null,
  selectedPoemSlug: null,
  showVariants: false,

  loadSections: async (projectId) => {
    set({ loadingSections: true, error: null })
    try {
      const sections = await sectionsApi.list(projectId)
      set({ sections, loadingSections: false, projectId })
      return sections
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error)
      set({ error: message, loadingSections: false, projectId })
      return []
    }
  },
  loadPoems: async (projectId, sectionId, force = false): Promise<PoemSummary[]> => {
    const current = get().poemsBySectionId[sectionId]
    if (current && !force) {
      return current
    }

    set((state) => ({
      loadingPoemsBySectionId: { ...state.loadingPoemsBySectionId, [sectionId]: true },
      error: null,
    }))

    try {
      const poems = await poemsApi.list(projectId, sectionId)
      set((state) => ({
        poemsBySectionId: { ...state.poemsBySectionId, [sectionId]: poems },
        loadingPoemsBySectionId: { ...state.loadingPoemsBySectionId, [sectionId]: false },
      }))
      return poems
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error)
      set((state) => ({
        error: message,
        loadingPoemsBySectionId: { ...state.loadingPoemsBySectionId, [sectionId]: false },
      }))
      return []
    }
  },
  setSections: (sections) => set({ sections }),
  setPoems: (sectionId, poems) =>
    set((state) => ({ poemsBySectionId: { ...state.poemsBySectionId, [sectionId]: poems } })),
  resetProjectData: () =>
    set({
      projectId: null,
      sections: [],
      poemsBySectionId: {},
      loadingSections: false,
      loadingPoemsBySectionId: {},
      error: null,
      selectedSectionId: null,
      selectedPoemSlug: null,
    }),
  selectSection: (id) => set({ selectedSectionId: id }),
  selectPoem: (slug) => set({ selectedPoemSlug: slug }),
  toggleVariants: () => set((state) => ({ showVariants: !state.showVariants })),
}))
