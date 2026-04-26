<script setup lang="ts">
import * as echarts from "echarts";
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import type { ImpactScore } from "../types";

const props = defineProps<{
  impactScore?: ImpactScore | null;
}>();

const chartRef = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;

function renderChart() {
  if (!chartRef.value || !props.impactScore) {
    return;
  }
  chart ??= echarts.init(chartRef.value);
  chart.setOption({
    backgroundColor: "transparent",
    radar: {
      indicator: [
        { name: "E", max: 1 },
        { name: "S", max: 1 },
        { name: "R", max: 1 },
        { name: "C", max: 1 },
        { name: "A", max: 1 },
      ],
      radius: "62%",
      splitNumber: 4,
      axisName: { color: "#d8f8ff" },
      splitArea: { areaStyle: { color: ["rgba(20,42,62,0.2)", "rgba(6,20,34,0.45)"] } },
      splitLine: { lineStyle: { color: "rgba(120,220,255,0.25)" } },
      axisLine: { lineStyle: { color: "rgba(120,220,255,0.25)" } },
    },
    series: [
      {
        type: "radar",
        symbolSize: 8,
        data: [
          {
            value: [
              props.impactScore.E,
              props.impactScore.S,
              props.impactScore.R,
              props.impactScore.C,
              props.impactScore.A,
            ],
            areaStyle: { color: "rgba(88, 198, 255, 0.24)" },
            lineStyle: { width: 2, color: "#6cf6ff" },
            itemStyle: { color: "#fff08f" },
          },
        ],
      },
    ],
  });
}

function resize() {
  chart?.resize();
}

onMounted(() => {
  renderChart();
  window.addEventListener("resize", resize);
});

watch(() => props.impactScore, renderChart, { deep: true });

onBeforeUnmount(() => {
  window.removeEventListener("resize", resize);
  chart?.dispose();
});
</script>

<template>
  <section class="panel chart-panel">
    <div class="section-title">
      <span>NIS 评分雷达</span>
      <strong v-if="impactScore">{{ impactScore.NIS_total.toFixed(3) }} / {{ impactScore.impact_level }}</strong>
    </div>
    <div ref="chartRef" class="chart-body"></div>
  </section>
</template>

