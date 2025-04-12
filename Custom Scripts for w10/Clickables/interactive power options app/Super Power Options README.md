# **Super Power Options**

Super Power Options is a Python-based application that provides a user-friendly graphical interface (GUI) for scheduling power actions on Windows systems. Users can set a timer to trigger sleep, restart, or shutdown operations.  
**Functionality:**

* **Timed Power Actions:** Schedule sleep, restart, or shutdown after a specified delay.  
* **Flexible Time Input:** Enter a numerical value and select the time unit (seconds, minutes, hours, etc.) using a dropdown menu.  
* **Progress Visualization:** A progress bar visually displays the remaining time until the action is executed.  
* **Cancel Feature:** A "Cancel Timer" button allows users to abort the scheduled power action.  
* **User-Friendly Interface:** The application uses image buttons and tooltips for an intuitive experience.

**Technical Details:**

* **Implementation:** The application is written in Python and utilizes the tkinter library for the GUI.  
* **Bundling:** The included PyInstaller .spec file automates the process of creating a standalone executable. This ensures that all necessary files (including images and the application icon) are packaged correctly.  
* **PyInstaller Spec:** The spec file specifies the Python script (Power\_Options.py) as the main script, lists the data files to be included (images, icon), and configures the executable output.

**Usage:**

1. Run the script or the bundled executable.  
2. Enter the timer duration and select the time unit.  
3. Choose a power action (Sleep, Restart, Shutdown).  
4. Monitor the progress.  
5. Cancel the timer if needed.
6. As of the current ver, closing the program ends the countdown

This application simplifies the process of scheduling power actions, offering a more convenient and visual alternative to using command-line tools
