from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import redis
import json
import uuid
import os

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

r = redis.Redis(host='redis', port=6379, db=0)

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

    print(f"Spremam rezervaciju {booking_id} u bazu...")

    try:
        r.rpush("email_queue", json.dumps(booking_data))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri radu s Redisom: {e}")

    return {"message": "Rezervacija kreirana!", "booking_id": booking_id}