#!/usr/bin/env python3

from pathlib import Path

PARENT: Path = Path(__file__).parent.absolute()

DATA_DIR: Path = PARENT / "data"
TRADATE2025PATH: Path = DATA_DIR / "2025.csv"
TRADATE2026PATH: Path = DATA_DIR / "2026.csv"

DESKTOP_PATH: Path = Path.home().absolute() / "Desktop"
