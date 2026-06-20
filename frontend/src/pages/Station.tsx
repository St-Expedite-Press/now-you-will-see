import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useStationStore } from '@/store/useStationStore'
import type { ChatEntry, StageStep } from '@/types/station'

const PURPLE = '#7B2CBF'

export default function Station() {
  const { projectId } = useParams<{ projectId: string }>()
  const {
    screens,
    activeScreen,
    activeStage,
    agent,
    threads,
    sending,
    error,
    init,
    selectScreen,
    send,
    handOff,
  } = useStationStore()
  const [draft, setDraft] = useState('')

  useEffect(() => {
    if (projectId) void init(projectId)
  }, [projectId, init])

  const thread = activeStage ? threads[activeStage] ?? [] : []
  const isLast = screens.length > 0 && screens[screens.length - 1]?.id === activeScreen

  const submit = () => {
    const text = draft.trim()
    if (!text) return
    setDraft('')
    void send(text)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', fontFamily: 'system-ui' }}>
      {/* Stage rail */}
      <nav style={{ display: 'flex', gap: 8, padding: 12, borderBottom: '1px solid #e5e5e5', alignItems: 'center' }}>
        <strong style={{ marginRight: 12 }}>✦ {projectId}</strong>
        {screens.map((s) => {
          const on = s.id === activeScreen
          return (
            <button
              key={s.id}
              onClick={() => void selectScreen(s.id)}
              style={{
                padding: '6px 14px',
                borderRadius: 6,
                border: `1px solid ${on ? PURPLE : '#ccc'}`,
                background: on ? PURPLE : '#fff',
                color: on ? '#fff' : '#333',
                cursor: 'pointer',
              }}
            >
              {s.id} · {s.title}
            </button>
          )
        })}
      </nav>

      <div style={{ display: 'flex', flex: 1, minHeight: 0 }}>
        {/* Agent panel */}
        <aside style={{ width: 280, borderRight: '1px solid #e5e5e5', padding: 16, overflowY: 'auto', fontSize: 13 }}>
          {agent ? (
            <>
              <h3 style={{ margin: '0 0 4px' }}>{agent.title}</h3>
              <div style={{ color: '#888' }}>gated · {agent.stage}</div>
              <Section label="Scope">{agent.scope ?? '—'}</Section>
              <Section label="Skills">{agent.skills.join(', ') || '—'}</Section>
              <Section label="Tools">
                <ul style={{ margin: 0, paddingLeft: 16 }}>
                  {agent.tools.map((t) => (
                    <li key={t}><code>{t}</code></li>
                  ))}
                </ul>
              </Section>
            </>
          ) : (
            <div style={{ color: '#999' }}>Loading agent…</div>
          )}
        </aside>

        {/* Gated chat */}
        <main style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
          <div style={{ flex: 1, overflowY: 'auto', padding: 16 }}>
            {thread.length === 0 && (
              <p style={{ color: '#999' }}>
                Talk to the <b>{agent?.title}</b> agent. It can only act within this stage.
              </p>
            )}
            {thread.map((m, i) => (
              <Bubble key={i} entry={m} />
            ))}
            {sending && <div style={{ color: '#999' }}>…thinking</div>}
            {error && <div style={{ color: '#b00' }}>{error}</div>}
          </div>

          <div style={{ display: 'flex', gap: 8, padding: 12, borderTop: '1px solid #e5e5e5' }}>
            <input
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && submit()}
              placeholder={`Message the ${agent?.title ?? 'stage'} agent…`}
              style={{ flex: 1, padding: 10, borderRadius: 6, border: '1px solid #ccc' }}
            />
            <button onClick={submit} disabled={sending} style={btn(PURPLE)}>Send</button>
          </div>
        </main>
      </div>

      {/* Gate / hand-off bar */}
      <footer style={{ display: 'flex', alignItems: 'center', gap: 16, padding: '10px 16px', borderTop: '1px solid #e5e5e5', background: '#faf9f7' }}>
        <span style={{ fontSize: 13 }}>
          ⛩️ Gate: <code>{agent?.gate ?? 'none'}</code>
        </span>
        <span style={{ fontSize: 13, color: '#666' }}>
          produces: {agent?.io.produces.join(', ') || '—'}
        </span>
        <div style={{ flex: 1 }} />
        <button onClick={handOff} disabled={isLast} style={btn('#009688')}>
          {isLast ? 'Final stage' : 'Hand off →'}
        </button>
      </footer>
    </div>
  )
}

function Section({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ marginTop: 14 }}>
      <div style={{ textTransform: 'uppercase', fontSize: 11, color: '#aaa', letterSpacing: 0.5 }}>{label}</div>
      <div style={{ marginTop: 2 }}>{children}</div>
    </div>
  )
}

function Bubble({ entry }: { entry: ChatEntry }) {
  const mine = entry.role === 'user'
  return (
    <div style={{ display: 'flex', justifyContent: mine ? 'flex-end' : 'flex-start', margin: '8px 0' }}>
      <div style={{ maxWidth: '70%' }}>
        <div
          style={{
            padding: '8px 12px',
            borderRadius: 10,
            background: mine ? PURPLE : '#f1f0ee',
            color: mine ? '#fff' : '#222',
            whiteSpace: 'pre-wrap',
          }}
        >
          {entry.content}
        </div>
        {entry.steps?.map((s, i) => (
          <ToolStep key={i} step={s} />
        ))}
      </div>
    </div>
  )
}

function ToolStep({ step }: { step: StageStep }) {
  const color = !step.allowed ? '#b00' : step.ok ? '#009688' : '#c80'
  const label = !step.allowed ? 'refused' : step.ok ? 'ran' : 'failed'
  return (
    <div style={{ marginTop: 4, fontSize: 12, border: `1px solid ${color}`, borderRadius: 6, padding: '4px 8px' }}>
      <span style={{ color, fontWeight: 600 }}>{label}</span> · <code>{step.tool}</code>
      {step.output && <div style={{ color: '#666', marginTop: 2, whiteSpace: 'pre-wrap' }}>{step.output.slice(0, 400)}</div>}
    </div>
  )
}

function btn(bg: string): React.CSSProperties {
  return { padding: '8px 16px', borderRadius: 6, border: 'none', background: bg, color: '#fff', cursor: 'pointer' }
}
