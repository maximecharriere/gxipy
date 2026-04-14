#!/usr/bin/python
# -*- coding:utf-8 -*-
# -*-mode:python ; tab-width:4 -*- ex:set tabstop=4 shiftwidth=4 expandtab: -*-

import numpy
from gxipy.gxwrapper import *
from gxipy.dxwrapper import *
from gxipy.gxidef import *
from gxipy.gxiapi import *
from gxipy.StatusProcessor import *
from gxipy.Interface import *
from gxipy.Feature import *
from gxipy.Exception import *
from gxipy.ImageProc import *
import ctypes
import types

class DataStream:
    def __init__(self, dev_handle, stream_handle):
        """
        :brief  Constructor for instance initialization
        :param dev_handle:      Device handle
        :param stream_handle:   Device Stream handle
        """
        self.__dev_handle = dev_handle

        self.__c_capture_callback = CAP_CALL(self.__on_capture_callback)
        self.__py_capture_callback = None

        self.StreamAnnouncedBufferCount = IntFeature(self.__dev_handle, GxFeatureID.INT_ANNOUNCED_BUFFER_COUNT)
        self.StreamDeliveredFrameCount = IntFeature(self.__dev_handle, GxFeatureID.INT_DELIVERED_FRAME_COUNT)
        self.StreamLostFrameCount = IntFeature(self.__dev_handle, GxFeatureID.INT_LOST_FRAME_COUNT)
        self.StreamIncompleteFrameCount = IntFeature(self.__dev_handle, GxFeatureID.INT_INCOMPLETE_FRAME_COUNT)
        self.StreamDeliveredPacketCount = IntFeature(self.__dev_handle, GxFeatureID.INT_DELIVERED_PACKET_COUNT)
        self.StreamBufferHandlingMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_STREAM_BUFFER_HANDLING_MODE)
        self.payload_size = 0
        self.acquisition_flag = False
        self.__data_stream_handle = stream_handle
        self.__stream_feature_control = FeatureControl(stream_handle)
        self.__frame_buf_map = {}
        self.__register_buf_param_map = {}
        self.__register_buf_param_content_map = {}

    def get_feature_control(self):
        """
        :brief      Get device stream feature control object
        :return:    Device stream feature control object
        """
        return self.__stream_feature_control

    def get_payload_size(self):
        """
        :brief      Get device stream payload size
        :return:    Payload size
        """
        status, stream_payload_size = gx_get_payload_size(self.__data_stream_handle)
        StatusProcessor.process(status, 'DataStreamHandle', 'get_payload_size')
        return stream_payload_size

    def get_image(self, timeout=1000):
        """
        :brief          Get an image, get successfully create image class object
        :param          timeout:    Acquisition timeout, range:[0, 0xFFFFFFFF]
        :return:        image object
        """
        if not isinstance(timeout, INT_TYPE):
            raise ParameterTypeError("DataStream.get_image: "
                                     "Expected timeout type is int, not %s" % type(timeout))

        if (timeout < 0) or (timeout > UNSIGNED_INT_MAX):
            print("DataStream.get_image: "
                  "timeout out of bounds, minimum=0, maximum=%s"
                  % hex(UNSIGNED_INT_MAX).__str__())
            return None

        if self.acquisition_flag is False:
            print("DataStream.get_image: Current data steam don't  start acquisition")
            return None

        frame_data = GxFrameData()
        frame_data.image_size = self.payload_size
        frame_data.image_buf = None
        image = RawImage(frame_data)

        status = gx_get_image(self.__dev_handle, image.frame_data, timeout)
        if status == GxStatusList.SUCCESS:
            try:
                if sys.platform != 'linux2' and sys.platform != 'linux':
                    image.user_param = self.__register_buf_param_content_map[frame_data.user_param]
            except KeyError:
                image.user_param = None

            return image
        elif status == GxStatusList.TIMEOUT:
            return None
        else:
            StatusProcessor.process(status, 'DataStream', 'get_image')
            return None

    def dq_buf(self, timeout=1000):
        if not isinstance(timeout, INT_TYPE):
            raise ParameterTypeError("DataStream.dq_buf: "
                                     "Expected timeout type is int, not %s" % type(timeout))

        if (timeout < 0) or (timeout > UNSIGNED_INT_MAX):
            print("DataStream.get_image: "
                  "timeout out of bounds, minimum=0, maximum=%s"
                  % hex(UNSIGNED_INT_MAX).__str__())
            return None

        if self.__py_capture_callback != None:
            raise InvalidCall("Can't call dq_buf after register capture callback")

        if self.acquisition_flag is False:
            print("DataStream.get_image: Current data steam don't  start acquisition")
            return None

        ptr_frame_buffer = ctypes.POINTER(GxFrameBuffer)()
        status = gx_dq_buf(self.__dev_handle, ctypes.byref(ptr_frame_buffer), timeout)
        if status == GxStatusList.SUCCESS:
            frame_buffer = ptr_frame_buffer.contents
            self.__frame_buf_map[frame_buffer.buf_id] = ptr_frame_buffer
            frame_data = GxFrameData()
            frame_data.status = frame_buffer.status
            frame_data.image_buf = frame_buffer.image_buf
            frame_data.width = frame_buffer.width
            frame_data.height = frame_buffer.height
            frame_data.pixel_format = frame_buffer.pixel_format
            frame_data.image_size = frame_buffer.image_size
            frame_data.frame_id = frame_buffer.frame_id
            frame_data.timestamp = frame_buffer.timestamp
            frame_data.user_param = frame_buffer.user_param
            frame_data.buf_id = frame_buffer.buf_id

            if sys.platform == 'linux2' or sys.platform == 'linux':
                frame_data.offset_x = frame_buffer.offset_x
                frame_data.offset_y = frame_buffer.offset_y

            image = RawImage(frame_data)
            try:
                image.user_param = self.__register_buf_param_content_map[frame_data.user_param]
            except KeyError:
                image.user_param = None

            return image
        elif status == GxStatusList.TIMEOUT:
            return None
        else:
            StatusProcessor.process(status, 'DataStream', 'dq_buf')
            return None

    def q_buf(self, image):
        if not isinstance(image, RawImage):
            raise ParameterTypeError("DataStream.q_buf: "
                                     "Expected image type is RawImage, not %s" % type(image))

        if self.acquisition_flag is False:
            print("DataStream.q_buf: Current data steam don't  start acquisition")
            return

        if self.__py_capture_callback != None:
            raise InvalidCall("Can't call q_buf after register capture callback")

        ptr_frame_buffer = ctypes.POINTER(GxFrameBuffer)()
        try:
            ptr_frame_buffer = self.__frame_buf_map[image.frame_data.buf_id]
        except KeyError:
            print("Key {} not found in frame buffer map.".format(image.frame_data.buf_id))
            return

        status = gx_q_buf(self.__dev_handle, ptr_frame_buffer)
        StatusProcessor.process(status, 'DataStream', 'q_buf')
        self.__frame_buf_map.pop(image.frame_data.buf_id)

    def flush_queue(self):
        status = gx_flush_queue(self.__dev_handle)
        StatusProcessor.process(status, 'DataStream', 'flush_queue')

    # old call mode,Not recommended
    def set_payload_size(self, payload_size):
        self.payload_size = payload_size

    def set_acquisition_flag(self, flag):
        self.acquisition_flag = flag

    def set_acquisition_buffer_number(self, buf_num):
        """
        :brief      set the number of acquisition buffer
        :param      buf_num:   the number of acquisition buffer, range:[1, 0xFFFFFFFF]
        """
        if not isinstance(buf_num, INT_TYPE):
            raise ParameterTypeError("DataStream.set_acquisition_buffer_number: "
                                     "Expected buf_num type is int, not %s" % type(buf_num))

        if (buf_num < 1) or (buf_num > UNSIGNED_LONG_LONG_MAX):
            print("DataStream.set_acquisition_buffer_number:"
                  "buf_num out of bounds, minimum=1, maximum=%s"
                  % hex(UNSIGNED_LONG_LONG_MAX).__str__())
            return

        status = gx_set_acquisition_buffer_number(self.__dev_handle, buf_num)
        StatusProcessor.process(status, 'DataStream', 'set_acquisition_buffer_number')

    def register_capture_callback(self, callback_func):
        """
        :brief      Register the capture event callback function.
        :param      callback_func:  callback function
        :return:    none
        """
        if not isinstance(callback_func, types.FunctionType):
            raise ParameterTypeError("DataStream.register_capture_callback: "
                                     "Expected callback type is function not %s" % type(callback_func))

        status = gx_register_capture_callback(self.__dev_handle, self.__c_capture_callback)
        StatusProcessor.process(status, 'DataStream', 'register_capture_callback')

        # callback will not recorded when register callback failed.
        self.__py_capture_callback = callback_func

    def unregister_capture_callback(self):
        """
        :brief      Unregister the capture event callback function.
        :return:    none
        """
        status = gx_unregister_capture_callback(self.__dev_handle)
        StatusProcessor.process(status, 'DataStream', 'unregister_capture_callback')
        self.__py_capture_callback = None

    def register_buffer(self, user_buf, user_param=None):
        """
        :brief      Register the extern buffer for grab.
        :param      user_buf:  Extern buffer.
        :param      user_param:  User params.
        :return:    none
        """
        if not isinstance(user_buf, ctypes.Array):
            raise ParameterTypeError("DataStream.register_buffer: "
                                     "Expected buff type is Buffer, not %s" % type(user_buf))

        status = gx_register_buffer(self.__dev_handle, user_buf, user_param)
        if status is GxStatusList.SUCCESS:
            self.__register_buf_param_map[id(user_buf)] = user_param
            self.__register_buf_param_content_map[id(user_param)] = user_param
        StatusProcessor.process(status, 'DataStream', 'register_buffer')

    def unregister_buffer(self, user_buf):
        """
        :brief      Unregister the extern buffer.
        :param      user_buf:  Extern buffer.
        :return:    none
        """
        if not isinstance(user_buf, ctypes.Array):
            raise ParameterTypeError("DataStream.unregister_buffer: "
                                     "Expected buff type is Buffer, not %s" % type(user_buf))

        status = gx_unregister_buffer(self.__dev_handle, user_buf)
        if status is GxStatusList.SUCCESS:
            user_param = self.__register_buf_param_map[id(user_buf)]
            del self.__register_buf_param_content_map[id(user_param)]
            del self.__register_buf_param_map[id(user_buf)]
        StatusProcessor.process(status, 'DataStream', 'unregister_buffer')

    def __on_capture_callback(self, capture_data):
        """
        :brief      Capture event callback function with capture date.
        :return:    none
        """
        frame_data = GxFrameData()
        frame_data.image_buf = capture_data.contents.image_buf
        frame_data.width = capture_data.contents.width
        frame_data.height = capture_data.contents.height
        frame_data.pixel_format = capture_data.contents.pixel_format
        frame_data.image_size = capture_data.contents.image_size
        frame_data.frame_id = capture_data.contents.frame_id
        frame_data.timestamp = capture_data.contents.timestamp
        frame_data.status = capture_data.contents.status
        # frame_data.buf_id = capture_data.contents.buf_id

        if sys.platform == 'linux2' or sys.platform == 'linux':
            frame_data.offset_x = capture_data.contents.offset_x
            frame_data.offset_y = capture_data.contents.offset_y

        image = RawImage(frame_data)
        self.__py_capture_callback(image)

