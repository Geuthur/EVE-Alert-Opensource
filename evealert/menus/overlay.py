from typing import TYPE_CHECKING

import customtkinter

if TYPE_CHECKING:
    from .alert import AlertMenu


class OverlaySystem:
    def __init__(self, root: "AlertMenu"):
        self.root = root
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.rect = None
        self.overlay = None
        self.canvas = None

    def create_overlay(self, monitor):
        self.cleanup()
        self.overlay = customtkinter.CTkToplevel(self.root)
        self.overlay.attributes("-alpha", 0.3)
        self.overlay.attributes("-topmost", True)
        self.overlay.configure(bg="black")
        self.overlay.geometry(
            f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}"
        )

        self.canvas = customtkinter.CTkCanvas(
            self.overlay, bg="black", highlightthickness=0
        )
        self.canvas.pack(fill=customtkinter.BOTH, expand=True)
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def cleanup(self):
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None
        if self.canvas:
            self.canvas.destroy()
            self.canvas = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.rect = None

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x,
            self.start_y,
            self.start_x,
            self.start_y,
            outline="red",
            width=3,
        )

    def on_mouse_drag(self, event):
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        self.end_x, self.end_y = (event.x, event.y)

        # Check if the user selected a region
        if self.end_x is None or self.start_x is None:
            return

        if self.end_x < self.start_x:
            self.start_x, self.end_x = self.end_x, self.start_x
        if self.end_y < self.start_y:
            self.start_y, self.end_y = self.end_y, self.start_y

        # Get the current monitor where the mouse is
        monitor = self.root.get_current_monitor()
        if monitor:
            self.start_x += monitor.x
            self.start_y += monitor.y
            self.end_x += monitor.x
            self.end_y += monitor.y

        self.root.write_message(
            f"Selected region: ({self.start_x}, {self.start_y}) to ({self.end_x}, {self.end_y})"
        )

        if self.root.set_alert_region:
            self.set_alert_region()
        elif self.root.set_faction_region:
            self.set_faction_region()

    def set_alert_region(self):
        self.root.settingsmenu.alert_region_x_first.delete(0, customtkinter.END)
        self.root.settingsmenu.alert_region_y_first.delete(0, customtkinter.END)
        self.root.settingsmenu.alert_region_x_first.insert(0, str(self.start_x + 10))
        self.root.settingsmenu.alert_region_y_first.insert(
            0, str(self.start_y + 30)
        )  # Add 30 pixels to the y-coordinate to solve weird bug?

        self.root.settingsmenu.alert_region_x_second.delete(0, customtkinter.END)
        self.root.settingsmenu.alert_region_y_second.delete(0, customtkinter.END)
        self.root.settingsmenu.alert_region_x_second.insert(0, str(self.end_x + 10))
        self.root.settingsmenu.alert_region_y_second.insert(
            0, str(self.end_y + 30)
        )  # Add 30 pixels to the y-coordinate to solve weird bug?
        self.root.save_settings()
        self.root.set_alert_region = False
        self.cleanup()
        self.root.write_message("Settings: Enemy Deactivated.")

    def set_faction_region(self):
        self.root.settingsmenu.faction_region_x_first.delete(0, customtkinter.END)
        self.root.settingsmenu.faction_region_y_first.delete(0, customtkinter.END)
        self.root.settingsmenu.faction_region_x_first.insert(0, str(self.start_x + 10))
        self.root.settingsmenu.faction_region_y_first.insert(0, str(self.start_y + 30))

        self.root.settingsmenu.faction_region_x_second.delete(0, customtkinter.END)
        self.root.settingsmenu.faction_region_y_second.delete(0, customtkinter.END)
        self.root.settingsmenu.faction_region_x_second.insert(0, str(self.end_x + 10))
        self.root.settingsmenu.faction_region_y_second.insert(0, str(self.end_y + 30))
        self.root.save_settings()
        self.root.set_faction_region = False
        self.cleanup()
        self.root.write_message("Settings: Faction Deactivated.")
