import { useEffect, useState } from 'react'
import {
  Background,
  Controls,
  ReactFlow,
  useEdgesState,
  useNodesState,
  type Edge,
  type Node,
  type ReactFlowInstance,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { Compass, Layers3 } from 'lucide-react'
import { useGraphStore } from '@/store/useGraphStore'
import CardStackNode from './CardStackNode'
import RenderConfigPanel from './RenderConfigPanel'

interface CardStackData extends Record<string, unknown> {
  poemTitle: string
  poemSlug: string
  poemType: string
  lineCount: number
  versionCount: number
  hasWarning: boolean
  warningMessage: string
  isCanonical: boolean
  sectionLabel: string
  sectionId: string
  projectId: string
  sectionSelected: boolean
  poemSelected: boolean
}

type CardStackNodeType = Node<CardStackData, 'cardStack'>

const nodeTypes = { cardStack: CardStackNode }

interface Props {
  projectId: string
}

export default function GraphCanvas({ projectId }: Props) {
  const {
    sections,
    poemsBySectionId,
    loadingSections,
    selectedSectionId,
    selectedPoemSlug,
    loadSections,
    loadPoems,
    selectSection,
  } = useGraphStore()
  const [nodes, setNodes, onNodesChange] = useNodesState<CardStackNodeType>([])
  const [edges, , onEdgesChange] = useEdgesState<Edge>([])
  const [flow, setFlow] = useState<ReactFlowInstance<CardStackNodeType> | null>(null)

  useEffect(() => {
    let cancelled = false

    void (async () => {
      const loadedSections = await loadSections(projectId)
      if (cancelled || loadedSections.length === 0) return

      const currentSectionId = useGraphStore.getState().selectedSectionId
      selectSection(currentSectionId ?? loadedSections[0].id)

      await Promise.all(loadedSections.map((section) => loadPoems(projectId, section.id)))
    })()

    return () => {
      cancelled = true
    }
  }, [projectId, loadPoems, loadSections, selectSection])

  const sectionOffsets = buildSectionOffsets(sections)

  useEffect(() => {
    const nextNodes: CardStackNodeType[] = []

    sections.forEach((section) => {
      const sectionPoems = poemsBySectionId[section.id] ?? []
      const sectionY = sectionOffsets[section.id] ?? 0

      sectionPoems.forEach((poem, poemIndex) => {
        nextNodes.push({
          id: `${section.id}::${poem.slug}`,
          type: 'cardStack',
          position: {
            x: 56 + poemIndex * 188,
            y: sectionY,
          },
          data: {
            poemTitle: poem.title,
            poemSlug: poem.slug,
            poemType: poem.type,
            lineCount: poem.line_count,
            versionCount: poem.version_count,
            hasWarning: poem.has_warning,
            warningMessage: poem.warning_message,
            isCanonical: poem.is_canonical,
            sectionLabel: section.label,
            sectionId: section.id,
            projectId,
            sectionSelected: selectedSectionId === section.id,
            poemSelected: selectedSectionId === section.id && selectedPoemSlug === poem.slug,
          },
          draggable: false,
        })
      })
    })

    setNodes(nextNodes)
  }, [poemsBySectionId, projectId, sectionOffsets, sections, selectedPoemSlug, selectedSectionId, setNodes])

  async function handleFocusSection(sectionId: string) {
    selectSection(sectionId)
    await loadPoems(projectId, sectionId)
    const y = sectionOffsets[sectionId] ?? 0
    flow?.setCenter(360, y + 80, { zoom: 1, duration: 300 })
  }

  return (
    <div className="flex flex-1 overflow-hidden bg-canvas">
      <aside className="w-72 border-r border-border bg-panel/95 px-4 py-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-[11px] uppercase tracking-[0.24em] text-text-muted">Graph</p>
            <h3 className="mt-2 text-sm text-text-primary">Section overview</h3>
          </div>
          <span className="rounded-full border border-border px-2 py-1 text-[11px] text-text-muted">
            {sections.length} lanes
          </span>
        </div>

        <p className="mt-3 text-xs leading-5 text-text-muted">
          Use the section list to jump across the collection. Clicking a card opens it back in Cards mode.
        </p>

        <div className="mt-4 space-y-2 overflow-y-auto pr-1">
          {sections.map((section) => (
            <button
              key={section.id}
              type="button"
              onClick={() => void handleFocusSection(section.id)}
              className={`w-full rounded-2xl border px-3 py-3 text-left transition ${
                selectedSectionId === section.id
                  ? 'border-accent/35 bg-accent/10'
                  : 'border-border bg-surface/80 hover:border-border/80'
              }`}
            >
              <div className="flex items-center justify-between gap-3">
                <div className="min-w-0">
                  <p className="truncate text-sm text-text-primary">{section.label}</p>
                  <p className="mt-1 truncate text-[11px] text-text-muted">{section.id}</p>
                </div>
                <span className="rounded-full border border-border px-2 py-1 text-[11px] text-text-muted">
                  {section.poem_count}
                </span>
              </div>
            </button>
          ))}

          {!loadingSections && sections.length === 0 && (
            <div className="rounded-2xl border border-dashed border-border px-4 py-6 text-sm text-text-muted">
              No sections to graph yet.
            </div>
          )}
        </div>
      </aside>

      <div className="relative flex-1">
        <div className="absolute left-4 top-4 z-10 max-w-sm rounded-2xl border border-border bg-surface/95 px-4 py-3 shadow-lg backdrop-blur">
          <div className="flex items-center gap-2 text-sm text-text-primary">
            <Compass className="h-4 w-4 text-accent" />
            Graph view
          </div>
          <p className="mt-2 text-xs leading-5 text-text-muted">
            Sections are stacked vertically and poems run left to right within each lane.
            Use the cards rail for creation; use the graph for spatial browsing and quick jumps.
          </p>
        </div>

        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onInit={setFlow}
          nodeTypes={nodeTypes}
          fitView
          nodesDraggable={false}
          nodesConnectable={false}
          proOptions={{ hideAttribution: true }}
        >
          <Background color="#1d1d1d" gap={28} size={1} />
          <Controls className="!border-border !bg-panel" showInteractive={false} />
        </ReactFlow>

        <div className="pointer-events-none absolute bottom-4 left-4 z-10 rounded-2xl border border-border bg-surface/90 px-4 py-3 text-xs text-text-muted shadow-lg backdrop-blur">
          <div className="flex items-center gap-2 text-text-secondary">
            <Layers3 className="h-4 w-4" />
            {selectedSectionId
              ? `${sections.find((section) => section.id === selectedSectionId)?.label ?? selectedSectionId}`
              : 'Select a section'}
          </div>
        </div>

        <RenderConfigPanel projectId={projectId} sectionId={selectedSectionId ?? undefined} />
      </div>
    </div>
  )
}

function buildSectionOffsets(sections: { id: string }[]): Record<string, number> {
  return sections.reduce<Record<string, number>>((offsets, section, index) => {
    offsets[section.id] = 96 + index * 224
    return offsets
  }, {})
}
