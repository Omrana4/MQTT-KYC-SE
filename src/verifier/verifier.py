import paho.mqtt.client as mqtt
import json
import logging
import os
import csv
import re
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, List
from tenacity import retry, stop_after_attempt, wait_exponential

class Verifier:
    def __init__(self):
        """Initialize Verifier with MQTT and storage."""
        load_dotenv()
        self.broker = os.getenv("MQTT_BROKER", "localhost")
        self.port = int(os.getenv("MQTT_PORT", 1883))
        self.qos = int(os.getenv("MQTT_QOS", 1))
        self.client = mqtt.Client(client_id="Verifier", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.valid_regions = ["US", "EU", "ASIA", "MEA", "LATAM"]
        self.valid_card_types = ["Visa", "MasterCard", "Amex", "Discover"]
        self.results = []
        self.stats = {"total": 0, "approved": 0, "rejected": 0}
        self.setup_logging()
        self.connect_with_retry()

    def setup_logging(self) -> None:
        """Configure logging with rotation."""
        os.makedirs("data", exist_ok=True)
        logging.basicConfig(
            filename="data/verifier.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        logging.info("Verifier initialized")

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
    def connect_with_retry(self) -> None:
        """Connect to MQTT broker with retry logic."""
        try:
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
            logging.info("Verifier connected")
        except Exception as e:
            logging.error(f"Connection failed: {e}")
            raise

    def on_connect(self, client, userdata, flags, reason_code, properties) -> None:
        """Handle MQTT connection."""
        print(f"Connected with code {reason_code}")
        client.subscribe("kyc/card_data", qos=self.qos)
        logging.info("Subscribed to kyc/card_data")

    def on_disconnect(self, client, userdata, flags, reason_code, properties) -> None:
        """Handle MQTT disconnection."""
        logging.warning(f"Disconnected with code {reason_code}")
        self.connect_with_retry()

    def on_message(self, client, userdata, msg) -> None:
        """Process incoming KYC card data."""
        try:
            card = json.loads(msg.payload.decode())
            result = self.verify_card(card)
            self.results.append(result)
            self.stats["total"] += 1
            self.stats[result["status"]] += 1
            self.client.publish("kyc/result", json.dumps(result), qos=self.qos)
            print(f"Verified: {result}, Stats: {self.stats}")
            logging.info(f"Verified: {result}, Stats: {self.stats}")
            self.save_results()
        except Exception as e:
            logging.error(f"Message processing error: {e}")

    def verify_card(self, card: Dict) -> Dict:
        """Validate KYC card data."""
        reasons: List[str] = []
        card_id = card.get("id", "")
        name = card.get("name", "")
        expiry = card.get("expiry", "")
        region = card.get("region", "")
        card_type = card.get("card_type", "")

        # ID validation
        if not re.match(r"^[0-9]{4}-[0-9]{4}-[0-9]{4}$", card_id):
            reasons.append("Invalid ID format")

        # Name validation
        if len(name.strip()) < 2:
            reasons.append("Name too short")

        # Expiry validation
        try:
            expiry_date = datetime.strptime(expiry, "%Y-%m-%d")
            if expiry_date < datetime.now():
                reasons.append("Card expired")
        except ValueError:
            reasons.append("Invalid expiry format")

        # Region validation
        if region not in self.valid_regions:
            reasons.append("Invalid region")

        # Card type validation
        if card_type not in self.valid_card_types:
            reasons.append("Invalid card type")

        status = "rejected" if reasons else "approved"
        return {
            "id": card_id,
            "status": status,
            "reasons": reasons,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "card_type": card_type,
            "region": region
        }

    def save_results(self) -> None:
        """Save verification results to CSV."""
        os.makedirs("data", exist_ok=True)
        with open("data/verifier_results.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "status", "reasons", "timestamp", "card_type", "region"])
            writer.writeheader()
            writer.writerows(self.results)
        logging.info("Results saved")

    def close(self) -> None:
        """Gracefully close client."""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            logging.info("Verifier closed")
        except Exception as e:
            logging.error(f"Close failed: {e}")

if __name__ == "__main__":
    try:
        verifier = Verifier()
        verifier.client.loop_forever()
    except KeyboardInterrupt:
        verifier.close()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        verifier.close()
