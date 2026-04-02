import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import App from "./App.vue";
import Login from "./components/Login.vue";
import Dashboard from "./components/Dashboard.vue";
import Bookings from "./components/Bookings.vue";
import DamageUpload from "./components/DamageUpload.vue";
import CrashControls from "./components/CrashControls.vue";
import * as Sentry from "@sentry/vue";

const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", component: Login },
  { path: "/dashboard", component: Dashboard, meta: { requiresAuth: true } },
  { path: "/bookings", component: Bookings, meta: { requiresAuth: true } },
  { path: "/damage", component: DamageUpload, meta: { requiresAuth: true } },
  { path: "/crash", component: CrashControls, meta: { requiresAuth: true } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token");
  if (to.meta.requiresAuth && !token) {
    next("/login");
  } else {
    next();
  }
});

const app = createApp(App);

Sentry.init({
  app,
  dsn: import.meta.env.VITE_SENTRY_DSN, 
  integrations: [
    Sentry.browserTracingIntegration({ router }),
    Sentry.replayIntegration(),
  ],
  tracesSampleRate: 1.0, 
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
});

app.use(router);
app.mount("#app");
