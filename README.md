# 🚦 AI-Based Smart Traffic Signal Control using Vehicle Density Detection

An Engineering Day exhibition project that uses **Computer Vision** to count vehicles in
each lane of a road junction and automatically calculates how long the green signal
should stay on — busier lanes get more green time, automatically.

---

## 1. Project Title and Abstract

**Title:** AI-Based Smart Traffic Signal Control using Vehicle Density Detection

**Abstract:**
Traditional traffic signals operate on a **fixed timer** — every lane gets the same
green-light duration regardless of how many vehicles are actually waiting. This causes
unnecessary congestion on busy lanes and wasted idle time on empty ones. This project
builds a web-based Smart Traffic Management System that uses **Computer Vision (OpenCV)**
to analyze a photo/frame of each lane, detect and count the number of vehicles present,
and automatically compute an optimal green-signal duration for that lane. The system is
built with a Flask (Python) backend, an SQLite database for storing every detection log,
and an interactive HTML/CSS/JavaScript dashboard that visually simulates a real traffic
signal cycling through all four lanes based on the AI-calculated timings.

## 2. Problem Statement

Fixed-time traffic signals are inefficient because they cannot adapt to real-time traffic
conditions. A lane with 20 vehicles gets the same green time as a lane with 2 vehicles,
leading to traffic pile-ups, fuel wastage, and increased pollution — especially at busy
city junctions. There is a need for an intelligent, low-cost system that can sense
traffic density in real time and adjust signal timing accordingly.

## 3. Objectives

- To detect and count vehicles in a lane image using computer vision techniques.
- To dynamically calculate the ideal green-signal duration based on vehicle density.
- To simulate a complete 4-lane traffic signal cycle on a web dashboard.
- To log every detection into a database for traffic pattern analysis and reporting.
- To build an easy-to-demo, professional, working prototype for an exhibition.

## 4. Main Features

- 📸 Upload a lane image and get an **instant AI vehicle count**.
- 🧮 **Automatic green-signal time calculation** based on vehicle density.
- 🚦 **Live animated traffic-light simulation** for all 4 lanes in a full cycle.
- 🟢🟡🔴 Density classification: Low / Medium / High.
- 🗄️ Every scan is **logged into an SQLite database** with timestamp.
- 📊 A **History & Reports** page with statistics (total scans, total vehicles, average
  per lane).
- 🧹 One-click **reset** for repeated exhibition demos.
- 🎨 Clean, modern, dark-themed, responsive UI.

## 5. Frontend Design

Built with plain **HTML5, CSS3, and vanilla JavaScript** (no frameworks needed, so it's
easy to explain in a viva):

- `index.html` — Dashboard with 4 lane upload cards + traffic light simulation panel.
- `history.html` — Table of all past detections + summary statistic cards.
- `style.css` — A dark, modern "control-room" themed UI with card layouts, badges,
  and animated traffic-light glow effects.
- `script.js` — Handles file upload previews, calls the backend API using `fetch()`,
  and animates the traffic-light countdown sequence.
- `history.js` — Fetches and renders logs/statistics from the backend.

## 6. Backend Functionality

Built with **Python + Flask**:

- Receives an uploaded lane image via a REST API.
- Passes the image to the **vehicle detection module** (`vehicle_detection.py`), which
  uses OpenCV to:
  1. Convert the image to grayscale and blur it.
  2. Apply adaptive thresholding to separate vehicle shapes from the road.
  3. Use morphological operations to clean up the mask.
  4. Find contours — each contour above a minimum size is counted as one vehicle.
  5. Draw bounding boxes on the detected vehicles and save an annotated result image.
- Calculates the recommended green signal time using the formula:
  ```
  green_time = min_time + (vehicle_count × seconds_per_vehicle)
  (capped between 10s and 60s)
  ```
- Classifies density as Low / Medium / High.
- Saves every result into the SQLite database.
- Exposes REST API endpoints for the frontend to fetch logs, statistics, and reset data.

## 7. Database Design

**Database:** SQLite (`traffic.db`) — no separate DB server installation needed, perfect
for a Windows laptop demo. (Can be swapped for MySQL — see note in Section 10.)

**Table: `traffic_logs`**

| Column          | Type     | Description                              |
|-----------------|----------|-------------------------------------------|
| id              | INTEGER  | Primary key, auto-increment               |
| junction_name   | TEXT     | Name of the junction                      |
| lane_number     | INTEGER  | Lane number (1–4)                         |
| vehicle_count   | INTEGER  | Number of vehicles detected by AI         |
| green_time      | INTEGER  | Calculated green signal time (seconds)    |
| density_level   | TEXT     | Low / Medium / High                       |
| image_name      | TEXT     | Filename of the annotated result image    |
| timestamp       | DATETIME | Auto-recorded time of detection           |

