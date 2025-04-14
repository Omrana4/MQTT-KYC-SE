# Real-Time KYC Card Verification System

## Overview
A real-time KYC verification system using MQTT for card data processing, validation, and analysis, with a Flask-based frontend for monitoring.

- **Card Client**: Generates and publishes card data (~30% edge cases: invalid IDs, short names, expired dates) to `kyc/card_data`.
- **Verifier**: Validates data and publishes results to `kyc/result`.
- **Analyst**: Stores results in SQLite, generates visualizations, and exports CSV.
- **Frontend**: Displays real-time stats and visualizations at `http://localhost:5000`.

## Team
- Ali: Card Client
- Omran: Verifier
- Ahmed: Analyst

## Prerequisites
- Ubuntu 24
- Python 3.12
- Mosquitto MQTT broker
- SQLite

## Setup
1. **Clone Repository**:
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

4. **Set Up Python Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Create Environment File**:
   ```bash
   echo 'MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_QOS=1' > .env
   ```

## Running
1. **Start Verifier**:
   ```bash
   python3 src/verifier/verifier.py
   ```

2. **Start Analyst**:
   ```bash
   python3 src/analyst/analyst.py
   ```

3. **Start Card Client** (single instance):
   ```bash
   python3 src/card_client/card_client.py --count 30 --sleep 0.15
   ```

4. **Start Card Client** (multiple instances):
   ```bash
   python3 src/card_client/card_client.py --count 10 --sleep 0.1 & python3 src/card_client/card_client.py --count 10 --sleep 0.1
   ```

5. **Start Frontend**:
   ```bash
   python3 frontend/app.py
   ```
   Open `http://localhost:5000` to view the dashboard.

## Outputs
- **Logs**:
  - Card Client: `data/card_client.log`
  - Verifier: `data/verifier.log`
  - Analyst: `data/analyst.log`
- **Data**:
  - SQLite: `data/kyc_results.db`
  - CSV: `data/card_metrics.csv`, `verifier_results.csv`, `analysis_results.csv`
- **Visualizations**:
  - Pie chart: `docs/diagrams/status_pie.png`
  - Heatmaps: `docs/diagrams/card_type_heatmap.png`, `region_heatmap.png`
- **Frontend**:
  - Dashboard: Real-time stats (total, approved, rejected, rejection rate) and PNGs
- **Documentation**:
  - Plan: `docs/plan.txt`
  - Tests: `docs/test_log.txt`
  - Pseudocode: `docs/pseudocode.txt`
  - Flowchart: `docs/flowchart.txt`
  - UML: `docs/uml.txt`
  - Report: `docs/report/report.md`
  - Gantt Chart: `docs/report/gantt.txt`

## Results
- **Statistics**:
  - Total: 50 cards
  - Approved: 43
  - Rejected: 7
  - Rejection Rate: ~14%
- **Edge Cases**:
  - Invalid IDs (`invalid_id`)
  - Short names (`A`)
  - Expired dates (e.g., 2024-09-07)
- **Visualizations**:
  - Pie chart: Status distribution
  - Heatmaps: Card type and region analysis
- **Frontend**:
  - Displays stats and PNGs, updates every 10s

## Troubleshooting
- **No Images in Frontend**:
  - Check `docs/diagrams/` for PNGs.
  - Run `curl -I http://localhost:5000/docs/diagrams/status_pie.png`.
  - Verify Flask logs for file errors.
- **MQTT Errors**:
  - Ensure Mosquitto is running (`sudo systemctl status mosquitto`).
  - Check `.env` for correct broker settings.
- **Database Issues**:
  - Verify `data/kyc_results.db` exists.
  - Run `sqlite3 data/kyc_results.db 'SELECT * FROM results LIMIT 5'`.

## Repository
[github.com/QuantumBreakz/MQTT-K-Project](https://github.com/QuantumBreakz/MQTT-K-Project)
