"""
encoder.py

Face encoder utility to populate the SQLite database with known faces.
- Encodes face images from a folder.
- Stores the encodings along with names in the database.
"""

import sqlite3
import numpy as np
import face_recognition
import os
from config import DATABASE_PATH, FACES_DIR

# Connect to the database
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

def encode_face(image_path, name):
    """Encode a single face image and store it in the database.

    Args:
        image_path (str): Path to the image file.
        name (str): Name associated with the face.
    """
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    
    if not encodings:
        print(f"No faces found in {image_path}")
        return
    
    for encoding in encodings:  # Store multiple faces per image
        encoding_bytes = np.array(encoding).tobytes()
        cursor.execute("CREATE TABLE IF NOT EXISTS faces (name TEXT, encoding BLOB)")
        cursor.execute("INSERT INTO faces (name, encoding) VALUES (?, ?)", (name, encoding_bytes))
        conn.commit()
        print(f"Stored {name}'s face from {image_path} in database.")

def encode_faces_from_folder(folder_path, name):
    """Encode all face images in a folder for a specific person.

    Args:
        folder_path (str): Path to the folder containing images.
        name (str): Name to associate with all images in the folder.
    """
    for filename in os.listdir(folder_path):
        if filename.endswith((".jpg", ".png", ".jpeg", ".JPG", ".jpG")):
            image_path = os.path.join(folder_path, filename)
            encode_face(image_path, name)

# Example Usage: Encode multiple users
encode_faces_from_folder(os.path.join(FACES_DIR, "veeran"), "Veeran Reddy")
encode_faces_from_folder(os.path.join(FACES_DIR, "james"), "James Moyes")
encode_faces_from_folder(os.path.join(FACES_DIR, "noah"), "Noah Johnson")
encode_faces_from_folder(os.path.join(FACES_DIR, "hugh"), "Hugh Webber")

# Close the database connection
conn.close()
