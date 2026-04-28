<script setup lang="ts">
import { computed, reactive, ref } from "vue";
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
const rawResult = ref<unknown>(null);
const submitting = ref(false);
const errorMessage = ref("");

interface AnalyzerFallbackState {
  active: boolean;
  title: string;
  summary: string;
  reason: string;
  rawText: string;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isVariableList(value: unknown): value is AnalysisResponse["economic_variables"] {
  return Array.isArray(value) && value.every((item) => {
    if (!isRecord(item)) return false;
    return ["variable", "direction", "logic", "meaning"].every((key) => typeof item[key] === "string");
  });
}

function isTargetList(value: unknown): value is AnalysisResponse["affected_targets"] {
  return Array.isArray(value) && value.every((item) => {
    if (!isRecord(item)) return false;
    return ["name", "category", "direction", "rationale"].every((key) => typeof item[key] === "string");
  });
}

function isImpactScore(value: unknown): value is AnalysisResponse["impact_score"] {
  if (!isRecord(value)) return false;
  return ["E", "S", "R", "C", "A", "NIS_total"].every((key) => typeof value[key] === "number")
    && typeof value.impact_level === "string";
}

function isEventStudy(value: unknown): value is AnalysisResponse["event_study"] {
  if (!isRecord(value)) return false;
  return ["window", "AR", "CAR", "verification_result"].every((key) => typeof value[key] === "string");
}

function isAnalysisResponse(value: unknown): value is AnalysisResponse {
  if (!isRecord(value)) return false;
  return typeof value.news_title === "string"
    && typeof value.event_type === "string"
    && typeof value.event_name === "string"
    && typeof value.event_subject === "string"
    && typeof value.summary === "string"
    && typeof value.transmission_chain === "string"
    && typeof value.decision_support === "string"
    && typeof value.risk_warning === "string"
    && isVariableList(value.economic_variables)
    && isTargetList(value.affected_targets)
    && isImpactScore(value.impact_score)
    && isEventStudy(value.event_study);
}

function extractNestedPayload(value: unknown): unknown {
  if (typeof value === "string") {
    return value;
  }
  if (!isRecord(value)) {
    return value;
  }
  const candidates = ["analysis", "result", "data", "output"];
  for (const key of candidates) {
    if (key in value) {
      return value[key];
    }
  }
  return value;
}

function normalizeAnalysisPayload(value: unknown): {
  parsed: AnalysisResponse | null;
  fallback: AnalyzerFallbackState;
} {
  if (value == null) {
    return {
      parsed: null,
      fallback: {
        active: false,
        title: "",
        summary: "",
        reason: "",
        rawText: "",
      },
    };
  }

  const payload = extractNestedPayload(value);
  let parsedValue: unknown = payload;
  let reason = "";

  if (typeof payload === "string") {
    try {
      parsedValue = JSON.parse(payload);
    } catch {
      reason = "返回内容不是合法 JSON，已退回默认输出展示。";
    }
  }

  if (!reason && !isAnalysisResponse(parsedValue)) {
    reason = "分析流程返回的数据结构不完整，已退回默认输出展示。";
  }

  if (!reason && isAnalysisResponse(parsedValue)) {
    return {
      parsed: parsedValue,
      fallback: {
        active: false,
        title: "",
        summary: "",
        reason: "",
        rawText: "",
      },
    };
  }

  const fallbackText =
    typeof payload === "string"
      ? payload
      : JSON.stringify(payload ?? value, null, 2);

  return {
    parsed: null,
    fallback: {
      active: true,
      title: form.news_title || "分析输出",
      summary: "未能生成可直接渲染的结构化结果，当前展示默认输出，便于继续人工核对。",
      reason,
      rawText: fallbackText,
    },
  };
}

const viewState = computed(() => normalizeAnalysisPayload(rawResult.value));

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
    const response = await analyzeNews({
      ...form,
      related_assets: form.related_assets,
    });
    rawResult.value = response;
    result.value = normalizeAnalysisPayload(response).parsed;
  } catch (error) {
    rawResult.value = null;
    result.value = null;
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
            <span class="tag">主体：{{ result.event_subject }}</span>
            <span class="tag">{{ result.impact_score.impact_level }}</span>
          </div>
          <div class="analysis-grid">
            <article class="sub-card">
              <h4>经济变量</h4>
              <div class="detail-list">
                <div
                  v-for="item in result.economic_variables"
                  :key="`${item.variable}-${item.direction}`"
                  class="detail-item"
                >
                  <strong>{{ item.variable }} · {{ item.direction }}</strong>
                  <p>{{ item.logic }}</p>
                  <small>{{ item.meaning }}</small>
                </div>
              </div>
            </article>

            <article class="sub-card">
              <h4>影响标的</h4>
              <div class="detail-list">
                <div
                  v-for="item in result.affected_targets"
                  :key="`${item.name}-${item.direction}`"
                  class="detail-item"
                >
                  <strong>{{ item.name }} · {{ item.direction }}</strong>
                  <p>{{ item.category }}</p>
                  <small>{{ item.rationale }}</small>
                </div>
              </div>
            </article>
          </div>
          <div class="score-grid">
            <article class="score-card">
              <span>E</span>
              <strong>{{ result.impact_score.E.toFixed(2) }}</strong>
            </article>
            <article class="score-card">
              <span>S</span>
              <strong>{{ result.impact_score.S.toFixed(2) }}</strong>
            </article>
            <article class="score-card">
              <span>R</span>
              <strong>{{ result.impact_score.R.toFixed(2) }}</strong>
            </article>
            <article class="score-card">
              <span>C</span>
              <strong>{{ result.impact_score.C.toFixed(2) }}</strong>
            </article>
            <article class="score-card">
              <span>A</span>
              <strong>{{ result.impact_score.A.toFixed(2) }}</strong>
            </article>
            <article class="score-card score-card-total">
              <span>NIS</span>
              <strong>{{ result.impact_score.NIS_total.toFixed(3) }}</strong>
            </article>
          </div>
          <div class="two-col">
            <article class="sub-card">
              <h4>事件研究验证</h4>
              <p>窗口：{{ result.event_study.window }}</p>
              <p>AR：{{ result.event_study.AR }}</p>
              <p>CAR：{{ result.event_study.CAR }}</p>
              <small>{{ result.event_study.verification_result }}</small>
            </article>
            <article class="sub-card">
              <h4>决策支持</h4>
              <p>{{ result.decision_support }}</p>
              <h4>风险提示</h4>
              <p>{{ result.risk_warning }}</p>
            </article>
          </div>
          <details class="raw-output">
            <summary>查看原始 JSON</summary>
            <pre class="json-preview">{{ JSON.stringify(result, null, 2) }}</pre>
          </details>
        </template>
        <template v-else-if="viewState.fallback.active">
          <div class="fallback-banner">
            <strong>默认输出</strong>
            <p>{{ viewState.fallback.reason }}</p>
          </div>
          <h3>{{ viewState.fallback.title }}</h3>
          <p class="result-summary">{{ viewState.fallback.summary }}</p>
          <details class="raw-output" open>
            <summary>查看默认输出内容</summary>
            <pre class="json-preview">{{ viewState.fallback.rawText }}</pre>
          </details>
        </template>
        <p v-else class="empty-state">提交新闻后，这里会显示符合规范的 JSON 结果。</p>
      </section>
    </section>
  </div>
</template>