class U3VDataStream(DataStream):
    def __init__(self, dev_handle, stream_handle):
        self.__handle = dev_handle
        DataStream.__init__(self, self.__handle, stream_handle)
        self.StreamTransferSize = IntFeature(self.__handle, GxFeatureID.INT_STREAM_TRANSFER_SIZE)
        self.StreamTransferNumberUrb = IntFeature(self.__handle, GxFeatureID.INT_STREAM_TRANSFER_NUMBER_URB)
        self.StopAcquisitionMode = EnumFeature(self.__handle, GxFeatureID.ENUM_STOP_ACQUISITION_MODE)


class GEVDataStream(DataStream):
    def __init__(self, dev_handle, stream_handle):
        self.__handle = dev_handle
        DataStream.__init__(self, self.__handle, stream_handle)
        self.StreamResendPacketCount = IntFeature(self.__handle, GxFeatureID.INT_RESEND_PACKET_COUNT)
        self.StreamRescuedPacketCount = IntFeature(self.__handle, GxFeatureID.INT_RESCUED_PACKET_COUNT)
        self.StreamResendCommandCount = IntFeature(self.__handle, GxFeatureID.INT_RESEND_COMMAND_COUNT)
        self.StreamUnexpectedPacketCount = IntFeature(self.__handle, GxFeatureID.INT_UNEXPECTED_PACKET_COUNT)
        self.MaxPacketCountInOneBlock = IntFeature(self.__handle, GxFeatureID.INT_MAX_PACKET_COUNT_IN_ONE_BLOCK)
        self.MaxPacketCountInOneCommand = IntFeature(self.__handle, GxFeatureID.INT_MAX_PACKET_COUNT_IN_ONE_COMMAND)
        self.ResendTimeout = IntFeature(self.__handle, GxFeatureID.INT_RESEND_TIMEOUT)
        self.MaxWaitPacketCount = IntFeature(self.__handle, GxFeatureID.INT_MAX_WAIT_PACKET_COUNT)
        self.ResendMode = EnumFeature(self.__handle, GxFeatureID.ENUM_RESEND_MODE)
        self.StreamMissingBlockIDCount = IntFeature(self.__handle, GxFeatureID.INT_MISSING_BLOCK_ID_COUNT)
        self.BlockTimeout = IntFeature(self.__handle, GxFeatureID.INT_BLOCK_TIMEOUT)
        self.MaxNumQueueBuffer = IntFeature(self.__handle, GxFeatureID.INT_MAX_NUM_QUEUE_BUFFER)
        self.PacketTimeout = IntFeature(self.__handle, GxFeatureID.INT_PACKET_TIMEOUT)
        self.SocketBufferSize = IntFeature(self.__handle, GxFeatureID.INT_SOCKET_BUFFER_SIZE)

