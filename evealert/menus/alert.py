from datetime import datetime
from threading import Lock, Thread

import customtkinter
import pyautogui
from PIL import Image
from pynput import keyboard, mouse

from evealert import __version__
from evealert.exceptions import ScreenshotError
from evealert.managers.alertmanager import AlertAgent, wincap
from evealert.managers.regionmanager import RegionDisplay
from evealert.managers.settingsmanager import SettingsManager
from evealert.menus.configuration import ConfigMenu
from evealert.menus.description import DescriptionMenu
from evealert.settings.constants import ICON
from evealert.settings.functions import get_resource_path
from evealert.settings.logger import logging

logger = logging.getLogger("alert")

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 350


class Screenshot:
    """Screenshot Class for the Alert System"""

    def __init__(self, main):
        self.main = main
        self.taking_screenshot = False
        self.screenshot_overlay = None
        self.screenshot_mode = 0
        self.start_x, self.start_y = None, None
        self.end_x, self.end_y = None, None


class AlertButton:
    def __init__(self, main):
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
            command=self.config_mode_toggle,
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
        self.main.log_field.insert(
            "1.0",
            f"[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Settings Saved.\n",
            "green",
        )
        self.main.save_settings()

    def description_mode_toggle(self):
        self.main.descmenu.open_description_window()

    def config_mode_toggle(self):
        self.main.configmenu.open_description_window()


