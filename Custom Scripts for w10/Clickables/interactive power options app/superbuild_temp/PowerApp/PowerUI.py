# PowerUI.py
# GUI layer: handles user interaction and visual state.
# This is where all the clicky, shiny, user-facing magic happens using tkinter.

import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk, PhotoImage
from PowerApp.PowerLogic import PowerManager
from pystray import Icon, MenuItem as item, Menu
from PIL import Image


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)

class PowerApp:

    # Initialize the display window, handle clicks, and run timer logic
    def __init__(self):
        self.root = tk.Tk() # Main application window
        self.root.title("⚡ Super Power Options ⚡")
        self.root.geometry("600x500")
        self.root.configure(bg="#1e1e1e")  # Dark mode by default
        self.manager = PowerManager(self) # Instantiates logic handler, where the timer lives and the actual power commands run
        self.load_images() # Custom method to preload icons and button images, avoids loading delays mid-interaction
        self.build_ui() # Where widgets are linked and placed
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray) # For hiding the app in a tray. On clicking the ❌, minimizes to system tray

    def hide_to_tray(self):
        self.root.withdraw()  # Hide window

        if os.getenv("DISABLE_TRAY") == "1":
            print("[*] Tray icon disabled via environment.")
            return

        icon_image = Image.open(resource_path("assets/icon.ico"))

        self.tray_icon = Icon(
            "SuperPowerOptions",
            icon_image,
            menu=Menu(
                item("Restore", lambda: self.restore_window()),
                item("Exit", lambda: self.exit_app())
            )
        )

        self.tray_icon.run_detached()


    def restore_window(self):
        self.root.deiconify()
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()

    def exit_app(self):
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()
        self.root.quit()

    def load_images(self):
        # Preload UI button images from the assets folder
        base_path = os.path.join(os.path.dirname(__file__), "..", "assets")
        self.img_sleep = PhotoImage(file=os.path.join(base_path, "Sleep_Button.png"))
        self.img_restart = PhotoImage(file=os.path.join(base_path, "Restart_Button.png"))
        self.img_shutdown = PhotoImage(file=os.path.join(base_path, "Shutdown_Button.png"))
        self.img_cancel = PhotoImage(file=os.path.join(base_path, "Cancel_Button.png"))
        self.img_icon = PhotoImage(file=os.path.join(base_path, "icon.png"))
        

        app_icon_path = resource_path("assets/icon.ico")

        if os.path.exists(app_icon_path):
            try:
                self.root.iconbitmap(app_icon_path)
            except Exception as e:
                print(f"[WARN] Failed to load icon: {e}")
        else:
            print("[WARN] icon.ico not found at runtime")



    def build_ui(self):
        # Set up styles for labels and buttons
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TLabel", background="#1e1e1e", foreground="white", font=("Verdana", 10))
        style.configure("TButton", font=("Verdana", 10, "bold"))

        # Timer input
        tk.Label(self.root, text="Timer Value:").pack(pady=5)
        self.time_entry = tk.Entry(self.root, font=("Verdana", 12), bg="#333", fg="white", justify="center")
        self.time_entry.pack(pady=5)

        # Time unit selector
        tk.Label(self.root, text="Time Unit:").pack(pady=5)
        self.unit_combobox = ttk.Combobox(self.root, values=[
            "seconds", "minutes", "hours", "days", "weeks", "months", "years", "centuries", "millennia"
        ])
        self.unit_combobox.set("seconds")
        self.unit_combobox.pack(pady=5)

        # Action buttons
        button_frame = tk.Frame(self.root, bg="#1e1e1e")
        button_frame.pack(pady=20)

        btn_sleep = tk.Button(button_frame, image=self.img_sleep, command=lambda: self.confirm_and_start('sleep'))
        btn_sleep.grid(row=0, column=0, padx=10)
        ToolTip(btn_sleep, "Put the system to sleep", self.root)

        btn_restart = tk.Button(button_frame, image=self.img_restart, command=lambda: self.confirm_and_start('restart'))
        btn_restart.grid(row=0, column=1, padx=10)
        ToolTip(btn_restart, "Restart the system", self.root)

        btn_shutdown = tk.Button(button_frame, image=self.img_shutdown, command=lambda: self.confirm_and_start('shutdown'))
        btn_shutdown.grid(row=0, column=2, padx=10)
        ToolTip(btn_shutdown, "Shut down the system", self.root)

        btn_cancel = tk.Button(self.root, image=self.img_cancel, command=self.cancel_timer)
        btn_cancel.pack(pady=10)
        ToolTip(btn_cancel, "Cancel the current timer", self.root)

        # Countdown display
        self.timer_label = tk.Label(self.root, text="", fg="white", bg="#1e1e1e", font=("Verdana", 12, "bold"))
        self.timer_label.pack(pady=5)

        self.status_label = tk.Label(self.root, text="No Timer Set", fg="gray", bg="#1e1e1e", font=("Courier New", 10))
        self.status_label.pack(pady=5)


    def confirm_and_start(self, action):
        # Prompt user to confirm before executing power action.
        if messagebox.askokcancel("Confirm", f"Really {action} the system?"):
            self.manager.set_action(action)
            self.start_timer()

    def start_timer(self):
        # Parse timer input and convert units to seconds
        try:
            value = int(self.time_entry.get())
            if value == 1337:
                self.timer_label.config(text="⚠️ DEV MODE ENABLED ⚠️")  # 👀
            unit = self.unit_combobox.get()
            sec = 1
            multiplier = {
                "seconds": sec,
                "minutes": sec * 60,
                "hours": sec * 3600,
                "days": sec * 86400,
                "weeks": sec * 604800,
                "months": sec * 2592000,
                "years": sec * 31536000,
                "centuries": sec * 3153600000,
                "millennia": sec * 31536000000
            }.get(unit, 1)
            seconds = value * multiplier
            if seconds <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number.")
            return

        self.manager.set_timer(seconds)
        self.manager.start_countdown()
        self.update_timer_display(seconds)

    def cancel_timer(self):
        self.manager.cancel()

    def update_timer_display(self, remaining):
        if isinstance(remaining, int):
            self.timer_label.config(text=f"Time Left: {remaining} seconds")
            self.status_label.config(text="")  # Clear status if numeric update
        else:
            # Show status (cancelled, etc.)
            self.status_label.config(text=str(remaining))
            self.timer_label.config(text="")  # Clear timer if status message


    def run(self):
        self.root.mainloop()

# -- Tooltip class for hover descriptions --
class ToolTip:
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
        label = tk.Label(self.tooltip_window, text=self.text, background="#FFFFE0", relief="solid", borderwidth=1)
        label.pack()
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None