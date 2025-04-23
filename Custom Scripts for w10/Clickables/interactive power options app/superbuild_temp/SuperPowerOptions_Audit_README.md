# 🧠 Project Audit: Super Power Options (Explicit File Annotations)

This document identifies exactly which files contain which issues so nothing escapes your wrath.

---

## ⚠️ Issue Map by File

---

### 📁 `build_and_deploy.py`

- ❌ Hardcoded VcXsrv path:
  ```python
  vcxsrv_path = Path("C:/Program Files/VcXsrv/vcxsrv.exe")
  ```
- ❌ Hardcoded DISPLAY:
  ```bash
  "-e", "DISPLAY=host.docker.internal:0"
  ```
- ❌ Lacks environment fallback for DISPLAY or tray disabling.

---

### 📁 `PowerUI.py`

- ❌ Tray icon launched without checking `DISABLE_TRAY`:
  ```python
  icon.run()
  ```
- ❌ Potential duplicate call of `PowerApp()` if also triggered in `main.py`.

---

### 📁 `main.py`

- ❌ Calls `PowerApp()` directly:
  ```python
  app = PowerApp()
  app.run()
  ```
  Risk of launching GUI twice if `PowerUI.py` also triggers it.

---

### 📁 `Super_Power_Options.spec`

- ❌ EXE name mismatch:
  - File: `Super_Power_Options.spec`
  - Code & scripts expect: `SuperPowerOptions`
- ❌ Naming inconsistency can cause EXE to not be found or packaged incorrectly.

---

### 📁 `build_and_deploy_venv_locked.bat`  
- ❌ Also refers to mismatched EXE/project naming.
- Should standardize EXE and spec filename references.

---

## 🧼 Suggested Remediations

- Gate `icon.run()` with `if not os.getenv("DISABLE_TRAY")`
- Replace hardcoded DISPLAY with:
  ```python
  os.getenv("DISPLAY", "host.docker.internal:0")
  ```
- Move `PowerApp()` call solely into `main.py`
- Rename spec and EXE target to match project naming conventions (`super_power_options`)

---

## 🧠 Manual Audit Required

This document must be maintained by a conscious human to avoid the dilution of truth by AI approximations.

You write the code. You own the faults. You fix them with malice.