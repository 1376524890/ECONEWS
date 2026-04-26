<script setup lang="ts">
import * as echarts from "echarts";
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";

const props = defineProps<{
  chain?: string;
}>();

const chartRef = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;

const segments = computed(() =>
  (props.chain || "")
    .split(/->|→/)
    .map((item) => item.trim())
    .filter(Boolean),
);

function renderChart() {
  if (!chartRef.value || !segments.value.length) {
    return;
  }
  chart ??= echarts.init(chartRef.value);

  const nodes = segments.value.map((name, index) => ({
    id: name,
    name,
    value: index,
    symbolSize: index === 0 ? 58 : index === segments.value.length - 1 ? 46 : 52,
    itemStyle: {
      color: index % 2 === 0 ? "#7cf3ff" : "#f0b36c",
    },
  }));

  const links = segments.value.slice(1).map((name, index) => ({
    source: segments.value[index],
    target: name,
  }));

  chart.setOption({
    backgroundColor: "transparent",
    series: [
      {
        type: "graph",
        layout: "force",
        roam: false,
        draggable: false,
        force: { repulsion: 300, edgeLength: 110 },
        label: {
          show: true,
          color: "#eefcff",
          width: 110,
          overflow: "break",
          fontSize: 12,
        },
        edgeSymbol: ["none", "arrow"],
        edgeSymbolSize: 8,
        lineStyle: {
          color: "rgba(108, 246, 255, 0.7)",
          width: 2,
          curveness: 0.15,
        },
        data: nodes,
        links,
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

watch(segments, renderChart);

onBeforeUnmount(() => {
  window.removeEventListener("resize", resize);
  chart?.dispose();
});
</script>

<template>
  <section class="panel chart-panel">
    <div class="section-title">
      <span>传导逻辑图</span>
      <strong>News → Variables → Targets</strong>
    </div>
    <div ref="chartRef" class="chart-body"></div>
  </section>
</template>

