<template>
  <div class="bookings">
    <div class="card">
      <h1>Rezervacije Vozila</h1>

      <div v-if="success" class="alert alert-success">
        {{ success }}
      </div>

      <div v-if="error" class="alert alert-error">
        {{ error }}
      </div>

      <form @submit.prevent="createBooking" class="booking-form">
        <div class="form-row">
          <div class="form-group">
            <label for="carId">Vozilo *</label>
            <select id="carId" v-model="formData.carId" required>
              <option value="">Odaberite vozilo</option>
              <option value="BMW-X5-2024">BMW X5 (2024) - 150€/dan</option>
              <option value="AUDI-A6-2024">Audi A6 (2024) - 120€/dan</option>
              <option value="MERCEDES-C200-2024">
                Mercedes C200 (2024) - 130€/dan
              </option>
              <option value="VW-GOLF-2024">VW Golf (2024) - 50€/dan</option>
              <option value="SKODA-OCTAVIA-2024">
                Škoda Octavia (2024) - 60€/dan
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="email">Email adresa *</label>
            <input
              id="email"
              v-model="formData.email"
              type="email"
              placeholder="vas.email@example.com"
              required
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="dateFrom">Datum preuzimanja *</label>
            <input
              id="dateFrom"
              v-model="formData.dateFrom"
              type="date"
              required
              :min="today"
            />
          </div>

          <div class="form-group">
            <label for="dateTo">Datum vraćanja *</label>
            <input
              id="dateTo"
              v-model="formData.dateTo"
              type="date"
              required
              :min="formData.dateFrom || today"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="passengers">Broj putnika</label>
            <input
              id="passengers"
              v-model.number="formData.passengers"
              type="number"
              min="1"
              max="8"
              value="1"
            />
          </div>

          <div class="form-group">
            <label for="phone">Telefon</label>
            <input
              id="phone"
              v-model="formData.phone"
              type="tel"
              placeholder="+385 91 234 5678"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="notes">Napomena (opcionalno)</label>
          <textarea
            id="notes"
            v-model="formData.notes"
            rows="3"
            placeholder="Dodatne napomene ili posebni zahtjevi..."
          ></textarea>
        </div>

        <button type="submit" class="btn" :disabled="loading">
          {{ loading ? "Kreiram rezervaciju..." : "🚗 Kreiraj rezervaciju" }}
        </button>
      </form>

      <div class="info-box">
        <h3>ℹ️ Kako radi rezervacija?</h3>
        <ol>
          <li>Odaberite vozilo, datum i unesite kontakt podatke</li>
          <li>Sustav kreira rezervaciju u DynamoDB</li>
          <li>Asinkrono se šalje poruka u Redis queue</li>
          <li>
            Mail Worker preuzima poruku i šalje email potvrdu (simulacija)
          </li>
        </ol>
        <p>
          <strong>📧 Napomena o emailu:</strong> Ovo je demo - Mail Worker
          simulira slanje emaila. Možete vidjeti aktivnost u logovima:
          <code>docker-compose logs -f mail-worker</code>
        </p>
      </div>

      <div v-if="lastBooking" class="booking-result">
        <h3>✅ Posljednja rezervacija</h3>
        <div class="result-content">
          <div class="result-grid">
            <div class="result-item">
              <span class="label">Booking ID:</span>
              <code>{{ lastBooking.booking_id }}</code>
            </div>
            <div class="result-item">
              <span class="label">Vozilo:</span>
              <strong>{{ lastBooking.carId }}</strong>
            </div>
            <div class="result-item">
              <span class="label">Email:</span>
              <strong>{{ lastBooking.email }}</strong>
            </div>
            <div class="result-item">
              <span class="label">Datum:</span>
              <strong
                >{{ lastBooking.dateFrom }} → {{ lastBooking.dateTo }}</strong
              >
            </div>
            <div class="result-item" v-if="lastBooking.passengers">
              <span class="label">Putnici:</span>
              <strong>{{ lastBooking.passengers }}</strong>
            </div>
            <div class="result-item" v-if="lastBooking.phone">
              <span class="label">Telefon:</span>
              <strong>{{ lastBooking.phone }}</strong>
            </div>
            <div class="result-item" v-if="lastBooking.notes">
              <span class="label">Napomena:</span>
              <span>{{ lastBooking.notes }}</span>
            </div>
            <div class="result-item">
              <span class="label">Status:</span>
              <span class="badge-success">{{
                lastBooking.status || "Potvrđeno"
              }}</span>
            </div>
          </div>
          <div class="mail-info">
            <p>
              📧 <strong>Mail Worker status:</strong> Poruka poslana u Redis
              queue. Provjeri terminalne logove da vidiš simulaciju slanja
              emaila!
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed } from "vue";
import api from "../api";

