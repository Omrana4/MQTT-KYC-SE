# Risk Management
- **Risk: MQTT Broker Failure**
  - Mitigation: Added retry logic in Card Client and Verifier.
- **Risk: Frontend Image Caching**
  - Mitigation: Used static cache-busting (`?v=1`).
- **Quality Assurance**:
  - Validation: Regex for ID, name checks.
  - Testing: Ran 50 cards, verified 14% rejection rate.
