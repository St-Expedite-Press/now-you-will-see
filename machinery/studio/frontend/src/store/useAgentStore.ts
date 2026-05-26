import { create } from 'zustand'
import type { AgentMessage, AgentWizardState } from '@/types/agent'

interface AgentStore {
  messages: AgentMessage[]
  streaming: boolean
  streamBuffer: string
  wizardState: AgentWizardState | null
  isOpen: boolean
  mode: 'chat' | 'wizard'
  appendMessage: (msg: AgentMessage) => void
  appendToken: (token: string) => void
  finalizeStream: () => void
  setWizardState: (state: AgentWizardState | null) => void
  setOpen: (open: boolean) => void
  setMode: (mode: 'chat' | 'wizard') => void
  clearMessages: () => void
}

export const useAgentStore = create<AgentStore>((set) => ({
  messages: [],
  streaming: false,
  streamBuffer: '',
  wizardState: null,
  isOpen: false,
  mode: 'chat',

  appendMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),

  appendToken: (token) =>
    set((state) => ({ streaming: true, streamBuffer: state.streamBuffer + token })),

  finalizeStream: () =>
    set((state) => ({
      messages: [...state.messages, { role: 'assistant', content: state.streamBuffer }],
      streaming: false,
      streamBuffer: '',
    })),

  setWizardState: (ws) => set({ wizardState: ws }),
  setOpen: (open) => set({ isOpen: open }),
  setMode: (mode) => set({ mode }),
  clearMessages: () => set({ messages: [], streamBuffer: '', streaming: false }),
}))
