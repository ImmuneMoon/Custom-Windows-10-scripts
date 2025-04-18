import os
import sys
import subprocess
import tkinter as tk
from tkinter import Tk, ttk, Label, Entry, Button, PhotoImage, Canvas
import time  # Potentially needed for more precise timing

def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller bundle.
    try:
        # PyInstaller creates a temporary folder and stores path in _MEIPASS.
        base_path = sys._MEIPASS
        print(f"Running from bundle, base path: {base_path}")
    except Exception:
        base_path = os.path.abspath(".")
        print(f"Running as script, base path: {base_path}")

    full_path = os.path.join(base_path, relative_path)
    print(f"Resource path: {full_path}")
    return full_path

def calculate_seconds(value, unit):
    value = int(value)
    if unit == "seconds":
        return value
    elif unit == "minutes":
        return value * 60
    elif unit == "hours":
        return value * 3600
    elif unit == "days":
        return value * 86400
    elif unit == "weeks":
        return value * 604800
    elif unit == "months":  # Approximate as 30 days
        return value * 2592000
    elif unit == "years":   # Approximate as 365 days
        return value * 31536000
    elif unit == "centuries": # Approximate as 100 years
        return value * 3153600000
    elif unit == "millennia": # Approximate as 1000 years
        return value * 31536000000
    return value

# Global variables for timer and -- if added -- progress bar
# progress_bar = None  # Initialize progress_bar

root = tk.Tk()
remaining_time = 0
total_seconds = 0
timer_running = False
progress_text = None
initial_time = 0
power_option = "NONE"
task = "NONE" # To store the previous timer type
cancel_task = False
timer_value = 0

# -- Status label for feedback
status_label = Label(root, 
                     text="", 
                     fg="red",
                     font=("Verdana", 12, "bold"))
status_label.pack(pady=10)

# Function to handle the execution of each button press
def start_power_action(power_option, cancel_task):
    global remaining_time, timer_running, initial_time, task, status_label, total_seconds
    try:
        
        if cancel_task:
            root.after(1000, cancel_timer) # Execute after delay
        if task == "NONE":
            timer_value = int(timer_entry.get())
            if timer_value > 0:
                timer_unit = unit_combobox.get()
                total_seconds = calculate_seconds(timer_value, timer_unit)
                
            if total_seconds > 0:
                remaining_time = total_seconds
                initial_time = total_seconds
                timer_running = True
                update_progress_timer()  # Start updating the progress timer
                status_label.config(text=f"{power_option} timer started for {total_seconds} seconds.")
                if remaining_time == 0:
                    if power_option == "SLEEP":
                        root.after(total_seconds * 1000, set_sleep_timer_execute) # Execute after delay
                    elif power_option == "RESTART":
                        root.after(total_seconds * 1000, set_restart_timer_execute) # Execute after delay
                    elif power_option == "SHUTDOWN":
                        root.after(total_seconds * 1000, set_shutdown_timer_execute) # Execute after delay
            else:
                status_label.config(text="Please enter a positive timer value.", fg="white")
    except ValueError:
        status_label.config(text="Please enter a valid number.")
    
    task = power_option

def update_progress_timer():
    global remaining_time, timer_running, progress_text, initial_time
    if timer_running and initial_time > 0:
        progress_text.config(text=f"Time Left: {remaining_time} seconds")
        remaining_time -= 1
        if remaining_time >= 0 and timer_running:
            root.after(1000, update_progress_timer)
        elif remaining_time <= 0:
            timer_running = False
            status_label.config(text="Timer finished!", fg="white")

def cancel_timer():
    global timer_value, unit_combobox, timer_running, power_option, task, cancel_task, status_label, initial_time, remaining_time, total_seconds #, progress_bar
    timer_running = False
    progress_text.config(text="No Timer Set")
    task = "NONE"
    power_option = "NONE"
    initial_time = 0
    remaining_time = 0
    timer_entry.delete(0, tk.END)
    timer_entry.insert(0, 0)
    timer_value = 0
    status_label.config(text="Timer cancelled.",
                        font=("Verdana", 12, "bold"),
                        fg="white")
    cancel_task = False
    return cancel_task


# -- Function to execute a batch file for the sleep timer (now called after delay)
def set_sleep_timer_execute():
    subprocess.run("C:\\WINDOWS\\System32\\rundll32.exe PowrProf.dll,SetSuspendState 0,1,0", shell=True)
    status_label.config(text="Sleeping...")
    global timer_running
    timer_running = False

