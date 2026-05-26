import { useRef, useEffect } from 'react'
import { useAgentStore } from '@/store/useAgentStore'
import { useAgentStream } from '@/hooks/useAgentStream'
import { useEditorStore } from '@/store/useEditorStore'
import AgentMessage from './AgentMessage'

interface Props {
  projectId: string
}

export default function AgentPanel({ projectId }: Props) {
  const { messages, streaming, streamBuffer, setOpen } = useAgentStore()
  const { send } = useAgentStream()
  const { activeSection, activePoem, editorContent } = useEditorStore()
  const inputRef = useRef<HTMLInputElement>(null)
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamBuffer])

  const handleSend = () => {
    const content = inputRef.current?.value.trim()
    if (!content) return
    if (inputRef.current) inputRef.current.value = ''
    send(content, {
      mode: 'chat',
      project_id: projectId,
      section_id: activeSection?.id,
      poem_slug: activePoem?.slug,
      active_poem_content: editorContent,
    })
  }

  return (
    <div className="h-full bg-agent-surface flex flex-col text-xs font-mono">
      <div className="flex items-center justify-between px-3 py-2 border-b border-agent/30 shrink-0">
        <span className="text-agent-text">⬡ Agent</span>
        <button onClick={() => setOpen(false)} className="text-text-muted hover:text-text-primary">✕</button>
      </div>

      <div className="flex-1 overflow-y-auto px-3 py-2">
        {messages.map((msg, i) => (
          <AgentMessage key={i} message={msg} />
        ))}
        {streaming && (
          <div className="text-agent-text leading-relaxed mb-2 whitespace-pre-wrap">{streamBuffer}<span className="animate-pulse">▋</span></div>
        )}
        <div ref={endRef} />
      </div>

      <div className="shrink-0 border-t border-agent/30 p-2">
        <div className="flex gap-1">
          <input
            ref={inputRef}
            placeholder="Ask about this poem…"
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            className="flex-1 bg-transparent border border-agent/30 rounded px-2 py-1 text-text-primary placeholder:text-text-muted focus:outline-none focus:border-agent"
          />
          <button
            onClick={handleSend}
            className="px-2 py-1 bg-agent hover:bg-agent-hover text-white rounded transition-colors"
          >
            ↑
          </button>
        </div>
      </div>
    </div>
  )
}
