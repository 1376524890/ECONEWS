<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import { fetchAnalyses, fetchFeed, fetchHeartbeats, fetchOverview, runCrawlerOnce } from "../api/client";
import HeartbeatPanel from "../components/HeartbeatPanel.vue";
import NewsTicker from "../components/NewsTicker.vue";
import RadarChart from "../components/RadarChart.vue";
import StatCard from "../components/StatCard.vue";
import TransmissionGraph from "../components/TransmissionGraph.vue";
import type { AnalysisResponse, DashboardOverview, FeedItem, HeartbeatStatus } from "../types";

const overview = ref<DashboardOverview>({
  total_events: 0,
  strong_events: 0,
  avg_nis: 0,
  top_event_type: "暂无数据",
  latest_updated_at: new Date().toISOString(),
});
const feed = ref<FeedItem[]>([]);
const heartbeats = ref<HeartbeatStatus[]>([]);
const analyses = ref<AnalysisResponse[]>([]);
const loading = ref(false);
let timer: number | undefined;

async function refresh() {
  loading.value = true;
  try {
    const [overviewData, feedData, heartbeatData, analysisData] = await Promise.all([
      fetchOverview(),
      fetchFeed(),
      fetchHeartbeats(),
      fetchAnalyses(),
    ]);
    overview.value = overviewData;
    feed.value = feedData;
    heartbeats.value = heartbeatData;
    analyses.value = analysisData;
  } finally {
    loading.value = false;
  }
}

async function triggerCrawler() {
  await runCrawlerOnce();
  await refresh();
}

onMounted(async () => {
  await refresh();
  timer = window.setInterval(refresh, 30000);
});

onBeforeUnmount(() => {
  if (timer) {
    window.clearInterval(timer);
  }
});
</script>

<template>
  <div class="dashboard-grid">
    <section class="hero panel">
      <div>
        <p class="eyebrow">24×7 Macro Event Pipeline</p>
        <h2>从财经快讯到事件研究验证的一体化量化看板</h2>
        <p class="hero-copy">
          采集东方财富与第一财经新闻流，自动完成事件类型识别、经济变量映射、NIS 打分与事件研究降级验证。
        </p>
      </div>
      <button class="primary-btn" :disabled="loading" @click="triggerCrawler">
        {{ loading ? "刷新中..." : "手动触发采集" }}
      </button>
    </section>

    <section class="stats-grid">
      <StatCard label="累计事件" :value="overview.total_events" hint="已完成结构化分析的新闻数量" />
      <StatCard label="较强以上" :value="overview.strong_events" hint="NIS > 0.6 的高关注事件" />
      <StatCard label="平均 NIS" :value="overview.avg_nis.toFixed(3)" hint="当前分析样本的平均影响评分" />
      <StatCard label="热点类型" :value="overview.top_event_type" hint="样本中出现频次最高的事件类别" />
    </section>

    <NewsTicker :items="feed" />

    <TransmissionGraph class="span-4" :chain="analyses[0]?.transmission_chain" />
    <RadarChart class="span-4" :impact-score="analyses[0]?.impact_score" />
    <HeartbeatPanel class="span-4" :items="heartbeats" />

    <section class="panel latest-panel">
      <div class="section-title">
        <span>最新分析结果</span>
        <strong v-if="analyses[0]">{{ analyses[0].event_type }}</strong>
      </div>
      <article v-if="analyses[0]" class="analysis-card">
        <h3>{{ analyses[0].news_title }}</h3>
        <p>{{ analyses[0].summary }}</p>
        <div class="tag-row">
          <span class="tag">主体：{{ analyses[0].event_subject }}</span>
          <span class="tag">事件：{{ analyses[0].event_name }}</span>
          <span class="tag">验证：{{ analyses[0].event_study.verification_result }}</span>
        </div>
      </article>
      <p v-else class="empty-state">暂无分析数据，可点击上方按钮触发样本采集。</p>
    </section>

    <section class="panel list-panel">
      <div class="section-title">
        <span>事件变量映射</span>
      </div>
      <div v-if="analyses[0]" class="variables-list">
        <article
          v-for="item in analyses[0].economic_variables"
          :key="item.variable"
          class="variable-item"
        >
          <h4>{{ item.variable }} · {{ item.direction }}</h4>
          <p>{{ item.logic }}</p>
          <small>{{ item.meaning }}</small>
        </article>
      </div>
      <p v-else class="empty-state">等待分析结果。</p>
    </section>
  </div>
</template>

