import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

from ..base.opencv_gst_rtmp import OpenCVGSTRTMP

from ..config.logging_config import LogConfig
log_config = LogConfig(__name__)
logger = log_config.logger

class OpenCVFrameGSTRTMP(OpenCVGSTRTMP):
    def __init__(self, rtmp_url: str, width: int, height: int, fps: int, channel: int = 3, use_gpu: bool = False):
        super().__init__(rtmp_url=rtmp_url, width=width, height=height,
                         channel=channel, fps=fps, use_gpu=use_gpu)

    def set_frame(self, frame):
        self.frame = frame

    def on_need_data(self, src, length: int):
        if self.frame is not None:
            data = self.frame.tostring()

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
            logger.debug(retval)
            if retval != Gst.FlowReturn.OK:
                logger.debug(retval)
            return True
