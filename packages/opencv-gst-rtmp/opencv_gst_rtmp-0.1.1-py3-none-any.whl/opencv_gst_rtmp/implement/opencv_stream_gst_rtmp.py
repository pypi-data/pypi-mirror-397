import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

from ..base.opencv_gst_rtmp import OpenCVGSTRTMP
import cv2

from ..config.logging_config import LogConfig
log_config = LogConfig(__name__)
logger = log_config.logger

class OpenCVStreamGSTRTMP(OpenCVGSTRTMP):
    def __init__(self, rtmp_url: str, stream_link: str, channel: int = 3, use_gpu: bool = False):
        if stream_link.isnumeric():
            self.stream_link = int(stream_link)
        else:
            self.stream_link = stream_link
        self.use_gpu = use_gpu
        self.cap = cv2.VideoCapture(self.stream_link)

        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.width = self.width if self.width > 0 else 1920

        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.height = self.height if self.height > 0 else 1080

        self.channel = channel
        
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.fps = self.fps if  60 > self.fps > 0 else 30

        self.duration = 1 / self.fps * Gst.SECOND  # duration of a frame in nanoseconds
        logger.debug(f"self.width = {self.width}, self.height = {self.height}, self.channel = {self.channel}, self.fps = {self.fps}, self.duration = {self.duration}")

        super().__init__(rtmp_url=rtmp_url, width=self.width, height=self.height,
                         channel=self.channel, fps=self.fps, use_gpu=use_gpu)

    def on_need_data(self, src, length: int):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                data = frame.tostring()
                buf = Gst.Buffer.new_allocate(None, len(data), None)
                buf.fill(0, data)
                buf.duration = self.duration
                timestamp = self.frame_num * self.duration
                buf.pts = buf.dts = int(timestamp)
                buf.offset = timestamp
                self.frame_num += 1
                retval = src.emit('push-buffer', buf)
                logger.debug('pushed buffer, frame {}, duration {} ns, durations {} s'.format(self.frame_num,
                                                                                       self.duration,
                                                                                       self.duration / Gst.SECOND))
                if retval != Gst.FlowReturn.OK:
                    logger.debug(retval)