**Table: `signal_cycles`**

| Column            | Type     | Description                            |
|-------------------|----------|------------------------------------------|
| id                | INTEGER  | Primary key, auto-increment               |
| junction_name     | TEXT     | Name of the junction                      |
| total_vehicles    | INTEGER  | Total vehicles across the full cycle      |
| total_cycle_time  | INTEGER  | Total signal cycle duration (seconds)     |
| created_at        | DATETIME | Auto-recorded time                        |

## 8. Complete Folder Structure

```
smart_traffic_management/
│
├── backend/
│   ├── app.py                 # Flask application & API routes
│   ├── database.py            # SQLite database functions
│   ├── vehicle_detection.py   # OpenCV vehicle counting logic
│   ├── requirements.txt       # Python dependencies
│   └── traffic.db             # Auto-created on first run
│
├── frontend/
│   ├── templates/
│   │   ├── index.html         # Main dashboard page
│   │   └── history.html       # History/reports page
│   └── static/
│       ├── css/style.css      # All styling
│       ├── js/script.js       # Dashboard logic
│       ├── js/history.js      # History page logic
│       └── results/           # Annotated output images (auto-created)
│
├── uploads/                    # Temporary storage for uploaded lane images
└── README.md                   # This documentation
```

## 9. Complete Source Code

All source files are included in this project package:
`backend/app.py`, `backend/database.py`, `backend/vehicle_detection.py`,
`frontend/templates/index.html`, `frontend/templates/history.html`,
`frontend/static/css/style.css`, `frontend/static/js/script.js`,
`frontend/static/js/history.js`. Every file is complete, tested, and ready to run —
no missing pieces or placeholders.

## 10. Database SQL Queries

The Flask app auto-creates tables on first run, but here is the equivalent raw SQL
(useful for viva explanation, or if you switch to MySQL):

```sql
CREATE TABLE traffic_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    junction_name TEXT NOT NULL,
    lane_number INTEGER NOT NULL,
    vehicle_count INTEGER NOT NULL,
    green_time INTEGER NOT NULL,
    density_level TEXT NOT NULL,
    image_name TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE signal_cycles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    junction_name TEXT NOT NULL,
    total_vehicles INTEGER NOT NULL,
    total_cycle_time INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Example queries
SELECT * FROM traffic_logs ORDER BY timestamp DESC;
SELECT lane_number, AVG(vehicle_count) FROM traffic_logs GROUP BY lane_number;
SELECT COUNT(*) FROM traffic_logs;
```

> **To use MySQL instead of SQLite:** replace `sqlite3` calls in `database.py` with
> `mysql-connector-python`, change `AUTOINCREMENT` to `AUTO_INCREMENT`, and update the
> connection string with your MySQL host/user/password. The rest of the code (Flask
> routes, frontend) stays exactly the same because it only calls the functions in
> `database.py`.

## 11. API / Backend Routes

| Method | Route              | Description                                          |
|--------|--------------------|-------------------------------------------------------|
| GET    | `/`                | Renders the main dashboard page                       |
| GET    | `/history`         | Renders the history/reports page                      |
| POST   | `/api/detect`      | Accepts an image + lane number, runs AI detection      |
| POST   | `/api/save-cycle`  | Saves a completed 4-lane signal cycle summary          |
| GET    | `/api/logs`        | Returns all detection logs as JSON                     |
| GET    | `/api/stats`       | Returns summary statistics as JSON                      |
| POST   | `/api/reset`       | Clears all logs (for demo reset)                        |

**Example — `/api/detect` response:**
```json
{
  "success": true,
  "lane_number": 1,
  "vehicle_count": 6,
  "green_time": 28,
  "density_level": "Medium",
  "result_image_url": "/static/results/result_lane1_photo.jpg"
}
```

## 12. Step-by-Step Installation (Windows)

