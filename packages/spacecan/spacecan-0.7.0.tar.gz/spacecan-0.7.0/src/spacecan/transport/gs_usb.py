import threading

import can

from ..primitives.can_frame import CanFrame
from .base import Bus


class GsUsbBus(Bus):
    def __init__(self, parent, channel):
        super().__init__(parent)
        self.channel = channel
        self._bus = can.Bus(interface="gs_usb", channel=self.channel, bitrate=500000)
        self._thread = None
        self._stop_event = threading.Event()

    def disconnect(self):
        self._bus.shutdown()

    def set_filters(self, filters):
        self._bus.set_filters(filters)

    def send(self, can_frame):
        msg = can.Message(
            arbitration_id=can_frame.can_id, data=can_frame.data, is_extended_id=False
        )
        try:
            self._bus.send(msg)
        except can.exceptions.CanOperationError:
            pass

    def start_receive(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._receive)
        self._thread.start()

    def stop_receive(self):
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join()

    def _receive(self):
        while not self._stop_event.is_set():
            msg = self._bus.recv(0.1)
            if self._stop_event.is_set():
                break
            if msg:
                can_frame = CanFrame(msg.arbitration_id, msg.data)
                self.frame_buffer.put(can_frame)
