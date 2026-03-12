# 🚗 RS-Rently - Rent a Car Mikroservisni Sustav

Kompletan rent-a-car sustav izgrađen s mikroservisnom arhitekturom, Vue.js frontendom i različitim komunikacijskim protokolima.

## 🏗️ Arhitektura

### Backend Servisi (8 servisa)

1. **Auth Service** (FastAPI, port 8000) - JWT autentifikacija
2. **Booking Service** (FastAPI, port 8001) - Rezervacije vozila
3. **Damage Service** (FastAPI, port 8002) - Upload slika šteta
4. **Mail Worker** (Python) - Asinkroni email worker
5. **GPS Tracker** (gRPC, port 50051) - GPS praćenje vozila
6. **LocalStack** (port 4566) - AWS DynamoDB i S3 simulacija
7. **Redis** (port 6379) - Message broker i cache
8. **Frontend** (Vue.js, port 3000) - Korisničko sučelje

### Komunikacijski Protokoli

- **REST API**: Auth, Booking, Damage servisi
- **gRPC**: GPS Tracker
- **Redis Queue**: Asinkrona komunikacija (Booking → Mail Worker)
- **HTTP/REST**: Inter-service komunikacija

## Pokretanje

### Potrebno

- Docker & Docker Compose
- Preglednik (Chrome, Firefox, Safari)

### Pokretanje cijelog sustava

```bash
# Pokreni sve servise
docker-compose up --build
```

Sustav će biti dostupan na:

- **Frontend**: http://localhost:3000
- Auth Service: http://localhost:8000
- Booking Service: http://localhost:8001
- Damage Service: http://localhost:8002
- GPS Tracker (gRPC): localhost:50051

### Pristup aplikaciji

1. Otvori preglednik na **http://localhost:3000**
2. Prijavi se s demo pristupom:
   - **Username**: `admin`
   - **Password**: `admin`
3. Istraži funkcionalnosti:
   - Dashboard - pregled sustava
   - Rezervacije - kreiranje novih rezervacija
   - Štete - upload slika oštećenja

## 📱 Korištenje Frontend Aplikacije

### Login

- Demo korisnik: `admin` / `admin`
- JWT token se sprema u localStorage
- Automatska provjera autentifikacije

### Kreiranje Rezervacije

1. Idi na **Rezervacije**
2. Odaberi vozilo iz dropdown-a
3. Unesi email adresu
4. Klikni **Kreiraj rezervaciju**
5. Rezervacija se sprema u DynamoDB
6. Mail Worker automatski šalje email (provjeri logove!)

### Upload Slike Štete

1. Idi na **Štete**
2. Odaberi sliku (JPG, PNG, GIF)
3. Pregled slike prije uploada
4. Klikni **Upload sliku**
5. Slika se sprema na S3 (LocalStack)

## 🔍 Što se događa u pozadini?

### Rezervacija

```
Frontend → Booking Service → DynamoDB (spremi) → Redis Queue → Mail Worker → Email
                          ↓
                    Auth Service (verifikacija JWT)
```

### Upload Štete

```
Frontend → Damage Service → LocalStack S3 (spremi sliku)
```

## Praćenje Sustava

### Logovi

**Svi servisi:**

```bash
docker-compose logs -f
```

**Pojedinačni servis:**

```bash
docker-compose logs -f frontend
docker-compose logs -f booking-service
docker-compose logs -f mail-worker
```

### Status servisa

```bash
docker-compose ps
```

### Zaustavljanje

```bash
docker-compose down
```

### Ponovno pokretanje

```bash
docker-compose restart frontend
```

## 🛠️ Razvoj

### Frontend Development

Za development mode sa hot reload:

```bash
cd frontend
npm install
npm run dev
```

Frontend će biti dostupan na http://localhost:5173

### Struktura Frontend Projekta

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

### API Endpoints

**Auth Service (8000)**

- `POST /login` - Prijava korisnika
- `GET /verify?token=` - Verifikacija tokena

**Booking Service (8001)**

- `POST /bookings?car_id=X&user_email=Y` - Nova rezervacija
- Header: `Authorization: Bearer <token>`

**Damage Service (8002)**

- `POST /upload-damage` - Upload slike
- FormData: `file`

## Testiranje

### 1. Test Login

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```

### 2. Test Booking

```bash
TOKEN="<tvoj_token>"
curl -X POST "http://localhost:8001/bookings?car_id=BMW-X5&user_email=test@test.com" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Provjera Redis Queue

```bash
docker exec -it rs-rently-redis-1 redis-cli LLEN email_queue
```

### 4. Provjera Mail Worker Logova

```bash
docker-compose logs -f mail-worker
```

## Značajke Frontend-a

- ✅ Vue 3 Composition API
- ✅ Vue Router za navigaciju
- ✅ Axios za HTTP zahtjeve
- ✅ JWT autentifikacija
- ✅ Protected routes
- ✅ Responsive dizajn
- ✅ Gradient UI
- ✅ File upload s previewom
- ✅ Error handling
- ✅ Loading states

## Sigurnost

**Trenutna implementacija (DEV):**

- CORS: `allow_origins=["*"]`
- Hardkodirani kredencijali
- LocalStorage za token

**Za produkciju:**

- Ograniči CORS na specifične domene
- Koristi environment varijable
- HttpOnly cookies za token
- HTTPS/TLS
- Rate limiting
- Input validacija

## Tehnologije

### Frontend

- Vue 3
- Vue Router 4
- Axios
- Vite
- Nginx

### Backend

- Python 3.10
- FastAPI
- gRPC
- Redis
- LocalStack (DynamoDB, S3)
- Docker & Docker Compose

## Troubleshooting

**Problem**: Frontend ne može spojiti na backend

```bash
# Provjeri jesu li svi servisi running
docker-compose ps

# Restart servisa
docker-compose restart auth-service booking-service damage-service
```

**Problem**: CORS greška

```bash
# Provjeri da backend servisi imaju CORS middleware
docker-compose logs auth-service | grep CORS
```

**Problem**: Token ne radi

```bash
# Očisti localStorage i ponovo se prijavi
# U browseru: F12 → Console → localStorage.clear()
```

## 📖 Dokumentacija API-ja

Dok su servisi pokrenuti:

- Auth Service: http://localhost:8000/docs
- Booking Service: http://localhost:8001/docs
- Damage Service: http://localhost:8002/docs

## Koncepti Raspodijeljenih Sustava

Ovaj projekt demonstrira:

1. **Mikroservisna arhitektura** - odvojeni servisi
2. **Service Discovery** - Docker DNS
3. **Asinkrona komunikacija** - Redis queue
4. **API Gateway pattern** - Frontend kao gateway
5. **Različiti protokoli** - REST, gRPC, Message Queue
6. **Caching** - Redis
7. **Cloud services** - AWS simulacija
8. **Containerization** - Docker

## Licenca

Edukacijski projekt za kolegij Raspodijeljeni Sustavi 2025/2026.
