import customtkinter

from evealert.client.listener import MainMenu

if __name__ == "__main__":
    root = customtkinter.CTk()
    app = MainMenu(root)
    root.mainloop()
