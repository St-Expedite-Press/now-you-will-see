import { api } from './client'
import type { VersionList } from '@/types/version'

const base = (p: string, s: string, slug: string) =>
  `/projects/${p}/sections/${s}/poems/${slug}/versions`

export const versionsApi = {
  list: (p: string, s: string, slug: string) =>
    api.get<VersionList>(base(p, s, slug)).then((r) => r.data),
  create: (p: string, s: string, slug: string, body: unknown) =>
    api.post<VersionList>(base(p, s, slug), body).then((r) => r.data),
  setCanonical: (p: string, s: string, slug: string, file: string) =>
    api.post<VersionList>(`${base(p, s, slug)}/canonical`, { file }).then((r) => r.data),
}
