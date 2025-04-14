# src/logger/logger.py
import paho.mqtt.client as mqtt
import json

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    with open("data/logger.log", "a") as f:
        f.write(f"Logged: {data}\n")
    client.publish("kyc/log", json.dumps({"log": f"Processed {data['id']}"}))
