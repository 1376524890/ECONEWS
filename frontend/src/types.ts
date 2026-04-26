export interface VariableImpact {
  variable: string;
  direction: string;
  logic: string;
  meaning: string;
}

export interface AffectedTarget {
  name: string;
  category: string;
  direction: "利多" | "利空" | "中性" | "不确定";
  rationale: string;
}

export interface ImpactScore {
  E: number;
  S: number;
  R: number;
  C: number;
  A: number;
  NIS_total: number;
  impact_level: string;
}

export interface EventStudy {
  window: string;
  AR: string;
  CAR: string;
  verification_result: string;
}

export interface AnalysisResponse {
  news_title: string;
  event_type: string;
  event_name: string;
  event_subject: string;
  summary: string;
  economic_variables: VariableImpact[];
  transmission_chain: string;
  affected_targets: AffectedTarget[];
  impact_score: ImpactScore;
  event_study: EventStudy;
  decision_support: string;
  risk_warning: string;
}

export interface AnalysisRequest {
  news_title: string;
  news_content: string;
  source: string;
  published_at?: string | null;
  related_assets: string[];
  benchmark: string;
}

export interface DashboardOverview {
  total_events: number;
  strong_events: number;
  avg_nis: number;
  top_event_type: string;
  latest_updated_at: string;
}

export interface HeartbeatStatus {
  source: string;
  status: string;
  last_run?: string;
  latest_count: number;
  message: string;
}

export interface FeedItem {
  title: string;
  source: string;
  published_at?: string;
  url?: string;
}

