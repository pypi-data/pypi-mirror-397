import os
from threading import Lock

import logging
logger = logging.getLogger(__name__)
class ConfigMeta(type):
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class Config(metaclass=ConfigMeta):
    def __init__(self):
        if "OPENCV_GST_RTMP_LOG_LEVEL" in os.environ:
            self.OPENCV_GST_RTMP_LOG_LEVEL = os.environ["OPENCV_GST_RTMP_LOG_LEVEL"]
        else:
            self.OPENCV_GST_RTMP_LOG_LEVEL = "ERROR"
        logger.info(self.__dict__)
        