export interface SectionSummary {
  id: string
  dir_name: string
  label: string
  order: number
  poem_count: number
  section_is_cycle: boolean
}

export interface SectionDetail extends SectionSummary {
  poem_slugs: string[]
  has_title_page: boolean
  render_config?: Record<string, unknown>
}

export interface SectionCreateInput {
  id: string
  label: string
  order: number
  section_is_cycle?: boolean
  title_page_title?: string
  title_page_epigraph?: string
  title_page_epigraph_author?: string
}
