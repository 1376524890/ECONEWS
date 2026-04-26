import axios from "axios";
import type {
  AnalysisRequest,
  AnalysisResponse,
  DashboardOverview,
  FeedItem,
  HeartbeatStatus,
} from "../types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1",
  timeout: 10000,
});

export async function fetchOverview() {
  const { data } = await api.get<DashboardOverview>("/dashboard/overview");
  return data;
}

export async function fetchFeed() {
  const { data } = await api.get<FeedItem[]>("/dashboard/feed");
  return data;
}

export async function fetchAnalyses() {
  const { data } = await api.get<AnalysisResponse[]>("/dashboard/analyses");
  return data;
}

export async function fetchHeartbeats() {
  const { data } = await api.get<HeartbeatStatus[]>("/system/heartbeats");
  return data;
}

export async function runCrawlerOnce() {
  const { data } = await api.post("/crawlers/run-once");
  return data;
}

export async function analyzeNews(payload: AnalysisRequest) {
  const { data } = await api.post<AnalysisResponse>("/analyze", payload);
  return data;
}

