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

class Analyst:
    def __init__(self):
        load_dotenv()
        self.broker = os.getenv("MQTT_BROKER", "localhost")
        self.port = int(os.getenv("MQTT_PORT", 1883))
        self.qos = int(os.getenv("MQTT_QOS", 1))
        self.db_path = "data/kyc_results.db"
        self.client = mqtt.Client(client_id="Analyst", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.setup_logging()
        self.setup_db()
        try:
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
            logging.info("Analyst connected")
        except Exception as e:
            logging.error(f"Connection failed: {e}")
            raise

    def setup_logging(self):
        os.makedirs("data", exist_ok=True)
        logging.basicConfig(filename="data/analyst.log", level=logging.INFO,
                           format="%(asctime)s - %(levelname)s - %(message)s")
        logging.info("Analyst initialized")

    def setup_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS results (id TEXT, status TEXT, timestamp TEXT, reasons TEXT, card_type TEXT, region TEXT)")
        logging.info("Database initialized")

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print(f"Analyst connected with code {reason_code}")
        client.subscribe("kyc/result", qos=self.qos)
        logging.info("Subscribed to kyc/result")

    def on_message(self, client, userdata, msg):
        try:
            result = json.loads(msg.payload.decode())
            timestamp = result.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            reasons = json.dumps(result.get("reasons", []))
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("INSERT INTO results (id, status, timestamp, reasons, card_type, region) VALUES (?, ?, ?, ?, ?, ?)",
                            (result["id"], result["status"], timestamp, reasons, result.get("card_type", "Unknown"), result.get("region", "Unknown")))
                conn.commit()
            print(f"Stored: {result}")
            logging.info(f"Stored: {result}")
        except Exception as e:
            logging.error(f"Message processing error: {e}")

    def analyze(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query("SELECT * FROM results", conn)
            if df.empty:
                print("No data to analyze")
                logging.info("No data to analyze")
                return
            counts = df["status"].value_counts()
            rejection_rate = counts.get("rejected", 0) / len(df) * 100
            type_counts = df.groupby(["card_type", "status"]).size().unstack(fill_value=0)
            region_counts = df.groupby(["region", "status"]).size().unstack(fill_value=0)
            print(f"Verification Stats: {counts.to_dict()}")
            print(f"Rejection Rate: {rejection_rate:.2f}%")
            print(f"By Card Type:\n{type_counts}")
            print(f"By Region:\n{region_counts}")
            logging.info(f"Stats: {counts.to_dict()}, Rejection: {rejection_rate:.2f}%")
            os.makedirs("docs/diagrams", exist_ok=True)
            plt.figure(figsize=(8, 6))
            counts.plot(kind="pie", autopct="%1.1f%%")
            plt.title("KYC Verification Status")
            plt.savefig("docs/diagrams/status_pie.png")
            plt.close()
            plt.figure(figsize=(10, 6))
            sns.heatmap(type_counts, annot=True, fmt="d")
            plt.title("Verification by Card Type")
            plt.savefig("docs/diagrams/card_type_heatmap.png")
            plt.close()
            plt.figure(figsize=(10, 6))
            sns.heatmap(region_counts, annot=True, fmt="d")
            plt.title("Verification by Region")
            plt.savefig("docs/diagrams/region_heatmap.png")
            plt.close()
            df.to_csv("data/analysis_results.csv", index=False)
            logging.info("Exported analysis results")
        except Exception as e:
            logging.error(f"Analysis error: {e}")

    def close(self):
        self.client.loop_stop()
        self.client.disconnect()
        logging.info("Analyst closed")

if __name__ == "__main__":
    try:
        analyst = Analyst()
        print("Running Analyst for 90 seconds to collect data...")
        time.sleep(90)  # Extended for full pipeline
        analyst.analyze()
        analyst.close()
    except KeyboardInterrupt:
        analyst.close()
