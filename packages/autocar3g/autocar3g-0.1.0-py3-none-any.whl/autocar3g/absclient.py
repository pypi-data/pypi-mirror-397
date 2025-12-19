import paho.mqtt.client as mqtt
from threading import Thread, Lock, Event
import time, os, signal, traceback

product_file_path = "product"

TIMEOUT_SEC = 5

class AbstractPopClient:
    with open(product_file_path, 'r') as file:
        BROKER_DOMAIN = None
        DEV_NUM = None
        DEV_NAME = None
        INSITUTION_NAME = None
        for line in file:
            line = line.strip()
            if line.startswith('BROKER_DOMAIN='):
                BROKER_DOMAIN = line.split('=')[1].strip()
            if line.startswith('DEV_NUM='):
                DEV_NUM = line.split('=')[1].strip()
            if line.startswith('DEVICE_NAME='):
                DEV_NAME = line.split('=')[1].strip()
            if line.startswith('INSITUTION_NAME='):
                INSITUTION_NAME = line.split('=')[1].strip()
        if BROKER_DOMAIN is None:
            raise ValueError("[Error] There is no product file. Please make sure the device has product info")

    def __init__(self):
        self.__update_lock = Lock()
        self.__update_time_tag = time.time()
        self.__close_event = Event()

        self._TOPIC_HEADER = __class__.DEV_NAME + '/' + __class__.INSITUTION_NAME + __class__.DEV_NUM
        self._client = mqtt.Client()
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.connect(__class__.BROKER_DOMAIN)
        self._client_enabled = False
        self._client.loop_start()

        wait_time_tag = time.time()
        while not self._client_enabled:
            if time.time() - wait_time_tag > 4:
                raise TimeoutError("Please check the broker connection state.")

    def __connection_check(self):
        try:
            while True:
                if self.__close_event.set():
                    break
                self.__update_lock.acquire()
                if time.time() - self.__update_time_tag > TIMEOUT_SEC:
                    raise ConnectionError()
                self.__update_lock.release()
                time.sleep(1)
        except ConnectionError:
            traceback.print_exc()
            os.kill(os.getpid(), signal.SIGINT)
            
    def _on_connect(self, client, userdata, flags, rc):
        self.__connection_check_thread = Thread(target=self.__connection_check, daemon=True)
        self.__connection_check_thread.start()
        self._client_enabled = True

    def _on_message(self, client, userdata, message):
        self.__update_lock.acquire()
        self.__update_time_tag = time.time()
        self.__update_lock.release()
        self._decode(message)

    def _decode(self, message):
        raise NotImplementedError()