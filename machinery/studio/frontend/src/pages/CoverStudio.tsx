import { useEffect, useState } from 'react'
import { Download, ImageIcon, Palette, BookOpen } from 'lucide-react'
import { useCoverStore } from '@/store/useCoverStore'
import type { CoverAsset, TypographyRegime } from '@/types/cover'

// â”€â”€â”€ Asset gallery card â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

function AssetCard({ asset }: { asset: CoverAsset }) {
  const label = `${asset.book} â€” ${asset.role} (${asset.variant})`
  return (
    <div className="group flex flex-col gap-2 rounded-2xl border border-border bg-surface p-3 transition hover:border-accent/40">
      <div className="relative aspect-[3/4] overflow-hidden rounded-xl bg-canvas">
        <img
          src={asset.url}
          alt={label}
          className="h-full w-full object-contain"
          loading="lazy"
        />
      </div>
      <div className="min-w-0">
        <p className="truncate text-xs font-medium text-text-primary">{asset.book}</p>
        <p className="truncate text-[11px] uppercase tracking-[0.14em] text-text-muted">
          {asset.role} Â· {asset.variant}
        </p>
      </div>
      <a
        href={asset.url}
        download={asset.filename}
        className="inline-flex items-center gap-1.5 rounded-xl border border-border px-3 py-1.5 text-xs text-text-secondary
                   opacity-0 transition group-hover:opacity-100 hover:border-accent/40 hover:text-accent"
      >
        <Download className="h-3 w-3" />
        Download
      </a>
    </div>
  )
}

// â”€â”€â”€ Regime card â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

function RegimeCard({ regime }: { regime: TypographyRegime }) {
  return (
    <div
      className={`rounded-2xl border p-4 transition ${
        regime.active
          ? 'border-accent/50 bg-accent/10'
          : 'border-border bg-surface'
      }`}
    >
      <div className="mb-2 flex items-center gap-2">
        <span
          className={`inline-flex h-7 w-7 items-center justify-center rounded-full text-sm font-bold ${
            regime.active ? 'bg-accent text-white' : 'bg-canvas text-text-muted'
          }`}
        >
          {regime.id}
        </span>
        <div>
          <p className="text-sm font-medium text-text-primary">{regime.name}</p>
          {regime.active && (
            <span className="text-[10px] uppercase tracking-[0.15em] text-accent">Active</span>
          )}
        </div>
      </div>
      <p className="text-xs text-text-secondary">
        <span className="font-medium">Face:</span> {regime.face}
      </p>
      <p className="text-xs text-text-secondary">
        <span className="font-medium">Alignment:</span> {regime.alignment}
      </p>
      <p className="mt-1 text-[11px] leading-relaxed text-text-muted">{regime.distinctive}</p>
    </div>
  )
}

// â”€â”€â”€ Main page â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

type Tab = 'assets' | 'regimes'

export default function CoverStudio({ projectId }: { projectId: string }) {
  const { assets, regimes, activeRegime, loading, error, loadAssets, loadRegimes } = useCoverStore()
  const [tab, setTab] = useState<Tab>('assets')
  const [filter, setFilter] = useState<'all' | 'cover' | 'art'>('all')

  useEffect(() => {
    loadAssets(projectId)
    loadRegimes(projectId)
  }, [loadAssets, loadRegimes, projectId])

  const visibleAssets = filter === 'all' ? assets : assets.filter((a) => a.role === filter)

  return (
    <div className="flex h-full flex-col bg-canvas">
      {/* Header */}
      <div className="shrink-0 border-b border-border bg-surface px-6 py-4">
        <div className="flex items-center gap-3">
          <span className="inline-flex rounded-full border border-accent/30 bg-accent/10 p-2 text-accent">
            <Palette className="h-4 w-4" />
          </span>
          <div>
            <p className="text-sm font-medium text-text-primary">Cover Studio</p>
            <p className="text-[11px] uppercase tracking-[0.18em] text-text-muted">
              St. Expedite Press Â· Fletcher Edition
            </p>
          </div>
        </div>

        {/* Tab bar */}
        <div className="mt-4 flex gap-1 rounded-xl border border-border bg-canvas p-1 w-fit">
          {([
            { id: 'assets', label: 'Cover Assets', icon: ImageIcon },
            { id: 'regimes', label: 'Typography Regimes', icon: BookOpen },
          ] as const).map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              type="button"
              onClick={() => setTab(id)}
              className={`inline-flex items-center gap-2 rounded-lg px-3 py-1.5 text-xs font-medium transition ${
                tab === id ? 'bg-accent/15 text-accent' : 'text-text-muted hover:text-text-primary'
              }`}
            >
              <Icon className="h-3.5 w-3.5" />
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto px-6 py-6">
        {loading && (
          <p className="text-sm text-text-muted">Loading cover assetsâ€¦</p>
        )}
        {error && (
          <p className="text-sm text-error">{error}</p>
        )}

        {/* â”€â”€ Assets tab â”€â”€ */}
        {tab === 'assets' && !loading && (
          <>
            <div className="mb-4 flex items-center gap-2">
              <span className="text-xs text-text-muted">{visibleAssets.length} asset{visibleAssets.length !== 1 ? 's' : ''}</span>
              <div className="ml-auto flex gap-1 rounded-xl border border-border bg-surface p-1">
                {(['all', 'cover', 'art'] as const).map((f) => (
                  <button
                    key={f}
                    type="button"
                    onClick={() => setFilter(f)}
                    className={`rounded-lg px-3 py-1 text-xs capitalize transition ${
                      filter === f ? 'bg-accent/15 text-accent' : 'text-text-muted hover:text-text-primary'
                    }`}
                  >
                    {f}
                  </button>
                ))}
              </div>
            </div>

            {visibleAssets.length === 0 ? (
              <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border py-16 text-center">
                <ImageIcon className="mb-3 h-8 w-8 text-text-muted" />
                <p className="text-sm text-text-muted">No cover assets found in this project's covers module.</p>
                <p className="mt-1 text-xs text-text-muted">
                  Add PNG files following the naming schema: {'{author}_{book}_{role}_{variant}.png'}
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
                {visibleAssets.map((asset) => (
                  <AssetCard key={asset.rel_path} asset={asset} />
                ))}
              </div>
            )}
          </>
        )}

        {/* â”€â”€ Regimes tab â”€â”€ */}
        {tab === 'regimes' && !loading && (
          <>
            {activeRegime && (
              <p className="mb-4 text-xs text-text-secondary">
                Active regime: <span className="font-medium text-accent">Regime {activeRegime}</span>.
                Set <code className="rounded bg-surface px-1 py-0.5">active_regime</code> in{' '}
                <code className="rounded bg-surface px-1 py-0.5">projects/fletcher-series/covers/STYLES.md</code> to change.
              </p>
            )}
            {!activeRegime && (
              <p className="mb-4 text-xs text-text-muted">
                No active regime set. Edit{' '}
                <code className="rounded bg-surface px-1 py-0.5">projects/fletcher-series/covers/STYLES.md</code> and set{' '}
                <code className="rounded bg-surface px-1 py-0.5">active_regime: A|B|C|D</code>.
              </p>
            )}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              {regimes.map((r) => (
                <RegimeCard key={r.id} regime={r} />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

