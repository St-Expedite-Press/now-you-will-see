import { create } from 'zustand'

export type BuildStatus = 'idle' | 'running' | 'success' | 'failed'

interface BuildStore {
  status: BuildStatus
  logLines: string[]
  lastBuiltAt: string | null
  appendLine: (line: string) => void
  setStatus: (s: BuildStatus) => void
  clearLog: () => void
}

export const useBuildStore = create<BuildStore>((set) => ({
  status: 'idle',
  logLines: [],
  lastBuiltAt: null,

  appendLine: (line) => set((state) => ({ logLines: [...state.logLines, line] })),
  setStatus: (s) =>
    set((state) => ({
      status: s,
      lastBuiltAt: s === 'success' ? new Date().toISOString() : state.lastBuiltAt,
    })),
  clearLog: () => set({ logLines: [] }),
}))
