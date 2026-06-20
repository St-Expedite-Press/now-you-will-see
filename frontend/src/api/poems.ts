import { api } from './client'
import type { PoemCreateInput, PoemDetail, PoemRaw, PoemSummary } from '@/types/poem'

const base = (p: string, s: string) => `/projects/${p}/sections/${s}/poems`

export const poemsApi = {
  list: (projectId: string, sectionId: string) =>
    api.get<PoemSummary[]>(base(projectId, sectionId)).then((r) => r.data),
  get: (projectId: string, sectionId: string, slug: string) =>
    api.get<PoemDetail>(`${base(projectId, sectionId)}/${slug}`).then((r) => r.data),
  getRaw: (projectId: string, sectionId: string, slug: string) =>
    api.get<PoemRaw>(`${base(projectId, sectionId)}/${slug}/raw`).then((r) => r.data),
  create: (projectId: string, sectionId: string, body: PoemCreateInput) =>
    api.post<PoemDetail>(base(projectId, sectionId), body).then((r) => r.data),
  update: (projectId: string, sectionId: string, slug: string, content: string) =>
    api.put<PoemDetail>(`${base(projectId, sectionId)}/${slug}`, { content }).then((r) => r.data),
  delete: (projectId: string, sectionId: string, slug: string) =>
    api.delete(`${base(projectId, sectionId)}/${slug}`),
}
