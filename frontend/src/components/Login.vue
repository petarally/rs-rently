<template>
  <div class="login-container">
    <div class="card login-card">
      <h1>🚗 RS-Rently</h1>
      <p class="subtitle">Rent-a-Car Sustav</p>

      <div v-if="error" class="alert alert-error">
        {{ error }}
      </div>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">Korisničko ime</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="admin"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">Lozinka</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="••••••"
            required
          />
        </div>

        <button type="submit" class="btn btn-block" :disabled="loading">
          {{ loading ? "Prijavljivanje..." : "Prijava" }}
        </button>
      </form>

      <div class="demo-info">
        <p><small>Demo pristup: admin / admin</small></p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api";

export default {
  name: "Login",
  setup() {
    const router = useRouter();
    const username = ref("");
    const password = ref("");
    const loading = ref(false);
    const error = ref("");

    const handleLogin = async () => {
      loading.value = true;
      error.value = "";

      try {
        const response = await api.login(username.value, password.value);
        const { access_token } = response.data;

        localStorage.setItem("token", access_token);
        localStorage.setItem("username", username.value);

        router.push("/dashboard");
      } catch (err) {
        error.value =
          err.response?.data?.detail || "Greška pri prijavi. Pokušajte ponovo.";
      } finally {
        loading.value = false;
      }
    };

    return {
      username,
      password,
      loading,
      error,
      handleLogin,
    };
  },
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
}

.login-card {
  max-width: 400px;
  width: 100%;
  text-align: center;
}

.login-card h1 {
  color: #667eea;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #666;
  margin-bottom: 2rem;
}

.btn-block {
  width: 100%;
}

.demo-info {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
  color: #666;
}
</style>
