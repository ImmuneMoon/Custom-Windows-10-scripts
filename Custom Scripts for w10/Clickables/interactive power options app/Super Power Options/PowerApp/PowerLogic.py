# PowerLogic.py
# Handles all the backend timer logic, system power commands, and triggering the doom (aka sleep/restart/shutdown)
# Manages timer execution, threading, and system-level power actions.

import os
import time
import threading
import platform
import subprocess

class PowerManager:
    def __init__(self, app):
        self.app = app  # Reference to the UI for callback updates, so we can update the display from here
        self.timer_seconds = 0
        self.cancel_flag = False  # Used to bail out of countdown if user cancels
        self.action = None  # What are we doing? Action to perform: 'sleep', 'restart', or 'shutdown'
        self.thread = None  # Thread that runs the countdown so we don’t freeze the UI

    def set_action(self, action):
        self.action = action  # Store the desired action

    def set_timer(self, seconds):
        self.timer_seconds = seconds
        self.cancel_flag = False  # Reset cancel flag for a fresh countdown

    def start_countdown(self):
        # Avoid stacking multiple threads
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self._countdown_loop)
        self.thread.start()

    def _countdown_loop(self):
        # This loop runs inside a thread
        remaining = self.timer_seconds
        while remaining > 0 and not self.cancel_flag:
            self.app.update_timer_display(remaining)
            time.sleep(1)
            remaining -= 1
        if not self.cancel_flag:
            self.app.update_timer_display(0)
            self._play_sound()  # Ding dong, time’s up
            self.execute_action()  # Trigger the system-level event

    def cancel(self):
        self.cancel_flag = True  # Abort countdown execution. User said "Wait I played games instead of doing my homework, I've actually gotta be up all night now"
        self.app.update_timer_display("Cancelled")

    def execute_action(self):
        # System calls for each power state. Windows-only.
        if self.action == 'sleep':
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        elif self.action == 'restart':
            os.system("shutdown /r /t 0")
        elif self.action == 'shutdown':
            os.system("shutdown /s /t 0")

    def _play_sound(self):
        # Attempts to play an alert sound cross-platform
        sound_path = os.path.join(os.path.dirname(__file__), "..", "assets", "alert.wav")
        if platform.system() == "Windows":
            import winsound
            winsound.PlaySound(sound_path, winsound.SND_FILENAME)
        else:
            subprocess.call(["aplay", sound_path])
