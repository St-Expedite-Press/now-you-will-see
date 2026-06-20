import { create } from 'zustand'
import type { VersionList } from '@/types/version'
import { versionsApi } from '@/api/versions'

interface VersionStore {
  versionsBySlug: Record<string, VersionList>
  loadVersions: (projectId: string, sectionId: string, slug: string) => Promise<void>
  setCanonical: (projectId: string, sectionId: string, slug: string, file: string) => Promise<void>
}

export const useVersionStore = create<VersionStore>((set) => ({
  versionsBySlug: {},

  loadVersions: async (projectId, sectionId, slug) => {
    const data = await versionsApi.list(projectId, sectionId, slug)
    set((state) => ({ versionsBySlug: { ...state.versionsBySlug, [versionKey(sectionId, slug)]: data } }))
  },

  setCanonical: async (projectId, sectionId, slug, file) => {
    const data = await versionsApi.setCanonical(projectId, sectionId, slug, file)
    set((state) => ({ versionsBySlug: { ...state.versionsBySlug, [versionKey(sectionId, slug)]: data } }))
  },
}))

function versionKey(sectionId: string, slug: string): string {
  return `${sectionId}::${slug}`
}
