import tkinter as tk
from tkinter import filedialog, messagebox, ttk, PhotoImage
import json
from pathlib import Path
import subprocess
import os, sys
import pyperclip
import shutil


# === Default values ===
default_config = {
    "vcxsrv_path": "C:/Program Files/VcXsrv/vcxsrv.exe",
    "docker_path": "C:/Program Files/Docker/Docker Desktop.exe",
    "project_dir": str(Path(__file__).parent.parent.resolve())

}


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)


# === Browse helpers ===
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


def copy_self_to_project(target_path):
    source_dir = Path(__file__).parent
    destination = Path(target_path)

    # Files to copy (add more if needed)
    files_to_copy = [
        "build_and_deploy.py",
        "build_and_deploy_venv_locked.bat",
        "minimize_xwindows.ps1",
        "Run_Deploy.bat",
        "Build_Deploy_Run.spec"
    ]

    # Optional: ensure project folder exists
    destination.mkdir(parents=True, exist_ok=True)

    for file_name in files_to_copy:
        src = source_dir / file_name
        dst = destination / file_name
        if src.exists():
            dst.write_bytes(src.read_bytes())
            print(f"[✓] Copied {file_name} to {destination}")
        else:
            print(f"[!] Missing file: {src}")


# === Save config ===
def save_config():
    config = {
        "vcxsrv_path": vcxsrv_entry.get(),
        "docker_path": docker_entry.get(),
        "project_dir": project_entry.get()
    }

    target_dir = Path(__file__).parent
    with open(target_dir / "user_config.json", "w") as f:
        json.dump(config, f, indent=2)
    print("[✓] user_config.json saved.")


    if run_xlaunch_var.get():
        try:
            subprocess.Popen([config["vcxsrv_path"], ":0", "-multiwindow", "-clipboard", "-wgl", "-ac"])
            print("[✓] VcXsrv launched.")
        except Exception as e:
            messagebox.showerror("XLaunch Failed", str(e))

    messagebox.showinfo("Saved", "Configuration saved successfully.")
    copy_self_to_project(config["project_dir"])


# User instructions
def show_instruction():
    exe_name = "Build Deploy Run.exe"  # Or dynamically fetched if needed
    bat_name = Path("build_and_deploy_venv_locked.bat")
    
    command = r".\Build_Deploy_Run\build_and_deploy_venv_locked.bat"
    pyperclip.copy(command)

    project_dir = Path(project_entry.get())
    exe_shortcut = project_dir / exe_name

    if exe_shortcut.exists():
        launch_cmd = f'"{exe_name}"'  # Enclose in quotes for spaces
    else:
        launch_cmd = f'.\\Build_Deploy_Run\\{bat_name.name}'

    message = (
        "To build and deploy your project,\n"
        "run the following command in your terminal:\n\n"
        f"{command}\n\n"
        "[✓] This command has been copied to your clipboard."
    )
    messagebox.showinfo("Build Deploy Run", message)
    root.after(4000, root.destroy)


def copy_files_to_project():
    src_dir = Path(__file__).parent
    dest_dir = Path(project_entry.get()) 

    dest_dir.mkdir(parents=True, exist_ok=True)

    for fname in ["Run_Deploy.bat", "build_and_deploy.py", "build_and_deploy_venv_locked.bat", "minimize_xwindows.ps1"]:
        src = src_dir / fname
        dst = dest_dir / fname
        if src.exists():
            shutil.copy(src, dst)
        else:
            print(f"[!] Missing: {src}")

    print("[✓] Scripts copied to project folder.")



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

try:
    # Try .ico first (Windows-style icon)
    icon_path = os.path.join(base_path, "icon.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(default=icon_path)
    else:
        raise FileNotFoundError
except:
    # Fallback to .png
    png_icon_path = os.path.join(base_path, "icon.png")
    if os.path.exists(png_icon_path):
        icon_img = PhotoImage(file=png_icon_path)
        root.iconphoto(False, icon_img)
    else:
        print("[!] No icon file found. Skipping icon setup.")



tk.Label(root, text="VcXsrv Path:", bg="black", fg="white").grid(row=0, column=0, sticky="e")
vcxsrv_entry = tk.Entry(root, width=60)
vcxsrv_entry.insert(0, default_config["vcxsrv_path"])
vcxsrv_entry.grid(row=0, column=1)
tk.Button(root, text="Browse", command=lambda: browse_file(vcxsrv_entry)).grid(row=0, column=2)

tk.Label(root, text="Docker Path:", bg="black", fg="white").grid(row=1, column=0, sticky="e")
docker_entry = tk.Entry(root, width=60)
docker_entry.insert(0, default_config["docker_path"])
docker_entry.grid(row=1, column=1)
tk.Button(root, text="Browse", command=lambda: browse_file(docker_entry)).grid(row=1, column=2)

tk.Label(root, text="Project Folder:", bg="black", fg="white").grid(row=2, column=0, sticky="e")
project_entry = tk.Entry(root, width=60)
project_entry.insert(0, default_config["project_dir"])
project_entry.grid(row=2, column=1)
tk.Button(root, text="Browse", command=lambda: browse_folder(project_entry)).grid(row=2, column=2)

# Run XLaunch checkbox
run_xlaunch_var = tk.BooleanVar()
tk.Checkbutton(root, text="Run XLaunch now after save", variable=run_xlaunch_var, bg="black", fg="lime").grid(row=3, column=1, sticky="w")

# Action buttons
tk.Button(root, text="💾 Install", command=save_and_notify, bg="lime", fg="black", width=20).grid(row=5, column=1, pady=10)

root.mainloop()
