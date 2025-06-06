"""
admin_panel.py

Web-based admin panel using NiceGUI for starting face recognition sessions.
"""

from nicegui import ui, app
import asyncio
import cv2
import base64
import numpy as np
from recognizer import FaceRecognizer

class FaceRecognitionApp:
    def __init__(self):
        self.running = False
        self.recognizer = None
        self.frame_update_task = None
        self.webcam_image = None
        self.update_interval = 0.066  # Reduced to ~15 FPS for stability

    def encode_image(self, frame):
        _, buffer = cv2.imencode('.jpg', frame)
        return 'data:image/jpeg;base64,' + base64.b64encode(buffer).decode('utf-8')

    async def update_frame(self):
        """Continuously update the video frame"""
        try:
            while self.running and self.recognizer:
                frame = self.recognizer.process_frame()
                if frame is not None:
                    img_data = self.encode_image(frame)
                    if img_data and self.webcam_image:
                        self.webcam_image.source = img_data
                        await asyncio.sleep(self.update_interval)
        except Exception as e:
            print(f"Error updating frame: {e}")
        finally:
            print("Frame update loop ended")

    async def start_recognition(self, name: str, duration: int):
        """Start the recognition process"""
        if not name:
            ui.notify('Please enter a name', type='warning')
            return

        try:
            # Initialize recognition
            self.recognizer = FaceRecognizer()
            self.recognizer.start()
            self.running = True
            
            # Update UI state
            self.start_button.disable()
            self.stop_button.enable()
            
            # Start frame updates
            self.frame_update_task = asyncio.create_task(self.update_frame())
            
            # Wait for duration
            await asyncio.sleep(duration * 60)
            
        except Exception as e:
            print(f"Error in recognition: {e}")
        finally:
            await self.stop_recognition()

    async def stop_recognition(self):
        """Stop the recognition process"""
        self.running = False
        
        if self.frame_update_task and not self.frame_update_task.done():
            self.frame_update_task.cancel()
            try:
                await self.frame_update_task
            except asyncio.CancelledError:
                pass

        if self.recognizer:
            try:
                self.recognizer.stop()
            except Exception as e:
                print(f"Error stopping recognizer: {e}")
            self.recognizer = None

        # Reset UI state
        self.start_button.enable()
        self.stop_button.disable()
        if self.webcam_image:
            self.webcam_image.source = ''

    def setup_ui(self):
        """Setup the UI components"""
        with ui.card().classes('w-96 m-auto mt-10'):
            ui.label('Face Recognition Admin Panel').classes('text-2xl font-bold mb-4')
            self.name_input = ui.input(label='Enter your name')
            self.duration_slider = ui.slider(min=1, max=60, value=5, step=1)
            self.duration_slider.label = 'Select run time (minutes)'
            
            with ui.row():
                self.start_button = ui.button(
                    'Start Recognition',
                    on_click=lambda: asyncio.create_task(
                        self.start_recognition(
                            self.name_input.value,
                            self.duration_slider.value
                        )
                    )
                )
                self.stop_button = ui.button(
                    'Stop Recognition',
                    on_click=lambda: asyncio.create_task(self.stop_recognition())
                ).props('outline')
                self.stop_button.disable()

        self.webcam_image = ui.image().classes('w-full mt-6').style('max-width: 640px')

# Create and setup the application
face_recognition_app = FaceRecognitionApp()
face_recognition_app.setup_ui()

# Cleanup on disconnect
@app.on_disconnect
async def on_disconnect():
    await face_recognition_app.stop_recognition()

# Handle shutdown
@app.on_shutdown
def on_shutdown():
    asyncio.create_task(face_recognition_app.stop_recognition())

ui.run(
    title='Face Recognition System',
    reload=False,
    show=True,
    port=8080,
    dark=True
)
