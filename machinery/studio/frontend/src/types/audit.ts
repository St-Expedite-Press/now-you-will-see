export type AuditVerdict =
  | 'not_ready'
  | 'promising_not_ready'
  | 'narrowly_usable'
  | 'ready_for_limited_users'
  | 'product_ready'

export type AuditRunStatus = 'pending' | 'running' | 'complete' | 'failed'
export type AuditSubagentStatus = 'pass' | 'warn' | 'fail' | 'blocked'
export type FindingSeverity = 'critical' | 'high' | 'medium' | 'low'
export type EvidenceKind = 'file' | 'command' | 'test' | 'doc' | 'api' | 'ui'

export interface EvidenceRef {
  id: string
  kind: EvidenceKind
  path?: string | null
  command?: string | null
  observed: string
}

export interface Finding {
  severity: FindingSeverity
  claim: string
  evidence_refs: string[]
  product_risk: string
  recommended_next_step: string
}

export interface AuditSubagentResult {
  id: string
  name: string
  category: string
  status: AuditSubagentStatus
  score: number
  max_score: number
  findings: Finding[]
  evidence: EvidenceRef[]
  open_questions: string[]
}

export interface ReadinessReport {
  one_sentence_product: string
  specific_user: string
  works_today_without_founder: string[]
  breaks_first: string[]
  next_risk_reducing_milestone: string
  verdict: AuditVerdict
  category_scores: Record<string, number>
  executive_summary: string
  highest_risk_assumption: string
  priority_findings: Finding[]
}

export interface AuditRun {
  id: string
  created_at: string
  repo_root: string
  persona: 'burned_out_bay_area_engineer'
  frontend_framework: 'react'
  mode: 'read_only'
  target: 'texgraph_current_system'
  status: AuditRunStatus
  subagents: AuditSubagentResult[]
  report: ReadinessReport | null
}
