import time
import json
import random
import logging
import uuid
import os
import csv
import argparse
import paho.mqtt.client as mqtt  # Fix import
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jsonschema import validate, ValidationError

class CardClient:
    SCHEMA = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string", "minLength": 3},
            "expiry": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
            "region": {"type": "string", "enum": ["US", "EU", "ASIA", "MEA"]},
            "card_type": {"type": "string", "enum": ["Visa", "MasterCard", "Amex", "Discover"]}
        },
        "required": ["id", "name", "expiry", "region", "card_type"]
    }

    def __init__(self):
        load_dotenv()
        self.broker = os.getenv("MQTT_BROKER", "localhost")
        self.port = int(os.getenv("MQTT_PORT", 1883))
        self.qos = int(os.getenv("MQTT_QOS", 1))
        self.client = mqtt.Client(client_id=f"CardClient-{uuid.uuid4()}", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.setup_logging()
        self.cards = []
        self.regions = ["US", "EU", "ASIA", "MEA"]
        self.card_types = ["Visa", "MasterCard", "Amex", "Discover"]
        self.names = ["Alice Smith", "Bob Jones", "Charlie Brown", "Diana Lee", "Ahmed Khan", "Fatima Ali"]
        self.metrics = {"sent": 0, "failed": 0}
        self.retry_connect()

    def setup_logging(self):
        os.makedirs("data", exist_ok=True)
        logging.basicConfig(filename="data/card_client.log", level=logging.INFO,
                           format="%(asctime)s - %(levelname)s - %(message)s")
        logging.info("CardClient initialized")

    def retry_connect(self, max_attempts=5):
        for attempt in range(max_attempts):
            try:
                self.client.connect(self.broker, self.port, keepalive=60)
                self.client.loop_start()
                logging.info(f"Connected to {self.broker}:{self.port}")
                return
            except Exception as e:
                logging.error(f"Attempt {attempt+1}/{max_attempts}: {e}")
                time.sleep(2)
        raise Exception("Connection failed after retries")

    def generate_card(self):
        is_invalid = random.random() < 0.3
        id_formats = [
            f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
            f"{random.randint(100000, 999999)}-{random.randint(1000, 9999)}"
        ]
        id_number = random.choice(id_formats)
        if is_invalid and random.random() < 0.3:
            id_number = "invalid_id"
        name = random.choice(self.names)
        if is_invalid and random.random() < 0.2:
            name = "A"
        expiry_date = datetime.now() + timedelta(days=random.randint(0, 1095))
        if is_invalid and random.random() < 0.3:
            expiry_date = datetime.now() - timedelta(days=random.randint(1, 365))
        card = {
            "id": id_number,
            "name": name,
            "expiry": expiry_date.strftime("%Y-%m-%d"),
            "region": random.choice(self.regions),
            "card_type": random.choice(self.card_types)
        }
        try:
            validate(instance=card, schema=self.SCHEMA)
            logging.info(f"Valid card: {card}")
        except ValidationError as e:
            logging.warning(f"Schema invalid: {card}, Error: {e}")
        self.cards.append(card)
        return card

    def publish_cards(self, count=30, topic="kyc/card_data"):
        try:
            for i in range(count):
                card_data = self.generate_card()
                payload = json.dumps(card_data)
                result = self.client.publish(topic, payload, qos=self.qos)
                self.metrics["sent"] += 1
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    print(f"Published [{i+1}/{count}]: {card_data}")
                    logging.info(f"Published: {card_data}")
                else:
                    self.metrics["failed"] += 1
                    logging.error(f"Publish failed: {result.rc}")
                time.sleep(0.15)
            self.save_metrics()
        except Exception as e:
            logging.error(f"Publish error: {e}")

    def save_metrics(self):
        with open("data/card_metrics.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "name", "expiry", "region", "card_type"])
            writer.writeheader()
            writer.writerows(self.cards)
        logging.info(f"Metrics saved: {self.metrics}")

    def close(self):
        self.client.loop_stop()
        self.client.disconnect()
        logging.info(f"CardClient closed: {self.metrics}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KYC Card Client")
    parser.add_argument("--count", type=int, default=30, help="Number of cards to publish")
    parser.add_argument("--sleep", type=float, default=0.15, help="Sleep time between publishes")
    args = parser.parse_args()
    try:
        client = CardClient()
        client.publish_cards(count=args.count)  # Update call
        time.sleep(args.sleep)
        client.close()
    except Exception as e:
        logging.error(f"Error: {e}")
        client.close()
