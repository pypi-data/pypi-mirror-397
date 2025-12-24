import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

from abc import abstractmethod

from ..exception.element_exception import ElementNotFoundException
from ..base.gst_base import GstBase

from ..utils.gst_utils import GstUtilities

from ..config.logging_config import LogConfig
log_config = LogConfig(__name__)
logger = log_config.logger

class OpenCVGSTRTMP(GstBase):
    width: int
    height: int
    channel: int = 3
    fps: int
    frame = None
    use_gpu: bool = False
    rtmp_url: str
    frame_num: int = 0

    def __init__(self, rtmp_url: str, width: int, height: int, fps: int, channel: int = 3, use_gpu: bool = False):
        self.rtmp_url = rtmp_url
        self.width = width
        self.height = height
        self.channel = channel
        self.fps = fps
        self.use_gpu = use_gpu
        self.duration = 1 / self.fps * Gst.SECOND
        self.src_format = 'BGR' if self.channel == 3 else 'BGRx'
        super().__init__()

    def create_element(self):
        if self.use_gpu:
            if GstUtilities.is_element_exist(element_name='nvvideoconvert'):
                gpu_videoconvert_element_name = 'nvvideoconvert'
            elif GstUtilities.is_element_exist(element_name='nvvidconv'):
                # NguyenNH: nvvidconv doesn't support 3 channel so have to use videoconvert to convert to 4 channel:
                if self.channel == 3:
                    gpu_videoconvert_element_name = 'videoconvert ! video/x-raw,format=BGRx ! nvvidconv'
                else:
                    gpu_videoconvert_element_name = 'nvvidconv'
            else:
                raise ElementNotFoundException(
                    element_name='nvvideoconvert, nvvidconv')

            self.videoconvert: str = f'{gpu_videoconvert_element_name} ! video/x-raw(memory:NVMM),format=NV12'

            if GstUtilities.is_element_exist(element_name='nvv4l2h264enc'):
                self.encoder: str = 'nvv4l2h264enc idrinterval=1'
            else:
                raise ElementNotFoundException(element_name=self.encoder)

        else:
            self.videoconvert: str = 'videoconvert ! video/x-raw,format=NV12'
            self.encoder: str = 'x264enc'

        self.parser = "h264parse"
        self.flvmux = 'flvmux streamable=true'
        self.queue = 'queue'
        self.rtmpsink = f'rtmpsink location={self.rtmp_url}'

        self.launch_string = 'appsrc format=time name=source ' \
            f'caps=video/x-raw,format={self.src_format},width={self.width},height={self.height},framerate={self.fps}/1 ' \
            f'! {self.videoconvert} ' \
            f'! {self.queue} ' \
            f'! {self.encoder} ' \
            f'! {self.queue} ' \
            f'! {self.parser} ' \
            f'! {self.queue} ' \
            f'! {self.flvmux} ' \
            f'! {self.queue} ' \
            f'! {self.rtmpsink} '

        logger.info(f"launch_string = {self.launch_string}")
        self.pipeline = Gst.parse_launch(self.launch_string)

        appsrc = self.pipeline.get_child_by_name("source")
        self.frame_num = 0
        appsrc.connect('need-data', self.on_need_data)

    @abstractmethod
    def on_need_data(self, src, length: int):
        pass
