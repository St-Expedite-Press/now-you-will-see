import { useMemo, useState } from 'react'
import {
  AlertTriangle,
  CheckCircle2,
  FileSearch,
  Gauge,
  Play,
  ShieldAlert,
} from 'lucide-react'
import { useAuditStore } from '@/store/useAuditStore'
import type { AuditRun, AuditSubagentResult, EvidenceKind, FindingSeverity } from '@/types/audit'

type Tab = 'overview' | 'evidence' | 'subagents' | 'report'

const TABS: { id: Tab; label: string }[] = [
  { id: 'overview', label: 'Overview' },
  { id: 'evidence', label: 'Evidence' },
  { id: 'subagents', label: 'Subagents' },
  { id: 'report', label: 'Final Report' },
]

const severityClass: Record<FindingSeverity, string> = {
  critical: 'border-red-500/40 bg-red-500/10 text-red-200',
  high: 'border-orange-500/40 bg-orange-500/10 text-orange-100',
  medium: 'border-amber-500/40 bg-amber-500/10 text-amber-100',
  low: 'border-border bg-surface text-text-secondary',
}

const evidenceKinds: EvidenceKind[] = ['file', 'command', 'test', 'doc', 'api', 'ui']

interface Props {
  projectId: string
}

export default function AuditDashboard({ projectId }: Props) {
  const { activeRun, running, error, runAudit } = useAuditStore()
  const [tab, setTab] = useState<Tab>('overview')
  const [kind, setKind] = useState<EvidenceKind | 'all'>('all')

  const evidence = useMemo(() => {
    const refs = activeRun?.subagents.flatMap((agent) =>
      agent.evidence.map((item) => ({ ...item, agent: agent.name, category: agent.category }))
    ) ?? []
    return kind === 'all' ? refs : refs.filter((item) => item.kind === kind)
  }, [activeRun, kind])

  return (
    <div className="flex h-full min-w-0 flex-1 flex-col overflow-hidden bg-canvas">
      <div className="shrink-0 border-b border-border bg-surface px-5 py-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="min-w-0">
            <div className="flex items-center gap-2 text-text-primary">
              <ShieldAlert className="h-4 w-4 text-accent" />
              <h1 className="text-sm font-semibold">Product Readiness Audit</h1>
            </div>
            <p className="mt-1 text-xs text-text-muted">
              Read-only inspection for {projectId}. Evidence first, verdict last.
            </p>
          </div>
          <button
            type="button"
            onClick={runAudit}
            disabled={running}
            className="inline-flex items-center gap-2 rounded-md border border-accent/30 bg-accent/15 px-3 py-2 text-xs font-medium text-accent transition hover:bg-accent/20 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <Play className="h-3.5 w-3.5" />
            {running ? 'Running Audit' : activeRun ? 'Run Again' : 'Run Audit'}
          </button>
        </div>
        {error && (
          <div className="mt-3 rounded-md border border-red-500/30 bg-red-500/10 px-3 py-2 text-xs text-red-100">
            {error}
          </div>
        )}
      </div>

      <div className="flex shrink-0 border-b border-border bg-canvas px-5">
        {TABS.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => setTab(item.id)}
            className={`border-b-2 px-3 py-3 text-xs font-medium transition ${
              tab === item.id
                ? 'border-accent text-accent'
                : 'border-transparent text-text-muted hover:text-text-primary'
            }`}
          >
            {item.label}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-4">
        {!activeRun && !running && <EmptyState onRun={runAudit} />}
        {running && <RunningState />}
        {activeRun && tab === 'overview' && <Overview run={activeRun} />}
        {activeRun && tab === 'evidence' && (
          <EvidenceList evidence={evidence} kind={kind} onKindChange={setKind} />
        )}
        {activeRun && tab === 'subagents' && <Subagents agents={activeRun.subagents} />}
        {activeRun && tab === 'report' && <FinalReport run={activeRun} />}
      </div>
    </div>
  )
}

function EmptyState({ onRun }: { onRun: () => void }) {
  return (
    <div className="flex h-full items-center justify-center">
      <div className="max-w-md rounded-md border border-border bg-surface px-6 py-8 text-center">
        <FileSearch className="mx-auto h-8 w-8 text-accent" />
        <p className="mt-4 text-sm text-text-primary">No audit run yet</p>
        <p className="mt-2 text-xs leading-5 text-text-muted">
          The audit reads the repo, runs verification commands, and records failures as evidence.
        </p>
        <button
          type="button"
          onClick={onRun}
          className="mt-5 inline-flex items-center gap-2 rounded-md border border-accent/30 bg-accent/15 px-3 py-2 text-xs font-medium text-accent"
        >
          <Play className="h-3.5 w-3.5" />
          Run Audit
        </button>
      </div>
    </div>
  )
}

