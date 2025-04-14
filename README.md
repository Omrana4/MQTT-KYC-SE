# Real-Time KYC Card Verification System

## Overview
This project implements a real-time Know Your Customer (KYC) card verification system using MQTT for secure, scalable data processing. It includes a Flask-based frontend for monitoring verification stats and visualizations. The system is designed to generate card data, validate it, analyze results, and display them dynamically.

- **Card Client**: Generates and publishes card data (~30% edge cases: invalid IDs, short names, expired dates) to the MQTT topic `kyc/card_data`.
- **Verifier**: Subscribes to `kyc/card_data`, validates fields (ID, name, expiry, region, card type), and publishes results to `kyc/result`.
- **Analyst**: Subscribes to `kyc/result`, stores data in SQLite (`kyc_results.db`), generates visualizations (pie chart, heatmaps), and exports results to CSV.
- **Frontend**: A Flask-based dashboard at `http://localhost:5000` displays real-time stats (total cards, approved, rejected, rejection rate) and visualizations.

## Team
- **Ali**: Card Client (data generation and publishing)
- **Omran**: Verifier (data validation)
- **Ahmed**: Analyst (data storage and visualization)

## Prerequisites
- **Operating System**: Ubuntu 24
- **Python**: 3.12
- **MQTT Broker**: Mosquitto
- **Database**: SQLite
- **Dependencies**: Listed in `requirements.txt`

## Directory Structure
```
MQTT-KYC-Project/
├── data/                    # Logs, database, and CSV outputs
│   ├── kyc_results.db       # SQLite database for results
│   ├── card_client.log      # Card Client logs
│   ├── verifier.log         # Verifier logs
│   ├── analyst.log          # Analyst logs
│   ├── card_metrics.csv     # Card Client metrics
│   ├── verifier_results.csv # Verifier results
│   └── analysis_results.csv # Analyst results
├── docs/                    # Documentation and diagrams
│   ├── diagrams/            # Visualizations
│   │   ├── status_pie.png
│   │   ├── card_type_heatmap.png
│   │   ├── region_heatmap.png
│   │   ├── flowchart.txt
│   │   └── uml.txt
│   ├── appendix/            # Additional docs
│   │   └── pseudocode.txt
│   ├── plan.txt
│   ├── test_log.txt
│   └── report/              # Project report
│       ├── report.md
│       ├── gantt.png
│       └── generate_gantt.py
├── frontend/                # Flask frontend
│   ├── app.py
│   ├── templates/
│   │   └── index.html
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   ├── js/
│   │   │   └── script.js
│   │   └── images/
│   │       └── placeholder.png
├── src/                     # Core components
│   ├── card_client/
│   │   └── card_client.py
│   ├── verifier/
│   │   └── verifier.py
│   └── analyst/
│       └── analyst.py
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

## Setup
Follow these steps to set up the project on your local machine.

### 1. Clone the Repository
```bash
git clone https://github.com/QuantumBreakz/MQTT-K-Project.git
cd MQTT-KYC-Project
```

### 2. Install Mosquitto MQTT Broker
```bash
sudo apt update
sudo apt install mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

### 3. Configure Mosquitto
Enable anonymous access for simplicity (update for production use with authentication).
```bash
sudo nano /etc/mosquitto/conf.d/local.conf
# Add the following lines:
listener 1883
allow_anonymous true
# Save and exit, then restart Mosquitto:
sudo systemctl restart mosquitto
```

### 4. Set Up Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
The `requirements.txt` includes:
```
paho-mqtt==2.0.0
pandas==2.2.2
matplotlib==3.9.2
seaborn==0.13.2
jsonschema==4.23.0
python-dotenv==1.0.1
flask==3.0.3
```

### 5. Configure Environment Variables
Create a `.env` file for MQTT settings.
```bash
echo 'MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_QOS=1' > .env
```

### 6. Create Required Directories
```bash
mkdir -p data docs/diagrams docs/appendix docs/report frontend/templates frontend/static/css frontend/static/js frontend/static/images
```

## Running the System
Run each component in separate terminal sessions. Ensure the virtual environment is activated (`source venv/bin/activate`).

### 1. Start the Verifier
```bash
python3 src/verifier/verifier.py
```
- Subscribes to `kyc/card_data`, validates data, and publishes results to `kyc/result`.
- Logs to `data/verifier.log`, saves results to `verifier_results.csv`.

### 2. Start the Analyst
```bash
python3 src/analyst/analyst.py
```
- Subscribes to `kyc/result`, stores data in `kyc_results.db`.
- Generates visualizations: `status_pie.png`, `card_type_heatmap.png`, `region_heatmap.png` in `docs/diagrams/`.
- Logs to `data/analyst.log`, exports to `analysis_results.csv`.

### 3. Start the Card Client
Run a single instance:
```bash
python3 src/card_client/card_client.py --count 30 --sleep 0.15
```
Run multiple instances simultaneously:
```bash
python3 src/card_client/card_client.py --count 10 --sleep 0.1 & python3 src/card_client/card_client.py --count 10 --sleep 0.1
```
- Generates card data with ~30% edge cases (invalid IDs, short names, expired dates).
- Publishes to `kyc/card_data`, logs to `data/card_client.log`, saves metrics to `card_metrics.csv`.

