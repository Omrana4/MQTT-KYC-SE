import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Define tasks and their start/end dates (April 5–13, 2025)
tasks = [
    {"task": "Setup", "start": "2025-04-05", "end": "2025-04-06"},
    {"task": "Card Client", "start": "2025-04-06", "end": "2025-04-08"},
    {"task": "Verifier", "start": "2025-04-07", "end": "2025-04-09"},
    {"task": "Analyst", "start": "2025-04-08", "end": "2025-04-10"},
    {"task": "Frontend", "start": "2025-04-09", "end": "2025-04-11"},
    {"task": "Docs", "start": "2025-04-10", "end": "2025-04-12"},
    {"task": "Report", "start": "2025-04-11", "end": "2025-04-13"},
]

# Convert dates to datetime
for task in tasks:
    task["start"] = datetime.strptime(task["start"], "%Y-%m-%d")
    task["end"] = datetime.strptime(task["end"], "%Y-%m-%d")
    task["duration"] = (task["end"] - task["start"]).days + 1

# Create figure
fig, ax = plt.subplots(figsize=(10, 5))
colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"]

# Plot tasks
for i, task in enumerate(reversed(tasks)):
    start_day = (task["start"] - datetime(2025, 4, 5)).days
    ax.barh(task["task"], task["duration"], left=start_day, color=colors[i % len(colors)], edgecolor="black")

# Customize
ax.set_xlabel("Date")
ax.set_title("Gantt Chart: KYC Verification Project (April 5–13, 2025)")
ax.set_xticks(range(9))
ax.set_xticklabels([f"Apr {d}" for d in range(5, 14)])
ax.grid(True, axis="x", linestyle="--", alpha=0.7)
plt.tight_layout()

# Save
plt.savefig("docs/report/gantt.png", dpi=300, bbox_inches="tight")
plt.close()
