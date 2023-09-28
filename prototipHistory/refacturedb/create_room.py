import json
import random
from faker import Faker
from datetime import datetime
import uuid

fake = Faker()

fixture_data = []

def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%dT%H:%M:%S")
    raise TypeError("Object of type datetime is not JSON serializable")

for i in range(1, 5001):
    room = {
        "model": "refacturedb.room",
        "pk": str(uuid.uuid4()),
        "fields": {
            "user": None,
            "contact": None,
            "queue": "3852241e-59c0-4db7-8f72-67edb3f13eea",
            "custom_fields": {},
            "urn": fake.word(),
            "callback_url": fake.url(),
            "created_on": fake.date_time_this_decade(),
            "modified_on": fake.date_time_this_decade(),
            "ended_at": fake.date_time_this_decade(),
            "ended_by": fake.name(),
            "is_active": random.choice([True, False]),
            "is_waiting": random.choice([True, False]),
            "transfer_history": []
        }
    }
    fixture_data.append(room)

with open("room_fixture.json", "w") as outfile:
    json.dump(fixture_data, outfile, default=serialize_datetime, indent=4)

print("Fixture para o modelo 'Room' gerada com sucesso!")