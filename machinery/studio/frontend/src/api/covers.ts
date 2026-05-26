import { api } from './client'
import type { CoverAssetsResponse, CoverRegimesResponse } from '@/types/cover'

export async function fetchCoverAssets(projectId?: string): Promise<CoverAssetsResponse> {
  const { data } = await api.get<CoverAssetsResponse>('/covers', {
    params: projectId ? { project_id: projectId } : undefined,
  })
  return data
}

export async function fetchRegimes(projectId?: string): Promise<CoverRegimesResponse> {
  const { data } = await api.get<CoverRegimesResponse>('/covers/regimes', {
    params: projectId ? { project_id: projectId } : undefined,
  })
  return data
}

export function coverAssetUrl(relPath: string): string {
  return `/api/covers/assets/${relPath}`
}
