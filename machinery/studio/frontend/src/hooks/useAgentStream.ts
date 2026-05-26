import { useCallback, useRef } from 'react'
import { createAgentSocket } from '@/api/agent'
import { useAgentStore } from '@/store/useAgentStore'
import type { AgentContext } from '@/types/agent'

export function useAgentStream() {
  const wsRef = useRef<WebSocket | null>(null)
  const { appendToken, finalizeStream, appendMessage, messages, mode } = useAgentStore()

  const send = useCallback(
    (content: string, context: AgentContext) => {
      if (wsRef.current) wsRef.current.close()

      appendMessage({ role: 'user', content })
      const allMessages = [...messages, { role: 'user' as const, content }]

      wsRef.current = createAgentSocket(
        { messages: allMessages, context: { ...context, mode } },
        appendToken,
        finalizeStream,
        (err) => {
          finalizeStream()
          console.error('Agent error:', err)
        }
      )
    },
    [messages, mode, appendMessage, appendToken, finalizeStream]
  )

  const abort = useCallback(() => wsRef.current?.close(), [])

  return { send, abort }
}
