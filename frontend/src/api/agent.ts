import { wsUrl } from './client'
import type { AgentChatRequest } from '@/types/agent'

export function createAgentSocket(
  request: AgentChatRequest,
  onToken: (token: string) => void,
  onDone: () => void,
  onError: (msg: string) => void
): WebSocket {
  const ws = new WebSocket(wsUrl('/agent/ws'))
  ws.onopen = () => ws.send(JSON.stringify(request))
  ws.onmessage = (e) => {
    const text: string = e.data
    if (text === '\x00') {
      onDone()
    } else if (text.startsWith('\x01')) {
      onError(text.slice(1))
    } else {
      onToken(text)
    }
  }
  ws.onerror = () => onError('WebSocket error')
  return ws
}

// Re-export the request type so callers only import from here
export type { AgentChatRequest }
