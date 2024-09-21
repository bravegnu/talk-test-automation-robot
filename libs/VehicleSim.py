import can
import time
import threading

from robot.api.deco import keyword

class Error(Exception):
    pass


class VehicleSim:
    def __init__(self):
        self._bus = None
        self._thread = None
        self._channel = None
        self._stop = False
        self._params = {"speed": 0}
        self._valid_params = {"speed"}

    def set_channel(self, channel: str):
        print(self._channel)
        self._channel = channel

    def start_vehicle_simulation(self):
        self._bus = can.Bus(interface="socketcan", channel=self._channel,
                            bitrate=5000, receive_own_messages=True)
        self._thread = threading.Thread(target=self._simulation_task)
        self._thread.start()

    def stop_vehicle_simulation(self):
        self._stop = True
        if self._thread is not None:
            self._thread.join()
            self._bus.shutdown()

    def set_vehicle_param(self, param: str, value: int):
        if param in self._params:
            self._params[param] = value
        else:
            raise Error("Invalid vehicle param {}".format(param))

    def _simulation_task(self):
        while not self._stop:
            msg = self._bus.recv(timeout=1)
            resp = None
            print(f"Recv: {msg}")
            if msg is None:
                continue

            if msg.arbitration_id != 0x7E0:
                continue

            if msg.data[1] != 0x01:
                continue

            if msg.data[2] == 0x00:
                resp = [0x06, 0x41, 0x00, 0xFF, 0xFF, 0xFF, 0xFF]

            if msg.data[2] == 0x0D:
                resp = [0x03, 0x41, 0x0D, self._params["speed"]]

            if msg.data[2] == 0x0C:
                resp = [0x04, 0x41, 0x0C, 0xFF, 0xFF]

            if resp is not None:
                print("Send: ", resp)
                resp_msg = can.Message(arbitration_id=0x7E8, data=resp, is_extended_id=False)
                self._bus.send(resp_msg)


if __name__ == "__main__":
    sim = VehicleSim("vcan0")
    sim.start_simulation()
    sim.set_param("speed", 10)
    time.sleep(10)
    sim.stop_simulation()
