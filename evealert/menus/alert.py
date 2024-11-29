import os
from datetime import datetime
from threading import Thread

import customtkinter
import pyautogui
from PIL import Image
from pynput import keyboard
from screeninfo import get_monitors

from evealert import __version__
from evealert.managers.alertmanager import AlertAgent
from evealert.managers.regionmanager import RegionDisplay
from evealert.managers.settingsmanager import SettingsManager
from evealert.menus.description import DescriptionMenu
from evealert.menus.overlay import OverlaySystem
from evealert.menus.settings import SettingsMenu
from evealert.settings.constants import ICON
from evealert.settings.functions import get_resource_path
from evealert.settings.logger import logging

logger = logging.getLogger("alert")

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 350


class AlertButton:
    def __init__(self, main: "AlertMenu"):
        self.main = main
        self.init_buttons()

    def init_buttons(self):
        # Create Settings System
        self.settings_label_frame = customtkinter.CTkFrame(self.main)
        self.alert_label_frame = customtkinter.CTkFrame(self.main)

        self.save_button = customtkinter.CTkButton(
            self.settings_label_frame,
            text="Save",
            command=self.save_button_clicked,
        )

        self.description_button = customtkinter.CTkButton(
            self.settings_label_frame,
            text="Config Mode",
            command=self.description_mode_toggle,
        )

        self.config_button = customtkinter.CTkButton(
            self.settings_label_frame,
            text="Settings",
            command=self.settings_mode_toggle,
        )
        self.save_button.grid(row=0, column=0, padx=(0, 10))
        self.description_button.grid(row=0, column=1, padx=(0, 10))
        self.config_button.grid(row=0, column=2)

        # Create Buttons
        self.show_alert_button = customtkinter.CTkButton(
            self.alert_label_frame,
            text="Show Alert Region",
            command=self.main.display_alert_region,
        )
        self.show_faction_button = customtkinter.CTkButton(
            self.alert_label_frame,
            text="Show Faction Region",
            command=self.main.display_faction_region,
        )
        self.show_status_label = customtkinter.CTkLabel(
            self.alert_label_frame,
            text="",
            compound="left",
            font=customtkinter.CTkFont(size=15, weight="bold"),
        )

        self.show_status_label.grid(row=0, column=0, padx=20, pady=20)
        self.show_alert_button.grid(row=0, column=1, padx=(0, 10))
        self.show_faction_button.grid(row=0, column=2)

    def save_button_clicked(self):
        self.main.write_message(
            "Settings Saved.",
            "green",
        )
        self.main.save_settings()

    def description_mode_toggle(self):
        self.main.descmenu.open_description_window()

    def settings_mode_toggle(self):
        self.main.settingsmenu.open_menu()


