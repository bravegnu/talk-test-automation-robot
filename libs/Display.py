#!/usr/bin/env python3
from SSHLibrary import SSHLibrary
from robot.api.deco import keyword
from ScreenCapture import ScreenCapture
import OCRLib

class Display:
    def __init__(self):
        self.ssh = SSHLibrary()
        self.screencapture = ScreenCapture()
        self.ocrlib = OCRLib
        self.open_connection = None
        self.tempfile = "/tmp/capture-buffer.png"
        self.output_image = "capture-image.png"

    def _copy_file(self, img):
        self.ssh.get_file(self.tempfile, img)

    @keyword("Configure RPI")
    def configure_rpi(self, hostname, username, password):
        self.open_connection = self.ssh.open_connection(hostname)
        self.ssh.login(username, password)

    @keyword("Crop")
    def crop(self, source_image, speedgauge_region):
        x, y, height, width = speedgauge_region
        self.screencapture.crop_image(x, y, height, width, source_image)

    @keyword("Take Screenshot")
    def take_screenshot(self, shutter_speed: int=10000):
        cmd = f"rpicam-still --autofocus-mode manual --lens-position 6 -o {self.tempfile} -t 5 --shutter {shutter_speed}"
        self.ssh.execute_command(cmd)
        self._copy_file(self.output_image)
        self.screencapture.initialize_capture_screen(self.output_image, 1000, 1496)
        self.screencapture.capture_screen()

    @keyword("Ocr")
    def ocr(self, file_name: str):
        text = self.ocrlib.image_to_text(file_name)
        return str(text).strip(' ')
 
