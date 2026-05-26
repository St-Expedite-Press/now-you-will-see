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