class AlertMenu(customtkinter.CTk):
    """Main Menu for the Alert System"""

    def __init__(self):
        super().__init__()
        self.title(f"Alert - {__version__}")
        self.alarm = AlertAgent(self)

        self.settings = SettingsManager()
        self.settingsmenu = SettingsMenu(self)
        self.descmenu = DescriptionMenu(self)
        self.display = RegionDisplay(self)
        self.buttons = AlertButton(self)
        self.overlay_app = OverlaySystem(self)

        self.init_widgets()
        self.init_menu()
        self.config_mode = False
        self.set_alert_region = False
        self.alert_region_mode = 0
        self.set_faction_region = False
        self.faction_region_mode = 0
        self.taking_screenshot = False
        self.current_status = False
        self.check_status()

    def check_status(self):
        online = customtkinter.CTkImage(
            Image.open(get_resource_path("img/online.png")), size=(24, 24)
        )
        offline = customtkinter.CTkImage(
            Image.open(get_resource_path("img/offline.png")), size=(24, 24)
        )

        new_status = self.alarm.is_running()

        if new_status != self.current_status:
            if new_status:
                self.buttons.show_status_label.configure(image=online)
                self.buttons.show_status_label.image = (
                    online  # Keep a reference to the image
                )
            else:
                self.buttons.show_status_label.configure(image=offline)
                self.buttons.show_status_label.image = (
                    offline  # Keep a reference to the image
                )

            self.current_status = new_status

        # Check the status again after (2 seconds)
        self.buttons.show_status_label.after(1000, self.check_status)

    # Call the function for the first time to start the loop

    def init_widgets(self):
        # Create the main window
        self.set_icon(ICON)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        self.log_field = customtkinter.CTkTextbox(self, height=100, width=450)
        self.log_field.tag_config("normal", foreground="white")
        self.log_field.tag_config("green", foreground="lightgreen")
        self.log_field.tag_config("red", foreground="orange")

        # Create mouse position label
        self.mouse_position_label = customtkinter.CTkLabel(
            self, text="", justify="left"
        )

        # self.timer_var = customtkinter.CTkEntry(self)

        # Create Empty Space
        self.empty_label = customtkinter.CTkLabel(self, text="")
        # Create Empty Space
        self.empty_label2 = customtkinter.CTkLabel(self, text="")
        # Create Empty Space
        self.empty_label3 = customtkinter.CTkLabel(self, text="")

        # Start Stopp System
        self.engine_label_frame = customtkinter.CTkFrame(self)

        self.start_button = customtkinter.CTkButton(
            self.engine_label_frame,
            text="Start Script",
            command=self.start_alert_script,
        )
        self.stop_button = customtkinter.CTkButton(
            self.engine_label_frame, text="Stop Script", command=self.stop_alert_script
        )
        self.exit_button = customtkinter.CTkButton(
            self.engine_label_frame, text="Exit", command=self.exit_button_clicked
        )

        self.start_button.grid(row=0, column=0, padx=(0, 10))
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        self.exit_button.grid(row=0, column=2)

    def set_icon(self, icon):
        try:
            icon_path = get_resource_path(icon)
            if icon_path and os.path.exists(icon_path):
                self.iconbitmap(icon_path)
            else:
                logger.warning("Icon file not found: %s", icon_path)

            self.iconbitmap(default=icon_path)
        except Exception as e:
            logger.exception("Error setting icon: %s", e)

    def init_menu(self):
        """Initializes the Main Menu for the Alert System."""
        # Mouse Position Label
        self.mouse_position_label.pack()
        # Settings Label
        self.buttons.settings_label_frame.pack()
        # Empty Label
        self.empty_label.pack()
        # Alert Buttons Label
        self.buttons.alert_label_frame.pack()
        # Empty Label
        self.empty_label2.pack()
        # Engine Label
        self.engine_label_frame.pack()
        # Create Empty Space
        self.empty_label3.pack()
        # Log Field Label
        self.log_field.pack()

        keyboard_listener = keyboard.Listener(on_release=self.on_key_release)
        keyboard_listener.start()

        self.update_mouse_position_label()

    def write_message(self, text, color="normal"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_field.insert("1.0", f"[{now}] {text}\n", color)

    # Save Files
    def save_settings(self):
        """Save the settings to the settings.json file."""
        if not (
            self.settingsmenu.alert_region_x_first.get()
            and self.settingsmenu.alert_region_y_first.get()
        ) or not (
            self.settingsmenu.alert_region_x_second.get()
            and self.settingsmenu.alert_region_y_second.get()
        ):
            self.write_message(
                "Empty Fields. Minimum is Alert Region.",
                "red",
            )
            return
        self.settings.save_settings(
            {
                "logging": self.settingsmenu.logging.get(),
                "alert_region_x_first": self.settingsmenu.alert_region_x_first.get(),
                "alert_region_y_first": self.settingsmenu.alert_region_y_first.get(),
                "alert_region_x_second": self.settingsmenu.alert_region_x_second.get(),
                "alert_region_y_second": self.settingsmenu.alert_region_y_second.get(),
                "faction_region_x_first": self.settingsmenu.faction_region_x_first.get(),
                "faction_region_y_first": self.settingsmenu.faction_region_y_first.get(),
                "faction_region_x_second": self.settingsmenu.faction_region_x_second.get(),
                "faction_region_y_second": self.settingsmenu.faction_region_y_second.get(),
                "detectionscale": self.settingsmenu.detectionscale.get(),
                "faction_scale": self.settingsmenu.faction_scale.get(),
                "cooldown_timer": self.settingsmenu.cooldown_timer.get(),
            }
        )
        self.alarm.load_settings()

    def is_configmode(self) -> bool:
        """Returns the current config mode."""
        return self.config_mode

    def toggle_configmode(self):
        """Toggle the config mode."""
        if self.is_configmode():
            self.config_mode = False
            self.set_alert_region = False
            self.alert_region_mode = 0
            self.set_faction_region = False
            self.faction_region_mode = 0

    def display_alert_region(self):
        """Display the alert region on the screen."""
        self.after(0, self.alarm.set_vision)

    def display_faction_region(self):
        """Display the faction region on the screen."""
        self.after(0, self.alarm.set_vision_faction)

    # Mouse Functions
    def update_mouse_position_label(self):
        """Update the mouse position label."""
        x, y = pyautogui.position()
        self.mouse_position_label.configure(text=f"Mausposition: X={x}, Y={y}")
        self.after(100, self.update_mouse_position_label)

    def start_overlay(self):
        """Generate the overlay."""
        monitor = self.get_current_monitor()
        if monitor:
            self.overlay_app.create_overlay(monitor)

    def get_current_monitor(self):
        mouse_x, mouse_y = pyautogui.position()
        for monitor in get_monitors():
            if (
                monitor.x <= mouse_x <= monitor.x + monitor.width
                and monitor.y <= mouse_y <= monitor.y + monitor.height
            ):
                return monitor
        return None

    # pylint: disable=too-many-nested-blocks
    # Keyboard Functions
    def on_key_release(self, key):
        """Handle the key release event."""
        if self.config_mode:
            if key == keyboard.Key.f1:
                if not self.set_alert_region and not self.set_faction_region:
                    self.set_faction_region = False
                    self.set_alert_region = True
                    self.write_message("Settings: Enemy Active.")
                    self.after(0, self.start_overlay)
            if key == keyboard.Key.f2:
                if not self.set_faction_region and not self.set_alert_region:
                    self.set_alert_region = False
                    self.set_faction_region = True
                    self.write_message("Settings: Faction Active.")
                    self.after(0, self.start_overlay)
            elif key == keyboard.Key.esc:
                if self.set_faction_region:
                    self.set_faction_region = False
                if self.set_alert_region:
                    self.set_alert_region = False
                if self.overlay_app.overlay:
                    self.overlay_app.cleanup()
                    self.write_message("Settings: Aborted.")

    # Menu Button Section
    def exit_button_clicked(self):
        """Stop the Alert System and close the application."""
        if self.alarm.is_running():
            self.alarm.stop()
            self.write_message("System: ❎ EVE Alert stopped.", "red")
        else:
            self.write_message(
                "System: ❎ EVE Alert isn't running.",
                "red",
            )
        self.destroy()

    # Starten Sie den Alert-Thread, indem Sie die Alert-Funktion aus alert.py aufrufen
    def start_alert_script(self):
        """Start the Alert System (Thread)."""
        try:
            if not self.alarm.is_running():
                Thread(target=self.alarm.start).start()
            else:
                self.write_message("System: EVE Alert is already running.")
        except Exception as e:
            logger.error("Start Alert Error: %s", e, exc_info=True)
            self.write_message("System: Something went wrong.", "red")

    def stop_alert_script(self):
        """Stop the Alert System."""
        if self.alarm.is_running():
            self.alarm.stop()
            self.write_message("System: EVE Alert stopped.", "red")
            return
        self.write_message("System: EVE Alert isn't running.")
