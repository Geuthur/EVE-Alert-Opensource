from customtkinter import (
    CTk,
    CTkButton,
    CTkCheckBox,
    CTkEntry,
    CTkFrame,
    CTkLabel,
    CTkSlider,
    CTkToplevel,
    DoubleVar,
    StringVar,
)

from evealert.settings.constants import ICON
from evealert.settings.functions import get_resource_path


class ConfigMenu:
    """Configuration menu for the Alert System."""

    def __init__(self, root: CTk):
        self.root = root
        if self.root.settings:
            self.settingsvalue = self.root.settings.open_settings()
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

        self.config_menu()
        self.alarm_menu()

    def config_menu(self):
        """Load the settings from the settings file."""
        self.config_window = CTkToplevel(self.root)
        self.config_window.title("Settings")

        self.config_window.withdraw()

        parent_frame = CTkFrame(self.config_window)
        parent_frame.pack()

        # Verwende ein eigenes Frame für das Menü
        menu_frame = CTkFrame(parent_frame)
        menu_frame.pack(side="left", padx=10)

        self.alert_button = CTkButton(
            menu_frame, text="Alarm Settings", command=self.open_alert_window
        )

        self.faction_region_label_1 = CTkLabel(
            menu_frame, text="Faction Region Left Upper Corner:", justify="left"
        )

        self.faction_region_label_2 = CTkLabel(
            menu_frame, text="Faction Region Right Lower Corner:", justify="left"
        )

        self.cooldown_timer_label = CTkLabel(
            menu_frame, text="Cooldown Timer:", justify="left"
        )

        # Verwende ein eigenes Frame für das Menü
        menu_frame = CTkFrame(parent_frame)
        menu_frame.pack(side="left", padx=10)

        self.label_x_axis = CTkLabel(menu_frame, text="X-Achse")
        self.faction_region_x_first = CTkEntry(menu_frame)
        self.faction_region_x_second = CTkEntry(menu_frame)
        self.cooldown_timer = CTkEntry(menu_frame)

        # Verwende ein eigenes Frame für das Menü
        menu_frame = CTkFrame(parent_frame)
        menu_frame.pack(side="left", padx=10)

        self.label_y_axis = CTkLabel(menu_frame, text="Y-Achse")
        self.faction_region_y_first = CTkEntry(menu_frame)
        self.faction_region_y_second = CTkEntry(menu_frame)
        self.cooldown_timer_text = CTkLabel(menu_frame, text="Seconds", justify="left")

        # Verwende ein eigenes Frame für das Menü
        menu_frame = CTkFrame(parent_frame)
        menu_frame.pack(side="left", padx=10)
        # Row 6 - Init
        # Slider
        self.slider_label = CTkLabel(menu_frame, text="Detection Threshold")
        self.detectionscale = DoubleVar()
        self.detectionscale.set(70)  # Setzen Sie den Standardwert auf 70
        self.slider = CTkSlider(
            menu_frame,
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
            menu_frame,
            text="Detection Mode",
            variable=self.mode_var,
            onvalue="color",
            offvalue="picture",
            command=self.update_mode,
        )

        self.empty_label_1 = CTkLabel(menu_frame, text=self.slider.get())
        self.empty_label_00 = CTkLabel(menu_frame, text=self.mode_var.get())

        self.close_button = CTkButton(
            self.config_window, text="Schließen", command=self.close_windows
        )
        self.close_button.pack()

        self.logging = CTkEntry(menu_frame)
        self.logging.insert(0, self.settingsvalue["logging"])

    def alarm_menu(self):
        # Erstellen Sie ein neues Fenster für die Alarmregionen
        self.alert_window = CTkToplevel(self.root)

        self.alert_window.withdraw()

        parent_frame = CTkFrame(self.alert_window)
        parent_frame.pack()

        info = CTkFrame(parent_frame)
        info.pack(padx=10, pady=10)
        label = CTkLabel(info, text="")
        label.grid(row=0, column=0, padx=40)
        label = CTkLabel(info, text="X-Achse")
        label.grid(row=0, column=1, padx=50)
        label = CTkLabel(info, text="Y-Achse")
        label.grid(row=0, column=2, padx=50)

        # Laden der Alarmregionen
        for i, alert_location in enumerate(
            self.settingsvalue["alarm_locations"], start=1
        ):
            for _, coordinates in alert_location.items():
                # Erstellen Sie ein neues Frame für jede Alarmregion
                frame = CTkFrame(parent_frame)
                frame.pack(padx=10, pady=10)

                label = CTkLabel(frame, text=f"Alarmregion {i}: ")
                label.grid(row=0, column=0)

                self.alert_entry["x1"][i] = CTkEntry(frame)
                self.alert_entry["x1"][i].insert(0, coordinates["x1"])
                self.alert_entry["x1"][i].grid(row=0, column=1)
                self.entries.append(self.alert_entry["x1"][i])

                self.alert_entry["y1"][i] = CTkEntry(frame)
                self.alert_entry["y1"][i].insert(0, coordinates["y1"])
                self.alert_entry["y1"][i].grid(row=0, column=2)
                self.entries.append(self.alert_entry["y1"][i])

                self.alert_entry["x2"][i] = CTkEntry(frame)
                self.alert_entry["x2"][i].insert(0, coordinates["x2"])
                self.alert_entry["x2"][i].grid(row=1, column=1)
                self.entries.append(self.alert_entry["x2"][i])

                self.alert_entry["y2"][i] = CTkEntry(frame)
                self.alert_entry["y2"][i].insert(0, coordinates["y2"])
                self.alert_entry["y2"][i].grid(row=1, column=2)
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
            self.alert_button.configure(fg_color="#fa0202", hover_color="#bd291e")
            alert_window_x = self.root_menu_x + self.root_menu_width + 10
            alert_window_y = self.root_menu_y + self.root_menu_height + 40
            self.alert_window.update_idletasks()
            required_width = self.alert_window.winfo_reqwidth()
            required_height = self.alert_window.winfo_reqheight()

            self.alert_window.geometry(
                f"{required_width}x{required_height}+{alert_window_x}+{alert_window_y}"
            )

            self.alert_window.title("Alarm Settings")
            self.alert_window.deiconify()

            self.alert_window.protocol("WM_DELETE_WINDOW", self.close_alert_window)

            # Check if the close button has already been created
            if not hasattr(self, "alarm_close_button"):
                self.alarm_close_button = CTkButton(
                    self.alert_window, text="Schließen", command=self.close_alert_window
                )
                self.alarm_close_button.pack()
        else:
            self.alert_menu = False
            self.alert_button.configure(fg_color="#1f538d", hover_color="#14375e")
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

            self.label_x_axis.pack()
            self.label_y_axis.pack()

            self.alert_button.pack()

            # Faction Region 1 Visual
            self.faction_region_label_1.pack()
            self.faction_region_x_first.pack()
            self.faction_region_y_first.pack()

            # Faction Region 2 Visual
            self.faction_region_label_2.pack()
            self.faction_region_x_second.pack()
            self.faction_region_y_second.pack()

            # Faction Region 2 Visual
            self.cooldown_timer_label.pack()
            self.cooldown_timer.pack()
            self.cooldown_timer_text.pack()

            # Slider Visual
            self.empty_label_1.pack()

            # Slider Visual
            self.slider_label.pack()
            self.slider.pack()

            # Mode Change
            self.mode_checkbox.pack()
            self.empty_label_00.pack()

            # Position des Beschreibungsfensters rechts neben dem Hauptmenü
            self.config_window.update_idletasks()

            required_width = self.config_window.winfo_reqwidth()
            required_height = self.config_window.winfo_reqheight()
            config_window_x = self.root_menu_x + self.root_menu_width + 10
            config_window_y = (
                self.root_menu_y + self.root_menu_height + 40
                if self.root.config_mode
                else self.root_menu_y
            )
            if not self.root.descmenu.active:
                config_window_y = self.root_menu_y

            self.config_window.geometry(
                f"{required_width - 120}x{required_height}+{config_window_x}+{config_window_y}"
            )

            self.config_window.deiconify()

            self.config_window.protocol("WM_DELETE_WINDOW", self.close_windows)
        else:
            self.close_windows()

    def close_alert_window(self):
        self.alert_button.configure(fg_color="#1f538d", hover_color="#14375e")
        self.alert_menu = False
        self.alert_window.withdraw()

    def close_config_window(self):
        self.root.buttons.config_button.configure(
            fg_color="#1f538d", hover_color="#14375e"
        )
        self.active = False
        self.root.config_mode = False
        self.config_window.withdraw()

    def close_windows(self):
        self.close_alert_window()
        self.close_config_window()

    def update_mode(self):
        selected_mode = self.mode_var.get()
        if selected_mode == "color" and self.root.alarm.get_vision("Alert") is True:
            self.root.alarm.set_vision("Alert")
            self.root.alarm.set_vision("Faction")
        self.root.save_settings()
        self.empty_label_00.configure(text=selected_mode)

    def slider_event(self, slider_value):
        self.empty_label_1.configure(text=slider_value)
