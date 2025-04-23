# 🛠️ Build_Deploy_Run

**Build_Deploy_Run** is a zero-setup, one-command deployment utility for Python projects. It enables simultaneous Docker and EXE builds from a single `.bat` file — no file moving, no CLI hacking, no manual setup.

---

## 🎯 What It’s For

To make deploying **any** Python project as easy as:

```powershell
.\Build_Deploy_Runuild_and_deploy_venv_locked.bat
```

Once initialized, you can build and package your project without ever touching a Dockerfile or `pyinstaller` again.

---

## 🧪 First-Time Setup (via EXE)

1. **Download the EXE version** of Build_Deploy_Run.
2. Launch it — a GUI will open.
3. Select your target project directory (e.g., `Super Power Options`).
4. The tool will install itself inside that project’s folder:
   ```
   YourProject/
   └── Build_Deploy_Run/
   ```
5. Copy the command displayed in the final dialog — usually:
   ```powershell
   .\Build_Deploy_Runuild_and_deploy_venv_locked.bat
   ```

You’re now configured for instant builds on any machine with Python installed.

---

## 🚀 Daily Use

From your project root, just run:

```powershell
.\Build_Deploy_Runuild_and_deploy_venv_locked.bat
```

This will:

- Freeze your app into a Windows EXE
- Package your app into a Docker image
- Skip files in `Build_Deploy_Run/` automatically
- Use the stored config set during the initial EXE setup

---

## 🧱 Project Anatomy

```
YourProject/
├── main.py
├── README.md
├── Build_Deploy_Run/
│   ├── build_and_deploy_venv_locked.bat  ← ENTRYPOINT
│   ├── install_config/                   ← Used by the EXE for setup
│   ├── workers/                          ← Deployment logic
│   ├── requirements-*.txt
│   └── *.spec
```

---

## 📎 FAQ

**Do I have to move files manually?**  
No. Just run the EXE. It’ll place everything where it needs to go.

**Can I run the `.bat` from any terminal?**  
Yes — PowerShell, CMD, Windows Terminal all work.

**What happens after install?**  
You’ll never need the GUI again unless you want to reconfigure. All logic lives inside the `/Build_Deploy_Run` subfolder.

**Can I use this across multiple projects?**  
Yes. Just run the EXE per-project and follow the wizard.

---

## 🧠 Philosophy

> Download → Configure once → Run forever.

**No manual copying.  
No config rewriting.  
No stress.**

---

