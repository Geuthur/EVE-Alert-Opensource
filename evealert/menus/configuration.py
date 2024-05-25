from customtkinter import CTk, CTkFrame, CTkLabel, CTkEntry, CTkSlider, CTkCheckBox, DoubleVar, CTkButton, CTkToplevel, StringVar

from evealert.settings.constants import ICON
from evealert.settings.functions import get_resource_path


class ConfigMenu:
    """Configuration menu for the Alert System."""

    def __init__(self, root: CTk):
        self.root = root
        self.entries = []
        self.active = False
        self.alert_menu = False
        self.config_window_y = None
        self.root.iconbitmap(default=get_resource_path(ICON))
        self.alert_entry = {
            "x1": {},
            "y1": {},
            "x2": {},
            "y2": {},
        }

        self.load_settings()

    def load_settings(self):
        """Load the settings from the settings file."""
        self.config_window = CTkToplevel(self.root)
        self.config_window.title("Settings")

        self.config_window.withdraw()

        # Verwende ein eigenes Frame für das Menü
        self.menu_frame = CTkFrame(self.config_window)
        self.menu_frame.pack(side="left", padx=20, pady=20)

        self.logging = CTkEntry(self.menu_frame)

        # 1 Row - Init
        self.label_x_axis = CTkLabel(self.menu_frame, text="X-Achse")
        self.label_y_axis = CTkLabel(self.menu_frame, text="Y-Achse")

        self.alert_button = CTkButton(
                self.menu_frame, text="Alarm Settings", command=self.open_alert_window
            )


        # 4 Row - Init
        # Alert Region Position 1
        self.faction_region_label_1 = CTkLabel(
            self.menu_frame, text="Faction Region Left Upper Corner:", justify="left"
        )
        self.faction_region_x_first = CTkEntry(self.menu_frame)
        self.faction_region_y_first = CTkEntry(self.menu_frame)

        # 5 Row - Init
        # Alert Region Position 2
        self.faction_region_label_2 = CTkLabel(
            self.menu_frame, text="Faction Region Right Lower Corner:", justify="left"
        )
        self.faction_region_x_second = CTkEntry(self.menu_frame)
        self.faction_region_y_second = CTkEntry(self.menu_frame)

        # Row 6 - Init
        # Slider
        self.slider_label = CTkLabel(
            self.menu_frame, text="Detection Threshold"
        )
        self.detectionscale = DoubleVar()
        self.detectionscale.set(70)  # Setzen Sie den Standardwert auf 70
        self.slider = CTkSlider(
            self.menu_frame,
            from_=0,
            to=100,
            orientation="horizontal",
            number_of_steps=100,
            variable=self.detectionscale,
            command=self.slider_event,
        )
        self.mode_var = StringVar(value="color")

        # Row 7
        # Config / Detection Mode- Init
        self.mode_checkbox = CTkCheckBox(
            self.menu_frame,
            text="Detection Mode",
            variable=self.mode_var,
            onvalue="color",
            offvalue="picture",
            command=self.update_mode,
        )

        self.cooldown_timer_label = CTkLabel(
            self.menu_frame, text="Cooldown Timer:", justify="left"
        )
        self.cooldown_timer = CTkEntry(self.menu_frame)
        self.cooldown_timer_text = CTkLabel(
            self.menu_frame, text="Seconds", justify="left"
        )

        if self.root.settings:
            self.settingsvalue = self.root.settings.open_settings()
            self.logging.insert(0, self.settingsvalue["logging"])

        # Erstellen Sie ein neues Fenster für die Alarmregionen
        self.alert_window = CTkToplevel(self.root)

        self.alert_window.withdraw()

        # Laden der Alarmregionen
        for i, alert_location in enumerate(self.settingsvalue["alarm_locations"], start=1):
            for _, coordinates in alert_location.items():
                # Erstellen Sie dynamisch Labels und Eingabefelder für jede Alarmregion
                label = CTkLabel(self.alert_window, text=f"Alarmregion {i}")
                label.pack()

                self.alert_entry["x1"][i] = CTkEntry(self.alert_window)
                self.alert_entry["x1"][i].insert(0, coordinates["x1"])
                self.alert_entry["x1"][i].pack()
                self.entries.append(self.alert_entry["x1"][i])

                self.alert_entry["y1"][i] = CTkEntry(self.alert_window)
                self.alert_entry["y1"][i].insert(0, coordinates["y1"])
                self.alert_entry["y1"][i].pack()
                self.entries.append(self.alert_entry["y1"][i])

                self.alert_entry["x2"][i] = CTkEntry(self.alert_window)
                self.alert_entry["x2"][i].insert(0, coordinates["x2"])
                self.alert_entry["x2"][i].pack()
                self.entries.append(self.alert_entry["x2"][i])

                self.alert_entry["y2"][i] = CTkEntry(self.alert_window)
                self.alert_entry["y2"][i].insert(0, coordinates["y2"])
                self.alert_entry["y2"][i].pack()
                self.entries.append(self.alert_entry["y2"][i])

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

    def root_menu_position(self):
        self.root_menu_x, self.root_menu_y = (
            self.root.winfo_x(),
            self.root.winfo_y(),
        )
        self.root_menu_width, self.root_menu_height = (
            self.root.winfo_width(),
            self.root.winfo_height(),
        )

    def open_alert_window(self):
        """Opoens the alarm window for the configuration mode."""
            
        if not self.alert_menu:
            self.root_menu_position()
            self.alert_menu = True
            alert_window_x = self.root_menu_x + self.root_menu_width + 10
            alert_window_y = self.root_menu_y + self.root_menu_height + 40
            alert_window_width = 300
            alert_window_height = 400

            self.alert_window.geometry(
                f"{alert_window_width}x{alert_window_height}+{alert_window_x}+{alert_window_y}"
            )

            self.alert_window.title("Alarm Settings")
            self.alert_window.deiconify()

            def close_alert_window():
                self.alert_button.configure(
                    fg_color="#1f538d", hover_color="#14375e"
                )
                self.alert_menu = False
                self.alert_window.withdraw()

            self.alert_window.protocol("WM_DELETE_WINDOW", close_alert_window)

            # Check if the close button has already been created
            if not hasattr(self, 'alarm_close_button'):
                self.alarm_close_button = CTkButton(
                    self.alert_window, text="Schließen", command=close_alert_window
                )
                self.alarm_close_button.pack()
        else:
            self.alert_menu = False
            self.alert_button.configure(
                fg_color="#1f538d", hover_color="#14375e"
            )
            self.alert_window.withdraw()

    def open_description_window(self):
        """Opoens the description window for the configuration mode."""
        if not self.active:
            self.root_menu_position()
            self.active = True
            self.root.config_mode = True
            self.root.buttons.config_button.configure(
                fg_color="#fa0202", hover_color="#bd291e"
            )

            # Position des Beschreibungsfensters rechts neben dem Hauptmenü
            config_window_width = 650
            config_window_height = 320
            config_window_x = self.root_menu_x + self.root_menu_width + 10
            config_window_y = (
                self.root_menu_y + self.root_menu_height + 40
                if self.root.config_mode
                else self.root_menu_y
            )
            if not self.root.descmenu.active:
                config_window_y = self.root_menu_y

            self.config_window.geometry(
                f"{config_window_width}x{config_window_height}+{config_window_x}+{config_window_y}"
            )

            self.config_window.deiconify()

            self.empty_label_1 = CTkLabel(
                self.menu_frame, text=self.slider.get()
            )
            self.empty_label_00 = CTkLabel(
                self.menu_frame, text=self.mode_var.get()
            )

            self.label_x_axis.grid(row=0, column=1)
            self.label_y_axis.grid(row=0, column=2)

            self.alert_button.grid(row=0, column=0)

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
                self.root.buttons.config_button.configure(
                    fg_color="#1f538d", hover_color="#14375e"
                )
                self.root.configmenu.active = False
                self.root.configmenu.alert_menu = False
                self.root.config_mode = False
                self.config_window.withdraw()
                self.alert_window.withdraw()

            self.config_window.protocol("WM_DELETE_WINDOW", close_config_window)

            # Check if the close button has already been created
            if not hasattr(self, 'close_button'):
                self.close_button = CTkButton(
                    self.menu_frame, text="Schließen", command=close_config_window
                )
                self.close_button.grid(column=1, pady=10)
        else:
            self.root.configmenu.active = False
            self.root.config_mode = False
            self.root.buttons.config_button.configure(
                fg_color="#1f538d", hover_color="#14375e"
            )
            self.root.configmenu.alert_menu = False
            self.config_window.withdraw()
            self.alert_window.withdraw()

    def update_mode(self):
        selected_mode = self.mode_var.get()
        if selected_mode == "color" and self.root.alarm.get_vision() is True:
            self.root.alarm.set_vision()
            self.root.alarm.set_vision_faction()
        self.root.save_settings()
        self.empty_label_00.configure(text=selected_mode)

    def slider_event(self, slider_value):
        self.empty_label_1.configure(text=slider_value)
