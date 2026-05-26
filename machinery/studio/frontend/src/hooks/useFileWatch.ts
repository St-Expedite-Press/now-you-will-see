import { useEffect } from 'react'

/**
 * Polls the backend health endpoint and calls `onRefresh` whenever the
 * server indicates content has changed. Production implementation would
 * use a dedicated SSE or WebSocket channel; this is a polling stub.
 */
export function useFileWatch(onRefresh: () => void, intervalMs = 5000) {
  useEffect(() => {
    const id = setInterval(async () => {
      try {
        const res = await fetch('/api/health')
        if (res.ok) onRefresh()
      } catch {
        // server offline — skip
      }
    }, intervalMs)
    return () => clearInterval(id)
  }, [onRefresh, intervalMs])
}
