<script setup lang="ts">
import type { HeartbeatStatus } from "../types";

defineProps<{
  items: HeartbeatStatus[];
}>();
</script>

<template>
  <section class="panel heartbeat-panel">
    <div class="section-title">
      <span>爬虫心跳监控</span>
    </div>
    <div class="heartbeat-list">
      <article v-for="item in items" :key="item.source" class="heartbeat-item">
        <div>
          <p class="heartbeat-source">{{ item.source }}</p>
          <p class="heartbeat-meta">{{ item.message }}</p>
        </div>
        <div class="heartbeat-side">
          <span :class="['status-pill', item.status]">{{ item.status }}</span>
          <small>{{ item.latest_count }} 条</small>
        </div>
      </article>
    </div>
  </section>
</template>

