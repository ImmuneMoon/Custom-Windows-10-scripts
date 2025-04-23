import tkinter as tk
from tkinter import filedialog, messagebox
import json
from pathlib import Path
import subprocess
import os
import shutil
import sys
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


# === Resolve resource paths ===
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)


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

    config = {
        "vcxsrv_path": vcxsrv_entry.get(),
        "docker_path": docker_entry.get(),
        "project_dir": project_entry.get(),
        "entrypoint": entrypoint_entry.get()
    }
    target_dir = Path(config["project_dir"])

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
    msg = (
        "To build and deploy your project,\n"
        "run the following command in your terminal:\n\n"
        ".\\Build_Deploy_Run\\build_and_deploy_venv_locked.bat"
    )
    if pyperclip:
        try:
            pyperclip.copy(".\\Build_Deploy_Run\\build_and_deploy_venv_locked.bat")
        except:
            pass

    messagebox.showinfo("Build Deploy Run", msg)
    root.after(3000, root.destroy)


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
        "requirements.txt",
        "requirements-bootstrap.txt"
    ]

    # 🔁 This is now done once, not 5x
    src_root = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))
    fallback_root = Path(__file__).parent

    for file in files:
        print(f"Looking for {file} in: {src_root}")
        src = src_root / file

        if src.exists():
            shutil.copy2(src, subfolder)
            print(f"[→] Copied {file} to {subfolder}")
        else:
            alt_src = fallback_root / file
            if fallback_root != src_root and alt_src.exists():
                shutil.copy2(alt_src, subfolder)
                print(f"[✓] Fallback copy for {file}")
            else:
                print(f"[!] Missing file: {file}")



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


# === UI setup ===
root = tk.Tk()
root.title("Build Deploy Run - Setup Wizard")
root.geometry("640x300")
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

# VcXsrv Path
vcxsrv_entry = tk.Entry(root, width=60)
tk.Label(root, text="VcXsrv Path:", bg="black", fg="white").grid(row=0, column=0, sticky="e")
vcxsrv_entry.insert(0, default_config["vcxsrv_path"])
vcxsrv_entry.grid(row=0, column=1)
tk.Button(root, text="Browse", command=lambda: browse_file(vcxsrv_entry)).grid(row=0, column=2)

# Docker Path
docker_entry = tk.Entry(root, width=60)
tk.Label(root, text="Docker Path:", bg="black", fg="white").grid(row=1, column=0, sticky="e")
docker_entry.insert(0, default_config["docker_path"])
docker_entry.grid(row=1, column=1)
tk.Button(root, text="Browse", command=lambda: browse_file(docker_entry)).grid(row=1, column=2)

# Project Folder
project_entry = tk.Entry(root, width=60)
tk.Label(root, text="Project Folder:", bg="black", fg="white").grid(row=2, column=0, sticky="e")
project_entry.insert(0, default_config["project_dir"])
project_entry.grid(row=2, column=1)
tk.Button(root, text="Browse", command=lambda: browse_folder(project_entry)).grid(row=2, column=2)

# Entrypoint
tk.Label(root, text="Entrypoint Script:", bg="black", fg="white").grid(row=3, column=0, sticky="e")
entrypoint_entry = tk.Entry(root, width=60)
entrypoint_entry.insert(0, "main.py")  # default
entrypoint_entry.grid(row=3, column=1)


# Run XLaunch checkbox
run_xlaunch_var = tk.BooleanVar()
tk.Checkbutton(root, text="Run XLaunch now after save", variable=run_xlaunch_var, bg="black", fg="lime").grid(row=3, column=1, sticky="w")

# JSON/ENV toggle
save_mode = tk.StringVar(value="json")
tk.Radiobutton(root, text="Save as JSON", variable=save_mode, value="json", bg="black", fg="white").grid(row=4, column=1, sticky="w")
tk.Radiobutton(root, text="Save as .env", variable=save_mode, value="env", bg="black", fg="white").grid(row=4, column=1, sticky="e")

# Save button
tk.Button(root, text="\U0001F4BE Install", command=save_and_notify, bg="lime", fg="black", width=20).grid(row=5, column=1, pady=10)

root.mainloop()
