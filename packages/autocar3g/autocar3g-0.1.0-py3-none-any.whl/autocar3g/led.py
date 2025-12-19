import struct
import time
from autocar3g.absclient import AbstractPopClient

class Led(AbstractPopClient):
    def __init__(self, wait=True):
        super().__init__()
        self._client.subscribe(self._TOPIC_HEADER + '/drive/steering')

    def _decode(self, message):
        pass

    def onoff(self, front, rear):
        value = 0
        value += 1 if front else 0
        value += 2 if rear else 0
        self._client.publish(self._TOPIC_HEADER+"/lamp/set", struct.pack('<i', value), 0)