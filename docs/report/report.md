# KYC Verification Report

## Introduction
- **Objective**: Real-time KYC card verification using MQTT.
- **Team**: Ali (Card Client), Omran (Verifier), Ahmed (Analyst).

## System Design
- **Pipeline**:
  - Card Client: Publishes to `kyc/card_data`.
  - Verifier: Validates, publishes to `kyc/result`.
  - Analyst: Stores results, visualizes data.
- **MQTT**: Mosquitto on `localhost:1883`, QoS 1.

## Implementation
- **Card Client** (Ali):
  - Generates 30 cards (~30% edge cases: `invalid_id`, `A`, expired dates).
  - Configurable via `--count`, `--sleep`.
  - Logs to `data/card_client.log`, metrics to `card_metrics.csv`.
- **Verifier** (Omran): Validates ID, name, expiry, region, card type.
- **Analyst** (Ahmed): Stores in `kyc_results.db`, creates 3 PNGs.

## Results
- **Stats**: 50 cards, 43 approved, 7 rejected (14% rejection rate).
- **Outputs**: Logs, CSVs, `kyc_results.db`, PNGs (`docs/diagrams/`).
- **Visualizations**: Pie chart, heatmaps for card type and region.

## Conclusion
- **Success**: Pipeline verifies KYC data with robust analysis.
- **Future**: Add web UI, MQTT auth.

## Appendix
- Pseudocode: `docs/appendix/pseudocode.txt`
- Flowchart: `docs/diagrams/flowchart.txt`
- UML: `docs/diagrams/uml.txt`
