import json
import random
from faker import Faker
from datetime import datetime
import uuid

fake = Faker()

def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%dT%H:%M:%S")
    raise TypeError("Object of type datetime is not JSON serializable")

# Carregue os dados de fixture da sala (room) gerados anteriormente
with open("room_fixture_01.json", "r") as room_file:
    room_data = json.load(room_file)

message_data = []

for room in room_data:
    room_id = room["pk"]
    
    for _ in range(25):  # Crie 25 mensagens para cada sala
        message = {
            "model": "refacturedb.message",
            "pk": str(uuid.uuid4()),
            "fields": {
                "room": room_id,
                "user": None,
                "contact": None,
                "text": fake.text(),
                "created_on": fake.date_time_this_decade(),
                "modified_on": fake.date_time_this_decade(),
                "seen": random.choice([True, False])
            }
        }
        message_data.append(message)

with open("message_fixture.json", "w") as outfile:
    json.dump(message_data, outfile, default=serialize_datetime, indent=4)

print("Fixture para o modelo 'Message' gerada com sucesso!")