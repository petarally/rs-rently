import redis
import json
import time

r = redis.Redis(host='redis', port=6379, db=0)
queue_name = "email_queue"

print(f"[*] Mail Worker pokrenut. Čekam poruke na redu '{queue_name}'...")

while True:
    _, message_json = r.blpop(queue_name)
    
    data = json.loads(message_json)
    email = data.get("email")
    car = data.get("car")

    print(f"[MAIL] Šaljem potvrdu na: {email} za vozilo: {car}")
    
    time.sleep(2) 
    print(f"[OK] Mail uspješno poslan na {email}")