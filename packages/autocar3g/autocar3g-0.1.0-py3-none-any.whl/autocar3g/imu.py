import struct
import math
import time
from autocar3g.absclient import AbstractPopClient

_BNO055_QUAT_SCALE = 1.0 / (1 << 14)

class Imu(AbstractPopClient):
    def __init__(self, wait=True):
        super().__init__()
        self._client.subscribe(self._TOPIC_HEADER + '/imu')
        self.__accel_value = None
        self.__magnetic_value = None
        self.__gyro_value = None
        self.__quat_value = None
        self.__wait = wait

    def _decode(self, message):
        unpacked = struct.unpack('<13d', message.payload)
        self.__accel_value = tuple(unpacked[0:3])
        self.__magnetic_value = tuple(unpacked[3:6])
        self.__gyro_value = tuple(unpacked[6:9])
        self.__quat_value = tuple(unpacked[9:13])

    def accel(self):
        while self.__accel_value is None and self.__wait : time.sleep(0.01)
        value = self.__accel_value
        # self.__accel_value = None
        return value

    def magnetic(self):
        while self.__magnetic_value is None and self.__wait : time.sleep(0.01)
        value = self.__magnetic_value
        return value

    def gyro(self):
        while self.__gyro_value is None and self.__wait : time.sleep(0.01)
        value = self.__gyro_value
        # self.__gyro_value = None
        return value
    
    def euler(self):
        qw,qx,qy,qz = self.quat()
        
        w = qw * _BNO055_QUAT_SCALE
        x = qx * _BNO055_QUAT_SCALE
        y = qy * _BNO055_QUAT_SCALE
        z = qz * _BNO055_QUAT_SCALE

        norm = math.sqrt(w*w + x*x + y*y + z*z)
        if norm == 0.0:
            return 0.0, 0.0, 0.0
        w /= norm
        x /= norm
        y /= norm
        z /= norm

        sinr_cosp = 2.0 * (w * x + y * z)
        cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        sinp = 2.0 * (w * y - z * x)
        if abs(sinp) >= 1.0:
            pitch = math.copysign(math.pi / 2.0, sinp)
        else:
            pitch = math.asin(sinp)

        siny_cosp = 2.0 * (w * z + x * y)
        cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        roll_deg = math.degrees(roll)
        pitch_deg = math.degrees(pitch)
        yaw_deg = math.degrees(yaw)

        return (roll_deg, pitch_deg, yaw_deg)

    def quat(self):
        while self.__quat_value is None and self.__wait : time.sleep(0.01)
        value = self.__quat_value
        # self.__quat_value = None
        return value