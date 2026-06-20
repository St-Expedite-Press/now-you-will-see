import { api } from './client'
import type { ModuleVerifyResult, ProjectDetail, ProjectModule, ProjectModuleList, WorkspaceInfo } from '@/types/project'

export const projectsApi = {
  list: () => api.get<WorkspaceInfo>('/projects').then((r) => r.data),
  get: (id: string) => api.get<ProjectDetail>(`/projects/${id}`).then((r) => r.data),
  create: (body: unknown) => api.post<ProjectDetail>('/projects', body).then((r) => r.data),
  listModules: (id: string) => api.get<ProjectModuleList>(`/projects/${id}/modules`).then((r) => r.data),
  getModule: (id: string, moduleId: string) =>
    api.get<ProjectModule>(`/projects/${id}/modules/${moduleId}`).then((r) => r.data),
  verifyModule: (id: string, moduleId: string) =>
    api.post<ModuleVerifyResult>(`/projects/${id}/modules/${moduleId}/verify`).then((r) => r.data),
}
