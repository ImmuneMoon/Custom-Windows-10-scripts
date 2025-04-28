import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
from pathlib import Path
from install_workers.install_core import run_installer
from install_workers.utils import resource_path
from PIL import Image, ImageTk

# === Load Default Config ===
def load_default_config():
    default = {
        "vcxsrv_path": "C:/Program Files/VcXsrv/vcxsrv.exe",
        "docker_path": "C:/Program Files/Docker/Docker/Docker Desktop.exe",
        "project_dir": "",
        "entrypoint": ""
    }
    try:
        template_path = resource_path("Build_Deploy_Run/install_config/user_config_template.json")
        if template_path.exists():
            with open(template_path) as f:
                default.update(json.load(f))
    except Exception as e:
        print(f"[!] Failed to load default config: {e}")
    return default

# === GUI Helper Functions ===
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

def validate_fields():
    errors = []
    if not vcxsrv_entry.get().strip():
        errors.append("VcXsrv path is required.")
    if not docker_entry.get().strip():
        errors.append("Docker path is required.")
    if not project_entry.get().strip():
        errors.append("Project directory is required.")
    entry_text = entrypoint_entry.get().strip()
    if not entry_text or entry_text == entry_placeholder:
        errors.append("Entrypoint script is required.")
    else:
        project_dir = Path(project_entry.get())
        if not (project_dir / entry_text).exists():
            errors.append(f"Entrypoint script not found: {entry_text}")

    if errors:
        messagebox.showerror("Missing or Invalid Fields", "\n".join(errors))
        return False
    return True

def run_installer_wrapper():
    if not validate_fields():
        return

    vcxsrv_path = vcxsrv_entry.get()
    docker_path = docker_entry.get()
    project_dir = project_entry.get()
    entrypoint = entrypoint_entry.get()
    if entrypoint == entry_placeholder:
        entrypoint = ""

    run_installer(
        vcxsrv_path,
        docker_path,
        project_dir,
        entrypoint,
        open_project_var.get(),
        run_xlaunch_var.get(),
        run_docker_var.get()
    )

# === Main GUI ===
root = tk.Tk()
root.title("Build Deploy Run - Setup Wizard")
root.geometry("640x360")
root.configure(bg="black")

# === Set Window Icon ===
try:
    icon_path = resource_path("Build_Deploy_Run/assets/icon.ico")
    if icon_path.exists():
        root.iconbitmap(default=str(icon_path))
except Exception as e:
    print(f"[!] Failed to set window icon: {e}")

# === Add Logo Image ===
try:
    logo_path = resource_path("Build_Deploy_Run/assets/icon.png")
    if logo_path.exists():
        logo_img = Image.open(logo_path).resize((64, 64))
        logo_tk = ImageTk.PhotoImage(logo_img)
        logo_label = tk.Label(root, image=logo_tk, bg="black")
        logo_label.image = logo_tk
        logo_label.grid(row=0, column=0, rowspan=2, sticky="nw", padx=5, pady=5)
except Exception as e:
    print(f"[!] Failed to load logo image: {e}")

padx = 10
pady = 5
entry_placeholder = "e.g. main.py or app.py"
default_config = load_default_config()

# === GUI Layout ===
tk.Label(root, text="VcXsrv Path:", bg="black", fg="white").grid(row=0, column=1, sticky="e", padx=padx, pady=pady)
vcxsrv_entry = tk.Entry(root, width=60)
vcxsrv_entry.insert(0, default_config["vcxsrv_path"])
vcxsrv_entry.grid(row=0, column=2, padx=padx, pady=pady)
tk.Button(root, text="Browse", command=lambda: browse_file(vcxsrv_entry)).grid(row=0, column=3)

tk.Label(root, text="Docker Path:", bg="black", fg="white").grid(row=1, column=1, sticky="e", padx=padx, pady=pady)
docker_entry = tk.Entry(root, width=60)
docker_entry.insert(0, default_config["docker_path"])
docker_entry.grid(row=1, column=2, padx=padx, pady=pady)
tk.Button(root, text="Browse", command=lambda: browse_file(docker_entry)).grid(row=1, column=3)

tk.Label(root, text="Project Folder:", bg="black", fg="white").grid(row=2, column=1, sticky="e", padx=padx, pady=pady)
project_entry = tk.Entry(root, width=60)
project_entry.insert(0, default_config["project_dir"] or "E:/Files/GitHub Repos/YourProject")
project_entry.grid(row=2, column=2, padx=padx, pady=pady)
tk.Button(root, text="Browse", command=lambda: browse_folder(project_entry)).grid(row=2, column=3)

tk.Label(root, text="Entrypoint Script:", bg="black", fg="white").grid(row=3, column=1, sticky="e", padx=padx, pady=pady)
entrypoint_entry = tk.Entry(root, width=60, fg="grey", bg="black", insertbackground="white")
entrypoint_entry.insert(0, entry_placeholder)
entrypoint_entry.bind("<FocusIn>", lambda e: (entrypoint_entry.delete(0, tk.END), entrypoint_entry.config(fg="white")) if entrypoint_entry.get() == entry_placeholder else None)
entrypoint_entry.bind("<FocusOut>", lambda e: entrypoint_entry.insert(0, entry_placeholder) if entrypoint_entry.get().strip() == "" else None)
entrypoint_entry.grid(row=3, column=2, padx=padx, pady=pady)

# === Options ===
run_xlaunch_var = tk.BooleanVar()
tk.Checkbutton(root, text="Run XLaunch after install", variable=run_xlaunch_var, bg="black", fg="lime").grid(row=4, column=2, sticky="w", padx=padx)

run_docker_var = tk.BooleanVar()
tk.Checkbutton(root, text="Run Docker after install", variable=run_docker_var, bg="black", fg="lime").grid(row=5, column=2, sticky="w", padx=padx)

open_project_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="Open project folder after install", variable=open_project_var, bg="black", fg="lime").grid(row=6, column=2, sticky="w", padx=padx)

tk.Button(root, text="💾  Install", command=run_installer_wrapper, bg="lime", fg="black", width=20).grid(row=7, column=2, pady=20)

root.mainloop()
