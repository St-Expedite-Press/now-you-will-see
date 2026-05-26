import { wsUrl } from './client'

export function createBuildSocket(
  projectId: string,
  draft: boolean,
  onLine: (line: string) => void,
  onDone: (success: boolean) => void
): WebSocket {
  const url = `${wsUrl(`/projects/${projectId}/build/ws`)}?draft=${draft}`
  const ws = new WebSocket(url)
  ws.onmessage = (e) => {
    const line: string = e.data
    if (line === '[done]\n') {
      onDone(true)
    } else if (line === '[failed]\n') {
      onDone(false)
    } else {
      onLine(line)
    }
  }
  ws.onerror = () => onDone(false)
  return ws
}
