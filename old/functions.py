import customtkinter
import tkinter as tk
import json, os, sys
from config import *

alert_timer = None
faction_timer = None

def load_settings():
    try:
        with open(settings_file, 'r') as file:
            settings = json.load(file)
        return settings
    except FileNotFoundError:
        return {}
    
def open_settings():
    default_settings = {
        "alert_region_1": {"x": "0", "y": "0"},
        "alert_region_2": {"x": "0", "y": "0"},
        "faction_region_1": {"x": "0", "y": "0"},
        "faction_region_2": {"x": "0", "y": "0"},
        "detectionscale": {"value": 90.0},
        "detection_mode": {"value": "picture"}
    }

    try:
        with open(settings_file, 'r') as file:
            settings = json.load(file)
        return settings
    except FileNotFoundError:
        if os.path.exists(settings_file):  # Überprüfen, ob die Datei existiert
            # Wenn die Datei existiert, lösche sie
            os.remove(settings_file)

        # Erstelle die Datei mit den Standardwerten
        with open(settings_file, 'w') as file:
            json.dump(default_settings, file)

        return default_settings

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        # Wenn das Skript mit PyInstaller kompiliert wurde
        base_path = os.path.abspath(".")
    else:
        # Wenn das Skript direkt ausgeführt wird
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def create_overlay(x1, y1, x2, y2):
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
    settings = load_settings()
    if alert_timer:
        return
    try:
        # Annahme, dass die Einstellungen korrekte Werte für x1, y1, x2 und y2 enthalten
        x1 = int(settings.get("alert_region_1", {}).get("x", 0))
        y1 = int(settings.get("alert_region_1", {}).get("y", 0))
        x2 = int(settings.get("alert_region_2", {}).get("x", 100))
        y2 = int(settings.get("alert_region_2", {}).get("y", 100))

        def close_alert_region():
            global alert_timer
            alert_overlay.destroy()
            alert_timer = False

        width = x2 - x1
        height = y2 - y1

        alert_timer = True
        alert_overlay = create_overlay(x1, y1, width, height)
        root.after(5000, close_alert_region)
    except Exception as e:
        print(e)
        system_label.configure(text="System: ❎ Something is wrong.", text_color="red")

def create_faction_region(root, system_label):
    global faction_timer
    settings = load_settings()
    if faction_timer:
        return
    try:
        # Annahme, dass die Einstellungen korrekte Werte für x1, y1, x2 und y2 enthalten
        x1 = int(settings.get("faction_region_1", {}).get("x", 0))
        y1 = int(settings.get("faction_region_1", {}).get("y", 0))
        x2 = int(settings.get("faction_region_2", {}).get("x", 100))
        y2 = int(settings.get("faction_region_2", {}).get("y", 100))

        def close_alert_region():
            global faction_timer
            alert_overlay.destroy()
            faction_timer = False

        width = x2 - x1
        height = y2 - y1

        faction_timer = True
        alert_overlay = create_overlay(x1, y1, width, height)
        root.after(5000, close_alert_region)
    except Exception as e:
        print(e)
        system_label.configure(text="System: ❎ Something is wrong.", text_color="red")

def create_screenshot_region(x, y, width, height, root, system_label):
    global screenshot_overlay
    try:
        screenshot_overlay = create_overlay(x, y, width, height)
        if screenshot_overlay:
            def close_screenshot_region():
                screenshot_overlay.destroy()
            root.after(5000, close_screenshot_region)
            return screenshot_overlay
    except Exception as e:
        print(e)
        system_label.configure(text="System: ❎ Something is wrong.", text_color="red")

def open_description_window(root, config_mode):
    global description_window
    if not config_mode:
        if description_window:
            description_window.destroy()
        return
    description_window = customtkinter.CTkToplevel(root)
    description_window.title("Settings Description")
    
    # Position des Beschreibungsfensters rechts neben dem Hauptmenü
    main_menu_x, main_menu_y = root.winfo_x(), root.winfo_y()
    main_menu_width, main_menu_height = root.winfo_width(), root.winfo_height()
    
    description_window_width = 400
    description_window_height = 250
    description_window_x = main_menu_x + main_menu_width + 10
    description_window_y = main_menu_y
    
    description_window.geometry(f"{description_window_width}x{description_window_height}+{description_window_x}+{description_window_y}")

    description_text = "Alert Region: Press F1 to activate.\n"
    description_text += "If activated Press MIDDLE Mouse Button to set positions.\n"
    description_text += "Faction Mode: Press F2 to activate.\n"
    description_text += "If activated Press MIDDLE Mouse Button to set positions.\n"
    description_text += "Screenshot Mode: Press F3 to activate.\n"
    description_text += "If activated Press MIDDLE Mouse Button to set positions.\n"
    description_text += "\nImportant: You must begin \nfrom the left upper corner to the right lower corner.\n"

    description_label = customtkinter.CTkLabel(description_window, text=description_text, justify='left')
    description_label.pack(padx=20, pady=20)
    
    def close_description_window():
        global description_window
        description_window.destroy()

    description_window.protocol("WM_DELETE_WINDOW", close_description_window)

    close_button = customtkinter.CTkButton(description_window, text="Schließen", command=close_description_window)
    close_button.pack(pady=10)