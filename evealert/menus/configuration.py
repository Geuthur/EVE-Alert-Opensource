import customtkinter
from PIL import Image, ImageTk

from evealert.settings.constants import ICON
from evealert.settings.functions import get_resource_path
from evealert.settings.logger import logging

logger = logging.getLogger("alert")


class ConfigMenu:
    """Configuration menu for the Alert System."""

    def __init__(self, main: customtkinter.CTk):
        self.main = main
        self.active = False
        self.config_window_y = None
        self.set_icon()

        self.load_settings()

    def set_icon(self):
        try:
            icon_path = get_resource_path(ICON)
            img = Image.open(icon_path)
            self.icon = ImageTk.PhotoImage(img)
            self.main.iconphoto(True, self.icon)
        except Exception as e:
            logger.exception("Error setting icon: %s", e)

    def load_settings(self):
        """Load the settings from the settings file."""
        self.config_window = customtkinter.CTkToplevel(self.main)
        self.config_window.title("Settings")

        self.config_window.withdraw()

        # Verwende ein eigenes Frame für das Menü
        self.menu_frame = customtkinter.CTkFrame(self.config_window)
        self.menu_frame.pack(side="left", padx=20, pady=20)

        self.logging = customtkinter.CTkEntry(self.menu_frame)

        # 1 Row - Init
        self.label_x_axis = customtkinter.CTkLabel(self.menu_frame, text="X-Achse")
        self.label_y_axis = customtkinter.CTkLabel(self.menu_frame, text="Y-Achse")

        # 2 Row - Init
        # Alert Region Position 1
        self.alert_region_label_1 = customtkinter.CTkLabel(
            self.menu_frame, text="Alert Region Left Upper Corner:", justify="left"
        )
        self.alert_region_x_first = customtkinter.CTkEntry(self.menu_frame)
        self.alert_region_y_first = customtkinter.CTkEntry(self.menu_frame)

        # 3 Row - Init
        # Alert Region Position 2
        self.alert_region_label_2 = customtkinter.CTkLabel(
            self.menu_frame, text="Alert Region Right Lower Corner:", justify="left"
        )
        self.alert_region_x_second = customtkinter.CTkEntry(self.menu_frame)
        self.alert_region_y_second = customtkinter.CTkEntry(self.menu_frame)

        # 4 Row - Init
        # Alert Region Position 1
        self.faction_region_label_1 = customtkinter.CTkLabel(
            self.menu_frame, text="Faction Region Left Upper Corner:", justify="left"
        )
        self.faction_region_x_first = customtkinter.CTkEntry(self.menu_frame)
        self.faction_region_y_first = customtkinter.CTkEntry(self.menu_frame)

        # 5 Row - Init
        # Alert Region Position 2
        self.faction_region_label_2 = customtkinter.CTkLabel(
            self.menu_frame, text="Faction Region Right Lower Corner:", justify="left"
        )
        self.faction_region_x_second = customtkinter.CTkEntry(self.menu_frame)
        self.faction_region_y_second = customtkinter.CTkEntry(self.menu_frame)

        # Row 6 - Init
        # Slider
        self.slider_label = customtkinter.CTkLabel(
            self.menu_frame, text="Detection Threshold"
        )
        self.detectionscale = customtkinter.DoubleVar()
        self.detectionscale.set(70)  # Setzen Sie den Standardwert auf 70
        self.slider = customtkinter.CTkSlider(
            self.menu_frame,
            from_=0,
            to=100,
            orientation="horizontal",
            number_of_steps=100,
            variable=self.detectionscale,
            command=self.slider_event,
        )
        self.mode_var = customtkinter.StringVar(value="color")

        # Row 7
        # Config / Detection Mode- Init
        self.mode_checkbox = customtkinter.CTkCheckBox(
            self.menu_frame,
            text="Detection Mode",
            variable=self.mode_var,
            onvalue="color",
            offvalue="picture",
            command=self.update_mode,
        )

        self.cooldown_timer_label = customtkinter.CTkLabel(
            self.menu_frame, text="Cooldown Timer:", justify="left"
        )
        self.cooldown_timer = customtkinter.CTkEntry(self.menu_frame)
        self.cooldown_timer_text = customtkinter.CTkLabel(
            self.menu_frame, text="Seconds", justify="left"
        )

        if self.main.settings:
            self.settingsvalue = self.main.settings.open_settings()
            self.logging.insert(0, self.settingsvalue["logging"])
            self.alert_region_x_first.insert(
                0, self.settingsvalue["alert_region_1"]["x"]
            )
            self.alert_region_y_first.insert(
                0, self.settingsvalue["alert_region_1"]["y"]
            )
            self.alert_region_x_second.insert(
                0, self.settingsvalue["alert_region_2"]["x"]
            )
            self.alert_region_y_second.insert(
                0, self.settingsvalue["alert_region_2"]["y"]
            )
            self.faction_region_x_first.insert(
                0, self.settingsvalue["faction_region_1"]["x"]
            )
            self.faction_region_y_first.insert(
                0, self.settingsvalue["faction_region_1"]["y"]
            )
            self.faction_region_x_second.insert(
                0, self.settingsvalue["faction_region_2"]["x"]
            )
            self.faction_region_y_second.insert(
                0, self.settingsvalue["faction_region_2"]["y"]
            )
            self.detectionscale.set(self.settingsvalue["detectionscale"]["value"])
            self.mode_var.set(self.settingsvalue["detection_mode"]["value"])
            self.cooldown_timer.insert(0, self.settingsvalue["cooldown_timer"]["value"])

    def open_description_window(self):
        """Opoens the description window for the configuration mode."""
        if not self.active:
            self.active = True
            self.main.config_mode = True
            self.main.buttons.config_button.configure(
                fg_color="#fa0202", hover_color="#bd291e"
            )

            # Position des Beschreibungsfensters rechts neben dem Hauptmenü
            config_menu_x, config_menu_y = (
                self.main.winfo_x(),
                self.main.winfo_y(),
            )
            config_menu_width, config_menu_height = (
                self.main.winfo_width(),
                self.main.winfo_height(),
            )

            config_window_width = 650
            config_window_height = 320
            config_window_x = config_menu_x + config_menu_width + 10
            config_window_y = (
                config_menu_y + config_menu_height + 40
                if self.main.config_mode
                else config_menu_y
            )
            if not self.main.descmenu.active:
                config_window_y = config_menu_y

            self.config_window.geometry(
                f"{config_window_width}x{config_window_height}+{config_window_x}+{config_window_y}"
            )

            self.config_window.deiconify()

            self.empty_label_1 = customtkinter.CTkLabel(
                self.menu_frame, text=self.slider.get()
            )
            self.empty_label_00 = customtkinter.CTkLabel(
                self.menu_frame, text=self.mode_var.get()
            )

            self.label_x_axis.grid(row=0, column=1)
            self.label_y_axis.grid(row=0, column=2)

            # Alert Region 1 Visual
            self.alert_region_label_1.grid(row=1, column=0, padx=20)
            self.alert_region_x_first.grid(row=1, column=1)
            self.alert_region_y_first.grid(row=1, column=2)

            # Alert Region 2 Visual
            self.alert_region_label_2.grid(row=2, column=0, padx=20)
            self.alert_region_x_second.grid(row=2, column=1)
            self.alert_region_y_second.grid(row=2, column=2)

            # Faction Region 1 Visual
            self.faction_region_label_1.grid(row=3, column=0, padx=20)
            self.faction_region_x_first.grid(row=3, column=1)
            self.faction_region_y_first.grid(row=3, column=2)

            # Faction Region 2 Visual
            self.faction_region_label_2.grid(row=4, column=0, padx=20)
            self.faction_region_x_second.grid(row=4, column=1)
            self.faction_region_y_second.grid(row=4, column=2)

            # Faction Region 2 Visual
            self.cooldown_timer_label.grid(row=5, column=0, padx=20)
            self.cooldown_timer.grid(row=5, column=1, padx=20)
            self.cooldown_timer_text.grid(row=5, column=2)

            # Slider Visual
            self.empty_label_1.grid(row=6, column=2)

            # Slider Visual
            self.slider_label.grid(row=6, column=0)
            self.slider.grid(row=6, column=1)

            # Mode Change
            self.mode_checkbox.grid(row=7, column=1)
            self.empty_label_00.grid(row=7, column=2)

            def close_config_window():
                self.main.buttons.config_button.configure(
                    fg_color="#1f538d", hover_color="#14375e"
                )
                self.main.config_mode = False
                self.config_window.withdraw()

            self.config_window.protocol("WM_DELETE_WINDOW", close_config_window)

            self.close_button = customtkinter.CTkButton(
                self.menu_frame, text="Schließen", command=close_config_window
            )
            self.close_button.grid(column=1, pady=10)
        else:
            self.active = False
            self.main.config_mode = False
            self.main.buttons.config_button.configure(
                fg_color="#1f538d", hover_color="#14375e"
            )
            self.config_window.withdraw()

    def update_mode(self):
        selected_mode = self.mode_var.get()
        if selected_mode == "color" and self.main.alarm.get_vision() is True:
            self.main.alarm.set_vision()
            self.main.alarm.set_vision_faction()
        self.main.save_settings()
        self.empty_label_00.configure(text=selected_mode)

    def slider_event(self, slider_value):
        self.empty_label_1.configure(text=slider_value)
