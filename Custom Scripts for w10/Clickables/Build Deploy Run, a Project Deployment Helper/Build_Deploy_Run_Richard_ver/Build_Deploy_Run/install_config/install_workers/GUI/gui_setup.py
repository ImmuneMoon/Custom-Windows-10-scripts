# install_config/install_workers/GUI/gui_setup.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFile
from pathlib import Path
import logging
import inspect
from functools import partial

# Import GUI modules
from . import widgets
from . import callbacks
from .gui_utils import write_deploy_config

logger = logging.getLogger(__name__)
ImageFile.LOAD_TRUNCATED_IMAGES = True  # Failsafe for malformed PNGs

# --- Callback Wrapping ---

class CallbacksWrapper:
    def __init__(self, app_instance):
        self.app = app_instance
        for name, func in inspect.getmembers(callbacks, inspect.isfunction):
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())
            if params and params[0] in ('app', 'app_instance'):
                wrapped_func = partial(func, self.app)
                setattr(self, name, wrapped_func)
            elif name not in ('on_entry_focus_in', 'on_entry_focus_out'):
                setattr(self, name, func)

# --- Icon Setup ---

def setup_window_icon(app_instance):
    logger.debug("Setting up window icon...")
    try:
        icon_path = Path(app_instance.bdr_source_dir) / "assets" / "icon.ico"
        if icon_path.is_file():
            app_instance.root.iconbitmap(default=str(icon_path))
            logger.info(f"Window icon set from: {icon_path}")
        else:
            logger.warning(f"Window icon file not found: {icon_path}")
    except tk.TclError as e:
        logger.error(f"Failed to set .ico icon: {e}")
    except Exception as e:
        logger.error(f"Unexpected error setting icon.ico: {e}", exc_info=True)

def load_header_icon(app_instance):
    logger.debug("Loading header PNG icon...")
    app_instance.png_icon = None
    try:
        icon_path = Path(app_instance.bdr_source_dir) / "assets" / "icon.png"
        if icon_path.is_file():
            img = Image.open(icon_path)
            resized = img.resize(app_instance.icon_display_size, Image.Resampling.LANCZOS)
            app_instance.png_icon = ImageTk.PhotoImage(resized)
            logger.info(f"PNG icon loaded and resized: {icon_path}")
        else:
            logger.warning(f"icon.png not found: {icon_path}")
            logger.info("No icon.png found. Skipping header icon.")

    except Exception as e:
        logger.error(f"Failed to load or process icon.png: {e}", exc_info=True)

# --- Callbacks + Widget Setup ---

def setup_callbacks_wrapper(app_instance):
    try:
        app_instance.callbacks = CallbacksWrapper(app_instance)
        logger.debug("Callbacks wrapper attached.")
    except Exception as e:
        logger.critical(f"Could not initialize callbacks: {e}", exc_info=True)
        raise RuntimeError("Callback setup failed.")

def setup_ui_widgets(app_instance):
    logger.debug("Setting up GUI styles and widgets...")
    try:
        widgets.setup_styles()
    except Exception as e:
        logger.warning(f"Style setup failed: {e}", exc_info=True)

    try:
        widgets.create_all_widgets(app_instance)
    except Exception as e:
        logger.critical(f"Fatal error creating widgets: {e}", exc_info=True)
        try:
            messagebox.showerror("Widget Init Error", f"{e}")
        except: pass
        raise

    # Add optional post-install controls to final_frame if it exists
    try:
        # Expect run_after_install_var to be initialized in InstallerApp
        # Do nothing here
        if app_instance.final_frame:
            app_instance.run_after_checkbox = tk.Checkbutton(
                app_instance.final_frame,
                text="Run deployment after install",
                variable=app_instance.run_after_install_var
            )
            app_instance.run_after_checkbox.grid(row=2, column=0, sticky="w", padx=10, pady=5)
            logger.debug("Run-after-install checkbox added.")
        else:
            logger.warning("final_frame not found; checkbox not added.")
    except Exception as e:
        logger.error(f"Failed to add run-after-install checkbox: {e}", exc_info=True)

    try:
        if app_instance.final_frame:
            app_instance.save_config_button = tk.Button(
                app_instance.final_frame,
                text="Save Deploy Config",
                command=lambda: write_deploy_config(app_instance)
            )
            app_instance.save_config_button.grid(row=2, column=1, sticky="w", padx=10, pady=5)
            logger.debug("Save Deploy Config button added.")
        else:
            logger.warning("final_frame not found; Save Config button not added.")
    except Exception as e:
        logger.error(f"Failed to add Save Deploy Config button: {e}", exc_info=True)

    logger.debug("UI widgets setup completed.")
