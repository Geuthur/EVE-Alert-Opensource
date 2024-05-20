import customtkinter

from evealert import __version__
from evealert.functions import get_resource_path
from evealert.menus.alert import AlertMenu

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

ICON_PATH = "img/eve.ico"

# Create the Main Window
root = customtkinter.CTk()
root.title(f"Alert - {__version__}")
root.iconbitmap(default=get_resource_path(ICON_PATH))
# Start the application
app = AlertMenu(root)
root.mainloop()
