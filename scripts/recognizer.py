"""
recognizer.py

Real-time face recognition system using a webcam.
- Loads known faces from an SQLite database.
- Detects and recognizes faces in live video.
- Logs recognized users and allows new user registration.
"""

import cv2
import face_recognition
import numpy as np
import sqlite3
import os
import datetime
import re
# -----------------------------------
# Configuration Settings (easy to adjust for future changes)♾
# -----------------------------------
DATABASE_PATH = "faces.db"
LOG_FILE_PATH = "logs.txt"
CAMERA_INDEX = 1  # 1 = default webcam, 0, 2 = external webcam
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
TOLERANCE = 0.5  # Face recognition strictness
NEW_FACE_SAVE_DIR = "scripts/faces/"
FACE_BUFFER_SECONDS = 300  # Buffer to prevent duplicate logging (5 minutes)

# -----------------------------------
# Connect to the database
# -----------------------------------
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Ensure logs table exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

# -----------------------------------
# Functions
# -----------------------------------
def load_known_faces():
    """Load known face encodings and names from the database."""
    cursor.execute("SELECT name, encoding FROM faces")
    known_faces = []
    known_names = []
    for row in cursor.fetchall():
        name, encoding_bytes = row
        encoding = np.frombuffer(encoding_bytes, dtype=np.float64)
        known_faces.append(encoding)
        known_names.append(name)
    return known_faces, known_names

def log_recognition(name):
    """Log a recognized face with a timestamp."""
    timestamp = datetime.datetime.now()

    # Check if this person was already logged recently
    cursor.execute(
        "SELECT timestamp FROM logs WHERE name = ? ORDER BY timestamp DESC LIMIT 1", (name,)
    )
    last_entry = cursor.fetchone()

    if last_entry:
        last_time = datetime.datetime.strptime(last_entry[0], "%Y-%m-%d %H:%M:%S")
        if (timestamp - last_time).total_seconds() < FACE_BUFFER_SECONDS:
            return

    cursor.execute("INSERT INTO logs (name) VALUES (?)", (name,))
    conn.commit()

    with open(LOG_FILE_PATH, "a") as log_file:
        log_file.write(f"{timestamp} - {name} recognized\n")

    print(f"Logged {name} at {timestamp}")

# -----------------------------------
# Main Program
# -----------------------------------
known_faces, known_names = load_known_faces()

video_capture = cv2.VideoCapture(CAMERA_INDEX)
video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

while True:
    ret, frame = video_capture.read()
    if not ret:
        print("Failed to grab frame")
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    unknown_face_index = None  # <--- ADD THIS LINE

    for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_faces, face_encoding, tolerance=TOLERANCE)
        name = "Unknown"

        if True in matches:
            matched_index = matches.index(True)
            name = known_names[matched_index]
            log_recognition(name)
        else:
            cv2.putText(frame, "New face detected! Press 'n' to register", (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    cv2.imshow("Face Recognition System", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("n"):
        unknown_face_indices = [i for i, match in enumerate(matches) if not match]
        if unknown_face_indices:  # <-- Check if there is at least one unknown face
            unknown_face_index = unknown_face_indices[0]
            unknown_encoding = face_encodings[unknown_face_index]

            while True:
                user_name = input("Enter your name (letters only, max 20 characters): ").strip()


                if not user_name:
                    print("❌ Name cannot be empty. Please try again.")
                    continue

                if len(user_name) > 20:
                    print("❌ Name is too long. Please limit to 20 characters.")
                    continue
                
                if not re.fullmatch(r"[a-zA-Z0-9 _-]+", user_name):
                    print("❌ Name can only contain letters, numbers, spaces, underscores, and hyphens.")
                    continue

                user_name = user_name.title()  # Capitalize first letter of each word


                # Check if the name already exists in the database
                cursor.execute("SELECT COUNT(*) FROM faces WHERE name = ?", (user_name,))
                if cursor.fetchone()[0] > 0:
                    print(f"❌ The name '{user_name}' already exists. Please choose a different name.")
                    continue

                # Remove forbidden characters
                user_name = "".join(c for c in user_name if c.isalnum() or c in (" ", "_", "-")).rstrip()
                break  # Valid name!

            if not os.path.exists(NEW_FACE_SAVE_DIR):
                os.makedirs(NEW_FACE_SAVE_DIR)
            img_path = os.path.join(NEW_FACE_SAVE_DIR, f"{user_name}.jpg")
            cv2.imwrite(img_path, frame)

            encoding_bytes = np.array(unknown_encoding).tobytes()
            cursor.execute("INSERT INTO faces (name, encoding) VALUES (?, ?)", (user_name, encoding_bytes))
            conn.commit()
            print(f"✅ {user_name} added to database!")

            known_faces, known_names = load_known_faces()

    if key == ord("q"):
        break


# Cleanup
video_capture.release()
cv2.destroyAllWindows()
conn.close()
