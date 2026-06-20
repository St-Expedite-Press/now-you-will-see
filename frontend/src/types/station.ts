// Types for the linear publishing station (per-stage gated agents).

export interface ScreenDef {
  id: number
  title: string
  stages: string[]
}

export interface StageIO {
  receives: string[]
  produces: string[]
}

export interface StagesResponse {
  screens: ScreenDef[]
  stages: Record<string, unknown>
}

export interface AgentDescription {
  stage: string
  screen: number
  title: string
  module: string
  tools: string[]
  skills: string[]
  gate: string | null
  io: StageIO
  scope: string | null
}

export interface StageStep {
  tool: string
  allowed: boolean
  ok: boolean
  output: string
}

export interface StageChatResponse {
  text: string
  steps: StageStep[]
}

export interface StageMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatEntry extends StageMessage {
  steps?: StageStep[]
}
