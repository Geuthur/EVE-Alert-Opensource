import mss
import numpy as np
from PIL import Image


class WindowCapture:
    def __init__(self):
        pass

    def get_screenshot_value(self, y1, x1, x2, y2):
        with mss.mss() as sct:
            monitor = {"top": y1, "left": x1, "width": x2 - x1, "height": y2 - y1}
            try:
                screenshot = sct.grab(monitor)
            except Exception:
                return None, None

        # Convert the Image to a NumPy array and drop the alpha channel
        img_array = np.array(screenshot)

        img_array = img_array[
            :, :, :3
        ]  # Keep only RGB channels, drop the alpha channel
        # img_array.setflags(write=1)
        # Create an Image object directly from the NumPy array
        img = Image.fromarray(img_array)
        # Convert the Image to a NumPy array and drop the alpha channel
        img_array = np.asarray(img)

        return img_array, screenshot

    def take_screenshot(self, x1, y1, y2, x2):
        with mss.mss() as sct:
            monitor = {"top": y1, "left": x1, "width": x2, "height": y2}
            screenshot = sct.grab(monitor)

        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb, "raw", "RGB")

        img.save("evealert/img/image_replace.png")

        if img:
            return True

        return False
