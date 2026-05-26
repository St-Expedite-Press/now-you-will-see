import { create } from 'zustand'
import type { ProjectDetail, WorkspaceInfo } from '@/types/project'
import { projectsApi } from '@/api/projects'

interface ProjectStore {
  workspace: WorkspaceInfo | null
  activeProject: ProjectDetail | null
  loading: boolean
  error: string | null
  loadWorkspace: () => Promise<void>
  loadProject: (id: string) => Promise<void>
  setActiveProject: (p: ProjectDetail) => void
}

export const useProjectStore = create<ProjectStore>((set) => ({
  workspace: null,
  activeProject: null,
  loading: false,
  error: null,

  loadWorkspace: async () => {
    set({ loading: true, error: null })
    try {
      const ws = await projectsApi.list()
      set({ workspace: ws, loading: false })
    } catch (e) {
      set({ error: String(e), loading: false })
    }
  },

  loadProject: async (id) => {
    set({ loading: true, error: null, activeProject: null })
    try {
      const p = await projectsApi.get(id)
      set({ activeProject: p, loading: false })
    } catch (e) {
      const message = e instanceof Error ? e.message : String(e)
      set({ error: message, loading: false, activeProject: null })
    }
  },

  setActiveProject: (p) => set({ activeProject: p }),
}))
