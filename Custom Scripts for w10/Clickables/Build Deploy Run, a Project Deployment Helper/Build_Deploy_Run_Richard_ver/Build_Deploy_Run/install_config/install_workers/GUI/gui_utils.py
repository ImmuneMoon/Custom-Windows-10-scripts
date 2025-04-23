# install_config/install_workers/GUI/gui_utils.py

import subprocess, queue, logging, json
from pathlib import Path
import tkinter as tk

logger = logging.getLogger(__name__)


def log_to_queue(queue_obj, message, level=logging.INFO):
    """
    Enqueues a standardized (level, message) tuple for log processing.
    """
    try:
        queue_obj.put_nowait((level, str(message)))
    except Exception as e:
        logger.error(f"[QueueLogError] Failed to enqueue log: {e}")


def write_deploy_config(app_instance):
    """
    Write a deploy_config.json file into the user's project directory.
    Pulls paths and settings from app_instance variables.
    """
    try:
        target_path = Path(app_instance.target_project_dir_var.get())
        # Assuming config goes inside the BDR folder in target project
        config_path = target_path / "Build_Deploy_Run" / "deploy_config.json"

        deploy_config = {
            "entrypoint": app_instance.entrypoint_var.get(),
            "docker_path": app_instance.docker_path_var.get(),
            "xwindows_path": app_instance.xwindows_path_var.get(),
            "open_project": app_instance.open_project_var.get(),
        }

        # Ensure the target directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, 'w') as f:
            json.dump(deploy_config, f, indent=4)

        app_instance.log_message_action(f"[CONFIG] deploy_config.json written to: {config_path}", logging.INFO)

    except Exception as e:
        app_instance.log_message_action(f"[ERROR] Could not write deploy_config.json: {e}", logging.ERROR)
        logger.exception("Exception while writing deploy_config.json")


def log_message(app, message, level=logging.INFO):
    print(f"[DEBUG] log_message ENTERED with: Level={level}, Msg='{str(message)[:50]}...'") # Use str() for safety
    color_map = {
        logging.DEBUG:  ("gray", "🛠"),
        logging.INFO:   ("black", "ℹ️"),
        logging.WARNING:("orange", "⚠️"),
        logging.ERROR:  ("red", "❌"),
        logging.CRITICAL:("dark red", "💥")
    }

    tag_color, emoji = color_map.get(level, ("black", ""))
    # Ensure message is a string before stripping
    full_message = f"{emoji} {str(message).strip()}\n"

    if not hasattr(app, 'log_area') or app.log_area is None:
        print(f"[DEBUG] log_message: log_area not found, falling back to print: {full_message}")
        return

    try:
        print("[DEBUG] log_message: Configuring state NORMAL...")
        app.log_area.configure(state=tk.NORMAL)
        print("[DEBUG] log_message: Checking tags...")
        # Check tags exist before configuring - safer
        current_tags = app.log_area.tag_names()
        tags_to_configure = {"gray", "black", "orange", "red", "dark red"}
        if not tags_to_configure.issubset(current_tags):
             print("[DEBUG] log_message: Configuring tags...")
             app.log_area.tag_config("gray", foreground="gray")
             app.log_area.tag_config("black", foreground="black")
             app.log_area.tag_config("orange", foreground="orange")
             app.log_area.tag_config("red", foreground="red")
             app.log_area.tag_config("dark red", foreground="dark red")

        print(f"[DEBUG] log_message: Inserting text '{full_message.strip()}' with tag '{tag_color}'...")
        app.log_area.insert(tk.END, full_message, (tag_color,)) # Pass tag as a tuple
        print("[DEBUG] log_message: Scrolling...")
        app.log_area.see(tk.END)
        print("[DEBUG] log_message: Configuring state DISABLED...")
        app.log_area.configure(state=tk.DISABLED)
        print("[DEBUG] log_message: FINISHED update.")
    except Exception as e:
        print(f"[ERROR] log_message: EXCEPTION during widget update: {e}")
        # Fallback print if widget update fails
        print(f"[FALLBACK LOG] {full_message}")
        # Attempt to disable anyway if possible, might fail again
        try:
            if app.log_area: app.log_area.configure(state=tk.DISABLED)
        except:
            pass # Ignore secondary error


def start_queue_processing(app):
    print("[DEBUG] start_queue_processing ENTERED")

    def poll_log_queue():
        print("[DEBUG] poll_log_queue ENTERED")
        # FIX: Outer try was removed here
        processed_message = False
        while not app.log_queue.empty():
            processed_message = True
            print(f"[DEBUG] poll_log_queue found message in queue!")
            try: # Inner try/except handles processing errors
                data = app.log_queue.get_nowait()
                if isinstance(data, tuple):
                     if len(data) == 2:
                         level, msg = data
                         log_message(app, msg, level)
                     elif len(data) == 3: # Allow passing tag optionally
                         level, _tag, msg = data # Use _tag if tag not needed now
                         log_message(app, msg, level) # Ignoring tag for now
                     else:
                          # Log unexpected tuple format
                          print(f"[WARNING] poll_log_queue: Received unexpected tuple format: {data}")
                          log_message(app, str(data), logging.WARNING) # Log as string
                else:
                     # Log if data is not a tuple (e.g., just a string)
                     print(f"[WARNING] poll_log_queue: Received non-tuple data: {data}")
                     log_message(app, str(data), logging.INFO) # Log as string

            except queue.Empty:
                break # Exit while loop if queue becomes empty during processing
            except Exception as e:
                print(f"[ERROR] Error processing item from log queue: {e}")
                logger.error(f"Log queue item processing error: {e}")
        # End of the while loop

        if processed_message:
            try:
                print("[DEBUG] poll_log_queue: Calling app.root.update()")
                app.root.update() # Force update
            except Exception as e_update:
                print(f"[ERROR] Error calling app.root.update(): {e_update}")

        # Reschedule
        if app.root and app.root.winfo_exists():
            app.root.after(100, poll_log_queue)
        else:
            print("[DEBUG] poll_log_queue: Root window closed, not rescheduling.")


    print("[DEBUG] start_queue_processing: Making initial call to poll_log_queue.")
    poll_log_queue() # Initial call


# FIX: Ensure this function definition starts at column 0 (no indentation)
def run_subprocess_streamed(cmd, queue_obj, cwd=None, env=None):
    """Runs subprocess, streams stdout/stderr to queue."""
    try:
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, # Redirect stderr to stdout
            text=True,
            bufsize=1, # Line buffered
            encoding='utf-8', # Be explicit about encoding
            errors='replace'  # Handle potential decoding errors
        )
        # Log stdout line by line
        for line in process.stdout:
            log_to_queue(queue_obj, line.strip(), logging.INFO) # Pass level INFO

        process.wait() # Wait for process to complete
        if process.returncode != 0:
            # Log error with return code if process failed
            error_message = f"Subprocess failed with return code {process.returncode}: {' '.join(cmd)}"
            log_to_queue(queue_obj, error_message, logging.ERROR) # Pass level ERROR
            raise subprocess.CalledProcessError(process.returncode, cmd)

    except FileNotFoundError:
         error_message = f"Command not found: {cmd[0]}"
         log_to_queue(queue_obj, error_message, logging.CRITICAL)
         raise # Re-raise the exception
    except Exception as e:
         error_message = f"Error running subprocess {cmd[0]}: {e}"
         log_to_queue(queue_obj, error_message, logging.CRITICAL)
         raise # Re-raise the exception