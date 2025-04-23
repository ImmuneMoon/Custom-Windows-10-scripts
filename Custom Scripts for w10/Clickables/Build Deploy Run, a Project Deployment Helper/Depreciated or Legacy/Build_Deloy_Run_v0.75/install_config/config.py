import tkinter as tk
from tkinter import filedialog, messagebox
import json
from pathlib import Path
import subprocess
import os
import shutil
import sys
import winreg
import ctypes
try:
    import pyperclip
except ImportError:
    pyperclip = None
from shutil import copy2

# === Default values ===
default_config = {
    "vcxsrv_path": "C:/Program Files/VcXsrv/vcxsrv.exe",
    "docker_path": "C:/Program Files/Docker/Docker Desktop.exe",
    "project_dir": "C:/[INSERT MAIN PROJECT DIRECTORY]/"
}

def check_long_path_support():
    try:
        reg_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\FileSystem",
            0,
            winreg.KEY_READ
        )
        value, _ = winreg.QueryValueEx(reg_key, "LongPathsEnabled")
        winreg.CloseKey(reg_key)
        return value == 1
    except FileNotFoundError:
        return False
    except PermissionError:
        return False  # Can't access it = assume off (or warn later)


def maybe_warn_about_long_paths():
    if not check_long_path_support():
        if messagebox.askyesno(
            "Long Paths Disabled",
            "⚠️ Your system does not have long path support enabled.\n\n"
            "This can break package installs in deep folders (like venv).\n\n"
            "Do you want to try enabling it now? (Requires admin rights)"
        ):
            enable_long_paths_now()


def enable_long_paths_now():
    try:
        # Elevate via PowerShell
        script = (
            'Set-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\FileSystem" '
            '-Name "LongPathsEnabled" -Value 1'
        )
        subprocess.run([
            "powershell.exe",
            "-Command",
            f'Start-Process powershell -Verb runAs -ArgumentList \'-NoProfile -ExecutionPolicy Bypass -Command "{script}"\''
        ])
        messagebox.showinfo("Done", "✅ Long paths should now be enabled.\nPlease restart your computer to apply the change.")
    except Exception as e:
        messagebox.showerror("Failed", f"Could not enable long paths:\n{e}")


