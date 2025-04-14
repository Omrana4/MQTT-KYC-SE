import paho.mqtt.client as mqtt
import json
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict
from tenacity import retry, stop_after_attempt, wait_exponential
from contextlib import contextmanager

class Analyst:
    def __init__(self, runtime: int = 90):
        """Initialize Analyst with MQTT and SQLite."""
        load_dotenv()
        self.broker = os.getenv("MQTT_BROKER", "localhost")
        self.port = int(os.getenv("MQTT_PORT", 1883))
        self.qos = int(os.getenv("MQTT_QOS", 1))
        self.runtime = runtime
        self.db_path = "data/kyc_results.db"
        self.client = mqtt.Client(client_id="Analyst", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.setup_logging()
        self.setup_db()
        self.connect_with_retry()

    def setup_logging(self) -> None:
        """Configure logging with rotation."""
        os.makedirs("data", exist_ok=True)
        logging.basicConfig(
            filename="data/analyst.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        logging.info("Analyst initialized")

    def setup_db(self) -> None:
        """Initialize SQLite database."""
        os.makedirs("data", exist_ok=True)
        with self.get_db_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    id TEXT,
                    status TEXT,
                    timestamp TEXT,
                    reasons TEXT,
                    card_type TEXT,
                    region TEXT
                )
            """)
        logging.info("Database initialized")

    @contextmanager
    def get_db_connection(self):
        """Provide thread-safe SQLite connection."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        try:
            yield conn
        finally:
            conn.close()

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
    def connect_with_retry(self) -> None:
        """Connect to MQTT broker with retry logic."""
        try:
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
            logging.info("Analyst connected")
        except Exception as e:
            logging.error(f"Connection failed: {e}")
            raise

    def on_connect(self, client, userdata, flags, reason_code, properties) -> None:
        """Handle MQTT connection."""
        print(f"Connected with code {reason_code}")
        client.subscribe("kyc/result", qos=self.qos)
        logging.info("Subscribed to kyc/result")

    def on_disconnect(self, client, userdata, flags, reason_code, properties) -> None:
        """Handle MQTT disconnection."""
        logging.warning(f"Disconnected with code {reason_code}")
        self.connect_with_retry()

    def on_message(self, client, userdata, msg) -> None:
        """Process verification results."""
        try:
            result = json.loads(msg.payload.decode())
            timestamp = result.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            reasons = json.dumps(result.get("reasons", []))
            with self.get_db_connection() as conn:
                conn.execute(
                    "INSERT INTO results (id, status, timestamp, reasons, card_type, region) VALUES (?, ?, ?, ?, ?, ?)",
                    (result["id"], result["status"], timestamp, reasons,
                     result.get("card_type", "Unknown"), result.get("region", "Unknown"))
                )
                conn.commit()
            print(f"Stored: {result}")
            logging.info(f"Stored: {result}")
        except Exception as e:
            logging.error(f"Message processing error: {e}")

    def analyze(self) -> None:
        """Analyze stored results and generate visualizations."""
        try:
            with self.get_db_connection() as conn:
                df = pd.read_sql_query("SELECT * FROM results", conn)
            if df.empty:
                print("No data to analyze")
                logging.info("No data to analyze")
                return

            # Compute stats
            counts = df["status"].value_counts()
            rejection_rate = counts.get("rejected", 0) / len(df) * 100
            type_counts = df.groupby(["card_type", "status"]).size().unstack(fill_value=0)
            region_counts = df.groupby(["region", "status"]).size().unstack(fill_value=0)

            # Print stats
            print(f"Verification Stats: {counts.to_dict()}")
            print(f"Rejection Rate: {rejection_rate:.2f}%")
            print(f"By Card Type:\n{type_counts}")
            print(f"By Region:\n{region_counts}")
            logging.info(f"Stats: {counts.to_dict()}, Rejection: {rejection_rate:.2f}%")

            # Generate visualizations
            os.makedirs("docs/diagrams", exist_ok=True)

            # Pie chart
            plt.figure(figsize=(8, 6))
            counts.plot(kind="pie", autopct="%1.1f%%", colors=["#66b3ff", "#ff9999"])
            plt.title("KYC Verification Status")
            plt.ylabel("")
            plt.savefig("docs/diagrams/status_pie.png", bbox_inches="tight")
            plt.close()

            # Card type heatmap
            plt.figure(figsize=(10, 6))
            sns.heatmap(type_counts, annot=True, fmt="d", cmap="Blues")
            plt.title("Verification by Card Type")
            plt.savefig("docs/diagrams/card_type_heatmap.png", bbox_inches="tight")
            plt.close()

            # Region heatmap
            plt.figure(figsize=(10, 6))
            sns.heatmap(region_counts, annot=True, fmt="d", cmap="Blues")
            plt.title("Verification by Region")
            plt.savefig("docs/diagrams/region_heatmap.png", bbox_inches="tight")
            plt.close()

            # Export CSV
            df.to_csv("data/analysis_results.csv", index=False)
            logging.info("Exported analysis results")
        except Exception as e:
            logging.error(f"Analysis error: {e}")

    def close(self) -> None:
        """Gracefully close client."""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            logging.info("Analyst closed")
        except Exception as e:
            logging.error(f"Close failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KYC Analyst")
    parser.add_argument("--runtime", type=int, default=90, help="Runtime in seconds")
    args = parser.parse_args()
    try:
        analyst = Analyst(runtime=args.runtime)
        print(f"Running Analyst for {args.runtime} seconds...")
        time.sleep(args.runtime)
        analyst.analyze()
        analyst.close()
    except KeyboardInterrupt:
        analyst.close()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        analyst.close()
