
# 🧠 Build_Deploy_Run Integration for Super Power Options

This project is powered by `Build_Deploy_Run` — a modular, zero-clutter deployment pipeline for Python applications.

---

## 📦 Project Layout

```
Super Power Options/
├── main.py
├── Super_Power_Options.spec
├── requirements.txt                # Regenerated clean
├── venv/                           # Auto-managed project venv
├── dist/                           # EXE output
├── Dockerfile                      # Docker image logic
│
├── Build_Deploy_Run/
│   ├── deploy_fusion_runner.py    # 🧠 Main pipeline trigger
│   ├── venv/                      # Tooling-only env
│   ├── requirements.txt           # BDR tool deps only
│   ├── workers/                   # Helpers, smoke tests, etc.
│   ├── assets/, install_config/
│   └── user_config.json           # Config stored only here
```

---

## ⚙️ What Build_Deploy_Run Does

- Creates its **own isolated environment**
- Regenerates a **clean `requirements.txt`** for your project
- Replaces your project's `venv/` (with confirmation)
- Automatically builds:
  - ✅ **EXE** via PyInstaller
  - 🐳 **Docker Image**

---

## 🚀 One-Line Build

To run everything:

```bash
./Build_Deploy_Run/deploy_fusion_runner.py
```

Or on Windows:

```bash
cd Build_Deploy_Run
venv\Scripts\python.exe deploy_fusion_runner.py
```

---

## 🧼 Clean-by-Design

- Never pollutes your main environment
- Doesn’t leave behind stale `dist/`, `venv/`, or builds
- Can be reused in any compatible Python project

---

## 🛠️ To Reuse In Another Project

Just copy the `Build_Deploy_Run` folder into any new repo and run:

```Powershell
python install_config/config.py
```

Then follow the prompts and launch the deployer.

---

## 🔒 What You DON’T Need To Touch

- No manual `.env` or `user_config.json` editing
- No time consuming PyInstaller CLI args
- No Docker command writing

Everything’s controlled through config and run logic.

---

Built to save your time and automate everything you hate doing manually.
