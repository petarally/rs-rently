import redis
import json
import time
import traceback
import os
import sys

SENTRY_ENABLED = False
try:
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration

    logging_integration = LoggingIntegration(level=None, event_level=None)
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        environment=os.getenv("SENTRY_ENV", "development"),
        integrations=[logging_integration],
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0")),
        send_default_pii=True,
    )
    SENTRY_ENABLED = True
except Exception:
    pass


class SimulatedCrash(Exception):
    """Namjerno izazvan pad za demonstraciju Sentryja."""
    pass


r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=6379,
    db=0,
    socket_connect_timeout=2,
    socket_timeout=10,  # > brpoplpush timeout
    health_check_interval=30,
)

QUEUE = "email_queue"               # glavni red
PROCESSING = "email_queue_processing"  # in-flight poruke (reliable queue)
DLQ = "email_queue_dead"            # dead-letter: poruke koje se ne mogu obraditi
PROCESSED = "processed_bookings"    # set obrađenih ID-eva (idempotentnost)
MAX_ATTEMPTS = 3

print(f"[*] Mail Worker pokrenut. Čekam poruke na redu '{QUEUE}'...")


def recover_inflight():
    """Crash recovery: vrati u glavni red poruke koje su pri prošlom padu
    ostale u 'processing' listi. Bez ovoga bi poruka koju je obrađivao
    srušeni worker ostala zauvijek zaglavljena (izgubljena obrada)."""
    moved = 0
    while r.rpoplpush(PROCESSING, QUEUE):
        moved += 1
    if moved:
        print(f"[MAIL][RECOVERY] Vraćeno {moved} in-flight poruka natrag u red")


def ack(raw):
    """Ukloni točno obrađenu poruku iz 'processing' liste."""
    r.lrem(PROCESSING, 1, raw)


def dead_letter(payload, raw, reason):
    """Premjesti poruku u DLQ (poison message) — ne gubi se, ali ne blokira red."""
    print(f"[MAIL][DLQ] {reason}")
    r.rpush(DLQ, payload)
    ack(raw)


recover_inflight()

while True:
    try:
        # Provjeri crash signal na svakoj iteraciji (deterministicki) prije
        # nego sto zablokiramo na citanju reda.
        if r.get("crash_mail_worker"):
            r.delete("crash_mail_worker")
            raise SimulatedCrash("Simulirani pad: mail-worker")

        # Reliable queue: atomarno premjesti poruku iz reda u 'processing'
        # listu. Ako worker padne usred obrade, poruka preživi u processingu
        # i vrati se kroz recover_inflight() pri sljedećem pokretanju.
        raw = r.brpoplpush(QUEUE, PROCESSING, timeout=5)

        if raw is None:
            continue

        try:
            data = json.loads(raw)
        except Exception as e:
            dead_letter(raw, raw, f"Neispravan JSON, šaljem u DLQ: {e}")
            continue

        booking_id = data.get("id")
        email = data.get("email")
        car = data.get("car_id")

        if not email:
            dead_letter(raw, raw, f"Poruka nema email polje, šaljem u DLQ: {data}")
            continue

        # Idempotentnost: ako je ovaj booking već obrađen (npr. duplikat nakon
        # recoveryja ili requeue-a), preskoči slanje da ne pošaljemo 2x mail.
        if booking_id and r.sismember(PROCESSED, booking_id):
            print(f"[MAIL][IDEMPOTENT] Booking {booking_id} već obrađen, preskačem")
            ack(raw)
            continue

        attempts = int(data.get("_attempts", 0))
        print(f"[MAIL] Šaljem potvrdu na: {email} za vozilo: {car} (pokušaj {attempts + 1})")

        try:
            time.sleep(2)  # simulacija slanja maila
            if booking_id:
                r.sadd(PROCESSED, booking_id)
            ack(raw)
            print(f"[OK] Mail uspješno poslan na {email}")
        except Exception as e:
            # Prolazna greška slanja: retry s brojačem, pa DLQ kad se iscrpi.
            attempts += 1
            data["_attempts"] = attempts
            if attempts >= MAX_ATTEMPTS:
                dead_letter(json.dumps(data), raw,
                            f"Iscrpljeni pokušaji ({MAX_ATTEMPTS}) za {booking_id}: {e}")
            else:
                ack(raw)
                r.rpush(QUEUE, json.dumps(data))
                print(f"[MAIL][RETRY] {booking_id} vraćen u red (pokušaj {attempts}/{MAX_ATTEMPTS}): {e}")
            traceback.print_exc()
            continue
    except SimulatedCrash as e:
        # Prijavi u Sentry pa stvarno sruši proces (container se restarta po
        # docker-compose restart politici, a poruke u redu prežive).
        print(f"[MAIL][CRASH] {e}")
        if SENTRY_ENABLED:
            sentry_sdk.capture_exception(e)
            sentry_sdk.flush(timeout=2.0)
        traceback.print_exc()
        sys.exit(1)
    except redis.exceptions.RedisError as re:
        print(f"[MAIL][ERROR] Redis error: {re}")
        time.sleep(5)
        continue
    except KeyboardInterrupt:
        print("[MAIL] Mail worker zaustavljen (KeyboardInterrupt)")
        break
    except Exception as e:
        print(f"[MAIL][ERROR] Neočekivana greška: {e}")
        if SENTRY_ENABLED:
            sentry_sdk.capture_exception(e)
        traceback.print_exc()
        time.sleep(2)
        continue
