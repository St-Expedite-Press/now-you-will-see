import { create } from 'zustand'
import type { PoemDetail } from '@/types/poem'
import type { SectionDetail, SectionSummary } from '@/types/section'

export type ViewMode = 'cards' | 'graph' | 'build' | 'covers'

interface EditorStore {
  activeSection: SectionSummary | SectionDetail | null
  activePoem: PoemDetail | null
  editorContent: string
  isDirty: boolean
  activeView: ViewMode
  pendingSelect: { sectionId: string; poemSlug: string } | null
  setActiveSection: (s: SectionSummary | SectionDetail | null) => void
  setActivePoem: (p: PoemDetail | null) => void
  setEditorContent: (content: string) => void
  markClean: () => void
  setActiveView: (v: ViewMode) => void
  setPendingSelect: (sel: { sectionId: string; poemSlug: string } | null) => void
}

export const useEditorStore = create<EditorStore>((set) => ({
  activeSection: null,
  activePoem: null,
  editorContent: '',
  isDirty: false,
  activeView: 'cards',
  pendingSelect: null,

  setActiveSection: (s) => set({ activeSection: s }),
  setActivePoem: (p) => set({ activePoem: p, editorContent: p ? p.raw_content || buildRaw(p) : '', isDirty: false }),
  setEditorContent: (content) => set({ editorContent: content, isDirty: true }),
  markClean: () => set({ isDirty: false }),
  setActiveView: (v) => set({ activeView: v }),
  setPendingSelect: (sel) => set({ pendingSelect: sel }),
}))

function buildRaw(p: PoemDetail): string {
  const fm = p.frontmatter
  const lines = ['---']
  lines.push(`title: ${quoteYaml(fm.title)}`)
  lines.push(`type: ${fm.type}`)
  if (fm.order != null) lines.push(`order: ${fm.order}`)
  if (fm.epigraph) lines.push(`epigraph: ${quoteYaml(fm.epigraph)}`)
  if (fm.epigraph_author) lines.push(`epigraph_author: ${quoteYaml(fm.epigraph_author)}`)
  if (fm.dedication) lines.push(`dedication: ${quoteYaml(fm.dedication)}`)
  if (fm.subtitle) lines.push(`subtitle: ${quoteYaml(fm.subtitle)}`)
  if (fm.cycle) lines.push(`cycle: ${quoteYaml(fm.cycle)}`)
  if (fm.cycle_part != null) lines.push(`cycle_part: ${fm.cycle_part}`)
  lines.push('---', '', p.body)
  return lines.join('\n')
}

function quoteYaml(value: string): string {
  return `"${value.replace(/\\/g, '\\\\').replace(/"/g, '\\"')}"`
}
