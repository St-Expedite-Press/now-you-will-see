import { api } from './client'
import type { SectionCreateInput, SectionDetail, SectionSummary } from '@/types/section'

export const sectionsApi = {
  list: (projectId: string) =>
    api.get<SectionSummary[]>(`/projects/${projectId}/sections`).then((r) => r.data),
  get: (projectId: string, sectionId: string) =>
    api.get<SectionDetail>(`/projects/${projectId}/sections/${sectionId}`).then((r) => r.data),
  create: (projectId: string, body: SectionCreateInput) =>
    api.post<SectionDetail>(`/projects/${projectId}/sections`, body).then((r) => r.data),
  update: (projectId: string, sectionId: string, body: unknown) =>
    api.patch<SectionDetail>(`/projects/${projectId}/sections/${sectionId}`, body).then((r) => r.data),
}
