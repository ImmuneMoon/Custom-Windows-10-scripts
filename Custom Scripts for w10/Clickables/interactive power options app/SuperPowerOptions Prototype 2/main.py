# main.py
# This file launches the tkinter GUI app. That’s it. It's the bouncer for PowerApp.
# Entry point. Instantiates and runs the GUI.

# Import the main application class from the UI module
from PowerApp.PowerUI import PowerApp

# Check if this script is being run directly (not imported as a module)
if __name__ == '__main__':
    # 🔧 Instantiate the PowerApp:
    # Creates the main window, sets up UI, loads images, and hooks into the logic backend
    app = PowerApp()

    # 🚀 Start the application loop:
    # Keeps the window open, listens for user input, and handles events
    app.run()

