from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import redis
import json
import uuid
import os
import time
import threading

try:
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.stdlib import StdlibIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration

    logging_integration = LoggingIntegration(level=None, event_level=None)
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        environment=os.getenv("SENTRY_ENV", "development"),
        integrations=[logging_integration, StdlibIntegration(), StarletteIntegration()],
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0")),
        send_default_pii=True,
    )
except Exception:
    pass

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Timeouti na konekciji — bez njih bi pad Redisa mogao zablokirati zahtjev
# (i radničku nit) na neodređeno vrijeme.
r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=6379,
    db=0,
    socket_connect_timeout=2,
    socket_timeout=2,
    health_check_interval=30,
)


class CircuitBreaker:
    """Jednostavan circuit breaker. Nakon `threshold` uzastopnih grešaka prema
    Redisu sklopka se otvara na `cooldown` sekundi i pozivi se odmah odbijaju
    (fail-fast) umjesto da čekaju timeout. Nakon cooldowna propusti probni
    poziv (half-open): uspjeh zatvara sklopku, neuspjeh je opet otvara."""

    def __init__(self, threshold=5, cooldown=10):
        self.threshold = threshold
        self.cooldown = cooldown
        self.failures = 0
        self.opened_at = 0.0
        self._lock = threading.Lock()

    def allow(self):
        with self._lock:
            if self.failures >= self.threshold:
                if time.time() - self.opened_at < self.cooldown:
                    return False
            return True

    def record_success(self):
        with self._lock:
            self.failures = 0
            self.opened_at = 0.0

    def record_failure(self):
        with self._lock:
            self.failures += 1
            if self.failures >= self.threshold:
                self.opened_at = time.time()


redis_breaker = CircuitBreaker(threshold=5, cooldown=10)


def push_with_retry(key, value, retries=3, base_delay=0.1):
    """Gura u Redis s eksponencijalnim backoffom (0.1s, 0.2s, 0.4s).
    Apsorbira prolazne mrežne greške; trajne propagira pozivatelju."""
    last_err = None
    for attempt in range(retries):
        try:
            r.rpush(key, value)
            return
        except redis.exceptions.RedisError as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(base_delay * (2 ** attempt))
    raise last_err


@app.get("/health")
def health():
    # Liveness: gateway izbacuje mrtve replike iz rotacije.
    return {"status": "ok"}


@app.post("/bookings")
def create_booking(car_id: str, user_email: str, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Nedostaje token")

    if not car_id or not user_email:
        raise HTTPException(status_code=400, detail="Neispravni podaci rezervacije")

    booking_id = str(uuid.uuid4())
    booking_data = {
        "id": booking_id,
        "car_id": car_id,
        "email": user_email,
        "status": "confirmed"
    }

    print(f"Šaljem rezervaciju {booking_id} u Redis red email_queue...")

    # Fail-fast ako je sklopka otvorena (Redis je nedavno opetovano padao).
    if not redis_breaker.allow():
        raise HTTPException(
            status_code=503,
            detail="Servis za rezervacije je privremeno nedostupan (circuit breaker otvoren). Pokušajte ponovno.",
            headers={"Retry-After": "10"},
        )

    try:
        push_with_retry("email_queue", json.dumps(booking_data))
        redis_breaker.record_success()
    except redis.exceptions.RedisError as e:
        redis_breaker.record_failure()
        # 503 (ne 500) — jasna poruka da je riječ o privremenoj nedostupnosti
        # downstream ovisnosti, uz Retry-After.
        raise HTTPException(
            status_code=503,
            detail=f"Redis trenutno nedostupan: {e}",
            headers={"Retry-After": "5"},
        )

    return {"message": "Rezervacija kreirana!", "booking_id": booking_id}


@app.get("/__debug/crash")
def crash():
    raise Exception("Simulirani pad: booking-service")


@app.post("/__debug/crash-mail-worker")
def crash_mail_worker():
    try:
        r.set("crash_mail_worker", "1")
        return {"message": "Signal poslan mail-workeru"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))