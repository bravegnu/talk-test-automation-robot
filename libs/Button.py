from robot.api.deco import keyword
from  parrot.RelayController import RelayController
from time import sleep

class Button:
    
    ROBOT_LIBRARY_SCOPE = 'TEST'

    def __init__(self):
        self.button = RelayController()
    
    @keyword("Connect to Relay")
    def connect_to_relay(self, device: str):
        self.button.relay_connect(device=device)

    def _click_button(self, button: str):
        if button == "ESC":
            self.button.relay_on(8)
        elif button == "Up":
            self.button.relay_on(7)
        elif button == "Down":
            self.button.relay_on(6)
        elif button == "OK":
            self.button.relay_on(5)

    def _release_button(self, button: str):
        if button == "ESC":
            self.button.relay_off(8)
        elif button == "Up":
            self.button.relay_off(7)
        elif button == "Down":
            self.button.relay_off(6)
        elif button == "OK":
            self.button.relay_off(5)

    @keyword("Long Press")
    def long_press(self, button: str):
        self._click_button(button)
        sleep(3)
        self._release_button(button)

    @keyword("Short Press")
    def short_press(self, button: str):
        self._click_button(button)
        sleep(0.5)
        self._release_button(button)

    @keyword("Turn ON DUT")
    def turn_on_dut(self):
        self.button.relay_on(4)

    @keyword("Turn OFF DUT")
    def turn_off_dut(self):
        self.button.relay_off(4)