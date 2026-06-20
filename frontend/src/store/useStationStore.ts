import { create } from 'zustand'
import { stationApi } from '@/api/station'
import type { AgentDescription, ChatEntry, ScreenDef } from '@/types/station'

interface StationStore {
  projectId: string | null
  screens: ScreenDef[]
  activeScreen: number
  activeStage: string | null
  agent: AgentDescription | null
  threads: Record<string, ChatEntry[]> // keyed by stage
  loading: boolean
  sending: boolean
  error: string | null

  init: (projectId: string) => Promise<void>
  selectScreen: (screenId: number) => Promise<void>
  selectStage: (stage: string) => Promise<void>
  send: (text: string) => Promise<void>
  handOff: () => void
}

export const useStationStore = create<StationStore>((set, get) => ({
  projectId: null,
  screens: [],
  activeScreen: 0,
  activeStage: null,
  agent: null,
  threads: {},
  loading: false,
  sending: false,
  error: null,

  init: async (projectId) => {
    set({ loading: true, error: null, projectId })
    try {
      const { screens } = await stationApi.stages()
      set({ screens, loading: false })
      const first = screens[0]
      if (first) await get().selectScreen(first.id)
    } catch (e) {
      set({ error: e instanceof Error ? e.message : String(e), loading: false })
    }
  },

  selectScreen: async (screenId) => {
    const screen = get().screens.find((s) => s.id === screenId)
    set({ activeScreen: screenId })
    if (screen && screen.stages.length) await get().selectStage(screen.stages[0])
  },

  selectStage: async (stage) => {
    set({ activeStage: stage, agent: null, error: null })
    try {
      const agent = await stationApi.describe(stage, get().projectId)
      set({ agent })
    } catch (e) {
      set({ error: e instanceof Error ? e.message : String(e) })
    }
  },

  send: async (text) => {
    const { activeStage, projectId, threads } = get()
    if (!activeStage || !text.trim()) return
    const prior = threads[activeStage] ?? []
    const next = [...prior, { role: 'user' as const, content: text }]
    set({ threads: { ...threads, [activeStage]: next }, sending: true, error: null })
    try {
      const res = await stationApi.chat(
        activeStage,
        projectId,
        next.map(({ role, content }) => ({ role, content }))
      )
      set((s) => ({
        sending: false,
        threads: {
          ...s.threads,
          [activeStage]: [
            ...(s.threads[activeStage] ?? []),
            { role: 'assistant', content: res.text, steps: res.steps },
          ],
        },
      }))
    } catch (e) {
      set({ sending: false, error: e instanceof Error ? e.message : String(e) })
    }
  },

  handOff: () => {
    const { screens, activeScreen } = get()
    const idx = screens.findIndex((s) => s.id === activeScreen)
    const next = screens[idx + 1]
    if (next) void get().selectScreen(next.id)
  },
}))
