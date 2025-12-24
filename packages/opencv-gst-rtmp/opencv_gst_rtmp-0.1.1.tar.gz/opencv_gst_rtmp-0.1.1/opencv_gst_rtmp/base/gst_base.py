import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

from abc import ABC, abstractmethod
import gi
import threading
from ..utils.thread_utils import ThreadUtilities

gi.require_version('Gst', '1.0')

from ..config.logging_config import LogConfig
log_config = LogConfig(__name__)
logger = log_config.logger

class GstBase(ABC):
    pipeline: Gst.Pipeline = None
    thread: threading.Thread = None
    main_loop: GLib.MainLoop = None

    def __init__(self):
        super().__init__()
        Gst.init(None)
        self.pipeline = Gst.Pipeline()
        self.create_element()

    @abstractmethod
    def create_element(self):
        pass

    def start(self):
        if self.main_loop is None or not self.main_loop.is_running():
            self.pipeline.set_state(Gst.State.READY)
            self.pipeline.set_state(Gst.State.PLAYING)

            self.main_loop = GLib.MainLoop()
            self.main_loop.run()
        else:
            logger.debug("Main loop has already been run")

    def start_background(self) -> threading.Thread:
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.start)
            self.thread.setDaemon(True)
            self.thread.start()
        else:
            logger.debug("Thread has already been started")
        return self.thread
    
    def stop(self):
        if self.main_loop and self.main_loop.is_running():
            self.main_loop.quit()
        else:
            logger.debug("Main loop has already been quit")
        
        if self.thread:
            try:
                ThreadUtilities.async_raise(self.thread.ident)
            except:
                logger.error("Stop thread failed", exc_info=True)
        else:
            logger.debug("self.thread null")