class AlertMenu(customtkinter.CTk):
    """Main Menu for the Alert System"""

    def __init__(self):
        super().__init__()
        self.title(f"Alert - {__version__}")
        self.alarm = AlertAgent(self)
        self.settings = SettingsManager()
        self.configmenu = ConfigMenu(self)
        self.descmenu = DescriptionMenu(self)
        self.screenshot = Screenshot(self)
        self.display = RegionDisplay(self)
        self.buttons = AlertButton(self)
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
        self.iconbitmap(default=get_resource_path(ICON))
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        self.log_field = customtkinter.CTkTextbox(self, height=100, width=450)
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

        # Other
        mouse_listener = mouse.Listener(on_click=self.on_click)
        mouse_listener.start()

        keyboard_listener = keyboard.Listener(on_release=self.on_key_release)
        keyboard_listener.start()

        self.update_mouse_position_label()

    # Save Files
    def save_settings(self):
        """Save the settings to the settings.json file."""
        if not (
            self.configmenu.alert_region_x_first.get()
            and self.configmenu.alert_region_y_first.get()
        ) or not (
            self.configmenu.alert_region_x_second.get()
            and self.configmenu.alert_region_y_second.get()
        ):
            self.log_field.insert(
                "1.0",
                f"[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Empty Fields. Minimum is Alert Region.\n",
                "red",
            )
            return
        self.settings.save_settings(
            {
                "logging": self.configmenu.logging.get(),
                "alert_region_x_first": self.configmenu.alert_region_x_first.get(),
                "alert_region_y_first": self.configmenu.alert_region_y_first.get(),
                "alert_region_x_second": self.configmenu.alert_region_x_second.get(),
                "alert_region_y_second": self.configmenu.alert_region_y_second.get(),
                "faction_region_x_first": self.configmenu.faction_region_x_first.get(),
                "faction_region_y_first": self.configmenu.faction_region_y_first.get(),
                "faction_region_x_second": self.configmenu.faction_region_x_second.get(),
                "faction_region_y_second": self.configmenu.faction_region_y_second.get(),
                "detectionscale": self.configmenu.detectionscale.get(),
                "mode_var": self.configmenu.mode_var.get(),
                "cooldown_timer": self.configmenu.cooldown_timer.get(),
            }
        )
        self.alarm.set_settings()

    def is_configmode(self):
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
            self.taking_screenshot = False

    def display_alert_region(self):
        """Display the alert region on the screen."""
        selected_mode = self.configmenu.mode_var.get()
        if selected_mode == "picture":
            self.after(0, self.alarm.set_vision)
        else:
            self.after(0, self.display.create_alert_region())

    def display_faction_region(self):
        """Display the faction region on the screen."""
        selected_mode = self.configmenu.mode_var.get()
        if selected_mode == "picture":
            self.after(0, self.alarm.set_vision_faction)
        else:
            self.after(0, self.display.create_faction_region())

    def display_screenshot_region(self, x, y, width, height):
        """Display the screenshot region on the screen."""
        self.screenshot.screenshot_overlay = self.display.create_screenshot_region(
            x,
            y,
            width,
            height,
            self.screenshot.screenshot_overlay,
        )
        self.after(0)

    # Mouse Functions
    def update_mouse_position_label(self):
        """Update the mouse position label."""
        x, y = pyautogui.position()
        self.mouse_position_label.configure(text=f"Mausposition: X={x}, Y={y}")
        self.after(100, self.update_mouse_position_label)

    def on_click(self, x, y, button, pressed):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.config_mode:
            if (
                pressed
                and self.set_alert_region
                and not self.set_faction_region
                and not self.taking_screenshot
                and button == mouse.Button.middle
            ):
                y, x = pyautogui.position()
                self.alert_region_mode = (self.alert_region_mode) % 2

                if self.alert_region_mode == 0:
                    print("First Region Set.")
                    self.configmenu.alert_region_x_first.delete(0, customtkinter.END)
                    self.configmenu.alert_region_y_first.delete(0, customtkinter.END)
                    self.configmenu.alert_region_x_first.insert(0, str(y))
                    self.configmenu.alert_region_y_first.insert(0, str(x))
                    self.alert_region_mode = self.alert_region_mode + 1
                else:
                    print("Second Region Set")
                    self.configmenu.alert_region_x_second.delete(0, customtkinter.END)
                    self.configmenu.alert_region_y_second.delete(0, customtkinter.END)
                    self.configmenu.alert_region_x_second.insert(0, str(y))
                    self.configmenu.alert_region_y_second.insert(0, str(x))
                    self.set_alert_region = False
                    self.alert_region_mode = 0
                    self.save_settings()
                    self.log_field.insert(
                        "1.0",
                        f"[{now}] Alert Region Positions Saved.\n",
                        "green",
                    )

            if (
                pressed
                and self.set_faction_region
                and not self.set_alert_region
                and not self.taking_screenshot
                and button == mouse.Button.middle
            ):
                y, x = pyautogui.position()
                self.faction_region_mode = (self.faction_region_mode) % 2

                if self.faction_region_mode == 0:
                    print("First Region Set.")
                    self.configmenu.faction_region_x_first.delete(0, customtkinter.END)
                    self.configmenu.faction_region_y_first.delete(0, customtkinter.END)
                    self.configmenu.faction_region_x_first.insert(0, str(y))
                    self.configmenu.faction_region_y_first.insert(0, str(x))
                    self.faction_region_mode = self.faction_region_mode + 1
                else:
                    print("Second Region Set")
                    self.configmenu.faction_region_x_second.delete(0, customtkinter.END)
                    self.configmenu.faction_region_y_second.delete(0, customtkinter.END)
                    self.configmenu.faction_region_x_second.insert(0, str(y))
                    self.configmenu.faction_region_y_second.insert(0, str(x))
                    self.set_faction_region = False
                    self.faction_region_mode = 0
                    self.save_settings()
                    self.log_field.insert(
                        "1.0",
                        f"[{now}] Faction Region Positions Saved.\n",
                        "green",
                    )

            if (
                pressed
                and self.taking_screenshot
                and not self.set_faction_region
                and not self.set_alert_region
                and button == mouse.Button.middle
            ):
                x, y = pyautogui.position()
                self.screenshot.screenshot_mode = (self.screenshot.screenshot_mode) % 2

                if self.screenshot.screenshot_mode == 0:
                    if self.screenshot.screenshot_overlay:
                        self.screenshot.screenshot_overlay.destroy()
                    self.screenshot.start_x, self.screenshot.start_y = x, y
                    print("Screenshot Position Set")
                    self.screenshot.screenshot_mode = (
                        self.screenshot.screenshot_mode + 1
                    )
                elif self.screenshot.screenshot_mode == 1:
                    self.screenshot.end_x, self.screenshot.end_y = x, y
                    print("Screenshot Position 2 Set")
                    self.log_field.insert("1.0", f"[{now}] Press F3 to confirm.\n")
                    self.screenshot.screenshot_mode = 0
                    try:
                        self.display_screenshot_region(
                            self.screenshot.start_x,
                            self.screenshot.start_y,
                            abs(self.screenshot.end_x - self.screenshot.start_x),
                            abs(self.screenshot.end_y - self.screenshot.start_y),
                        )
                    except Exception as e:
                        logger.error("Screenshot Error: %s", e)
                        self.log_field.insert(
                            "1.0",
                            f"[{now}] System: Screenshot Error.\n",
                            "red",
                        )

    # pylint: disable=too-many-nested-blocks
    # Keyboard Functions
    def on_key_release(self, key):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.config_mode:
            if key == keyboard.Key.f1:
                if not self.set_alert_region:
                    self.taking_screenshot = False
                    self.set_faction_region = False
                    self.set_alert_region = True
                    self.log_field.insert("1.0", f"[{now}] Alert Mode: Activated.\n")
                else:
                    self.log_field.insert("1.0", f"[{now}] Alert Mode: Deactivated.\n")
                    self.set_alert_region = False
            if key == keyboard.Key.f2:
                if not self.set_faction_region:
                    self.taking_screenshot = False
                    self.set_alert_region = False
                    self.set_faction_region = True
                    self.log_field.insert("1.0", f"[{now}] Faction Mode: Activated.\n")
                else:
                    self.log_field.insert(
                        "1.0", f"[{now}] Faction Mode: Deactivated.\n"
                    )
                    self.set_faction_region = False
            if key == keyboard.Key.f3:
                if not self.taking_screenshot:
                    self.taking_screenshot = True
                    self.set_faction_region = False
                    self.set_alert_region = False
                    self.screenshot.start_x, self.screenshot.start_y = None, None
                    self.screenshot.end_x, self.screenshot.end_y = None, None
                    self.log_field.insert(
                        "1.0",
                        f"[{now}] Screenshot Mode: Activated.\n",
                    )
                else:
                    self.taking_screenshot = False
                    self.log_field.insert(
                        "1.0", f"[{now}] Screenshot Mode: Deactivated.\n"
                    )
                    if (
                        self.screenshot.start_x is not None
                        and self.screenshot.start_y is not None
                        and self.screenshot.end_x is not None
                        and self.screenshot.end_y is not None
                    ):
                        try:
                            if self.screenshot.screenshot_overlay:
                                self.screenshot.screenshot_overlay.destroy()
                            screenshot = wincap.take_screenshot(
                                self.screenshot.start_x,
                                self.screenshot.start_y,
                                self.screenshot.end_y - self.screenshot.start_y,
                                self.screenshot.end_x - self.screenshot.start_x,
                            )
                            # screenshot = pyautogui.screenshot(region=(start_x, start_y, end_x - start_x, end_y - start_y))
                            if screenshot:
                                self.log_field.insert(
                                    "1.0",
                                    f"[{now}] Screenshot Saved.\n",
                                    "green",
                                )
                            else:
                                raise ScreenshotError("Screenshot Error")
                        except Exception as e:
                            logger.error("Screenshot Error: %s", e)
                            self.log_field.insert(
                                "1.0",
                                f"[{now}] Screenshot Positions wrong.\n",
                                "red",
                            )

    # Menu Button Section

    def exit_button_clicked(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.alarm.is_running():
            self.alarm.stop()
            self.log_field.insert(
                "1.0", f"[{now}] System: ❎ EVE Alert stopped.\n", "red"
            )
        else:
            self.log_field.insert(
                "1.0",
                f"[{now}] System: ❎ EVE Alert isn't running.\n",
                "red",
            )
        self.destroy()

    # Starten Sie den Alert-Thread, indem Sie die Alert-Funktion aus alert.py aufrufen
    def start_alert_script(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            if not self.alarm.is_running():
                Thread(target=self.alarm.start).start()
            else:
                self.log_field.insert(
                    "1.0", f"[{now}] System: EVE Alert is already running.\n"
                )
        except Exception as e:
            logger.error("Start Alert Error: %s", e, exc_info=True)
            self.log_field.insert(
                "1.0", f"[{now}] System: Something went wrong.\n", "red"
            )

    def stop_alert_script(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.alarm.is_running():
            self.alarm.stop()
            self.log_field.insert("1.0", f"[{now}] System: EVE Alert stopped.\n", "red")
            return
        self.log_field.insert("1.0", f"[{now}] System: EVE Alert isn't running.\n")
