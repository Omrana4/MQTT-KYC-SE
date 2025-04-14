# Real-Time KYC Card Verification System

## Overview
Real-time KYC verification using MQTT for card data processing.
- **Card Client**: Publishes KYC data (~30% edge cases: invalid IDs, short names, expired dates) to `kyc/card_data`.
- **Verifier**: Validates ID, name, expiry, region, card type; publishes to `kyc/result`.
- **Analyst**: Stores results in SQLite, exports CSV, generates visualizations.

## Prerequisites
- Ubuntu 24
- Python 3.12
- Mosquitto MQTT broker

## Setup
1. **Clone**:
   ```bash
   git clone https://github.com/QuantumBreakz/MQTT-K-Project.git
   cd MQTT-K-Project
   ```
2. **Install Mosquitto**:
   ```bash
   sudo apt update
   sudo apt install mosquitto mosquitto-clients
   sudo systemctl enable mosquitto
   ```
3. **Configure Mosquitto**:
   ```bash
   sudo nano /etc/mosquitto/conf.d/local.conf
   # Add:
   listener 1883
   allow_anonymous true
   # Save, then:
   sudo systemctl restart mosquitto
   ```
4. **Python Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
5. **Environment**:
   ```bash
   echo 'MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_QOS=1' > .env
   ```

## Running
1. **Verifier**:
   ```bash
   python3 src/verifier/verifier.py
   ```
2. **Analyst**:
   ```bash
   python3 src/analyst/analyst.py
   ```
3. **Card Client**:
   ```bash
   python3 src/card_client/card_client.py --count 30 --sleep 0.15
   # Simultaneous:
   python3 src/card_client/card_client.py --count 10 --sleep 0.1 & python3 src/card_client/card_client.py --count 10 --sleep 0.1
   ```

## Outputs
- **Logs**: `data/card_client.log`, `verifier.log`, `analyst.log`
- **Data**: `data/kyc_results.db`, `card_metrics.csv`, `verifier_results.csv`, `analysis_results.csv`
- **Visualizations**: `docs/diagrams/status_pie.png`, `card_type_heatmap.png`, `region_heatmap.png`
- **Docs**: `docs/plan.txt`, `test_log.txt`, `pseudocode.txt`, `flowchart.txt`, `uml.txt`

## Results
- **Test Run**: 50 cards processed, 43 approved, 7 rejected (~14% rejection rate).
- **Edge Cases**: Handles `invalid_id`, short names (`A`), expired dates.
- **Visualizations**: Pie chart (status), heatmaps (card type, region).
