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


r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, db=0)
queue_name = "email_queue"

print(f"[*] Mail Worker pokrenut. Čekam poruke na redu '{queue_name}'...")

while True:
    try:
        # Provjeri crash signal na svakoj iteraciji (deterministicki, neovisno
        # o ishodu blpop-a) prije nego sto zablokiramo na citanju reda.
        if r.get("crash_mail_worker"):
            r.delete("crash_mail_worker")
            raise SimulatedCrash("Simulirani pad: mail-worker")

        # Kratak timeout da se periodicki vracamo na provjeru crash signala
        item = r.blpop(queue_name, timeout=5)

        if item is None:
            continue

        _, message_json = item

        try:
            data = json.loads(message_json)
        except Exception as e:
            print(f"[MAIL][ERROR] Ne mogu parsirati poruku: {e}")
            continue

        email = data.get("email")
        car = data.get("car_id")

        if not email:
            print(f"[MAIL][WARN] Poruka nema email polje: {data}")
            continue

        print(f"[MAIL] Šaljem potvrdu na: {email} za vozilo: {car}")

        try:
            time.sleep(2)
            print(f"[OK] Mail uspješno poslan na {email}")
        except Exception as e:
            print(f"[MAIL][ERROR] Greška pri slanju: {e}")
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
