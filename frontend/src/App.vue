<script setup lang="ts">
import { RouterLink, RouterView, useRoute } from "vue-router";

const route = useRoute();
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">Quant + NLP + Macro Monitor</p>
        <h1>EconoNews</h1>
      </div>
      <nav class="nav">
        <RouterLink :class="{ active: route.name === 'dashboard' }" to="/">数据看板</RouterLink>
        <RouterLink :class="{ active: route.name === 'analyzer' }" to="/analyzer">新闻分析</RouterLink>
      </nav>
    </header>

    <main class="page-shell">
      <RouterView />
    </main>
  </div>
</template>
