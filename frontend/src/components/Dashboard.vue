<template>
  <div class="dashboard">
    <div class="card">
      <h1>Dashboard</h1>
      <p class="welcome">
        Dobrodošli, <strong>{{ username }}</strong
        >! 👋
      </p>

      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">📋</div>
          <h3>Rezervacije</h3>
          <p>Upravljajte rezervacijama vozila</p>
          <router-link to="/bookings" class="btn">Otvori</router-link>
        </div>

        <div class="stat-card">
          <div class="stat-icon">📸</div>
          <h3>Štete</h3>
          <p>Upload slika šteta na vozilima</p>
          <router-link to="/damage" class="btn">Otvori</router-link>
        </div>

        <div class="stat-card">
          <div class="stat-icon">📍</div>
          <h3>GPS Tracking</h3>
          <p>Praćenje lokacija vozila (gRPC)</p>
          <button class="btn" disabled>Uskoro</button>
        </div>
      </div>

      <div class="info-section">
        <h3>ℹ️ Informacije o sustavu</h3>
        <ul>
          <li>✅ Auth Service - Autentifikacija s JWT tokenima</li>
          <li>✅ Booking Service - Kreiranje rezervacija</li>
          <li>✅ Damage Service - Upload slika na S3</li>
          <li>✅ Mail Worker - Asinkrono slanje emaila</li>
          <li>✅ GPS Tracker - gRPC praćenje lokacija</li>
          <li>✅ Redis - Message broker</li>
          <li>✅ LocalStack - AWS simulacija</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";

export default {
  name: "Dashboard",
  setup() {
    const username = ref("");

    onMounted(() => {
      username.value = localStorage.getItem("username") || "Korisnik";
    });

    return {
      username,
    };
  },
};
</script>

<style scoped>
.dashboard h1 {
  color: #333;
  margin-bottom: 1rem;
}

.welcome {
  color: #666;
  margin-bottom: 2rem;
  font-size: 1.1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  border-radius: 10px;
  text-align: center;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.stat-card h3 {
  margin-bottom: 0.5rem;
}

.stat-card p {
  margin-bottom: 1.5rem;
  opacity: 0.9;
}

.stat-card .btn {
  background: white;
  color: #667eea;
}

.stat-card .btn:hover {
  background: #f8f9fa;
}

.info-section {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 10px;
  margin-top: 2rem;
}

.info-section h3 {
  margin-bottom: 1rem;
  color: #333;
}

.info-section ul {
  list-style: none;
}

.info-section li {
  padding: 0.5rem 0;
  color: #666;
}
</style>
