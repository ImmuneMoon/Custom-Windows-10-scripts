import subprocess
from pathlib import Path
from colorama import Fore

def run_pyinstaller(spec_file: Path):
    """Run PyInstaller with the given spec file."""
    if not spec_file or not spec_file.exists():
        print(Fore.RED + "[X] No valid .spec file provided to PyInstaller.")
        return False

    print(Fore.YELLOW + f"[*] Building .exe with PyInstaller using {spec_file.name}...")
    try:
        subprocess.run(["pyinstaller", str(spec_file)], check=True)
        print(Fore.GREEN + "[✓] Executable build complete.")
        return True
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"[X] PyInstaller failed: {e}")
        return False
