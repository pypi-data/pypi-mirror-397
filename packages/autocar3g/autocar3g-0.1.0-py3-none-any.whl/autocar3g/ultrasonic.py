import struct
import time
from autocar3g.absclient import AbstractPopClient

class Ultrasonic(AbstractPopClient):
    def __init__(self, wait=True):
        super().__init__()
        self._client.subscribe(self._TOPIC_HEADER + '/ultra')
        self.__value = None
        self.__wait = wait

    def _decode(self, message):
        self.__value = tuple(struct.unpack("<ii", message.payload))

    def read(self):
        while self.__value is None and self.__wait: time.sleep(0.01)
        value = self.__value
        self.__value = None
        return value
