import customtkinter
import tkinter as tk
import json, os, sys
from config import *
from menus.settings import settings

alert_timer = None
faction_timer = None

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        # Wenn das Skript mit PyInstaller kompiliert wurde
        base_path = os.path.abspath(".")
    else:
        # Wenn das Skript direkt ausgeführt wird
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def create_overlay(root, x1, y1, x2, y2):
    overlay = tk.Toplevel(root)
    overlay.attributes('-topmost', 1)
    overlay.attributes('-alpha', 0.5)
    overlay.overrideredirect(True)

    overlay.geometry(f"{x2}x{y2}+{x1}+{y1}")

    alert_canvas = customtkinter.CTkCanvas(overlay, bg="blue", highlightthickness=0)
    
    alert_canvas.pack(fill="both", expand=True)

    # Zeichnen Sie ein rotes Rechteck als Alert-Bereich
    alert_canvas.create_rectangle(0, 0, x2, y2, outline="red", width=2)

    return overlay

def create_alert_region(root, system_label):
    global alert_timer
    config = settings().open_settings()
    if alert_timer:
        return
    try:
        # Annahme, dass die Einstellungen korrekte Werte für x1, y1, x2 und y2 enthalten
        x1 = int(config.get("alert_region_1", {}).get("x", 0))
        y1 = int(config.get("alert_region_1", {}).get("y", 0))
        x2 = int(config.get("alert_region_2", {}).get("x", 100))
        y2 = int(config.get("alert_region_2", {}).get("y", 100))

        def close_alert_region():
            global alert_timer
            alert_overlay.destroy()
            alert_timer = False

        width = x2 - x1
        height = y2 - y1

        alert_timer = True
        alert_overlay = create_overlay(root, x1, y1, width, height)
        root.after(5000, close_alert_region)
    except Exception as e:
        print(e)
        system_label.configure(text="System: ❎ Something is wrong.", text_color="red")

def create_faction_region(root, system_label):
    global faction_timer
    config = settings().open_settings()
    if faction_timer:
        return
    try:
        # Annahme, dass die Einstellungen korrekte Werte für x1, y1, x2 und y2 enthalten
        x1 = int(config.get("faction_region_1", {}).get("x", 0))
        y1 = int(config.get("faction_region_1", {}).get("y", 0))
        x2 = int(config.get("faction_region_2", {}).get("x", 100))
        y2 = int(config.get("faction_region_2", {}).get("y", 100))

        def close_alert_region():
            global faction_timer
            alert_overlay.destroy()
            faction_timer = False

        width = x2 - x1
        height = y2 - y1

        faction_timer = True
        alert_overlay = create_overlay(root, x1, y1, width, height)
        root.after(5000, close_alert_region)
    except Exception as e:
        print(e)
        system_label.configure(text="System: ❎ Something is wrong.", text_color="red")

def create_screenshot_region(x, y, width, height, root, system_label):
    global screenshot_overlay
    try:
        screenshot_overlay = create_overlay(root, x, y, width, height)
        if screenshot_overlay:
            def close_screenshot_region():
                screenshot_overlay.destroy()
            root.after(5000, close_screenshot_region)
            return screenshot_overlay
    except Exception as e:
        print(e)
        system_label.configure(text="System: ❎ Something is wrong.", text_color="red")