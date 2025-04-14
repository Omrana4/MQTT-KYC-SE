# Real-Time KYC Card Verification System

## Overview
A real-time KYC verification system using MQTT, with a Flask frontend for monitoring card data processing.

- **Card Client**: Publishes card data (~30% edge cases) to `kyc/card_data`.
- **Verifier**: Validates data and publishes to `kyc/result`.
- **Analyst**: Stores results in SQLite, generates visualizations.
- **Frontend**: Flask dashboard at `http://localhost:5000`.

## Team
- Ali: Card Client
- Omran: Verifier
- Ahmed: Analyst

## Prerequisites
- Ubuntu 24
- Python 3.12
- Mosquitto
- SQLite

## Setup
1. **Clone**:
   ```bash
   git clone https://github.com/QuantumBreakz/MQTT-K-Project.git
   cd MQTT-K-Project
   ```
2. **Mosquitto**:
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
   # Multiple:
   python3 src/card_client/card_client.py --count 10 --sleep 0.1 & python3 src/card_client/card_client.py --count 10 --sleep 0.1
   ```
4. **Frontend**:
   ```bash
   python3 frontend/app.py
   ```
   Open `http://localhost:5000`.

## Outputs
- **Logs**: `data/card_client.log`, `verifier.log`, `analyst.log`
- **Data**: `kyc_results.db`, `card_metrics.csv`, `verifier_results.csv`, `analysis_results.csv`
- **Visualizations**: `docs/diagrams/status_pie.png`, `card_type_heatmap.png`, `region_heatmap.png`
- **Frontend**: Real-time stats and PNGs
- **Docs**: `docs/plan.txt`, `pseudocode.txt`, `flowchart.txt`, `uml.txt`, `docs/report/report.md`, `gantt.png`

## Results
- **Stats**: 50 cards, 43 approved, 7 rejected (~14% rejection rate).
- **Edge Cases**: Invalid IDs, short names, expired dates.
- **Visualizations**: Pie chart, heatmaps.
- **Gantt Chart**: `docs/report/gantt.png`

## Troubleshooting
- **Images Not Rendering**:
  - Verify PNGs: `ls docs/diagrams/`.
  - Check: `curl -I http://localhost:5000/docs/diagrams/status_pie.png`.
  - Clear cache: Ctrl+Shift+R.
  - Check Flask logs: `tail -n 10 frontend.log`.
- **MQTT**:
  - Check Mosquitto: `sudo systemctl status mosquitto`.
  - Verify `.env`.
- **Database**:
  - Check: `sqlite3 data/kyc_results.db 'SELECT * FROM results LIMIT 5'`.

## Repository
[github.com/QuantumBreakz/MQTT-K-Project](https://github.com/QuantumBreakz/MQTT-K-Project)
