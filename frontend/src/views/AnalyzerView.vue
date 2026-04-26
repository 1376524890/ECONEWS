<script setup lang="ts">
import { reactive, ref } from "vue";
import { analyzeNews } from "../api/client";
import RadarChart from "../components/RadarChart.vue";
import TransmissionGraph from "../components/TransmissionGraph.vue";
import type { AnalysisRequest, AnalysisResponse } from "../types";

const form = reactive<AnalysisRequest>({
  news_title: "央行开展逆回购操作 释放稳定流动性信号",
  news_content:
    "中国人民银行开展逆回购操作，以保持银行体系流动性合理充裕。市场认为此举有助于缓和短端资金利率压力，并稳定风险偏好。",
  source: "东方财富",
  published_at: null,
  related_assets: [],
  benchmark: "000300.SH",
});

const result = ref<AnalysisResponse | null>(null);
const submitting = ref(false);
const errorMessage = ref("");

function updateAssets(value: string) {
  form.related_assets = value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function updateAssetsFromEvent(event: Event) {
  updateAssets((event.target as HTMLInputElement | null)?.value ?? "");
}

async function submit() {
  submitting.value = true;
  errorMessage.value = "";
  try {
    result.value = await analyzeNews({
      ...form,
      related_assets: form.related_assets,
    });
  } catch (error) {
    errorMessage.value = "分析请求失败，请确认后端已启动。";
    console.error(error);
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <div class="analyzer-grid">
    <section class="panel form-panel">
      <div class="section-title">
        <span>新闻分析输入</span>
      </div>
      <label class="field">
        <span>新闻标题</span>
        <input v-model="form.news_title" type="text" />
      </label>
      <label class="field">
        <span>新闻来源</span>
        <select v-model="form.source">
          <option>东方财富</option>
          <option>第一财经</option>
          <option>新华社</option>
          <option>manual</option>
        </select>
      </label>
      <label class="field">
        <span>关联资产（逗号分隔，可留空）</span>
        <input
          :value="form.related_assets.join(',')"
          type="text"
          placeholder="如 000001.SZ,600036.SH"
          @input="updateAssetsFromEvent"
        />
      </label>
      <label class="field">
        <span>新闻正文</span>
        <textarea v-model="form.news_content" rows="10"></textarea>
      </label>
      <button class="primary-btn full" :disabled="submitting" @click="submit">
        {{ submitting ? "分析中..." : "生成结构化分析" }}
      </button>
      <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
    </section>

    <section class="result-stack">
      <TransmissionGraph :chain="result?.transmission_chain" />
      <RadarChart :impact-score="result?.impact_score" />

      <section class="panel result-panel">
        <div class="section-title">
          <span>结构化结果</span>
        </div>
        <template v-if="result">
          <h3>{{ result.news_title }}</h3>
          <p class="result-summary">{{ result.summary }}</p>
          <div class="tag-row">
            <span class="tag">{{ result.event_type }}</span>
            <span class="tag">{{ result.event_name }}</span>
            <span class="tag">{{ result.impact_score.impact_level }}</span>
          </div>
          <div class="two-col">
            <article class="sub-card">
              <h4>决策支持</h4>
              <p>{{ result.decision_support }}</p>
            </article>
            <article class="sub-card">
              <h4>风险提示</h4>
              <p>{{ result.risk_warning }}</p>
            </article>
          </div>
          <pre class="json-preview">{{ JSON.stringify(result, null, 2) }}</pre>
        </template>
        <p v-else class="empty-state">提交新闻后，这里会显示符合规范的 JSON 结果。</p>
      </section>
    </section>
  </div>
</template>

