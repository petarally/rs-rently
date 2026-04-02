Kompletan rent-a-car sustav izgrađen s mikroservisnom arhitekturom, Vue.js frontendom i različitim komunikacijskim protokolima.

1. **Auth Service** (FastAPI, port 8000) - JWT autentifikacija
2. **Booking Service** (FastAPI, port 8001) - Rezervacije vozila
3. **Damage Service** (FastAPI, port 8002) - Upload slika šteta
4. **Mail Worker** (Python) - Asinkroni email worker
5. **GPS Tracker** (gRPC, port 50051) - GPS praćenje vozila
6. **LocalStack** (port 4566) - AWS DynamoDB i S3 simulacija
7. **Redis** (port 6379) - Message broker i cache
8. **Frontend** (Vue.js, port 3000) - Korisničko sučelje

- **REST API**: Auth, Booking, Damage servisi
- **gRPC**: GPS Tracker
- **Redis Queue**: Asinkrona komunikacija (Booking → Mail Worker)
- **HTTP/REST**: Inter-service komunikacija

```bash
docker-compose up --build
```

Sustav će biti dostupan na:

- **Frontend**: http://localhost:3000
- Auth Service: http://localhost:8000
- Booking Service: http://localhost:8001
- Damage Service: http://localhost:8002
- GPS Tracker (gRPC): localhost:50051

1. Otvori preglednik na **http://localhost:3000**
2. Prijavi se s demo pristupom:
   - **Username**: `admin`
   - **Password**: `admin`
3. Istraži funkcionalnosti:
   - Dashboard - pregled sustava
   - Rezervacije - kreiranje novih rezervacija
   - Štete - upload slika oštećenja

Za development mode sa hot reload:

```bash
cd frontend
npm install
npm run dev
```

Frontend će biti dostupan na http://localhost:5173

```
frontend/
├── src/
│   ├── components/
│   │   ├── Login.vue          # Login forma
│   │   ├── Dashboard.vue      # Glavni dashboard
│   │   ├── Bookings.vue       # Rezervacije
│   │   └── DamageUpload.vue   # Upload šteta
│   ├── api.js                 # API klijent (axios)
│   ├── main.js                # Vue app + router
│   └── App.vue                # Root komponenta
├── Dockerfile                 # Production build
├── nginx.conf                 # Nginx konfiguracija
├── vite.config.js            # Vite konfiguracija
└── package.json
```

```bash
docker-compose logs -f
```

```bash
docker-compose logs -f frontend
docker-compose logs -f booking-service
docker-compose logs -f mail-worker
```

```bash
docker-compose ps
```

```bash
docker-compose down
```

```bash
docker-compose restart frontend
```

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```

```bash
TOKEN="<tvoj_token>"
curl -X POST "http://localhost:8001/bookings?car_id=BMW-X5&user_email=test@test.com" \
  -H "Authorization: Bearer $TOKEN"
```

```bash
docker exec -it rs-rently-redis-1 redis-cli LLEN email_queue
```

```bash
docker-compose logs -f mail-worker
```

-- ✅ Vue 3 Composition API
-- ✅ Vue Router za navigaciju
-- ✅ Axios za HTTP zahtjeve
-- ✅ JWT autentifikacija
-- ✅ Protected routes
-- ✅ Responsive dizajn
-- ✅ Gradient UI
-- ✅ File upload s previewom
-- ✅ Error handling
-- ✅ Loading states

```bash
docker-compose ps

docker-compose restart auth-service booking-service damage-service
```

```bash
docker-compose logs auth-service | grep CORS
```

```bash
docker-compose restart auth-service booking-service damage-service
```

Dok su servisi pokrenuti:

- Auth Service: http://localhost:8000/docs
- Booking Service: http://localhost:8001/docs
- Damage Service: http://localhost:8002/docs

Ovaj projekt demonstrira:

1. **Mikroservisna arhitektura** - odvojeni servisi
2. **Service Discovery** - Docker DNS
3. **Asinkrona komunikacija** - Redis queue
4. **API Gateway pattern** - Frontend kao gateway
5. **Različiti protokoli** - REST, gRPC, Message Queue
6. **Caching** - Redis
7. **Cloud services** - AWS simulacija
8. **Containerization** - Docker

Edukacijski projekt za kolegij Raspodijeljeni Sustavi 2025/2026.
