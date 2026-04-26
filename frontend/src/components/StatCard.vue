<script setup lang="ts">
defineProps<{
  label: string;
  value: string | number;
  hint: string;
}>();
</script>

<template>
  <section class="panel stat-card">
    <p class="stat-label">{{ label }}</p>
    <h3>{{ value }}</h3>
    <p class="stat-hint">{{ hint }}</p>
  </section>
</template>

