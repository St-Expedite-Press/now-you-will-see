import { useCallback, useRef } from 'react'
import { createBuildSocket } from '@/api/build'
import { useBuildStore } from '@/store/useBuildStore'

export function useBuildStream(projectId: string) {
  const wsRef = useRef<WebSocket | null>(null)
  const { appendLine, setStatus, clearLog } = useBuildStore()

  const start = useCallback(
    (draft = false) => {
      if (wsRef.current) wsRef.current.close()
      clearLog()
      setStatus('running')
      wsRef.current = createBuildSocket(
        projectId,
        draft,
        (line) => appendLine(line),
        (success) => setStatus(success ? 'success' : 'failed')
      )
    },
    [projectId, appendLine, setStatus, clearLog]
  )

  const stop = useCallback(() => {
    wsRef.current?.close()
    setStatus('idle')
  }, [setStatus])

  return { start, stop }
}
