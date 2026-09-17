"""
app.py
------
Main Flask application for the AI-Based Smart Traffic Management System.

Run with:
    python app.py

Then open http://127.0.0.1:5000 in a browser.
"""

import os
import cv2
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

import database
from vehicle_detection import detect_vehicles, calculate_green_signal_time, get_density_level

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, "uploads")
RESULT_FOLDER = os.path.join(PROJECT_ROOT, "frontend", "static", "results")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

app = Flask(
    __name__,
    template_folder=os.path.join(PROJECT_ROOT, "frontend", "templates"),
    static_folder=os.path.join(PROJECT_ROOT, "frontend", "static"),
)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8 MB max upload

JUNCTION_NAME = "Main City Junction"


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------------------------------------------------
# PAGE ROUTES
# ---------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html", junction_name=JUNCTION_NAME)


@app.route("/history")
def history():
    return render_template("history.html", junction_name=JUNCTION_NAME)


# ---------------------------------------------------------------------
# API ROUTES
# ---------------------------------------------------------------------

@app.route("/api/detect", methods=["POST"])
def api_detect():
    """
    Accepts a lane image + lane number, runs vehicle detection,
    calculates the recommended green signal time, saves the
    annotated image, logs the result in the database, and
    returns everything as JSON for the frontend dashboard.
    """
    if "image" not in request.files:
        return jsonify({"success": False, "error": "No image file uploaded."}), 400

    file = request.files["image"]
    lane_number = request.form.get("lane_number", type=int)

    if lane_number is None:
        return jsonify({"success": False, "error": "lane_number is required."}), 400

    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"success": False, "error": "Please upload a valid PNG/JPG image."}), 400

    filename = secure_filename(f"lane{lane_number}_{file.filename}")
    upload_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(upload_path)

    try:
        vehicle_count, annotated_image = detect_vehicles(upload_path)
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

    green_time = calculate_green_signal_time(vehicle_count)
    density_level = get_density_level(vehicle_count)

    result_filename = f"result_{filename}"
    result_path = os.path.join(RESULT_FOLDER, result_filename)
    cv2.imwrite(result_path, annotated_image)

    database.insert_log(
        junction_name=JUNCTION_NAME,
        lane_number=lane_number,
        vehicle_count=vehicle_count,
        green_time=green_time,
        density_level=density_level,
        image_name=result_filename,
    )

    return jsonify({
        "success": True,
        "lane_number": lane_number,
        "vehicle_count": vehicle_count,
        "green_time": green_time,
        "density_level": density_level,
        "result_image_url": f"/static/results/{result_filename}",
    })


@app.route("/api/save-cycle", methods=["POST"])
def api_save_cycle():
    """Save a completed 4-lane signal cycle summary."""
    data = request.get_json(force=True)
    total_vehicles = data.get("total_vehicles", 0)
    total_cycle_time = data.get("total_cycle_time", 0)

    database.insert_cycle(JUNCTION_NAME, total_vehicles, total_cycle_time)
    return jsonify({"success": True})


@app.route("/api/logs", methods=["GET"])
def api_logs():
    logs = database.get_all_logs(limit=200)
    return jsonify({"success": True, "logs": logs})


@app.route("/api/stats", methods=["GET"])
def api_stats():
    stats = database.get_stats()
    return jsonify({"success": True, "stats": stats})


@app.route("/api/reset", methods=["POST"])
def api_reset():
    """Clears all logs - useful to reset the demo between visitors."""
    database.clear_logs()
    return jsonify({"success": True, "message": "All logs cleared."})


# ---------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------

if __name__ == "__main__":
    database.init_db()
    print("=" * 60)
    print(" AI-Based Smart Traffic Management System")
    print(" Server running at: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
