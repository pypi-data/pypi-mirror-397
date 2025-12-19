import struct
import time
from autocar3g.absclient import AbstractPopClient

class Driving(AbstractPopClient):
    def __init__(self, wait=True):
        super().__init__()
        self._client.subscribe(self._TOPIC_HEADER + '/drive/steering')
        self._client.subscribe(self._TOPIC_HEADER + '/drive/throttle')
        self._client.subscribe(self._TOPIC_HEADER+'/int')
        self.__steering_value = None
        self.__throttle_value = None
        self.__wait = wait

    def _decode(self, message):
        if 'steering' in message.topic:
            self.__steering_value = struct.unpack("<f", message.payload)[0]
        elif 'throttle' in message.topic:
            self.__throttle_value = struct.unpack("<i", message.payload)[0]
        else:
            print(message.payload)

    @property
    def steering(self):
        while self.__steering_value is None and self.__wait: time.sleep(0.01)
        value = self.__steering_value
        self.__steering_value = None
        return value

    @steering.setter
    def steering(self, value:float):
        if value < -1.0 or value > 1.0:
            raise ValueError("Wrong steering value.")
        self._client.publish(self._TOPIC_HEADER+"/drive/set", struct.pack('<fi', value, self.throttle), 0)

    @property
    def throttle(self):
        while self.__throttle_value is None and self.__wait: time.sleep(0.01)
        value = self.__throttle_value
        self.__throttle_value = None
        return value

    @throttle.setter
    def throttle(self, value:int):
        if value < -99 or value > 99:
            raise ValueError("Wrong throttle value.")
        self._client.publish(self._TOPIC_HEADER+"/drive/set", struct.pack('<fi', self.steering, value), 0)