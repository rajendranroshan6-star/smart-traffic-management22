"""
vehicle_detection.py
---------------------
Core "AI / Computer Vision" module of the project.

It analyzes a lane image (photo/frame of a road) and estimates the
number of vehicles present using classical image-processing techniques:

    1. Convert image to grayscale
    2. Blur to remove noise
    3. Adaptive threshold to separate vehicles (dark/solid shapes)
       from the road surface
    4. Morphological operations to clean up small noise blobs
    5. Contour detection -> each sufficiently large contour is
       treated as one detected vehicle

This approach does not need any pretrained deep-learning model,
so it installs and runs instantly on any Windows laptop for a
live exhibition demo, while still genuinely being real computer
vision (not a random number generator).
"""

import cv2
import numpy as np

# Minimum contour area (in pixels) to be counted as a vehicle.
# Tune this value based on the image resolution used in the demo.
MIN_VEHICLE_AREA = 1200


def detect_vehicles(image_path):
    """
    Detect vehicles in the given image.

    Returns:
        vehicle_count (int)
        annotated_image (numpy array) - original image with boxes drawn
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Could not read the uploaded image. Please upload a valid JPG/PNG file.")

    # Resize for consistent processing speed/accuracy
    image = cv2.resize(image, (640, 480))
    output = image.copy()

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Adaptive threshold works well for varying lighting in road photos
    thresh = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        21, 5
    )

    # Morphological closing to merge nearby edges of the same vehicle
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    morphed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    morphed = cv2.dilate(morphed, kernel, iterations=1)

    contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    vehicle_count = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > MIN_VEHICLE_AREA:
            vehicle_count += 1
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(output, "Vehicle", (x, y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    return vehicle_count, output


def calculate_green_signal_time(vehicle_count, min_time=10, max_time=60, per_vehicle_seconds=3):
    """
    Calculate the recommended green signal duration based on vehicle density.

    Formula:
        green_time = min_time + (vehicle_count * per_vehicle_seconds)
        capped between min_time and max_time

    This is the core "smart" decision logic of the system -
    lanes with more vehicles automatically get a longer green signal.
    """
    green_time = min_time + (vehicle_count * per_vehicle_seconds)
    green_time = max(min_time, min(green_time, max_time))
    return int(green_time)


def get_density_level(vehicle_count):
    """Classify traffic density into a human-readable label."""
    if vehicle_count <= 3:
        return "Low"
    elif vehicle_count <= 8:
        return "Medium"
    else:
        return "High"