1. **Install Python 3.10+** from [python.org](https://www.python.org/downloads/) —
   during install, check ✅ *"Add Python to PATH"*.
2. **Download/extract** this project folder anywhere, e.g. `D:\smart_traffic_management`.
3. Open **Command Prompt** and navigate into the backend folder:
   ```
   cd D:\smart_traffic_management\backend
   ```
4. (Recommended) create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
5. Install the required libraries:
   ```
   pip install -r requirements.txt
   ```
6. Run the application:
   ```
   python app.py
   ```
7. Open your browser and go to: **http://127.0.0.1:5000**

## 13. How to Run the Project in VS Code

1. Open VS Code → **File → Open Folder** → select `smart_traffic_management`.
2. Install the **Python extension** (by Microsoft) if not already installed.
3. Open a new terminal: **Terminal → New Terminal**.
4. In the terminal, run:
   ```
   cd backend
   pip install -r requirements.txt
   python app.py
   ```
5. VS Code will show the server URL in the terminal — **Ctrl+Click** on
   `http://127.0.0.1:5000` to open it directly in your browser.
6. Any time you edit a file and save, Flask's debug mode will auto-reload the server.

## 14. Testing

The project was tested end-to-end during development:

- ✅ **Unit test** — `vehicle_detection.py` tested on a sample image containing 4
  synthetic vehicle shapes → correctly detected all 4.
- ✅ **API test** — `/api/detect` tested with `curl`, correctly returns vehicle
  count, green time, density, and saves an annotated result image.
- ✅ **Database test** — Verified rows are correctly inserted into `traffic_logs`
  and retrievable via `/api/logs` and `/api/stats`.
- ✅ **Reset test** — `/api/reset` correctly clears all records.
- ✅ **UI test** — Dashboard correctly enables "Run Signal Cycle" only after all 4
  lanes are analyzed, and the traffic-light animation runs in the correct
  red → yellow → green → red sequence per lane.

**Manual test checklist for your demo:**
1. Upload 4 different road photos (or the same one 4 times for a quick demo).
2. Click "Analyze Lane" on each — confirm a vehicle count and green time appear.
3. Click "Run Signal Cycle Simulation" — watch each lane's light turn green for
   its own calculated duration.
4. Go to the History page — confirm all 4 scans appear in the table with correct data.
5. Click "Clear All Logs" and confirm the table empties.

## 15. Advantages and Future Scope

**Advantages:**
- Reduces unnecessary waiting time at low-traffic lanes.
- Improves overall traffic flow and reduces fuel wastage/pollution.
- Low-cost — works with ordinary cameras/images, no special hardware.
- Easy to understand, demonstrate, and extend for a student project.

**Future Scope:**
- Replace static image upload with **live webcam/CCTV video feed** processing.
- Use a **deep learning model (YOLOv8)** for more accurate vehicle detection and
  classification (car/bus/bike/truck).
- Add **emergency vehicle priority detection** (ambulance/fire truck).
- Integrate with **real IoT traffic light hardware** via Raspberry Pi/Arduino.
- Build a **city-wide dashboard** connecting multiple junctions for traffic-pattern
  analytics and congestion prediction.

## 16. Simple Viva Questions and Answers

**Q1. What problem does this project solve?**
A: It replaces fixed-timer traffic signals with a system that adjusts green-light
duration based on actual vehicle density in each lane, reducing congestion.

**Q2. How does the system "see" the vehicles? Are you using AI/ML models?**
A: We use classical computer vision (OpenCV) — grayscale conversion, adaptive
thresholding, and contour detection — to identify vehicle-shaped regions in an
image. It's a rule-based CV pipeline, not a trained neural network, which keeps it
lightweight and easy to run on any laptop without a GPU.

**Q3. Why did you choose SQLite over MySQL?**
A: SQLite requires no separate server installation — the whole database is a single
file — making it ideal for a portable student project demo on any Windows machine.
The same code can be adapted to MySQL by only changing `database.py`.

**Q4. How is the green signal time calculated?**
A: `green_time = min_time + (vehicle_count × seconds_per_vehicle)`, capped between a
minimum (10s) and maximum (60s), so no lane waits forever or gets an unnecessarily
short signal.

**Q5. What is a contour in OpenCV?**
A: A contour is a curve joining continuous points of the same intensity along a
boundary — essentially the outline of a detected shape. We treat each large-enough
contour in the processed image as one vehicle.

**Q6. What is the role of Flask in this project?**
A: Flask is the backend web framework that serves the HTML pages, exposes REST API
routes (like `/api/detect`), receives uploaded images, runs the detection logic,
and returns JSON results to the frontend.

**Q7. What happens if two vehicles overlap in the image?**
A: They may be detected as a single larger contour, slightly under-counting in dense
traffic. This is a known limitation of contour-based detection and is mentioned in
our future-scope as a reason to upgrade to a deep-learning model like YOLO.

**Q8. Can this work with a live camera instead of uploaded photos?**
A: Yes — the same `detect_vehicles()` function works on any single image frame, so a
webcam feed can be sampled frame-by-frame and passed to it. We used image upload for
the exhibition demo for simplicity and reliability.

**Q9. What is stored in the database and why?**
A: Every detection (lane number, vehicle count, computed green time, density level,
and timestamp) is stored so we can show historical reports, calculate averages, and
prove the system is actually logging real data, not just displaying random numbers.

**Q10. How would you scale this to a real city?**
A: By connecting to live CCTV feeds at each junction, upgrading detection to a deep
learning model, deploying the Flask backend on a cloud server with a MySQL database,
and integrating with actual traffic light controller hardware via IoT.
