"""Configuration settings for the face recognition system"""

import os

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "faces.db")
LOG_FILE_PATH = os.path.join(BASE_DIR, "logs.txt")
FACES_DIR = os.path.join(BASE_DIR, "scripts", "faces")

# Recognition settings
CAMERA_INDEX = 1  # Changed to 0 for built-in webcam
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
TOLERANCE = 0.5
FACE_BUFFER_SECONDS = 300