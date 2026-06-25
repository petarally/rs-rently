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

Cijeli sustav je iza **Traefik gatewaya** (jedinstvena ulazna točka):

- **Frontend**: http://localhost (port 80)
- Auth Service: http://localhost/api/auth (npr. `/api/auth/login`)
- Booking Service: http://localhost/api/booking (npr. `/api/booking/bookings`)
- Damage Service: http://localhost/api/damage (npr. `/api/damage/upload-damage`)
- GPS Tracker (gRPC): localhost:50051
- **Traefik dashboard**: http://localhost:8080 (pregled rutiranja i replika)

Gateway automatski round-robin balansira promet preko svih replika svakog servisa.

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
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```

```bash
TOKEN="<tvoj_token>"
curl -X POST "http://localhost/api/booking/bookings?car_id=BMW-X5&user_email=test@test.com" \
  -H "Authorization: Bearer $TOKEN"
```

## Horizontalno skaliranje

Svi aplikacijski servisi su **stateless** (stanje je u Redisu / S3 / JWT-u), nemaju
fiksne host-portove i otkrivaju se kroz Traefik gateway, pa se svaki može
replicirati. `docker-compose.yaml` već diže po 2 replike svakog servisa.

Ručno skaliranje na proizvoljan broj replika:

```bash
docker compose up --build -d \
  --scale auth-service=3 \
  --scale booking-service=3 \
  --scale damage-service=3 \
  --scale mail-worker=3 \
  --scale gps-tracker=3
```

Provjera da promet ide na različite replike (Traefik round-robin):

```bash
docker compose ps                        # vidi sve replike
for i in $(seq 1 6); do \
  curl -s http://localhost/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin"}' >/dev/null; done
docker compose logs auth-service | grep -c "POST /login"   # raspodijeljeno po replikama
```

- **REST servisi** (auth/booking/damage): Traefik round-robin po PathPrefixu.
- **mail-worker**: competing consumers — svaka poruka iz `email_queue` (Redis `blpop`)
  ide točno jednom workeru, pa N workera dijeli posao.
- **gps-tracker**: gRPC (h2c) load-balansiran kroz Traefik `grpc` entrypoint.
- **redis / localstack**: singletoni (dijeljeno stanje), namjerno se ne skaliraju.

## Error handling raspodijeljenih sustava

Skaliranje bez resilience-a je polovično — sustav ima error handling na dvije razine.

### Na gatewayu (Traefik)

- **Health-check load balancera** — Traefik svakih 10s gađa `/health` svake
  replike; mrtve replike automatski izlaze iz rotacije (i vraćaju se kad ozdrave).
- **Retry** (`resilient-retry@file`) — na mrežnu grešku prema replici gateway
  automatski preusmjeri zahtjev na sljedeću zdravu repliku (failover).
- **Circuit breaker** (`resilient-cb@file`) — kad udio mrežnih grešaka prema
  servisu pređe 30%, sklopka se otvara i gateway odmah vraća 503 (fail-fast),
  pa se ne zatrpava servis koji ionako pada. Sama se zatvori kad se oporavi.
- **Timeouts** — `dialTimeout`/`responseHeaderTimeout` prema backendima i
  `respondingTimeouts` na ulazu sprječavaju zaglavljene konekcije.

### U servisima

- **booking → Redis**: socket timeouti + retry s eksponencijalnim backoffom
  (0.1→0.2→0.4s) + **in-process circuit breaker**; kod nedostupnog Redisa vraća
  `503` + `Retry-After` (ne 500), tj. graceful degradacija.
- **damage → S3**: connect/read timeouti + automatski boto3 retry (standard mode).
- **mail-worker** (reliable messaging):
  - **Reliable queue** (`BRPOPLPUSH` red→processing) + **crash recovery** pri
    startu — poruka koju je obrađivao srušeni worker se ne gubi, vraća se u red.
  - **DLQ** (`email_queue_dead`) — poison poruke (neispravan JSON, bez emaila)
    i one s iscrpljenim pokušajima idu u dead-letter umjesto da blokiraju red.
  - **Retry brojač** (`MAX_ATTEMPTS=3`) na prolazne greške slanja.
  - **Idempotentnost** (`processed_bookings` set) — duplikat poruke (nakon
    recoveryja/requeue-a) ne šalje mail dvaput.

### Demo scenariji za obranu

```bash
# 1) Failover: ubij jednu auth repliku, promet i dalje radi (retry + healthcheck)
docker compose up -d --scale auth-service=3
docker kill $(docker compose ps -q auth-service | head -1)
curl -s http://localhost/api/auth/login -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin"}'        # i dalje 200

# 2) Graceful degradacija: ugasi Redis -> booking vraća 503 (ne 500)
docker compose stop redis
curl -i "http://localhost/api/booking/bookings?car_id=BMW&user_email=t@t.com" \
  -H "Authorization: Bearer X"                          # 503 + Retry-After

# 3) DLQ: pošalji neispravnu poruku u red pa pogledaj dead-letter
docker compose exec redis redis-cli RPUSH email_queue 'nije-json'
docker compose exec redis redis-cli LRANGE email_queue_dead 0 -1
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
4. **API Gateway pattern** - Traefik (jedinstvena ulazna točka + load balancer)
9. **Horizontalno skaliranje** - stateless servisi iza gatewaya, `--scale`
5. **Različiti protokoli** - REST, gRPC, Message Queue
6. **Caching** - Redis
7. **Cloud services** - AWS simulacija
8. **Containerization** - Docker

Edukacijski projekt za kolegij Raspodijeljeni Sustavi 2025/2026.
