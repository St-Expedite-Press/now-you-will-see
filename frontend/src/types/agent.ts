export type MessageRole = 'user' | 'assistant' | 'system'
export type AgentMode = 'chat' | 'wizard'

export interface AgentMessage {
  role: MessageRole
  content: string
}

export interface ActionChip {
  label: string
  action: string
  payload: Record<string, unknown>
}

export interface AgentContext {
  project_id?: string
  section_id?: string
  poem_slug?: string
  mode: AgentMode
  collection_yaml?: string
  active_section_meta?: string
  active_poem_content?: string
  notes_md?: string
  recent_build_log?: string
}

export interface AgentChatRequest {
  messages: AgentMessage[]
  context: AgentContext
}

export interface AgentWizardState {
  step: number
  total_steps: number
  confirmed_fields: Record<string, unknown>
  pending_sections: string[]
  is_complete: boolean
}
