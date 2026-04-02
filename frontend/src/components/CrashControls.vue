<template>
  <div style="padding: 1rem">
    <h2>Crash Controls</h2>
    <button @click="crash('auth')">Crash Auth Service</button>
    <button @click="crash('booking')">Crash Booking Service</button>
    <button @click="crash('damage')">Crash Damage Service</button>
    <button @click="crashMailWorker">Crash Mail Worker</button>
    <div v-if="result" style="margin-top:1rem">{{ result }}</div>
  </div>
</template>

<script>
import api from "../api";

export default {
  data() {
    return { result: null };
  },
  methods: {
    async crash(service) {
      try {
        const urlMap = {
          auth: "http://localhost:8000/__debug/crash",
          booking: "http://localhost:8001/__debug/crash",
          damage: "http://localhost:8002/__debug/crash",
        };
        await fetch(urlMap[service], { method: "GET" });
      } catch (e) {
        this.result = `Request sent (service may have crashed): ${service}`;
      }
    },
    async crashMailWorker() {
      try {
        await api.createBooking("SIM", "test@example.com");
        // send explicit signal
        await fetch("http://localhost:8001/__debug/crash-mail-worker", { method: "POST" });
        this.result = "Signal poslan mail-workeru";
      } catch (e) {
        this.result = "Signal poslan (provjeri logs)";
      }
    },
  },
};
</script>

<style scoped>
button {
  margin-right: 0.5rem;
  margin-bottom: 0.5rem;
}
</style>
