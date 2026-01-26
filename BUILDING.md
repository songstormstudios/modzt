# Building ModZT

This project provides two small helpers to build the executable with PyInstaller.

PowerShell (Windows)
- Run `build.ps1` from the project root in PowerShell. Example:

  .\build.ps1 -Clean -Name ModZT -Icon modzt.ico

Cross-platform (Python)
- Run the Python wrapper. Example:

  python build.py --clean --name ModZT --icon modzt.ico

Notes
- Both helpers will install packages listed in `requirements.txt` if present.
- The produced executable will be in the `dist` directory.
- If `pyinstaller` is not installed, the scripts call it as `python -m PyInstaller`.
