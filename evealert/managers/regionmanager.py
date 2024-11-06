import tkinter as tk

import customtkinter


class RegionDisplay:
    def __init__(self, main: customtkinter.CTk):
        self.main = main
        self.alerttimer = None
        self.factiontimer = None

    def create_overlay(self, x1, y1, x2, y2):
        overlay = tk.Toplevel(self.main)
        overlay.attributes("-topmost", 1)
        overlay.attributes("-alpha", 0.5)
        overlay.overrideredirect(True)

        overlay.geometry(f"{x2}x{y2}+{x1}+{y1}")

        alert_canvas = customtkinter.CTkCanvas(overlay, bg="blue", highlightthickness=0)

        alert_canvas.pack(fill="both", expand=True)

        # Zeichnen Sie ein rotes Rechteck als Alert-Bereich
        alert_canvas.create_rectangle(0, 0, x2, y2, outline="red", width=2)

        return overlay

    def create_alert_region(self):
        config = self.main.settings.open_settings()
        if self.alerttimer:
            return
        try:
            # Annahme, dass die Einstellungen korrekte Werte für x1, y1, x2 und y2 enthalten
            x1 = int(config.get("alert_region_1", {}).get("x", 0))
            y1 = int(config.get("alert_region_1", {}).get("y", 0))
            x2 = int(config.get("alert_region_2", {}).get("x", 100))
            y2 = int(config.get("alert_region_2", {}).get("y", 100))

            def close_alert_region():
                alert_overlay.destroy()
                self.alerttimer = False

            width = x2 - x1
            height = y2 - y1

            self.alerttimer = True
            alert_overlay = self.create_overlay(x1, y1, width, height)
            self.main.after(5000, close_alert_region)
        except Exception as e:
            print(e)
            self.main.log_field.configure(
                text="System: ❎ Something is wrong.", text_color="red"
            )

    def create_faction_region(self):
        config = self.main.settings.open_settings()
        if self.factiontimer:
            return
        try:
            # Annahme, dass die Einstellungen korrekte Werte für x1, y1, x2 und y2 enthalten
            x1 = int(config.get("faction_region_1", {}).get("x", 0))
            y1 = int(config.get("faction_region_1", {}).get("y", 0))
            x2 = int(config.get("faction_region_2", {}).get("x", 100))
            y2 = int(config.get("faction_region_2", {}).get("y", 100))

            def close_alert_region():
                alert_overlay.destroy()
                self.factiontimer = False

            width = x2 - x1
            height = y2 - y1

            self.factiontimer = True
            alert_overlay = self.create_overlay(x1, y1, width, height)
            self.main.after(5000, close_alert_region)
        except Exception as e:
            print(e)
            self.main.log_field.configure(
                text="System: ❎ Something is wrong.", text_color="red"
            )

    # pylint: disable=too-many-positional-arguments
    def create_screenshot_region(self, x, y, width, height, screenshot_overlay=None):
        """Create a screenshot region overlay."""
        try:
            screenshot_overlay = self.create_overlay(x, y, width, height)
            if screenshot_overlay:

                def close_screenshot_region():
                    screenshot_overlay.destroy()

                self.main.after(5000, close_screenshot_region)
        except Exception as e:
            print(e)
            self.main.log_field.configure(
                text="System: ❎ Something is wrong.", text_color="red"
            )
            screenshot_overlay = None
        return screenshot_overlay
