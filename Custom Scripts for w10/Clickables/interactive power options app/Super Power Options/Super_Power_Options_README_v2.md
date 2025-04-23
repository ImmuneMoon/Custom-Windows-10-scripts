# Super Power Options – Dual-Mode README

Because some of us want style, and others want a server to shut down *on schedule, quietly, and without sass.*

---

## 😎 Fun Mode (for humans, devs, and chaos engineers)

### 💣 What is This?
A stylish Python desktop app that lets you schedule your computer to:
- 💤 Sleep
- 🔁 Restart
- 💥 Shutdown

And it lets you do it in **seconds, centuries, or anything in between**. With custom PNG buttons, hover tooltips, optional sound alerts, and a Dev Mode Easter egg.

### 🚀 Cool Stuff in This Version

- **Threaded Timers** = No UI freezing
- **Custom Icons** = Sleep, Shutdown, Restart, Cancel
- **Delayed Hover Tooltips** = Gentle UX polish
- **Dev Mode:** Type `1337` to see what happens 😉
- **Sound Alerts:** Swap your own `.wav` into `/assets/`

### 🎮 How to Use It
1. Run `main.py` or `.exe`
2. Type a number (ex: `60`) and pick a time unit (`seconds`, `hours`, `millennia`)
3. Click the icon for what you want to happen
4. Timer updates on screen
5. Cancel if you regret your choices

### 🎁 Dev Notes
- Built with `tkinter`
- Packaged using PyInstaller
- Works on Windows (with WSL/Docker workarounds)

---

## 🧑‍💼 For Ops (or anyone who needs this app to behave)

### 📦 What This Is
**Super Power Options** is a `tkinter`-based Python GUI for programmatically scheduling Windows power events:
- System shutdown
- Sleep (suspend)
- Restart
- Cancel scheduled action

### 📁 Project Structure
```
SuperPowerOptions/
│
├── main.py               # Launch point
├── PowerApp/
│   ├── PowerUI.py        # GUI layer
│   └── PowerLogic.py     # Timer & execution logic
├── assets/               # Icons + .wav alert
│   ├── *.png / *.ico     # Button images + app icon
│   └── alert.wav         # Optional shutdown sound
├── Super_Power_Options.spec
└── Dockerfile (optional)
```

### 🔧 Requirements
- Python 3.8+
- Windows OS
- Tkinter (default for Python)
- Optional: `winsound` or `aplay` for sound

### 🛠️ Build Instructions
```bash
pyinstaller Super_Power_Options.spec
```
Output `.exe` appears in `/dist` with all assets embedded.

### ⚙️ Features
- Delayed execution using `root.after()`
- Fully cancelable timers
- Resource-path handling for PyInstaller
- Modular code: logic and GUI are separated

### 🧪 Special Case: Dev Mode
- If the timer value entered is `1337`, Dev Mode is activated.
- Behavior can be customized in `PowerLogic.py`

### 🐋 Docker Support
If needed for WSL testing or sandboxing:
- GUI and sound only work with forwarded `DISPLAY` and audio channels

---

## 📜 License
MIT License (millennia mode not guaranteed to function as intended)
