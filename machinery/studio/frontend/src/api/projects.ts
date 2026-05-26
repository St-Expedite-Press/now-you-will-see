import { api } from './client'
import type { ProjectDetail, WorkspaceInfo } from '@/types/project'

export const projectsApi = {
  list: () => api.get<WorkspaceInfo>('/projects').then((r) => r.data),
  get: (id: string) => api.get<ProjectDetail>(`/projects/${id}`).then((r) => r.data),
  create: (body: unknown) => api.post<ProjectDetail>('/projects', body).then((r) => r.data),
}
