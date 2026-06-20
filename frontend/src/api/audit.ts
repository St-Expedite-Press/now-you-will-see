import { api } from './client'
import type { AuditRun } from '@/types/audit'

export const auditApi = {
  run: () => api.post<AuditRun>('/audit/run').then((r) => r.data),
}
