export interface CollectionMeta {
  title: string
  author: string
  subtitle?: string
  year?: number
  publisher?: string
  isbn?: string
  content_dir: string
  output_dir: string
  lualatex_path: string
  draft_mode: boolean
}

export interface ProjectRef {
  id: string
  path: string
  description: string
}

export interface ProjectDetail extends ProjectRef {
  meta: CollectionMeta
  section_count: number
  poem_count: number
  last_built?: string
}

export interface WorkspaceInfo {
  workspace_path: string
  default_project?: string
  projects: ProjectRef[]
}

export interface ProjectModule {
  id: string
  label: string
  description: string
  path: string
  exists: boolean
  legacy_stage?: string | null
  legacy_path?: string | null
  workspace_alias: boolean
  verify_stage?: string | null
}

export interface ProjectModuleList {
  project_id: string
  modules: ProjectModule[]
}

export interface ModuleVerifyResult {
  project_id: string
  module_id: string
  ok: boolean
  status: string
  verify_stage?: string | null
  checked_path: string
  issues: string[]
}
