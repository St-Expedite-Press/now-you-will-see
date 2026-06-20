import { create } from 'zustand'
import { fetchCoverAssets, fetchRegimes } from '@/api/covers'
import type { CoverAsset, TypographyRegime } from '@/types/cover'

interface CoverStore {
  assets: CoverAsset[]
  regimes: TypographyRegime[]
  activeRegime: string | null
  loading: boolean
  error: string | null
  loadAssets: (projectId?: string) => Promise<void>
  loadRegimes: (projectId?: string) => Promise<void>
}

export const useCoverStore = create<CoverStore>((set) => ({
  assets: [],
  regimes: [],
  activeRegime: null,
  loading: false,
  error: null,

  loadAssets: async (projectId?: string) => {
    set({ loading: true, error: null })
    try {
      const data = await fetchCoverAssets(projectId)
      set({ assets: data.assets, loading: false })
    } catch (e) {
      set({ error: String(e), loading: false })
    }
  },

  loadRegimes: async (projectId?: string) => {
    try {
      const data = await fetchRegimes(projectId)
      set({ regimes: data.regimes, activeRegime: data.active_regime })
    } catch {
      // non-fatal
    }
  },
}))
