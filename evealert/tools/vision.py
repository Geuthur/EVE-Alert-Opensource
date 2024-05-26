import logging
from datetime import datetime

import cv2 as cv
import numpy as np

logger = logging.getLogger("alert")
now = datetime.now()


class Vision:

    draw_rectangle = False
    # properties
    needle_img = None
    needle_w = 0
    needle_h = 0
    method = None

    # constructor
    def __init__(self, needle_img_paths, vision_name):

        self.vision_name = vision_name
        self.window_created = False
        # Load the images we're trying to match
        self.needle_imgs = [
            cv.imread(path, cv.IMREAD_UNCHANGED) for path in needle_img_paths
        ]

        # Save the dimensions of the needle images
        self.needle_dims = [(img.shape[1], img.shape[0]) for img in self.needle_imgs]

        # There are 6 methods to choose from:
        # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
        self.method = cv.TM_CCOEFF_NORMED

    def find(self, haystack_img, show_vision = False, threshold=0.5):
        threshold = threshold / 100 if threshold > 1 else threshold
        all_points = []
        color = (0, 255, 0)
        for needle_img, needle_dim in zip(self.needle_imgs, self.needle_dims):
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

            # Copy the image to draw on
            haystack_img = haystack_img.copy()

            if show_vision:
                if not self.window_created:
                    cv.namedWindow(f'Vision {self.vision_name}', cv.WINDOW_NORMAL)
                    self.window_created = True
                cv.imshow(f'Vision {self.vision_name}', haystack_img)
                cv.waitKey(1)
            elif self.window_created:
                cv.destroyWindow(f'Vision {self.vision_name}')
                self.window_created = False

            points = []
            if len(rectangles):
                # Loop over all the rectangles
                for x, y, w, h in rectangles:
                    # Determine the center position
                    center_x = x + int(w / 2)
                    center_y = y + int(h / 2)
                    # Save the points
                    points.append((center_x, center_y))
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
                        logger.error("Reactangle Error: %s", e)

            all_points.extend(points)
        return all_points
