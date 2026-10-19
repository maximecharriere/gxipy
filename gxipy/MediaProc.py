from ctypes import c_void_p, byref
from gxipy.gxwrapper import *
from gxipy.StatusProcessor import *

class VideoSaver:
    handle_c = c_void_p()

    """
    :brief:     record the video
    :param      record_param:       Video information , See detail in GxRecordParam
    :return:    None
    """
    def __init__(self, record_param):
        status = gx_create_recorder(record_param, byref(self.handle_c))
        StatusProcessor.process(status, 'VideoSaver', '__init__')
    
    def add_frame(self, image_buffer):
        """
        :brief:     Add video frames
        :param      image_buffer:       Image buffer
        :return:    None
        """
        status = gx_add_frame(self.handle_c, image_buffer)
        StatusProcessor.process(status, 'VideoSaver', 'add_frame')

    def close(self):
        """
        :brief:      Stop recording
        :return:    None
        """
        status = gx_destroy_recorder(self.handle_c)
        StatusProcessor.process(status, 'VideoSaver', 'close')


class MediaProc:
    """
    :brief:     Save image
    :param      stSaveImageInfo:       Image information , See detail in GxSaveImageInfo
    :return:    None
    """
    def save_image(self, stSaveImageInfo):
        status = gx_save_image(stSaveImageInfo)
        StatusProcessor.process(status, 'MediaProc', 'save_image')
    
    """
    :brief:     Create video
    :param      record_param:       Video information , See detail in GxRecordParam
    :return:    None
    """
    def create_video_saver(self, record_param):
        return VideoSaver(record_param)