export type ConfigLevel = 'global' | 'section' | 'poem' | 'custom'

export interface RenderConfigValues {
  mainfont?: string
  fontsize?: string
  paperwidth?: string
  paperheight?: string
  top_margin?: string
  bottom_margin?: string
  inner_margin?: string
  outer_margin?: string
  verse_parskip?: string
  stanza_skip?: string
  line_spread?: string
}

export interface RenderConfigLayer {
  level: ConfigLevel
  scope_id: string
  values: RenderConfigValues
  source_file: string
}

export interface MergedRenderConfig {
  layers: RenderConfigLayer[]
  resolved: RenderConfigValues
}
