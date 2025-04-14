# Real-Time KYC Card Verification System Report

## Introduction
- **Objective**: Develop a real-time Know Your Customer (KYC) card verification system using MQTT for secure, scalable data processing.
- **Team**:
  - Ali: Card Client (data generation and publishing).
  - Omran: Verifier (data validation).
  - Ahmed: Analyst (data storage and visualization).
- **Timeline**: April 5–17, 2025, with deliverables due April 15–16 (report, Gantt chart).

## System Design
- **Architecture**:
  - **Card Client**: Generates and publishes card data (~30% edge cases: invalid IDs, short names, expired dates) to MQTT topic `kyc/card_data`.
  - **Verifier**: Subscribes to `kyc/card_data`, validates fields (ID, name, expiry, region, card type), and publishes results to `kyc/result`.
  - **Analyst**: Subscribes to `kyc/result`, stores data in SQLite (`kyc_results.db`), generates visualizations (pie chart, heatmaps), and exports CSV.
  - **Frontend**: Flask-based dashboard displays real-time stats and visualizations.
- **Technologies**:
  - MQTT: Mosquitto broker (`localhost:1883`, QoS 1).
  - Python: `paho-mqtt`, `pandas`, `matplotlib`, `seaborn`, `flask`.
  - Database: SQLite (`kyc_results.db\').
  - Frontend: HTML, CSS, JavaScript.

## Implementation
- **Card Client (Ali)**:
  - Generates 30 cards by default, configurable via `--count` and `--sleep` (e.g., `--count 10 --sleep 0.1`).
  - Edge cases (~30%): Invalid IDs (`invalid_id`), short names (`A`), expired dates.
  - Supports simultaneous runs using unique UUID client IDs.
  - Publishes to `kyc/card_data`, logs to `data/card_client.log`, saves metrics to `card_metrics.csv`.
- **Verifier (Omran)**:
  - Validates ID format (`^\d{4}-\d{4}-\d{4}$|^\d{6}-\d{4}$`), name length (\>=3, >=2 words), expiry (future date), region (`US`, `EU`, `ASIA`, `MEA\'), and card type (`Visa`, `MasterCard`, `Amex`, `Discover\').
  - Publishes results (`approved` or `rejected` with reasons) to `kyc/result`.
  - Logs to `data/verifier.log`, saves to `verifier_results.csv`.
- **Analyst (Ahmed)**:
  - Stores results in `kyc_results.db`.
  - Generates visualizations: pie chart (`status_pie.png`), heatmaps (`card_type_heatmap.png`, `region_heatmap.png\').
  - Exports analysis to `analysis_results.csv`.
- **Frontend**:
  - Flask app (`frontend/app.py`) serves dashboard at `http://localhost:5000`.
  - Displays real-time stats (total, approved, rejected, rejection rate) from `kyc_results.db`.
  - Shows visualizations from `docs/diagrams/`.
  - Uses HTML, CSS, JavaScript for responsive design and periodic updates (every 10s).

## Results
- **Statistics**:
  - Total cards processed: 50.
  - Approved: 43.
  - Rejected: 7.
  - Rejection rate: ~14%.
- **Edge Cases Handled**:
  - Invalid ID formats (`invalid_id\').
  - Short names (`A\').
  - Expired dates (e.g., 2024-09-07).
- **Outputs**:
  - Logs: `data/card_client.log`, `verifier.log`, `analyst.log`.
  - Data: `kyc_results.db`, `card_metrics.csv`, `verifier_results.csv`, `analysis_results.csv`.
  - Visualizations: `docs/diagrams/status_pie.png`, `card_type_heatmap.png`, `region_heatmap.png`.
  - Frontend: Dashboard at `http://localhost:5000` with stats and PNGs.
- **Performance**:
  - Card Client: Publishes ~6 cards/sec (`--sleep 0.1\').
  - Verifier: Processes messages in real-time.
  - Analyst: Generates visualizations in <1s.
  - Frontend: Updates stats every 10s, loads PNGs instantly.

## Challenges and Solutions
- **MQTT Connection**: Handled with retry logic (up to 5 attempts) in Card Client.
- **Edge Cases**: Verifier robustly detects invalid data using regex and schema validation.
- **Frontend Images**: Fixed path issues to serve PNGs via Flask route (`/docs/diagrams/`).
- **Scalability**: UUIDs enable multiple Card Client instances without conflicts.

## Conclusion
- **Achievements**:
  - Fully functional MQTT-based KYC system.
  - Real-time verification with detailed analytics.
  - User-friendly Flask dashboard for monitoring.
- **Future Work**:
  - Add MQTT TLS for secure communication.
  - Implement user authentication for Flask dashboard.
  - Extend edge cases (e.g., malformed JSON).
  - Deploy to cloud (e.g., AWS) for production.

## Appendix
- **Pseudocode**: `docs/appendix/pseudocode.txt`
- **Flowchart**: `docs/diagrams/flowchart.txt`
- **UML**: `docs/diagrams/uml.txt`
- **Gantt Chart**: `docs/report/gantt.txt`
- **Repository**: [github.com/QuantumBreakz/MQTT-K-Project](https://github.com/QuantumBreakz/MQTT-K-Project)
