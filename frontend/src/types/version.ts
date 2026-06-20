export interface VersionEntry {
  file: string
  label: string
  created: string
  lines: number
  is_canonical: boolean
}

export interface VersionList {
  slug: string
  canonical: string
  versions: VersionEntry[]
}
