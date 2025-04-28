"""
admin_panel.py

Web-based admin panel using NiceGUI for starting face recognition sessions.
- Allows input of user name and session duration.
- Starts and manages the recognition subprocess.
"""

from nicegui import ui
import subprocess
import threading
import time



process = None

def run_recognition(duration, name):
    global process
    end_time = time.time() + duration

    process = subprocess.Popen(["python", "recognizer.py"])

    while time.time() < end_time:
        time.sleep(1)

    if process:
        process.terminate()
        process = None

    ui.notify(f"Session ended for {name}", type='info')

def start_session(name, duration_minutes):
    if not name:
        ui.notify("Please enter a name", type='negative')
        return

    start_button.disable()
    thread = threading.Thread(target=run_recognition, args=(duration_minutes * 60, name))
    thread.start()

with ui.card().classes('w-96 m-auto mt-20'):
    ui.label('Face Recognition Admin Panel').classes('text-2xl font-bold mb-4')
    name_input = ui.input(label='Enter your name')

    duration_slider = ui.slider(min=1, max=60, value=5, step=1)
    duration_slider.label = 'Select run time (minutes)'

    start_button = ui.button('Start Recognition', 
                             on_click=lambda: start_session(name_input.value, duration_slider.value))

ui.run()
