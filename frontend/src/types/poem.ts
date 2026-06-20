export type PoemType =
  | 'poem'
  | 'prose'
  | 'poem-cycle'
  | 'poem-screenplay'
  | 'section-title'
  | 'halftitle'
  | 'titlepage'
  | 'copyright'
  | 'dedication'
  | 'epigraph'
  | 'toc'
  | 'notes'
  | 'index'
  | 'acknowledgments'
  | 'about-author'
  | 'colophon'

export interface PoemFrontmatter {
  title: string
  type: PoemType
  order?: number
  epigraph?: string
  epigraph_author?: string
  dedication?: string
  subtitle?: string
  cycle?: string
  cycle_part?: number
}

export interface PoemSummary {
  slug: string
  title: string
  type: PoemType
  order?: number
  line_count: number
  version_count: number
  has_warning: boolean
  warning_message: string
  is_canonical: boolean
}

export interface PoemDetail {
  slug: string
  filename: string
  frontmatter: PoemFrontmatter
  raw_frontmatter: Record<string, unknown>
  raw_content: string
  body: string
  line_count: number
  section_id: string
  canonical_filename?: string
  is_canonical?: boolean
}

export interface PoemRaw {
  slug: string
  raw_content: string
}

export interface PoemCreateInput {
  title: string
  type?: PoemType
  order?: number
}
