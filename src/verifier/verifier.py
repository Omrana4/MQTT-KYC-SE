import paho.mqtt.client as mqtt
import json
import time
import re
import logging
import os
import csv
from datetime import datetime
from dotenv import load_dotenv

class Verifier:
    def __init__(self):
        load_dotenv()
        self.broker = os.getenv("MQTT_BROKER", "localhost")
        self.port = int(os.getenv("MQTT_PORT", 1883))
        self.qos = int(os.getenv("MQTT_QOS", 1))
        self.client = mqtt.Client(client_id="Verifier", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.setup_logging()
        self.validations = {"total": 0, "approved": 0, "rejected": 0}
        self.results = []
        try:
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
            logging.info("Verifier connected")
        except Exception as e:
            logging.error(f"Connection failed: {e}")
            raise

    def setup_logging(self):
        os.makedirs("data", exist_ok=True)
        logging.basicConfig(filename="data/verifier.log", level=logging.INFO,
                           format="%(asctime)s - %(levelname)s - %(message)s")
        logging.info("Verifier initialized")

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print(f"Verifier connected with code {reason_code}")
        client.subscribe("kyc/card_data", qos=self.qos)
        logging.info("Subscribed to kyc/card_data")

    def on_message(self, client, userdata, msg):
        try:
            card = json.loads(msg.payload.decode())
            self.validations["total"] += 1
            reasons = []
            # ID validation
            id_valid = bool(re.match(r"^\d{4}-\d{4}-\d{4}$|^\d{6}-\d{4}$", card["id"]))
            if not id_valid:
                reasons.append("Invalid ID format")
            # Expiry validation
            expiry_valid = datetime.strptime(card["expiry"], "%Y-%m-%d") >= datetime.now()
            if not expiry_valid:
                reasons.append("Card expired")
            # Name validation
            name_valid = len(card["name"].split()) >= 2 and len(card["name"]) >= 3
            if not name_valid:
                reasons.append("Invalid name")
            # Region and type
            region_valid = card.get("region") in ["US", "EU", "ASIA", "MEA"]
            if not region_valid:
                reasons.append("Invalid region")
            type_valid = card.get("card_type") in ["Visa", "MasterCard", "Amex", "Discover"]
            if not type_valid:
                reasons.append("Invalid card type")
            # Status
            status = "approved" if id_valid and expiry_valid and name_valid and region_valid and type_valid else "rejected"
            self.validations[status] += 1
            result = {
                "id": card["id"],
                "status": status,
                "reasons": reasons,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "card_type": card.get("card_type", "Unknown"),
                "region": card.get("region", "Unknown")
            }
            self.results.append(result)
            client.publish("kyc/result", json.dumps(result), qos=self.qos)
            print(f"Verified: {result}")
            logging.info(f"Verified: {result}, Stats: {self.validations}")
            self.save_results()
        except Exception as e:
            logging.error(f"Message processing error: {e}")

    def save_results(self):
        with open("data/verifier_results.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "status", "reasons", "timestamp", "card_type", "region"])
            writer.writeheader()
            writer.writerows(self.results)
        logging.info("Saved verification results")

    def close(self):
        self.client.loop_stop()
        self.client.disconnect()
        logging.info(f"Verifier closed: {self.validations}")

if __name__ == "__main__":
    try:
        verifier = Verifier()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        verifier.close()
