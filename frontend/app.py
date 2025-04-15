from flask import Flask, render_template, send_from_directory, jsonify
import sqlite3
import os

app = Flask(__name__)

# Set absolute path for docs/diagrams
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DIAGRAMS_DIR = os.path.join(BASE_DIR, "..", "docs", "diagrams")

def get_stats():
    """Query kyc_results.db for verification stats."""
    try:
        db_path = os.path.join(BASE_DIR, "..", "data", "kyc_results.db")
        with sqlite3.connect(db_path) as conn:
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
    """Render the KYC dashboard."""
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
    """Return JSON stats for real-time updates."""
    return jsonify(get_stats())

@app.route("/docs/diagrams/<path:filename>")
def serve_diagrams(filename):
    """Serve PNGs from docs/diagrams."""
    try:
        full_path = os.path.join(DIAGRAMS_DIR, filename)
        if not os.path.exists(full_path):
            print(f"File not found: {full_path}")
            return "File not found", 404
        print(f"Serving file: {full_path}")
        return send_from_directory(DIAGRAMS_DIR, filename)
    except Exception as e:
        print(f"Error serving file {filename}: {e}")
        return "Error serving file", 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
