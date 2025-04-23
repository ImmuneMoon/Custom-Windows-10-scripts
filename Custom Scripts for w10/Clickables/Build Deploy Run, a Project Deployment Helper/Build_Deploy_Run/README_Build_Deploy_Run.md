# 🛠️ Build Deploy Run - Project Deployment Toolkit

Welcome to your new one-line deploy pipeline.

This project has been equipped with **Build Deploy Run**, a universal Python deployment system that:

- 🔒 Builds and locks virtual environments
- ⚙️ Generates Windows executables
- 🐳 Builds Docker containers (with X11 display support)
- 💾 Handles dependency freezing + config setup
- 💡 All from **one terminal command**

---

## 🚀 Quick Start

Inside your project directory, run:

```powershell
.\Build_Deploy_Run\build_and_deploy_venv_locked.bat
```

✅ This will:
- Freeze your current Python requirements
- Generate a new `venv` just for this project
- Build an `.exe` (if a `.spec` is defined)
- Build a Docker container with GUI support
- Output all results to the `/dist/` folder

---

## 🔧 Configuration

Configuration lives in:

- `Build_Deploy_Run/user_config.json`
- `Build_Deploy_Run/.env` (for CLI tools)

You can edit paths or default behavior there.

Default config includes:
- Your project folder
- Entrypoint script (`main.py`, `app.py`, etc.)
- Paths to Docker and VcXsrv (for GUI apps)

---

## 🧪 Smoke Testing

Want to verify everything's wired up?

```powershell
.\Build_Deploy_Run\smoke_test.bat
```

This tests:
- EXE launching
- Docker container launching
- Path correctness

---

## 🔁 Updating Your Build

Just re-run the same `.bat` file. It'll:
- Overwrite old EXEs
- Overwrite Docker containers
- Preserve your project folder + `.venv`

---

## 🖥️ Optional Tools

If you're building GUI apps with display support (Tkinter, etc), install:
- [VcXsrv](https://sourceforge.net/projects/vcxsrv/)
- Docker Desktop

They'll be launched for you if needed.

---

## 🧼 Clean Build Tip

Want to force a fresh rebuild?

```powershell
.\Build_Deploy_Run\build_and_deploy_venv_locked.bat clean
```

This nukes the old `.venv` and rebuilds from scratch.

---

## 💬 Support

For help, ideas, or to contribute, open an issue or pull request at the main [Build Deploy Run repo](https://github.com/YOUR-LINK-HERE).

---

📂 Happy building.
