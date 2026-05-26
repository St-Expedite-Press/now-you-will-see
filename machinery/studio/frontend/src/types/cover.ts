export interface CoverAsset {
  filename: string
  rel_path: string
  author: string
  book: string
  role: 'cover' | 'art' | string
  variant: string
  url: string
}

export interface TypographyRegime {
  id: string
  name: string
  face: string
  alignment: string
  distinctive: string
  active: boolean
}

export interface CoverAssetsResponse {
  assets: CoverAsset[]
  total: number
}

export interface CoverRegimesResponse {
  regimes: TypographyRegime[]
  active_regime: string | null
}
