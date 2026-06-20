import { api } from './client'
import type {
  AgentDescription,
  StageChatResponse,
  StageMessage,
  StagesResponse,
} from '@/types/station'

export const stationApi = {
  stages: async (): Promise<StagesResponse> => (await api.get<StagesResponse>('/agent/stages')).data,

  describe: async (stage: string, projectId?: string | null): Promise<AgentDescription> =>
    (
      await api.get<AgentDescription>(`/agent/stage/${stage}`, {
        params: projectId ? { project_id: projectId } : undefined,
      })
    ).data,

  chat: async (
    stage: string,
    projectId: string | null,
    messages: StageMessage[]
  ): Promise<StageChatResponse> =>
    (await api.post<StageChatResponse>('/agent/stage', { stage, project_id: projectId, messages }))
      .data,
}
