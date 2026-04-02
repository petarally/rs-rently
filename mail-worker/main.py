import redis
import json
import time
import traceback
import os
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
except Exception:
    pass

r = redis.Redis(host='redis', port=6379, db=0)
queue_name = "email_queue"

print(f"[*] Mail Worker pokrenut. Čekam poruke na redu '{queue_name}'...")

while True:
    try:
        # Use a short timeout so we can periodically check for crash signal
        item = r.blpop(queue_name, timeout=5)

        # Check crash signal in Redis
        try:
            if r.get("crash_mail_worker"):
                r.delete("crash_mail_worker")
                raise Exception("Simulirani pad: mail-worker")
        except Exception:
            raise

        if item is None:
            continue

        _, message_json = item

        try:
            data = json.loads(message_json)
        except Exception as e:
            print(f"[MAIL][ERROR] Ne mogu parsirati poruku: {e}")
            continue

        email = data.get("email")
        car = data.get("car")

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
    except redis.exceptions.RedisError as re:
        print(f"[MAIL][ERROR] Redis error: {re}")
        time.sleep(5)
        continue
    except KeyboardInterrupt:
        print("[MAIL] Mail worker zaustavljen (KeyboardInterrupt)")
        break
    except Exception as e:
        print(f"[MAIL][ERROR] Neočekivana greška: {e}")
        traceback.print_exc()
        time.sleep(2)
        continue