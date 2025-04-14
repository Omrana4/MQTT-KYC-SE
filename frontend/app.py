from flask import Flask, render_template, send_from_directory
import sqlite3
import os

app = Flask(__name__)

@app.route('/docs/diagrams/<path:filename>')
def serve_diagrams(filename):
    """Serve static PNGs from docs/diagrams."""
    return send_from_directory(os.path.join('docs', 'diagrams'), filename)

def get_stats():
    """Query kyc_results.db for verification stats."""
    try:
        with sqlite3.connect("data/kyc_results.db") as conn:
            cursor = conn.execute("SELECT status, COUNT(*) FROM results GROUP BY status")
            stats = dict(cursor.fetchall())
            total = sum(stats.values())
            rejection_rate = (stats.get("rejected", 0) / total * 100) if total > 0 else 0
            return {
                "approved": stats.get("approved", 0),
                "rejected": stats.get("rejected", 0),
                "total": total,
                "rejection_rate": round(rejection_rate, 2)
            }
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return {"approved": 0, "rejected": 0, "total": 0, "rejection_rate": 0}

@app.route("/")
def dashboard():
    """Render the KYC dashboard with stats and visualizations."""
    stats = get_stats()
    return render_template(
        "index.html",
        approved=stats["approved"],
        rejected=stats["rejected"],
        total=stats["total"],
        rejection_rate=stats["rejection_rate"]
    )

@app.route("/stats")
def stats():
    """Return JSON stats for JavaScript updates."""
    return get_stats()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

