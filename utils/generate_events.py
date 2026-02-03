import json
import random
from datetime import datetime, timedelta

users = [f"u{i}" for i in range(1, 6)]
event_types = ["view", "click", "purchase"]

start = datetime(
    datetime.now().year, 
    datetime.now().month, 
    datetime.now().day, 
    datetime.now().hour, 
    datetime.now().minute, 
    datetime.now().second
)

with open("sample_events.json", "w") as f:
    for i in range(50):
        event = {
            "event_id": f"e{i+1}",
            "user_id": random.choice(users),
            "event_type": random.choice(event_types),
            "timestamp": (start + timedelta(seconds=i * random.randint(5, 20))).isoformat() + "Z"
        }
        f.write(json.dumps(event) + "\n")
