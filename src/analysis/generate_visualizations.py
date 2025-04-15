import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure the output directory exists
import os
os.makedirs('docs/diagrams', exist_ok=True)
os.makedirs('docs/diagram', exist_ok=True)

# Connect to SQLite database
conn = sqlite3.connect('/home/yoboi/Documents/2025/Upwork 2025/Project 2/MQTT-KYC-Project/data/kyc_results.db')  # Fix path to include the database file
df = pd.read_sql_query("SELECT * FROM results", conn)
conn.close()

# Filter rejected cards
rejected_df = df[df['status'] == 'rejected']

# Figure 6: Rejection Reasons Bar Chart
if not rejected_df.empty:
    rejection_reasons = rejected_df['reasons'].value_counts()
    plt.figure(figsize=(8, 4))
    rejection_reasons.plot(kind='bar', color='#EF5350')
    plt.title('Rejection Reasons')
    plt.xlabel('Reason')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('docs/diagrams/rejection_reasons.png')
    plt.close()
else:
    # Fallback for no rejections
    plt.figure(figsize=(8, 4))
    plt.bar([], [], color='#EF5350')
    plt.title('Rejection Reasons (No Rejections)')
    plt.xlabel('Reason')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('docs/diagrams/rejection_reasons.png')
    plt.close()

# Figure 7: Rejection Heatmap by Region
if not rejected_df.empty:
    rejection_by_region = rejected_df.groupby('region').size() / df.groupby('region').size() * 100
    rejection_by_region = rejection_by_region.fillna(0).reset_index(name='rejection_rate')
else:
    # Fallback data if no rejections
    rejection_by_region = pd.DataFrame({'region': ['EU', 'US', 'ASIA'], 'rejection_rate': [0, 0, 0]})
pivot = rejection_by_region.pivot(columns='region', values='rejection_rate')
plt.figure(figsize=(8, 2))
sns.heatmap(pivot, annot=True, cmap='Reds', fmt='.1f')
plt.title('Rejection Rates by Region (%)')
plt.tight_layout()
plt.savefig('docs/diagrams/rejection_heatmap.png')
plt.close()
