import os
import json
import logging
from flask import Flask, jsonify, send_file
from pathlib import Path

import db

logger = logging.getLogger(__name__)

app = Flask(__name__)
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8080"))


@app.route("/api/stats")
def stats():
    return jsonify(db.get_dashboard_stats())


@app.route("/")
def index():
    return send_file("dashboard.html")


def run_dashboard():
    logger.info(f"Dashboard running on port {DASHBOARD_PORT}")
    app.run(host="0.0.0.0", port=DASHBOARD_PORT, debug=False)
