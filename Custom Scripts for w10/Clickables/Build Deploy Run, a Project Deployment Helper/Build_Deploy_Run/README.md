# 🌟 Build Deploy Run

> **One-line deployment pipeline for Python projects.**
> Automate your entire workflow — virtualenvs, EXEs, Docker images — all from one bat command.

---

## ✨ Features

🎯 **Build Deploy Run** is a universal toolset for developers who want fast, repeatable, foolproof Python deployments.

- 🔐 **Virtual Environment Locking**  
  Automatically freezes your Python dependencies and isolates them in a dedicated `.venv`.

- 💾 **PyInstaller EXE Generation**  
  Builds a Windows `.exe` of your app using a custom `.spec` file and your chosen entrypoint.

- 🐳 **Docker Image Creation**  
  Spins up GUI-ready Docker containers (including X11 forwarding support with VcXsrv).

- 🧪 **Smoke Testing**  
  Run simple pre-checks to verify EXE and Docker builds will work.

- 📋 **Environment Variables + Configs**  
  Clean `.env` + `user_config.json` generation for devs and CI tools alike.

- 🖱️ **Optional GUI Installer**  
  A simple Tkinter-based setup wizard helps users configure everything painlessly.

---

## ⚡ Quickstart

```powershell
.\Build_Deploy_Run\build_and_deploy_venv_locked.bat
```

That’s it. It will:
- Freeze `requirements.txt`
- Generate `.venv`
- Build EXE + Docker (if present)
- Output everything to `dist/`

---

## 🛠 Setup Wizard (Optional)

Run the installer EXE to:
- Configure VcXsrv / Docker / Entrypoint
- Enable long Windows paths (if needed)
- Launch a clean `.bat` workflow instantly

---

## 🧪 Smoke Test

Run:
```powershell
.\Build_Deploy_Run\smoke_test.bat
```

Checks:
- EXE launch
- Docker launch
- Paths + environment

---

## 🧹 Full Clean

```powershell
.\Build_Deploy_Run\build_and_deploy_venv_locked.bat clean
```

Deletes `.venv` and rebuilds from scratch.

---

## 🔍 File Structure

```
📁 Build_Deploy_Run/
├── install_config ──────────────────────├ install_workers ──├ install_core.py
├── build_and_deploy_venv_locked.bat     ├ config.py         ├ minimize_window.py
├── deploy_fusion_runner.py                                  ├ notify.py
├── requirements.txt                                         ├ utils.py
├── requirements-docker.txt                                  ├ BuildDeployInstaller.spec
├── workers/
├── assets/
└── README_Build_Deploy_Run.md
```

---

## 🤖 For CI/CD Systems

Use the `.env` values:
```bash
EXE_PATH="path/to/your_executable.exe"
DOCKER_IMAGE="your_project_name"
```

You can extract and use these from tools like GitHub Actions or local scripts.

---

## 🧠 Why This Exists

Too many projects get hung up in deployment hell.  
This system was built to **make "it just works" actually work.**

One command. One install. Any project.

---

## 🖤 Built With

- Python 3.10+
- PyInstaller
- Docker Desktop
- VcXsrv (for GUI containers)

---

## 🧑‍🚀 Credits

Designed for creative developers who don’t have time for boilerplate.  
Inspired by the madness of too many broken deploy scripts.

Made with caffeine and righteous fury.

---

## 🔗 License

MIT. Use it, remix it, burn it down and rebuild it better.

---

🚀 **Start deploying like you mean it.**