# === Resolve resource paths ===
def resource_path(relative_path):
    """ Get path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent

    return base_path / relative_path



# === File browsing helpers ===
def browse_file(entry):
    path = filedialog.askopenfilename()
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)


def browse_folder(entry):
    path = filedialog.askdirectory()
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)


# === Save user config ===
def save_config():

    entrypoint_val = entrypoint_entry.get().strip()
    if entrypoint_val == entry_placeholder:
        entrypoint_val = ""

    config = {
        "vcxsrv_path": vcxsrv_entry.get().strip(),
        "docker_path": docker_entry.get().strip(),
        "project_dir": project_entry.get().strip(),
        "entrypoint": entrypoint_val,
        "spec_file": "Super_Power_Options.spec"
    }


    target_dir = Path(config["project_dir"])    
    if not target_dir.exists():
        messagebox.showerror("Invalid Path", "Project directory does not exist.")
        return

    if save_mode.get() == "json":
        with open(target_dir / "user_config.json", "w") as f:
            json.dump(config, f, indent=2)
        print("[✓] user_config.json saved.")
    else:
        with open(target_dir / ".env", "w") as f:
            for k, v in config.items():
                f.write(f'{k.upper()}="{v}"\n')
        print("[✓] .env file saved.")

    # Also copy it into the project folder
    project_target = Path(config["project_dir"]) / "Build_Deploy_Run" / "user_config.json"
    project_target.parent.mkdir(parents=True, exist_ok=True)
    with open(project_target, "w") as f:
        json.dump(config, f, indent=2)

    if run_xlaunch_var.get():
        try:
            subprocess.Popen([config["vcxsrv_path"], ":0", "-multiwindow", "-clipboard", "-wgl", "-ac"])
            print("[✓] VcXsrv launched.")
        except Exception as e:
            messagebox.showerror("XLaunch Failed", str(e))


# === Instruction after saving ===
def show_instruction():
    exe_name = "Build Deploy Run.exe"
    bat_name = Path("build_and_deploy_venv_locked.bat")
    command = r".\Build_Deploy_Run\build_and_deploy_venv_locked.bat"

    clipboard_status = ""
    try:
        if pyperclip:
            pyperclip.copy(command)
            clipboard_status = "[✓] Command copied to clipboard (pyperclip)."
        else:
            raise ImportError("pyperclip not available")
    except Exception:
        # Fallback: Use Tkinter clipboard
        try:
            root.clipboard_clear()
            root.clipboard_append(command)
            root.update()  # Keeps it after app closes
            clipboard_status = "[✓] Command copied to clipboard (tkinter fallback)."
        except Exception as e:
            clipboard_status = f"[!] Clipboard copy failed: {e}"


    message = (
        "To build and deploy your project,\n"
        "run the following command in your terminal:\n\n"
        f"{command}\n\n"
        f"{clipboard_status}"
    )

    messagebox.showinfo("Build Deploy Run", message)
    root.after(4000, root.destroy)



# === Copy required files ===
def copy_files_to_project():
    target = Path(project_entry.get()).resolve()
    subfolder = target / "Build_Deploy_Run"
    subfolder.mkdir(exist_ok=True)

    files = [
        "build_and_deploy.py",
        "build_and_deploy_venv_locked.bat",
        "minimize_xwindows.ps1",
        "requirements-docker.txt",
        "requirements.txt"
    ]

    src_root = resource_path("")
    fallback_root = Path(__file__).parent

    for file in files:
        print(f"Looking for {file} in: {src_root}")
        src = src_root / file

        if src.exists():
            shutil.copy2(src, subfolder)
            print(f"[\u2192] Copied {file} to {subfolder}")
        else:
            alt_src = fallback_root / file
            if fallback_root != src_root and alt_src.exists():
                shutil.copy2(alt_src, subfolder)
                print(f"[\u2713] Fallback copy for {file}")
            else:
                print(f"[!] Missing file: {file}")

    # 🚚 Copy the workers/ folder recursively
    workers_src = src_root / "workers"
    workers_dst = subfolder / "workers"
    if workers_src.exists() and workers_src.is_dir():
        shutil.copytree(workers_src, workers_dst, dirs_exist_ok=True)
        print("[\u2713] workers/ module copied.")
    else:
        print("[!] workers/ folder not found.")




"""     # Also copy assets
    assets_src = Path(__file__).parent / "assets"
    assets_dst = subfolder / "assets"
    if assets_src.exists():
        shutil.copytree(assets_src, assets_dst, dirs_exist_ok=True)
        print("[✓] Assets copied.")
    else:
        print("[!] Assets folder not found.") """


# === Composite action ===
def save_and_notify():
        save_config()
        copy_files_to_project()
        show_instruction()

# === Longpath checks === #
check_long_path_support()
maybe_warn_about_long_paths()

# === UI setup ===
root = tk.Tk()
root.title("Build Deploy Run - Setup Wizard")
root.geometry("640x360")
root.configure(bg="black")

base_path = os.path.join(os.path.dirname(__file__), "..", "assets")
icon_path = os.path.join(base_path, "icon.ico")
if os.path.exists(icon_path):
    try:
        root.iconbitmap(default=icon_path)
    except:
        png_path = os.path.join(base_path, "icon.png")
        if os.path.exists(png_path):
            tk.PhotoImage(file=png_path)

padx = 10
pady = 5

# VcXsrv Path
tk.Label(root, text="VcXsrv Path:", bg="black", fg="white").grid(row=0, column=0, sticky="e", padx=padx, pady=pady)
vcxsrv_entry = tk.Entry(root, width=60)
vcxsrv_entry.insert(0, default_config["vcxsrv_path"])
vcxsrv_entry.grid(row=0, column=1, padx=padx, pady=pady)
tk.Button(root, text="Browse", command=lambda: browse_file(vcxsrv_entry)).grid(row=0, column=2, padx=padx, pady=pady)

# Docker Path
tk.Label(root, text="Docker Path:", bg="black", fg="white").grid(row=1, column=0, sticky="e", padx=padx, pady=pady)
docker_entry = tk.Entry(root, width=60)
docker_entry.insert(0, default_config["docker_path"])
docker_entry.grid(row=1, column=1, padx=padx, pady=pady)
tk.Button(root, text="Browse", command=lambda: browse_file(docker_entry)).grid(row=1, column=2, padx=padx, pady=pady)

# Project Folder
tk.Label(root, text="Project Folder:", bg="black", fg="white").grid(row=2, column=0, sticky="e", padx=padx, pady=pady)
project_entry = tk.Entry(root, width=60)
project_entry.insert(0, default_config["project_dir"])
project_entry.grid(row=2, column=1, padx=padx, pady=pady)
tk.Button(root, text="Browse", command=lambda: browse_folder(project_entry)).grid(row=2, column=2, padx=padx, pady=pady)

# Entrypoint Script with placeholder magic
tk.Label(root, text="Entrypoint Script:", bg="black", fg="white").grid(row=3, column=0, sticky="e", padx=padx, pady=pady)
entry_placeholder = "e.g. main.py or app.py"
entrypoint_entry = tk.Entry(root, width=60, fg="grey", bg="black", insertbackground="white")
entrypoint_entry.insert(0, entry_placeholder)

def clear_placeholder(_):
    if entrypoint_entry.get() == entry_placeholder:
        entrypoint_entry.delete(0, tk.END)
        entrypoint_entry.config(fg="white")

def restore_placeholder(_):
    if entrypoint_entry.get().strip() == "":
        entrypoint_entry.insert(0, entry_placeholder)
        entrypoint_entry.config(fg="grey")

entrypoint_entry.bind("<FocusIn>", clear_placeholder)
entrypoint_entry.bind("<FocusOut>", restore_placeholder)
entrypoint_entry.grid(row=3, column=1, padx=padx, pady=pady)

# Run XLaunch checkbox
run_xlaunch_var = tk.BooleanVar()
tk.Checkbutton(root, text="Run XLaunch after install", variable=run_xlaunch_var, bg="black", fg="lime").grid(row=4, column=1, sticky="w", padx=padx, pady=pady)

# JSON/ENV toggle
save_mode = tk.StringVar(value="json")
tk.Radiobutton(
    root,
    text="Save as JSON",
    variable=save_mode,
    value="json",
    bg="black",
    fg="white",
    selectcolor="black",           # keep consistent with bg
    activebackground="black",
    activeforeground="lime",
    highlightbackground="white",  # gives a visible outline
    highlightthickness=1,
    bd=1,
    indicatoron=1                 # make sure it's a circle not a toggle
).grid(row=5, column=1, sticky="w", padx=padx, pady=pady)

tk.Radiobutton(
    root,
    text="Save as .env",
    variable=save_mode,
    value="env",
    bg="black",
    fg="white",
    selectcolor="black",
    activebackground="black",
    activeforeground="lime",
    highlightbackground="white",
    highlightthickness=1,
    bd=1,
    indicatoron=1
).grid(row=5, column=1, sticky="e", padx=padx, pady=pady)

# Save button
tk.Button(root, text="\U0001F4BE  Install", command=save_and_notify, bg="lime", fg="black", width=20).grid(row=6, column=1, pady=20)

root.mainloop()


