import { create } from 'zustand'
import type { ProjectDetail, ProjectModule, WorkspaceInfo } from '@/types/project'
import { projectsApi } from '@/api/projects'

interface ProjectStore {
  workspace: WorkspaceInfo | null
  activeProject: ProjectDetail | null
  modules: ProjectModule[]
  loading: boolean
  error: string | null
  loadWorkspace: () => Promise<void>
  loadProject: (id: string) => Promise<void>
  setActiveProject: (p: ProjectDetail) => void
}

export const useProjectStore = create<ProjectStore>((set) => ({
  workspace: null,
  activeProject: null,
  modules: [],
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
    set({ loading: true, error: null, activeProject: null, modules: [] })
    try {
      const [p, moduleList] = await Promise.all([
        projectsApi.get(id),
        projectsApi.listModules(id),
      ])
      set({ activeProject: p, modules: moduleList.modules, loading: false })
    } catch (e) {
      const message = e instanceof Error ? e.message : String(e)
      set({ error: message, loading: false, activeProject: null, modules: [] })
    }
  },

  setActiveProject: (p) => set({ activeProject: p }),
}))
