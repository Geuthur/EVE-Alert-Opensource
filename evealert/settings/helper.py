import os

ICON = "img/eve.ico"


def get_resource_path(relative_path):
    base_path = os.path.abspath("evealert/.")
    return os.path.join(base_path, relative_path)
