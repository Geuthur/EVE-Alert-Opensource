import os
import sys


def get_resource_path(relative_path):
    if getattr(sys, "frozen", False):
        # Wenn das Skript mit PyInstaller kompiliert wurde
        base_path = os.path.abspath("evealert/.")
    else:
        # Wenn das Skript direkt ausgeführt wird
        base_path = os.path.abspath("evealert/.")

    return os.path.join(base_path, relative_path)
