import logging
from datetime import datetime

import cv2 as cv
import numpy as np

logger = logging.getLogger("alert")
now = datetime.now()


class Vision:

    # properties
    needle_img = None
    needle_w = 0
    needle_h = 0
    method = None

    # constructor
    def __init__(self, needle_img_paths, method=cv.TM_CCOEFF_NORMED):
        # Load the images we're trying to match
        self.needle_imgs = [
            cv.imread(path, cv.IMREAD_UNCHANGED) for path in needle_img_paths
        ]

        # Save the dimensions of the needle images
        self.needle_dims = [(img.shape[1], img.shape[0]) for img in self.needle_imgs]

        # There are 6 methods to choose from:
        # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
        self.method = method
        self.debug_mode = False
        self.debug_mode_faction = False
        self.enemy = None
        self.faction = None

    def find(self, haystack_img, threshold=0.5):
        all_points = []
        color = (0, 255, 0)
        for needle_img, needle_dim in zip(self.needle_imgs, self.needle_dims):
            # Ensure both images have the same type and depth
            if haystack_img.dtype != needle_img.dtype:
                print(
                    "Detection Error: The Region Image doesn't match the formats please use png."
                )
                logger.error(
                    "Detection Error: The Region Image doesn't match the formats please use png."
                )
                needle_img = needle_img.astype(haystack_img.dtype)

            # Check if the haystack image is larger than the needle image
            if (
                haystack_img.shape[0] < needle_img.shape[0]
                or haystack_img.shape[1] < needle_img.shape[1]
            ):
                print(
                    "Detection Error: Region is smaller than Detection Region please make a larger Area."
                )
                logger.error(
                    "Detection Error: Region is smaller than Detection Region please make a larger Area."
                )
                return "Error"

            # Run the OpenCV algorithm
            try:
                result = cv.matchTemplate(haystack_img, needle_img, self.method)
            except Exception as e:
                logger.error("Alert Region Error: %s", e)
                print("Something went wrong please set the Alert Region new")
                return "Error"

            # Get the positions from the match result that exceed our threshold
            locations = np.where(result >= threshold)
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

        if self.debug_mode:
            cv.imshow("Enemy Vision", haystack_img)
            self.enemy = True
            cv.waitKey(1)
        else:
            if self.enemy:
                cv.destroyWindow("Enemy Vision")
                self.enemy = None

        if self.debug_mode_faction:
            cv.imshow("Faction Vision", haystack_img)
            self.faction = True
            cv.waitKey(1)
        else:
            if self.faction:
                cv.destroyWindow("Faction Vision")
                self.faction = None
        return all_points
