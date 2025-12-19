import struct
import math
import time
from autocar3g.absclient import AbstractPopClient

class LiDAR(AbstractPopClient):
    def __init__(self, wait=True):
        super().__init__()
        self._client.subscribe(self._TOPIC_HEADER + '/scan')
        self.__value = None
        self.__wait = wait

    def _decode(self, message):
        header_ffi = '<ffI'
        header_size = struct.calcsize(header_ffi)

        angle_min, angle_increment, n = struct.unpack(
            header_ffi, message.payload[:header_size]
        )

        ranges_fmt = '<{}f'.format(n)
        ranges = struct.unpack(
            ranges_fmt, message.payload[header_size:]
        )

        self.__value = {
            'angle_min' : angle_min,
            'angle_increment' : angle_increment,
            'ranges' : ranges
        }

    def read(self):
        while self.__value is None and self.__wait : time.sleep(0.01)
        value = self.__value
        self.__value = None
        return value