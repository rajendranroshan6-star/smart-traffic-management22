"""
database.py
------------
Handles all SQLite database operations for the
AI-Based Smart Traffic Management System.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "traffic.db")


def get_connection():
    """Create and return a new SQLite connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the required tables if they do not already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS traffic_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            junction_name TEXT NOT NULL,
            lane_number INTEGER NOT NULL,
            vehicle_count INTEGER NOT NULL,
            green_time INTEGER NOT NULL,
            density_level TEXT NOT NULL,
            image_name TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signal_cycles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            junction_name TEXT NOT NULL,
            total_vehicles INTEGER NOT NULL,
            total_cycle_time INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def insert_log(junction_name, lane_number, vehicle_count, green_time, density_level, image_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO traffic_logs
        (junction_name, lane_number, vehicle_count, green_time, density_level, image_name)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (junction_name, lane_number, vehicle_count, green_time, density_level, image_name))
    conn.commit()
    log_id = cursor.lastrowid
    conn.close()
    return log_id


def insert_cycle(junction_name, total_vehicles, total_cycle_time):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO signal_cycles (junction_name, total_vehicles, total_cycle_time)
        VALUES (?, ?, ?)
    """, (junction_name, total_vehicles, total_cycle_time))
    conn.commit()
    conn.close()


def get_all_logs(limit=100):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM traffic_logs
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_stats():
    """Return summary statistics used on the dashboard/history page."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM traffic_logs")
    total_scans = cursor.fetchone()["total"]

    cursor.execute("SELECT COALESCE(SUM(vehicle_count),0) as total_vehicles FROM traffic_logs")
    total_vehicles = cursor.fetchone()["total_vehicles"]

    cursor.execute("""
        SELECT lane_number, AVG(vehicle_count) as avg_count
        FROM traffic_logs
        GROUP BY lane_number
        ORDER BY lane_number
    """)
    per_lane = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return {
        "total_scans": total_scans,
        "total_vehicles": total_vehicles,
        "per_lane": per_lane
    }


def clear_logs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM traffic_logs")
    cursor.execute("DELETE FROM signal_cycles")
    conn.commit()
    conn.close()
