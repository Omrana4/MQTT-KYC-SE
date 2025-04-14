import paho.mqtt.client as mqtt
import time
import json
import random
import logging
import os
import csv
import uuid
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jsonschema import validate, ValidationError
from typing import Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

class CardClient:
    def __init__(self, card_count: int = 25, sleep_time: float = 0.15, retry_attempts: int = 5):
        """Initialize Card Client with configurable parameters."""
        load_dotenv()
        self.broker = os.getenv("MQTT_BROKER", "localhost")
        self.port = int(os.getenv("MQTT_PORT", 1883))
        self.qos = int(os.getenv("MQTT_QOS", 1))
        self.card_count = card_count
        self.sleep_time = sleep_time
        self.retry_attempts = retry_attempts
        self.client = mqtt.Client(client_id=f"CardClient-{uuid.uuid4()}", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.regions = ["US", "EU", "ASIA", "MEA", "LATAM"]
        self.card_types = ["Visa", "MasterCard", "Amex", "Discover"]
        self.names = [
            "Alice Smith", "Bob Jones", "Charlie Brown", "Diana Lee", "Ahmed Khan",
            "Maria Garcia", "Li Wei", "A", ""  # Edge cases
        ]
        self.cards = []
        self.metrics = {"published": 0, "failed": 0, "invalid": 0}
        self.schema = {
            "type": "object",
            "properties": {
                "id": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{4}-[0-9]{4}$|^invalid_id$"},
                "name": {"type": "string"},
                "expiry": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
                "region": {"type": "string", "enum": self.regions},
                "card_type": {"type": "string", "enum": self.card_types}
            },
            "required": ["id", "name", "expiry", "region", "card_type"]
        }
        self.setup_logging()
        self.connect_with_retry()

    def setup_logging(self) -> None:
        """Configure logging with rotation."""
        os.makedirs("data", exist_ok=True)
        logging.basicConfig(
            filename="data/card_client.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        logging.info("Card Client initialized")

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
    def connect_with_retry(self) -> None:
        """Connect to MQTT broker with retry logic."""
        try:
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
            logging.info("Card Client connected")
        except Exception as e:
            logging.error(f"Connection failed: {e}")
            raise

    def on_connect(self, client, userdata, flags, reason_code, properties) -> None:
        """Handle MQTT connection."""
        print(f"Connected with code {reason_code}")
        logging.info(f"Connected with code {reason_code}")

    def on_disconnect(self, client, userdata, flags, reason_code, properties) -> None:
        """Handle MQTT disconnection."""
        logging.warning(f"Disconnected with code {reason_code}")
        self.connect_with_retry()

    def generate_card(self) -> Optional[Dict]:
        """Generate a KYC card with ~30% edge cases."""
        is_invalid = random.random() < 0.3
        card_id = (
            f"{random.randint(1000,9999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
            if not is_invalid else
            random.choice(["invalid_id", f"{random.randint(100,999)}-{random.randint(1000,9999)}"])
        )
        name = random.choice(self.names)
        expiry_date = datetime.now() + timedelta(days=random.randint(-365, 730))
        expiry = expiry_date.strftime("%Y-%m-%d")
        region = random.choice(self.regions)
        card_type = random.choice(self.card_types)
        card = {"id": card_id, "name": name, "expiry": expiry, "region": region, "card_type": card_type}
        try:
            validate(instance=card, schema=self.schema)
            self.cards.append(card)
            return card
        except ValidationError as e:
            logging.error(f"Schema validation failed: {e}")
            self.metrics["invalid"] += 1
            return None

    def publish_cards(self, count: Optional[int] = None, topic: str = "kyc/card_data") -> None:
        """Publish cards to MQTT topic."""
        count = count or self.card_count
        for i in range(count):
            card = self.generate_card()
            if card:
                try:
                    self.client.publish(topic, json.dumps(card), qos=self.qos)
                    self.metrics["published"] += 1
                    print(f"Published [{i+1}/{count}]: {card}")
                    logging.info(f"Published: {card}")
                except Exception as e:
                    self.metrics["failed"] += 1
                    logging.error(f"Publish failed: {e}")
            time.sleep(self.sleep_time)
        self.save_metrics()

    def save_metrics(self) -> None:
        """Save metrics to CSV."""
        os.makedirs("data", exist_ok=True)
        with open("data/card_metrics.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["published", "failed", "invalid"])
            writer.writeheader()
            writer.writerow(self.metrics)
        logging.info(f"Metrics saved: {self.metrics}")

    def close(self) -> None:
        """Gracefully close client."""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            logging.info("Card Client closed")
        except Exception as e:
            logging.error(f"Close failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KYC Card Client")
    parser.add_argument("--count", type=int, default=25, help="Number of cards to publish")
    parser.add_argument("--sleep", type=float, default=0.15, help="Sleep time between publishes")
    parser.add_argument("--retries", type=int, default=5, help="Connection retry attempts")
    args = parser.parse_args()
    try:
        client = CardClient(card_count=args.count, sleep_time=args.sleep, retry_attempts=args.retries)
        client.publish_cards()
        client.close()
    except KeyboardInterrupt:
        client.close()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        client.close()
