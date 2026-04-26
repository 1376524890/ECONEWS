<script setup lang="ts">
import type { FeedItem } from "../types";

defineProps<{
  items: FeedItem[];
}>();
</script>

<template>
  <section class="panel ticker-panel">
    <div class="section-title">
      <span>实时资讯滚播</span>
    </div>
    <div class="ticker-track">
      <div class="ticker-content">
        <span v-for="item in items" :key="`${item.source}-${item.title}`">
          {{ item.source }} / {{ item.title }}
        </span>
      </div>
    </div>
  </section>
</template>

