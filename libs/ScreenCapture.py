"""
Importing library for arUco-marker to take screen capture.
"""
import cv2
import imutils
import numpy as np
import os
import base64
from robot.api.deco import keyword
from robot.api import logger

class Error(Exception):
    """
    ArUco Exception Error Handler.
    """
    pass

class ScreenCapture:

    """
    ScreenCapture Module provides keywords for capture screen by initializing the screen.

    """
    ROBOT_AUTO_KEYWORDS = False
    ROBOT_LIBRARY_SCOPE = 'TEST'

    def __init__(self) -> None:
        self.cap = None
        self.height = None
        self.width = None
        self.original_image = None
        self.copy_img = None
        self.count = None
        self.cropped_points = None
        self.aruco_ids = None
        self.top_left_id = None
        self.top_right_id = None
        self.bottom_left_id = None
        self.bottom_right_id = None
        self.source = None

    def _order_points(self, pts):

        # Initialzie a list of coordinates that will be ordered
        # such that the first entop_righty in the list is the top-left,
        # the second entop_righty is the top-right, the third is the
        # bottom-right, and the fourth is the bottom-left.

        rect = np.zeros((4, 2), dtype="float32")

        # The top-left point will have the smallest sum, whereas
        # the bottom-right point will have the largest sum.

        smallest_sum = pts.sum(axis=1)
        rect[0] = pts[np.argmin(smallest_sum)]
        rect[2] = pts[np.argmax(smallest_sum)]

        # Now, compute the difference between the points, the
        # top-right point will have the smallest difference,
        # whereas the bottom-left will have the largest difference.

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        # return the ordered coordinates
        return rect

    def _four_point_top_rightansform(self, pts):
        """
        Obtain a consistent order of the points and unpack them
        individually.
        """
        rect = self._order_points(pts)
        (top_left, top_right, bottom_right, bottom_left) = rect

        # compute the width of the new image, which will be the
        # maximum distance between bottom-right and bottom-left
        # x-coordiates or the top-right and top-left x-coordinates.

        width_a = np.sqrt(((bottom_right[0] - bottom_left[0]) ** 2) +
                          ((bottom_right[1] - bottom_left[1]) ** 2))
        width_b = np.sqrt(((top_right[0] - top_left[0]) ** 2) +
                          ((top_right[1] - top_left[1]) ** 2))
        max_width = max(int(width_a), int(width_b))

        # compute the height of the new image, which will be the
        # maximum distance between the top-right and bottom-right
        # y-coordinates or the top-left and bottom-left y-coordinates.

        height_a = np.sqrt(((top_right[0] - bottom_right[0]) ** 2) +
                           ((top_right[1] - bottom_right[1]) ** 2))
        height_b = np.sqrt(((top_left[0] - bottom_left[0]) ** 2) +
                           ((top_left[1] - bottom_left[1]) ** 2))
        max_height = max(int(height_a), int(height_b))


        # Now that we have the dimensions of the new image, constop_rightuct
        # the set of destination points to obtain a "birds eye view",
        # (i.e. top-down view) of the image, again specifying points
        # in the top-left, top-right, bottom-right, and bottom-left
        # order.

        dst = np.array([
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1]], dtype="float32")

        # compute the perspective top_rightansform matop_rightix and then apply it
        actual_matrix = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(self.copy_img, actual_matrix, (max_width, max_height))

        # return the warped image
        return warped

    def _get_coordinates(self):
        # load the input image from disk and resize it

        # load the ArUCo dictionary, grab the ArUCo parameters, and
        # attempt to detect the markers for the current dictionary.

        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_1000)
        aruco_params = cv2.aruco.DetectorParameters()
        (corners, ids, _) = cv2.aruco.detectMarkers(
            self.original_image, aruco_dict, parameters=aruco_params)

        crop_coordinates = []
        # if at least one ArUco marker was detected display the ArUco name to our terminal
        if len(corners) == 4:
            # print("[INFO] detected {} markers for '{}'".format(len(corners)))

            crop_coordinates.append(corners[0][0][0])
            crop_coordinates.append(corners[1][0][0])
            crop_coordinates.append(corners[2][0][0])
            crop_coordinates.append(corners[3][0][0])

            # Check all the detected ids are same as the given aruco ids.
            check = all(item in ids for item in self.aruco_ids)
            if check is True:
                # Draw the detected markers on the image
                cv2.aruco.drawDetectedMarkers(self.original_image, corners, self.aruco_ids)
                print("Aruco Markers Detected")
            else:
                raise Error

        # Display the image with detected markers
        return crop_coordinates

    def _detect_aruco_marker(self):
        self.copy_img = self.original_image.copy()
        points = self._get_coordinates()
        return points

    @keyword("Check Length of Coordinates")
    def  check_length_of_coordinates(self, points):
        """
        Checking the Length of Coordinates of the Detected Aruco Markers Ids.
        """
        image = imutils.resize(self.original_image, height=500)
        if len(points) == 4:
            cropped_image = np.array(points, np.int32)
            ratio = image.shape[0] / 500.0
            re_shape = cropped_image.reshape(4, 2)
            warped = self._four_point_top_rightansform(re_shape * ratio)
            image = imutils.resize(warped, height=500)
        resized = cv2.resize(image, (self.width, self.height))
        return resized

    @keyword("Initialize Capture Screen")
    def initialize_capture_screen(self, source: str, height: int, width: int,
                                  aruco_ids=[87, 42, 24, 66]):
        """
        Initialize to setup the Android webcam with Specified system.
        Using the  cv2. VideoCapture() method is a function the OpenCV library provides for
        reading video input from a camera or a file.
            - source : webcam app endpoint url or UVC device or video file.
            - height : Required height  of the  cropped arUco image.
            - width  : Required width  of the  cropped arUco image.

       *Raises*

        _Error_ - Raises exception when Connection Failed.
        """
        self.height = height
        self.source = source
        self.width = width
        self.aruco_ids = np.array(aruco_ids)
        self.top_left_id = aruco_ids[0]
        self.top_right_id = aruco_ids[1]
        self.bottom_left_id = aruco_ids[2]
        self.bottom_right_id = aruco_ids[3]
        self.cap = cv2.VideoCapture(source)

    @keyword("Capture Screen")
    def capture_screen(self, filename: str='final-image.png') -> list:
        """
        Function to detect the arUco
        """
        # Reinitializing Videocapture for getting latest frame from the source.
        self.cap.open(self.source)
        ret, self.original_image = self.cap.read()
        if ret:
            print("Capture Device Initialized")
        else:
            raise Error("Connection Failed")
        self.cropped_points = self._detect_aruco_marker()
        img = self.check_length_of_coordinates(self.cropped_points)
        if filename:
            cv2.imwrite(filename, img)
            print(f"Image Saved as {filename}")
        # self._log_image(img, 300, 200)
        return img

    def _log_image(self, image="", width: str = "500", height: str = "300") -> bool:
        """
        Convert the image file into the HTML format and log.
        """
        if not image:
            image = "crop-image.png"
        with open(image, "rb") as file:
            encoded_image = base64.b64encode(file.read())
            decode = encoded_image.decode()
            html_img = f'data:image/png;base64,{decode}'
            image_source = f'<img src={html_img} width={width} height={height}>'
            logger.write(image_source, html=True)
            return True

    def _check_image(self, image):
        """
        Check the image is exists or not.

        Args:
            image (str): Path of the image to check.
        """
        if not os.path.exists(image):
            raise Error(f"Invalid File, check the {image}")

    def crop_image(self, x_coord: int, y_coord: int, width: int, height: int,
                               source_img="capture-image.png"):
        """
        Set region of interest by giving x-coordinate, y-coordinate,
        width and height of the required area of interest

        Args:
            x_coord (int): x-coordinate
            y_coord (int): y-coordinate
            width (int): width of the required area.
            height (int): height of the required area.
        """
        self._check_image(source_img)
        image = cv2.imread(source_img)
        region_of_interest = image[y_coord:height+y_coord, x_coord:width+x_coord]
        cv2.imwrite("crop-image.png", region_of_interest)
        self._log_image("crop-image.png", 300, 200)