# -- Function to execute a batch file for the sleep timer (now called after delay)
def set_restart_timer_execute():
    subprocess.run("shutdown /r /t 0", shell=True)
    status_label.config(text="Restarting...",
                        font=("Verdana", 12),
                        fg="white")
    global timer_running
    timer_running = False

# -- Function to execute a batch file for the shutdown timer (now called after delay)
def set_shutdown_timer_execute():
    subprocess.run("shutdown /s /f /t 0", shell=True)
    status_label.config(text="Shutting down...")
    global timer_running
    timer_running = False


# -- Accessibility tooltips
class _ToolTips:
    def __init__(self, widget, text, master, delay=500):
        self.widget = widget
        self.text = text
        self.master = master
        self.tooltip_window = None
        self.delay = delay
        self.show_tooltip_id = None  # To store the after ID
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        self.show_tooltip_id = self.widget.after(self.delay, self.show_tooltip)

    def leave(self, event=None):
        if self.show_tooltip_id:
            self.widget.after_cancel(self.show_tooltip_id)
            self.show_tooltip_id = None
        self.hide_tooltip()

    def show_tooltip(self, event=None):
        self.show_tooltip_id = None # Reset the ID after showing
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip_window = tk.Toplevel(self.master)
        self.tooltip_window.wm_overrideredirect(True)
        label = Label(self.tooltip_window, text=self.text, background="#FFFFE0", relief="solid", borderwidth=1)
        label.pack()
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

# -- Set up the GUI
root.config(bg="darkgrey")
root.title("Super Power Options")

# -- Styles
style = ttk.Style()
style.theme_use("default")

# Get screen size
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set window size to 42% screen size
target_size = int(min(screen_width, screen_height) * 0.42)
window_width = target_size
window_height = target_size

# Set Window Position
pos_x = (screen_width - window_width) // 2
pos_y = (screen_height - window_height) // 2

# Assign root size
root.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")
root.resizable(False, False)

# -- Images
# Set Paths
sleep_button_path = resource_path("Sleep_Button.png")
restart_button_path = resource_path("Restart_Button.png")
shutdown_button_path = resource_path("Power_Button.png")
cancel_button_path = resource_path("Cancel_Button.png")

# Load and assign images directly within the button creation scope
sleep_timer_img = PhotoImage(file=sleep_button_path)
restart_timer_img = PhotoImage(file=restart_button_path)
shutdown_timer_img = PhotoImage(file=shutdown_button_path)
cancel_timer_img = PhotoImage(file=cancel_button_path)

# -- Instructions and timer input field
Label(
      root, 
      text="Timer Length:",
      font=("Verdana", 12, "bold"),
      fg="white").pack(padx=10, pady=5)
timer_entry = Entry(root, 
                    width=10,
                    font=("Verdana", 12, "bold"),
                    fg="white", 
                    bg="#4CAF50")
timer_entry.insert(0, 0)
timer_entry.pack(padx=7, pady=7)

# -- Unit selection dropdown
Label(root, 
      text="Timespan:",
      font=("Verdana", 12, "bold"),
      fg="white",
      bg="#4CAF50").pack(padx=10, pady=5)
unit_options = ["seconds", "minutes", "hours", "days", "weeks", "months", "years", "centuries", "millennia"]
style.configure("CustomCombobox.TCombobox",
                foreground="white",
                background="#4CAF50",
                fieldbackground="#4CAF50",
                font=("Verdana", 12, "bold"))

unit_combobox = ttk.Combobox(root, 
                             values=unit_options, 
                             state="readonly", 
                             width=10,
                             style="CustomCombobox.TCombobox")

unit_combobox.set("seconds")  # Default unit
unit_combobox.pack(pady=5)

# -- Buttons
button_frame = ttk.Frame(root)
button_frame.pack(expand=True)

# Sleep Button
sleep_button = Button(button_frame, 
                      image=sleep_timer_img, 
                      command=lambda: start_power_action("SLEEP", cancel_task))
sleep_button.pack(side="left", 
                  padx=20, 
                  pady=20)
sleep_tooltip = "Set Sleep Timer"
_ToolTips(sleep_button, sleep_tooltip, root)

# Shutdown Button
shutdown_button = Button(button_frame, 
                         image=shutdown_timer_img, 
                         command=lambda: start_power_action("SHUTDOWN", cancel_task))