### 4. Start the Frontend
```bash
python3 frontend/app.py
```
- Access the dashboard at `http://localhost:5000`.
- Displays real-time stats (total cards, approved, rejected, rejection rate) and visualizations.
- Updates stats every 10 seconds via JavaScript.

## Outputs
The system generates the following outputs:

- **Logs**:
  - `data/card_client.log`: Card Client activity (e.g., "Published card data").
  - `data/verifier.log`: Verifier activity (e.g., "Verified card", "Rejected card").
  - `data/analyst.log`: Analyst activity (e.g., "Stored result", "Generated visualizations").
- **Data**:
  - `data/kyc_results.db`: SQLite database storing verification results.
  - `data/card_metrics.csv`: Card Client metrics (e.g., card ID, timestamp).
  - `data/verifier_results.csv`: Verifier results (e.g., card ID, status, reason).
  - `data/analysis_results.csv`: Analyst summary (e.g., status counts, rejection rate).
- **Visualizations**:
  - `docs/diagrams/status_pie.png`: Pie chart of approved vs. rejected cards.
  - `docs/diagrams/card_type_heatmap.png`: Heatmap of card types vs. status.
  - `docs/diagrams/region_heatmap.png`: Heatmap of regions vs. status.
- **Frontend**:
  - Real-time dashboard at `http://localhost:5000` showing stats and PNGs.
- **Documentation**:
  - `docs/plan.txt`: Project plan.
  - `docs/test_log.txt`: Test logs.
  - `docs/pseudocode.txt`: Pseudocode for components.
  - `docs/flowchart.txt`: System flowchart.
  - `docs/uml.txt`: UML diagram.
  - `docs/report/report.md`: Project report.
  - `docs/report/gantt.png`: Gantt chart (April 5–13, 2025).

## Results
- **Statistics**:
  - Total cards processed: 50.
  - Approved: 43.
  - Rejected: 7.
  - Rejection rate: ~14%.
- **Edge Cases Handled**:
  - Invalid ID formats (e.g., `invalid_id`).
  - Short names (e.g., `A`).
  - Expired dates (e.g., `2024-09-07`).
- **Visualizations**:
  - Pie chart: Status distribution (approved vs. rejected).
  - Heatmaps: Card type and region analysis.
- **Frontend**:
  - Displays stats and PNGs, updates every 10 seconds.
- **Gantt Chart**:
  - Visual timeline of tasks (Setup, Card Client, Verifier, Analyst, Frontend, Docs, Report) from April 5–13, 2025, in `docs/report/gantt.png`.

## Troubleshooting
### Images Not Rendering in Frontend
- Verify PNGs exist:
  ```bash
  ls docs/diagrams/
  ```
  Expect: `status_pie.png`, `card_type_heatmap.png`, `region_heatmap.png`.
- Check Flask route:
  ```bash
  curl -I http://localhost:5000/docs/diagrams/status_pie.png
  ```
  Expect HTTP 200 OK.
- Clear browser cache: Press `Ctrl+Shift+R` in the browser.
- Check Flask logs:
  ```bash
  tail -n 10 frontend.log
  ```
  Look for "File not found" or "Error serving file".

### MQTT Connection Issues
- Verify Mosquitto is running:
  ```bash
  sudo systemctl status mosquitto
  ```
- Check `.env` file for correct settings (`MQTT_BROKER=localhost`, `MQTT_PORT=1883`).
- Check logs for connection errors:
  ```bash
  cat data/card_client.log | grep "ERROR"
  ```

### Database Issues
- Verify database exists:
  ```bash
  ls data/kyc_results.db
  ```
- Query database:
  ```bash
  sqlite3 data/kyc_results.db 'SELECT * FROM results LIMIT 5'
  ```
- If empty or missing, ensure `analyst.py` ran successfully:
  ```bash
  cat data/analyst.log | tail -n 10
  ```

### General Debugging
- Check Card Client logs for published messages:
  ```bash
  cat data/card_client.log | grep "Published" | tail -n 3
  ```
- Check Verifier logs for validation:
  ```bash
  cat data/verifier.log | grep "Verified" | tail -n 3
  ```
- Check Analyst logs for rejection rate:
  ```bash
  cat data/analyst.log | tail -n 5
  ```

## Repository
[github.com/QuantumBreakz/MQTT-K-Project](https://github.com/QuantumBreakz/MQTT-K-Project)

## Notes
- The system is designed for local development. For production, enable MQTT authentication (`allow_anonymous false`) and add TLS.
- The frontend uses a static cache-busting parameter (`?v=1`). Increment the value or clear browser cache to refresh images.
- The Gantt chart (`docs/report/gantt.png`) was generated using `matplotlib`. Edit `docs/report/generate_gantt.py` to adjust tasks or dates.
