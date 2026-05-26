import CodeMirror from '@uiw/react-codemirror'
import { markdown } from '@codemirror/lang-markdown'
import { EditorView } from '@codemirror/view'
import { useEditorStore } from '@/store/useEditorStore'
import { poemsApi } from '@/api/poems'
import { useCallback, useEffect, useRef } from 'react'

interface Props {
  projectId: string
}

const darkTheme = EditorView.theme({
  '&': { backgroundColor: '#0a0a0a', height: '100%' },
  '.cm-scroller': { fontFamily: "'Courier New', monospace", fontSize: '13px' },
  '.cm-content': { padding: '16px', color: '#e8e8e8', caretColor: '#40916c' },
  '.cm-focused': { outline: 'none' },
  '.cm-gutters': { backgroundColor: '#111111', borderRight: '1px solid #2a2a2a', color: '#606060' },
  '.cm-activeLineGutter': { backgroundColor: '#1a1a1a' },
  '.cm-activeLine': { backgroundColor: '#1a1a1a' },
  '.cm-selectionBackground': { backgroundColor: '#1b4332 !important' },
})

export default function PoemEditor({ projectId }: Props) {
  const { activePoem, activeSection, editorContent, setEditorContent, markClean, isDirty } = useEditorStore()

  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const handleSave = useCallback(async () => {
    if (!activePoem) return
    const sectionId = activePoem.section_id || activeSection?.id
    if (!sectionId) return
    await poemsApi.update(projectId, sectionId, activePoem.slug, editorContent)
    markClean()
  }, [activePoem, activeSection, editorContent, projectId, markClean])

  // Debounced auto-save: 1.5s after last keystroke
  useEffect(() => {
    if (!isDirty) return
    if (saveTimerRef.current) clearTimeout(saveTimerRef.current)
    saveTimerRef.current = setTimeout(() => { handleSave() }, 1500)
    return () => { if (saveTimerRef.current) clearTimeout(saveTimerRef.current) }
  }, [editorContent, isDirty, handleSave])

  if (!activePoem) return null

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between px-4 py-1 border-b border-border bg-surface shrink-0">
        <span className="text-text-muted text-xs">{activePoem.filename}</span>
        <button
          onClick={handleSave}
          disabled={!isDirty}
          className="text-xs px-2 py-0.5 rounded border border-accent/40 text-accent disabled:opacity-30 hover:bg-accent/10 transition-colors"
        >
          {isDirty ? 'Save' : 'Saved'}
        </button>
      </div>
      <div className="flex-1 overflow-hidden">
        <CodeMirror
          value={editorContent}
          height="100%"
          extensions={[markdown(), darkTheme]}
          onChange={setEditorContent}
          basicSetup={{
            lineNumbers: true,
            highlightActiveLine: true,
            autocompletion: false,
          }}
        />
      </div>
    </div>
  )
}