shutdown_button.pack(side="left", padx=20, pady=20)
shutdown_tooltip = "Set Shutdown Timer"
_ToolTips(shutdown_button, 
          shutdown_tooltip, 
          root)

# Restart Button
restart_button = Button(button_frame, 
                        image=restart_timer_img, 
                        command=lambda: start_power_action("RESTART", cancel_task))
restart_button.pack(side="left", 
                    padx=20, 
                    pady=20)
restart_tooltip = "Set Restart Timer"
_ToolTips(restart_button, 
          restart_tooltip, 
          root)

# Cancel Button
cancel_button = Button(root, 
                       image=cancel_timer_img, 
                       command=lambda: start_power_action(power_option, True))
cancel_button.pack(side="top", 
                   padx=20, 
                   pady=20)
cancel_tooltip = "Cancel Timer"
_ToolTips(cancel_button, 
          cancel_tooltip, 
          root)

# -- Timer Progress Canvas
progress_canvas = Canvas(root, height=30)
progress_canvas.pack(fill="x", 
                     side="bottom", 
                     padx=5, 
                     pady=5)

progress_text = Label(progress_canvas, 
                      text="No Timer Set",
                      font=("Verdana", 12, "bold"),
                      fg="white",
                      bg="#4CAF50")
progress_text.place(relx=0.5, 
                    rely=0.5, 
                    anchor="center")

# -- Get the absolute path for icon.png
app_icon_path = resource_path("icon.png")
icon_img = PhotoImage(file=app_icon_path)
root.iconphoto(True, icon_img)
root.mainloop()

#### ---- Experimental

# Function to update a visible progress bar at the bottom of the window
# def update_progress_bar():
#     global remaining_time, timer_running, progress_text, initial_time # progress_bar
#     if timer_running and initial_time > 0:
#         progress = (initial_time - remaining_time) / initial_time
#         full_width = int(root.winfo_width() * 0.9) # 90% of window width
#         current_width = int((1 - progress) * full_width) # Calculate remaining width
#         canvas_width = root.winfo_width()
#         start_x = (canvas_width - current_width) // 2
#         end_x = start_x + current_width
#         progress_bar.coords(progress_rect, start_x, 5, end_x, 25)
#         progress_text.config(text=f"Time Left: {remaining_time} seconds")
#         remaining_time -= 1
#         if remaining_time >= 0 and timer_running:
#             root.after(1000, update_progress_bar)
#         elif remaining_time < 0:
#             timer_running = False
#             status_label.config(text="Timer finished!")
#     elif initial_time == 0:
#         progress_bar.coords(progress_rect, 0, 5, 0, 25) # Potential error here too



# Function to cancel timer, but for if theres a progress bar
# def cancel_timer():
#     global timer_running, scheduled_action, status_label #, progress_bar
#     if timer_running and scheduled_action:
#         root.after_cancel(scheduled_action)
#         timer_running = False
#         scheduled_action = None
#         status_label.config(text="Timer cancelled.")
#         # Optionally reset the progress bar
#         if progress_bar:
#             canvas_width = root.winfo_width()
#             progress_bar.coords(progress_rect, canvas_width // 2 - 1, 5, canvas_width // 2 + 1, 25)
#             progress_text.config(text="Timer Cancelled")


# -- Progress Bar Canvas
# progress_rect = progress_canvas.create_rectangle(0, 5, 0, 25, fill="lightblue")
# progress_bar = progress_rect  # Assign the rectangle to the global progress_bar


# Function to execute a batch file for the hibernate timer
#def set_hibernate_timer():
#    try:
#        timer_value = int(timer_entry.get())
#        with open("temp_set_hibernate_timer.bat", "w") as bat_file:
#            bat_file.write(f"@echo off\n")
#            bat_file.write(f"timeout /t {timer_value} /nobreak > nul\n")
#            bat_file.write("powercfg.exe /hibernate on\n") # Turn on Hibernation
#            bat_file.write(f"shutdown /h /t 0\n")
#            bat_file.write("exit\n")
#        subprocess.run("temp_set_hibernate_timer.bat", shell=True)
#        os.remove("temp_set_hibernate_timer.bat")  # Clean up
#    except ValueError:
#        status_label.config(text="Please enter a valid number!")
##############
# Not meant to be used unless on a HDD. Not generally advised to use, only here as a practice
# If you wish to use it, include this line with the rest of the buttons below and uncomment the code:
#   Button(root, text="Set Hibernate Timer", command=set_hibernate_timer).pack(pady=20)
# USE AT YOUR OWN RISK
##############