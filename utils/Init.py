from pathlib import Path
import os


def CheckDir(dir):
    Path(dir).mkdir(parents=True, exist_ok=True)
