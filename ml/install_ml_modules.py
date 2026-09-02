"""
AutoMind AI — ML Dependencies & Module Installer
Installs all required ML modules for Fine-Tuning and Vector Search:
  - torch
  - transformers
  - datasets
  - peft
  - bitsandbytes
  - accelerate
  - sentence-transformers
  - faiss-cpu
  - scikit-learn
"""

import sys
import subprocess
import os

REQ_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")

def install_modules():
    print("=" * 70)
    print(" INSTALLING AUTOMIND ML & FINE-TUNING MODULES ")
    print("=" * 70)
    
    python_exe = sys.executable
    print(f"[*] Python Interpreter: {python_exe}")
    print(f"[*] Installing requirements from: {REQ_FILE}")

    cmd = [python_exe, "-m", "pip", "install", "-r", REQ_FILE]
    
    try:
        res = subprocess.run(cmd, check=True)
        print("\n[✔] ALL ML MODULES INSTALLED SUCCESSFULLY!")
    except Exception as err:
        print(f"\n[-] Installation error: {err}")
        print("Fallback: Try running command manually in PowerShell:")
        print(f"  .\\.venv\\Scripts\\pip.exe install -r ml\\requirements.txt")

if __name__ == "__main__":
    install_modules()