function RunningState() {
  return (
    <div className="rounded-md border border-border bg-surface px-4 py-3 text-xs text-text-secondary">
      Collecting evidence. This can take a while because pytest, TypeScript, and frontend build checks run as part of the read-only audit.
    </div>
  )
}

function Overview({ run }: { run: AuditRun }) {
  const report = run.report
  const highFindings = report?.priority_findings.filter((f) => f.severity === 'critical' || f.severity === 'high') ?? []

  return (
    <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_22rem]">
      <div className="space-y-4">
        <section className="rounded-md border border-border bg-surface p-4">
          <div className="flex items-center gap-2 text-text-primary">
            <Gauge className="h-4 w-4 text-accent" />
            <h2 className="text-sm font-semibold">Verdict</h2>
          </div>
          <p className="mt-3 text-xl font-semibold text-text-primary">
            {formatVerdict(report?.verdict ?? 'promising_not_ready')}
          </p>
          <p className="mt-2 text-sm leading-6 text-text-secondary">{report?.executive_summary}</p>
        </section>

        <section className="rounded-md border border-border bg-surface p-4">
          <h2 className="text-sm font-semibold text-text-primary">Highest-Risk Assumption</h2>
          <p className="mt-2 text-sm leading-6 text-text-secondary">{report?.highest_risk_assumption}</p>
        </section>

        <section className="rounded-md border border-border bg-surface p-4">
          <h2 className="text-sm font-semibold text-text-primary">Priority Findings</h2>
          <div className="mt-3 space-y-3">
            {(report?.priority_findings ?? []).map((finding, index) => (
              <FindingBlock key={`${finding.claim}-${index}`} finding={finding} />
            ))}
          </div>
        </section>
      </div>

      <aside className="space-y-4">
        <section className="rounded-md border border-border bg-surface p-4">
          <h2 className="text-sm font-semibold text-text-primary">Category Scores</h2>
          <div className="mt-3 space-y-2">
            {Object.entries(report?.category_scores ?? {}).map(([category, score]) => (
              <div key={category}>
                <div className="flex items-center justify-between gap-3 text-xs">
                  <span className="truncate text-text-secondary">{category}</span>
                  <span className="text-text-primary">{score}/10</span>
                </div>
                <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-canvas">
                  <div className="h-full rounded-full bg-accent" style={{ width: `${score * 10}%` }} />
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-md border border-border bg-surface p-4">
          <h2 className="text-sm font-semibold text-text-primary">Audit Run</h2>
          <dl className="mt-3 space-y-2 text-xs">
            <Row label="Status" value={run.status} />
            <Row label="Mode" value={run.mode} />
            <Row label="Framework" value={run.frontend_framework} />
            <Row label="High risks" value={String(highFindings.length)} />
          </dl>
        </section>
      </aside>
    </div>
  )
}

function EvidenceList({
  evidence,
  kind,
  onKindChange,
}: {
  evidence: Array<{ id: string; kind: EvidenceKind; path?: string | null; command?: string | null; observed: string; agent: string; category: string }>
  kind: EvidenceKind | 'all'
  onKindChange: (kind: EvidenceKind | 'all') => void
}) {
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {(['all', ...evidenceKinds] as Array<EvidenceKind | 'all'>).map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => onKindChange(item)}
            className={`rounded-md border px-3 py-1.5 text-xs capitalize ${
              kind === item
                ? 'border-accent/40 bg-accent/15 text-accent'
                : 'border-border bg-surface text-text-muted hover:text-text-primary'
            }`}
          >
            {item}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {evidence.map((item) => (
          <article key={`${item.agent}-${item.id}`} className="rounded-md border border-border bg-surface p-4">
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className="rounded border border-border bg-canvas px-2 py-0.5 uppercase text-text-muted">
                {item.kind}
              </span>
              <span className="text-text-primary">{item.agent}</span>
              <span className="text-text-muted">{item.category}</span>
            </div>
            {(item.path || item.command) && (
              <p className="mt-2 break-all font-mono text-[11px] text-text-muted">
                {item.path ?? item.command}
              </p>
            )}
            <p className="mt-2 whitespace-pre-wrap text-xs leading-5 text-text-secondary">{item.observed}</p>
          </article>
        ))}
      </div>
    </div>
  )
}

function Subagents({ agents }: { agents: AuditSubagentResult[] }) {
  return (
    <div className="grid gap-3 lg:grid-cols-2">
      {agents.map((agent) => (
        <article key={agent.id} className="rounded-md border border-border bg-surface p-4">
          <div className="flex items-start justify-between gap-3">
            <div>
              <h2 className="text-sm font-semibold text-text-primary">{agent.name}</h2>
              <p className="mt-1 text-xs text-text-muted">{agent.category}</p>
            </div>
            <StatusPill status={agent.status} />
          </div>
          <div className="mt-4 flex items-center gap-3">
            <div className="text-2xl font-semibold text-text-primary">{agent.score}</div>
            <div className="min-w-0 flex-1">
              <div className="h-1.5 overflow-hidden rounded-full bg-canvas">
                <div className="h-full rounded-full bg-accent" style={{ width: `${(agent.score / agent.max_score) * 100}%` }} />
              </div>
              <p className="mt-1 text-[11px] text-text-muted">{agent.findings.length} findings, {agent.evidence.length} evidence refs</p>
            </div>
          </div>
          {agent.findings.length > 0 && (
            <div className="mt-4 space-y-2">
              {agent.findings.map((finding, index) => (
                <FindingBlock key={`${agent.id}-${index}`} finding={finding} compact />
              ))}
            </div>
          )}
        </article>
      ))}
    </div>
  )
}

function FinalReport({ run }: { run: AuditRun }) {
  const report = run.report
  if (!report) return null

  return (
    <div className="mx-auto max-w-4xl space-y-4">
      <section className="rounded-md border border-border bg-surface p-5">
        <h2 className="text-base font-semibold text-text-primary">{formatVerdict(report.verdict)}</h2>
        <p className="mt-3 text-sm leading-6 text-text-secondary">{report.executive_summary}</p>
      </section>

      <section className="grid gap-3 md:grid-cols-2">
        <ReportCard title="What is this?" value={report.one_sentence_product} />
        <ReportCard title="Who is it for?" value={report.specific_user} />
        <ReportList title="Works today" values={report.works_today_without_founder} icon="check" />
        <ReportList title="Breaks first" values={report.breaks_first} icon="warn" />
      </section>

      <section className="rounded-md border border-border bg-surface p-5">
        <h2 className="text-sm font-semibold text-text-primary">Next Milestone</h2>
        <p className="mt-2 text-sm leading-6 text-text-secondary">{report.next_risk_reducing_milestone}</p>
      </section>
    </div>
  )
}

function FindingBlock({ finding, compact = false }: { finding: { severity: FindingSeverity; claim: string; product_risk: string; recommended_next_step: string }; compact?: boolean }) {
  return (
    <div className={`rounded-md border p-3 ${severityClass[finding.severity]}`}>
      <div className="flex items-start gap-2">
        <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
        <div className="min-w-0">
          <p className="text-xs font-semibold">{finding.claim}</p>
          {!compact && <p className="mt-2 text-xs leading-5 opacity-90">{finding.product_risk}</p>}
          <p className="mt-2 text-xs leading-5 opacity-90">{finding.recommended_next_step}</p>
        </div>
      </div>
    </div>
  )
}

function StatusPill({ status }: { status: string }) {
  const ok = status === 'pass'
  return (
    <span className={`inline-flex items-center gap-1 rounded-md border px-2 py-1 text-[11px] uppercase ${
      ok ? 'border-green-500/30 bg-green-500/10 text-green-200' : 'border-amber-500/30 bg-amber-500/10 text-amber-100'
    }`}>
      {ok ? <CheckCircle2 className="h-3 w-3" /> : <AlertTriangle className="h-3 w-3" />}
      {status}
    </span>
  )
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <dt className="text-text-muted">{label}</dt>
      <dd className="truncate text-text-primary">{value}</dd>
    </div>
  )
}

function ReportCard({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-md border border-border bg-surface p-4">
      <h3 className="text-sm font-semibold text-text-primary">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-text-secondary">{value}</p>
    </div>
  )
}

function ReportList({ title, values, icon }: { title: string; values: string[]; icon: 'check' | 'warn' }) {
  const Icon = icon === 'check' ? CheckCircle2 : AlertTriangle
  return (
    <div className="rounded-md border border-border bg-surface p-4">
      <h3 className="text-sm font-semibold text-text-primary">{title}</h3>
      <div className="mt-3 space-y-2">
        {values.map((value) => (
          <div key={value} className="flex gap-2 text-sm leading-5 text-text-secondary">
            <Icon className="mt-0.5 h-3.5 w-3.5 shrink-0 text-accent" />
            <span>{value}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function formatVerdict(verdict: string): string {
  return verdict.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase())
}
