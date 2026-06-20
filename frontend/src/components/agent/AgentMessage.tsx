import type { AgentMessage as AgentMessageType } from '@/types/agent'

interface Props {
  message: AgentMessageType
}

export default function AgentMessage({ message }: Props) {
  const isUser = message.role === 'user'

  return (
    <div className={`mb-3 ${isUser ? 'pl-4' : ''}`}>
      <div className={`text-[10px] mb-1 ${isUser ? 'text-text-muted' : 'text-agent-text'}`}>
        {isUser ? 'you' : '⬡ agent'}
      </div>
      <div
        className={`leading-relaxed whitespace-pre-wrap ${
          isUser ? 'text-text-secondary' : 'text-text-primary'
        }`}
      >
        {message.content}
      </div>
    </div>
  )
}
