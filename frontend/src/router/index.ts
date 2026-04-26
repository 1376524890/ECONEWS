import { createRouter, createWebHistory } from "vue-router";
import AnalyzerView from "../views/AnalyzerView.vue";
import DashboardView from "../views/DashboardView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "dashboard", component: DashboardView },
    { path: "/analyzer", name: "analyzer", component: AnalyzerView },
  ],
});

export default router;

