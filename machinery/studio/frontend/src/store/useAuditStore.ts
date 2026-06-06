import { create } from 'zustand'
import { auditApi } from '@/api/audit'
import type { AuditRun } from '@/types/audit'

interface AuditStore {
  activeRun: AuditRun | null
  running: boolean
  error: string | null
  runAudit: () => Promise<void>
  clearAudit: () => void
}

export const useAuditStore = create<AuditStore>((set) => ({
  activeRun: null,
  running: false,
  error: null,

  runAudit: async () => {
    set({ running: true, error: null })
    try {
      const run = await auditApi.run()
      set({ activeRun: run, running: false })
    } catch (e) {
      const message = e instanceof Error ? e.message : String(e)
      set({ error: message, running: false })
    }
  },

  clearAudit: () => set({ activeRun: null, error: null, running: false }),
}))