export default {
  name: "Bookings",
  setup() {
    const formData = reactive({
      carId: "",
      email: "",
      dateFrom: "",
      dateTo: "",
      passengers: 1,
      phone: "",
      notes: "",
    });

    const loading = ref(false);
    const success = ref("");
    const error = ref("");
    const lastBooking = ref(null);

    const today = computed(() => {
      const date = new Date();
      return date.toISOString().split("T")[0];
    });

    const createBooking = async () => {
      loading.value = true;
      success.value = "";
      error.value = "";

      try {
        const response = await api.createBooking(
          formData.carId,
          formData.email,
        );

        lastBooking.value = {
          ...response.data,
          carId: formData.carId,
          email: formData.email,
          dateFrom: formData.dateFrom,
          dateTo: formData.dateTo,
          passengers: formData.passengers,
          phone: formData.phone,
          notes: formData.notes,
        };

        success.value =
          "✅ Rezervacija uspješno kreirana! Mail Worker procesira potvrdu u pozadini.";

        formData.carId = "";
        formData.email = "";
        formData.dateFrom = "";
        formData.dateTo = "";
        formData.passengers = 1;
        formData.phone = "";
        formData.notes = "";
      } catch (err) {
        error.value =
          err.response?.data?.detail || "Greška pri kreiranju rezervacije";
        console.error("Booking error:", err);
      } finally {
        loading.value = false;
      }
    };

    return {
      formData,
      loading,
      success,
      error,
      lastBooking,
      today,
      createBooking,
    };
  },
};
</script>

<style scoped>
.bookings h1 {
  color: #333;
  margin-bottom: 1.5rem;
}

.booking-form {
  max-width: 800px;
  margin-bottom: 2rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 0;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}

.info-box {
  background: #e7f3ff;
  border-left: 4px solid #2196f3;
  padding: 1.5rem;
  border-radius: 5px;
  margin-top: 2rem;
}

.info-box h3 {
  color: #1976d2;
  margin-bottom: 1rem;
}

.info-box ol {
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

.info-box li {
  margin-bottom: 0.5rem;
  color: #333;
}

.info-box p {
  margin-top: 1rem;
  color: #555;
}

.info-box code {
  background: #333;
  color: #0f0;
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
  font-size: 0.9rem;
}

.booking-result {
  background: #f0f9ff;
  border: 2px solid #667eea;
  padding: 1.5rem;
  border-radius: 10px;
  margin-top: 2rem;
}

.booking-result h3 {
  color: #667eea;
  margin-bottom: 1.5rem;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.result-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.result-item .label {
  color: #666;
  font-size: 0.9rem;
  font-weight: 500;
}

.result-item strong {
  color: #333;
  font-size: 1rem;
}

.result-item code {
  background: #e7e7e7;
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
  font-family: "Courier New", monospace;
  font-size: 0.85rem;
  display: inline-block;
}

.mail-info {
  background: #fff3cd;
  border: 1px solid #ffc107;
  padding: 1rem;
  border-radius: 5px;
  margin-top: 1rem;
}

.mail-info p {
  margin: 0;
  color: #856404;
  font-size: 0.95rem;
}

.badge-success {
  background: #10b981;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.9rem;
  display: inline-block;
}
</style>
