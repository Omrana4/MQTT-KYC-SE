# Real-Time KYC Card Verification System Report

## Introduction
- **Objective**: Build a real-time KYC verification system using MQTT, with a Flask frontend.
- **Team**:
  - Ash: Card Client (data generation).
  - Omran: Verifier (data validation).
  - Mohamed: Analyst (data analysis, visualizations).
- **Timeline**: April 5–13, 2025 (development), deliverables due April 15–16.

## System Design
- **Architecture**:
  - **Card Client**: Publishes card data (~30% edge cases) to `kyc/card_data`.
  - **Verifier**: Validates and publishes to `kyc/result`.
  - **Analyst**: Stores results in SQLite (`kyc_results.db`), generates PNGs.
  - **Frontend**: Flask dashboard (`http://localhost:5000`) shows stats and PNGs.
- **Technologies**:
  - MQTT: Mosquitto (`localhost:1883`, QoS 1).
  - Python: `paho-mqtt`, `pandas`, `matplotlib`, `seaborn`, `flask`.
  - Database: SQLite.
  - Frontend: HTML, CSS, JavaScript.
- **Gantt Chart**: See `gantt.png` for timeline (April 5–13).

## Implementation
- **Card Client (Ali)**:
  - Generates configurable cards (`--count`, `--sleep`).
  - Edge cases: Invalid IDs (`invalid_id`), short names (`A`), expired dates.
  - Uses UUIDs for simultaneous runs.
  - Logs: `data/card_client.log`, CSV: `card_metrics.csv`.
- **Verifier (Omran)**:
  - Validates ID (`^\d{4}-\d{4}-\d{4}$|^\d{6}-\d{4}$`), name (\>=3 chars, >=2 words), expiry, region, card type.
  - Logs: `data/verifier.log`, CSV: `verifier_results.csv`.
- **Analyst (Ahmed)**:
  - Stores data in `kyc_results.db`.
  - Generates: `status_pie.png`, `card_type_heatmap.png`, `region_heatmap.png`.
  - CSV: `analysis_results.csv`.
- **Frontend**:
  - Flask app serves stats from `kyc_results.db`.
  - Displays PNGs from `docs/diagrams/` with static cache-busting (`?v=1`).
  - Updates stats every 10s via JavaScript.

## Results
- **Statistics**:
  - Total: 50 cards.
  - Approved: 43.
  - Rejected: 7.
  - Rejection rate: ~14%.
- **Outputs**:
  - Logs: `data/card_client.log`, `verifier.log`, `analyst.log`.
  - Data: `kyc_results.db`, CSVs.
  - Visualizations: `docs/diagrams/`.
  - Frontend: Real-time dashboard.
- **Performance**:
  - Card Client: ~6 cards/sec.
  - Verifier: Real-time validation.
  - Analyst: Visualizations in <1s.
  - Frontend: Instant PNG loading, 10s stat refresh.
- **Gantt Chart**:

## Challenges and Solutions
- **Frontend Errors**: Fixed `TemplateAssertionError` (removed `strftime`) and `TypeError` (removed `random`, used static cache-busting).
- **MQTT**: Added retry logic for connectivity.
- **Edge Cases**: Robust validation with regex and schema.
- **Scalability**: UUIDs for multiple clients.

## Conclusion
- **Achievements**:
  - Real-time KYC pipeline.
  - Dynamic Flask dashboard.
  - Clear visualizations and stats.
- **Future Work**:
  - MQTT TLS.
  - Flask authentication.
  - Cloud deployment.

## Appendix
- Pseudocode: `docs/appendix/pseudocode.txt`
- Flowchart: `docs/diagrams/flowchart.txt`
- UML: `docs/diagrams/uml.txt`
- Gantt Chart: `docs/report/gantt.png`
- Repo: [github.com/Omrana4/MQTT-KYC-SE](https://github.com/Omrana4/MQTT-KYC-SE)
