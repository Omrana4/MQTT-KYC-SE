# Real-Time KYC Card Verification System

## Overview
This project implements a real-time Know Your Customer (KYC) verification system using MQTT for secure, scalable data processing, as part of the 4005CMD Integrative Project module (due April 17, 2025). It includes a Flask-based frontend for monitoring verification stats and visualizations, developed using agile methodology with sprints from April 5–13, 2025.

- **Card Client**: Generates and publishes card data (~30% edge cases: invalid IDs, short names, expired dates) to the MQTT topic `kyc/card_data`.
- **Verifier**: Subscribes to `kyc/card_data`, validates fields (ID, name, expiry, region, card type), and publishes results to `kyc/result`.
- **Analyst**: Subscribes to `kyc/result`, stores data in SQLite (`kyc_results.db`), generates visualizations (pie chart, heatmaps), and exports results to CSV.
- **Logger**: Subscribes to `kyc/result`, logs data, and publishes to `kyc/log`.
- **Frontend**: A Flask-based dashboard at `http://localhost:5000` displays real-time stats (total cards, approved, rejected, rejection rate) and visualizations.

## Team
- **Ali**: Card Client (data generation and publishing)
- **Omran**: Verifier (data validation)
- **Ahmed**: Analyst (data storage and visualization)

## Module Alignment
This project aligns with the 4005CMD learning outcomes:
- **MLO1**: Agile sprints (April 5–13), documented in `docs/meetings/logbook.md`.
- **MLO2**: Technical skills in MQTT, Flask, SQLite, and Python (see `src/`).
- **MLO3**: Teamwork and communication via meeting logs and proposals.
- **MLO4**: Professional practices (GitHub, agile, testing) with ethical considerations (data privacy in KYC).

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
│   ├── schema.sql           # Database schema
│   ├── card_client.log      # Card Client logs
│   ├── verifier.log         # Verifier logs
│   ├── analyst.log          # Analyst logs
│   ├── logger.log           # Logger logs
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
│   ├── prototypes/          # Paper prototypes
│   │   └── paper_prototype.jpg
│   ├── meetings/            # Meeting logs
│   │   ├── proposal_log.md
│   │   └── logbook.md
│   ├── plan.txt
│   ├── methodology.md
│   ├── risk_management.md
│   ├── test_log.txt
│   └── report/              # Project report
│       ├── report.md
│       ├── report.pdf
│       ├── glossary.md
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
│   ├── analyst/
│   │   └── analyst.py
│   └── logger/
│       └── logger.py
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
mkdir -p data docs/diagrams docs/appendix docs/prototypes docs/meetings docs/report frontend/templates frontend/static/css frontend/static/js frontend/static/images src/logger
```

## Running the System
Run each component in separate terminal sessions. Ensure the virtual environment is activated (`source venv/bin/activate`).

### 1. Start the Verifier
```bash
python3 src/verifier/verifier.py
```
- Subscribes to `kyc/card_data`, validates data, and publishes to `kyc/result`.

### 2. Start the Analyst
```bash
python3 src/analyst/analyst.py
```
- Subscribes to `kyc/result`, stores data in `kyc_results.db`, generates visualizations.

### 3. Start the Logger
```bash
python3 src/logger/logger.py
```
- Subscribes to `kyc/result`, logs data, publishes to `kyc/log`.

### 4. Start the Card Client
Run a single instance:
```bash
python3 src/card_client/card_client.py --count 30 --sleep 0.15
```
Run multiple instances:
```bash
python3 src/card_client/card_client.py --count 10 --sleep 0.1 & python3 src/card_client/card_client.py --count 10 --sleep 0.1
```
- Publishes card data to `kyc/card_data`.

### 5. Start the Frontend
```bash
python3 frontend/app.py
```
- Access the dashboard at `http://localhost:5000`.

## Outputs
- **Logs**:
  - `data/card_client.log`: Card Client activity.
  - `data/verifier.log`: Verifier activity.
  - `data/analyst.log`: Analyst activity.
  - `data/logger.log`: Logger activity.
- **Data**:
  - `data/kyc_results.db`: SQLite database.
  - `data/schema.sql`: Database schema.
  - `data/card_metrics.csv`, `verifier_results.csv`, `analysis_results.csv`: Metrics and results.
- **Visualizations**:
  - `docs/diagrams/status_pie.png`: Pie chart of approved vs. rejected cards.
  - `docs/diagrams/card_type_heatmap.png`: Heatmap of card types vs. status.
  - `docs/diagrams/region_heatmap.png`: Heatmap of regions vs. status.
- **Documentation**:
  - `docs/prototypes/paper_prototype.jpg`: Paper prototype.
  - `docs/meetings/proposal_log.md`: Project proposals.
  - `docs/meetings/logbook.md`: Meeting logs.
  - `docs/methodology.md`: Aim, objectives, research questions.
  - `docs/risk_management.md`: Risk and quality assurance.
  - `docs/report/report.pdf`: Final report.

## Results
- **Statistics**: 50 cards, 43 approved, 7 rejected (~14% rejection rate).
- **Edge Cases**: Handles invalid IDs, short names, expired dates.
- **Performance**: Card Client (~6 cards/sec), Verifier (real-time), Analyst (visualizations <1s), Frontend (10s refresh).
- **Gantt Chart**: `docs/report/gantt.png` (April 5–13, 2025).

## Troubleshooting
- **Images Not Rendering**:
  ```bash
  ls docs/diagrams/
  curl -I http://localhost:5000/docs/diagrams/status_pie.png
  tail -n 10 frontend.log
  ```
  Clear cache: Ctrl+Shift+R.
- **MQTT Issues**:
  ```bash
  sudo systemctl status mosquitto
  cat data/card_client.log | grep "ERROR"
  ```
- **Database Issues**:
  ```bash
  sqlite3 data/kyc_results.db 'SELECT * FROM results LIMIT 5'
  cat data/analyst.log | tail -n 10
  ```

## Repository
[github.com/QuantumBreakz/MQTT-K-Project](https://github.com/QuantumBreakz/MQTT-K-Project)

## Notes
- For production, enable MQTT TLS and Flask authentication.
- See `docs/report/report.pdf` for detailed documentation.
