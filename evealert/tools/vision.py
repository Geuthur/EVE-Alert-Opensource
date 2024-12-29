import logging
from datetime import datetime

import cv2 as cv
import numpy as np

from evealert.exceptions import RegionSizeError, ScreenshotError

logger = logging.getLogger("tools")
now = datetime.now()


class Vision:
    needle_img = None
    needle_w = 0
    needle_h = 0
    method = None

    # There are 6 methods to choose from:
    # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
    def __init__(self, needle_img_paths, method=cv.TM_CCOEFF_NORMED):
        # Load the images we're trying to match
        self.needle_imgs = [
            cv.imread(path, cv.IMREAD_UNCHANGED) for path in needle_img_paths
        ]

        # Save the dimensions of the needle images
        self.needle_dims = [(img.shape[1], img.shape[0]) for img in self.needle_imgs]

        self.method = method
        self.debug_mode = False
        self.debug_mode_faction = False
        self.enemy = None
        self.faction = None

    @property
    def is_vision_open(self):
        """Returns True if the vision window is open."""
        return self.debug_mode

    @property
    def is_faction_vision_open(self):
        """Returns True if the faction vision window is open."""
        return self.debug_mode_faction

    def vision_process(self, haystack_img, threshold=0.5, vision_mode="Enemy"):
        all_points = []
        color = (0, 255, 0)

        for idx, (needle_img, needle_dim) in enumerate(
            zip(self.needle_imgs, self.needle_dims)
        ):

            logger.debug("Detecting %s %s", vision_mode, idx)

            # Remove alpha channel if present (convert BGRA to BGR)
            if needle_img.shape[-1] == 4:
                needle_img = cv.cvtColor(needle_img, cv.COLOR_BGRA2BGR)

            logger.debug("%s: %s %s", vision_mode, needle_img, needle_dim)

            # Convert images to same type if necessary
            if haystack_img.dtype != needle_img.dtype:
                needle_img = needle_img.astype(haystack_img.dtype)

            # Ensure both images are in BGR format
            if len(haystack_img.shape) == 2:
                haystack_img = cv.cvtColor(haystack_img, cv.COLOR_GRAY2BGR)
            if len(needle_img.shape) == 2:
                needle_img = cv.cvtColor(needle_img, cv.COLOR_GRAY2BGR)

            # Normalize images to improve matching
            haystack_img_norm = cv.normalize(haystack_img, None, 0, 255, cv.NORM_MINMAX)
            needle_img_norm = cv.normalize(needle_img, None, 0, 255, cv.NORM_MINMAX)

            # Check if the haystack image is larger than the needle image
            if (
                haystack_img.shape[0] < needle_img.shape[0]
                or haystack_img.shape[1] < needle_img.shape[1]
            ):
                raise RegionSizeError(
                    f"Detection {vision_mode} Error: Region is smaller than Detection Region please make a larger Area."
                )

            # Run the OpenCV algorithm with normalized images
            try:
                result = cv.matchTemplate(
                    haystack_img_norm, needle_img_norm, self.method
                )
                detection_treshhold = max(
                    min(threshold / 100, 1.0), 0.1
                )  # Ensures value between 0.1 and 1.0

            except Exception as e:
                logger.error("Detection %s Error: %s", vision_mode, e)
                # pylint: disable=raise-missing-from
                raise ScreenshotError(
                    f"Detection {vision_mode} Error: Something went wrong"
                )

            # Get the positions from the match result that exceed our threshold
            locations = np.where(result >= detection_treshhold)
            locations = list(zip(*locations[::-1]))

            # You'll notice a lot of overlapping rectangles get drawn.
            rectangles = []
            for loc in locations:
                rect = [int(loc[0]), int(loc[1]), needle_dim[0], needle_dim[1]]
                # Add every box to the list twice to retain single (non-overlapping) boxes
                rectangles.append(rect)
                rectangles.append(rect)

            # Apply group rectangles.
            rectangles, _ = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.5)

            points = []
            if len(rectangles):
                # Loop over all the rectangles
                for x, y, w, h in rectangles:
                    # Determine the center position
                    center_x = x + int(w / 2)
                    center_y = y + int(h / 2)
                    # Save the points
                    points.append((center_x, center_y))
                    if self.debug_mode or self.debug_mode_faction:
                        # Ensure the image is writable
                        haystack_img = haystack_img.copy()
                        # Determine the box position
                        top_left = (x, y)
                        bottom_right = (x + w, y + h)
                        # Draw the box
                        try:
                            cv.rectangle(
                                haystack_img,
                                top_left,
                                bottom_right,
                                color=color,
                                lineType=cv.LINE_4,
                                thickness=2,
                            )
                        except Exception as e:
                            logger.error("Rectangle Error: %s", e)

            all_points.extend(points)
        return all_points, haystack_img

    def find(self, haystack_img, threshold=0.5):
        all_points, detection_image = self.vision_process(
            haystack_img, threshold, "Enemy"
        )

        if self.debug_mode:
            cv.imshow("Enemy Vision", detection_image)
            self.enemy = True
            cv.waitKey(1)
        else:
            if self.enemy:
                cv.destroyWindow("Enemy Vision")
                self.enemy = None
        return all_points

    def find_faction(self, haystack_img, threshold=0.5):
        all_points, detection_image = self.vision_process(
            haystack_img, threshold, "Faction"
        )

        if self.debug_mode_faction:
            cv.imshow("Faction Vision", detection_image)
            self.faction = True
            cv.waitKey(1)
        else:
            if self.faction:
                cv.destroyWindow("Faction Vision")
                self.faction = None
        return all_points
