#!/usr/bin/python
# -*- coding:utf-8 -*-
# -*-mode:python ; tab-width:4 -*- ex:set tabstop=4 shiftwidth=4 expandtab: -*-


import numpy
from gxipy.gxwrapper import *
from gxipy.dxwrapper import *
from gxipy.gxidef import *
from gxipy.gxiapi import *
from gxipy.StatusProcessor import *
import types

COLOR_TRANSFORM_MATRIX_SIZE = 9  # 3*3

if sys.version_info.major > 2:
    INT_TYPE = int
else:
    INT_TYPE = (int, long)

class Buffer:
    def __init__(self, data_array):
        try:
            addressof(data_array)
        except TypeError:
            error_msg = "Buffer.__init__: param is error type."
            raise ParameterTypeError(error_msg)

        self.data_array = data_array

    @staticmethod
    def from_file(file_name):
        file_object = open(file_name, "rb")
        file_string = file_object.read()
        # print("data_array_len0:", len(file_string))
        data_array = create_string_buffer(file_string,len(file_string))
        # print("data_array_len:",len(data_array))
        # print("data_array:",data_array)
        file_object.close()
        return Buffer(data_array)

    @staticmethod
    def from_string(string_data):
        data_array = create_string_buffer(string_data, len(string_data))
        return Buffer(data_array)

    def get_data(self):
        buff_p = c_void_p()
        buff_p.value = addressof(self.data_array)
        string_data = string_at(buff_p, len(self.data_array))
        return string_data

    def get_ctype_array(self):
        return self.data_array

    def get_numpy_array(self):
        numpy_array = numpy.array(self.data_array)
        return numpy_array

    def get_length(self):
        return len(self.data_array)


class RGBImage:
    def __init__(self, frame_data):
        self.frame_data = frame_data

        if self.frame_data.image_buf is not None:
            self.__image_array = string_at(self.frame_data.image_buf, self.frame_data.image_size)
        else:
            self.__image_array = (c_ubyte * self.frame_data.image_size)()
            self.frame_data.image_buf = addressof(self.__image_array)

    def image_improvement(self, color_correction_param=0, contrast_lut=None, gamma_lut=None, channel_order=DxRGBChannelOrder.ORDER_RGB):
        """
        :brief:     Improve image quality of the object itself
        :param      color_correction_param:     color correction param address
                                                (get from Device.ColorCorrectionParam.get_int())
        :param      contrast_lut:               contrast lut
        :param      gamma_lut:                  gamma lut
        :param      channel_order               RGB channel order of output image
        :return:    None
        """
        if (color_correction_param == 0) and (contrast_lut is None) and (gamma_lut is None):
            return

        if contrast_lut is None:
            contrast_parameter = None
        elif isinstance(contrast_lut, Buffer):
            contrast_parameter = contrast_lut.get_ctype_array()
        else:
            raise ParameterTypeError("RGBImage.image_improvement: "
                                     "Expected contrast_lut type is Buffer, not %s" % type(contrast_lut))

        if gamma_lut is None:
            gamma_parameter = None
        elif isinstance(gamma_lut, Buffer):
            gamma_parameter = gamma_lut.get_ctype_array()
        else:
            raise ParameterTypeError("RGBImage.image_improvement: "
                                     "Expected gamma_lut type is Buffer, not %s" % type(gamma_lut))

        if not isinstance(color_correction_param, INT_TYPE):
            raise ParameterTypeError("RGBImage.image_improvement: "
                                     "Expected color_correction_param type is int, not %s" % type(color_correction_param))

        if not isinstance(channel_order, INT_TYPE):
            raise ParameterTypeError("RGBImage.image_improvement: "
                                     "Expected channel_order type is int, not %s" % type(channel_order))

        status = dx_image_improvement_ex(self.frame_data.image_buf, self.frame_data.image_buf,
                                      self.frame_data.width, self.frame_data.height,
                                      color_correction_param, contrast_parameter, gamma_parameter, channel_order)

        if status != DxStatus.OK:
            raise UnexpectedError("RGBImage.image_improvement: failed, error code:%s" % hex(status).__str__())

    def brightness(self, factor):
        """
        :brief      Brightness adjustment (RGB24)
        :factor:    factor, range(-150 ~ 150)
        :return:    None
        """
        if not isinstance(factor, INT_TYPE):
            raise ParameterTypeError("RGBImage.brightness: "
                                     "Expected factor type is int, not %s" % type(factor))

        status = dx_brightness(self.frame_data.image_buf, self.frame_data.image_buf, self.frame_data.image_size, factor)

        if status != DxStatus.OK:
            raise UnexpectedError("RGBImage.brightness: failed, error code:%s" % hex(status).__str__())

    def contrast(self, factor):
        """
        :brief      Contrast adjustment (RGB24)
        :factor:    factor, range(-50 ~ 100)
        :return:    None
        """
        if not isinstance(factor, INT_TYPE):
            raise ParameterTypeError("RGBImage.contrast: "
                                     "Expected factor type is int, not %s" % type(factor))

        status = dx_contrast(self.frame_data.image_buf, self.frame_data.image_buf, self.frame_data.image_size, factor)

        if status != DxStatus.OK:
            raise UnexpectedError("RGBImage.contrast: failed, error code:%s" % hex(status).__str__())

    def saturation(self, factor):
        """
        :brief      Saturation adjustment (RGB24)
        :param      factor:                 saturation factor,range(0 ~ 128)
        :return:    RGBImage object
        """
        if not isinstance(factor, INT_TYPE):
            raise ParameterTypeError("RGBImage.saturation: "
                                     "Expected factor type is int, not %s" % type(factor))

        status = dx_saturation(self.frame_data.image_buf, self.frame_data.image_buf,
                               self.frame_data.width * self.frame_data.height, factor)

        if status != DxStatus.OK:
            raise UnexpectedError("RGBImage.saturation: failed, error code:%s" % hex(status).__str__())

    def sharpen(self, factor):
        """
        :brief      Sharpen adjustment (RGB24)
        :param      factor:                 sharpen factor, range(0.1 ~ 5.0)
        :return:    None
        """
        if not isinstance(factor, (INT_TYPE, float)):
            raise ParameterTypeError("RGBImage.sharpen: "
                                     "Expected factor type is float, not %s" % type(factor))

        status = dx_sharpen_24b(self.frame_data.image_buf, self.frame_data.image_buf, self.frame_data.width,
                                self.frame_data.height, factor)

        if status != DxStatus.OK:
            raise UnexpectedError("RGBImage.sharpen: failed, error code:%s" % hex(status).__str__())

    def get_white_balance_ratio(self):
        """
        :brief      Get white balance ratios(RGB24), In order to calculate accurately, the camera should shoot
                    objective "white" area,or input image is white area.
        :return:    rgb_ratio:      (r_ratio, g_ratio, b_ratio)
        """
        status, rgb_ratio = dx_get_white_balance_ratio(self.frame_data.image_buf, self.frame_data.width, self.frame_data.height)

        if status != DxStatus.OK:
            raise UnexpectedError("RGBImage.get_white_balance_ratio: failed, error code:%s" % hex(status).__str__())

        return rgb_ratio

    def get_numpy_array(self):
        """
        :brief:     Return data as a numpy.Array type with dimension Image.height * Image.width * 3
        :return:    numpy.Array objects
        """
        image_np = numpy.frombuffer(self.__image_array, dtype=numpy.ubyte).reshape(self.frame_data.height, self.frame_data.width, 3)
        return image_np

    def get_image_size(self):
        """
        :brief      Get RGB data size
        :return:    size
        """
        return self.frame_data.image_size

class RawImage:
    def __init__(self, frame_data):
        self.frame_data = frame_data

        if self.frame_data.image_buf is not None:
            self.__image_array = string_at(self.frame_data.image_buf, self.frame_data.image_size)
        else:
            self.__image_array = (c_ubyte * self.frame_data.image_size)()
            self.frame_data.image_buf = addressof(self.__image_array)

        self.user_param = None

    def __pixel_format_raw16_to_raw8(self, pixel_format):
        """
        :brief      convert raw16 to raw8, the pixel format need convert to 8bit bayer format
        :param      pixel_format(10bit, 12bit, 16bit)
        :return:    pixel_format(8bit)
        """
        gr16_tup = (GxPixelFormatEntry.BAYER_GR10, GxPixelFormatEntry.BAYER_GR12, GxPixelFormatEntry.BAYER_GR16)
        rg16_tup = (GxPixelFormatEntry.BAYER_RG10, GxPixelFormatEntry.BAYER_RG12, GxPixelFormatEntry.BAYER_RG16)
        gb16_tup = (GxPixelFormatEntry.BAYER_GB10, GxPixelFormatEntry.BAYER_GB12, GxPixelFormatEntry.BAYER_GB16)
        bg16_tup = (GxPixelFormatEntry.BAYER_BG10, GxPixelFormatEntry.BAYER_BG12, GxPixelFormatEntry.BAYER_BG16)
        mono16_tup = (GxPixelFormatEntry.MONO10, GxPixelFormatEntry.MONO12,
                      GxPixelFormatEntry.MONO14, GxPixelFormatEntry.MONO16)

        if pixel_format in gr16_tup:
            return GxPixelFormatEntry.BAYER_GR8
        elif pixel_format in rg16_tup:
            return GxPixelFormatEntry.BAYER_RG8
        elif pixel_format in gb16_tup:
            return GxPixelFormatEntry.BAYER_GB8
        elif pixel_format in bg16_tup:
            return GxPixelFormatEntry.BAYER_BG8
        elif pixel_format in mono16_tup:
            return GxPixelFormatEntry.MONO8
        else:
            return -1

    def __raw16_to_raw8(self, pixel_bit_depth, valid_bits):
        """
        :brief      convert raw16 to raw8
        :param      pixel_bit_depth     pixel bit depth
        :param      valid_bits:         data valid digit[DxValidBit]
        :return:    RAWImage object
        """
        if pixel_bit_depth == GxPixelSizeEntry.BPP10:
            valid_bits = min(valid_bits, DxValidBit.BIT2_9)
        elif pixel_bit_depth == GxPixelSizeEntry.BPP12:
            valid_bits = min(valid_bits, DxValidBit.BIT4_11)
        elif pixel_bit_depth == GxPixelSizeEntry.BPP14:
            valid_bits = min(valid_bits, DxValidBit.BIT6_13)
        elif pixel_bit_depth == GxPixelSizeEntry.BPP16:
            valid_bits = min(valid_bits, DxValidBit.BIT8_15)
        else:
            print("RawImage.__dx_raw16_to_raw8: Only support 10bit and 12bit")
            return None

        frame_data = GxFrameData()
        frame_data.status = self.frame_data.status
        frame_data.width = self.frame_data.width
        frame_data.height = self.frame_data.height
        frame_data.pixel_format = self.__pixel_format_raw16_to_raw8(self.frame_data.pixel_format)
        frame_data.image_size = self.frame_data.width * self.frame_data.height
        frame_data.frame_id = self.frame_data.frame_id
        frame_data.timestamp = self.frame_data.timestamp
        # frame_data.buf_id = self.frame_data.buf_id
        frame_data.image_buf = None
        image_raw8 = RawImage(frame_data)

        status = dx_raw16_to_raw8(self.frame_data.image_buf, image_raw8.frame_data.image_buf,
                                  self.frame_data.width, self.frame_data.height, valid_bits)

        if status != DxStatus.OK:
            raise UnexpectedError("RawImage.convert: raw16 convert to raw8 failed, Error core: %s"
                                  % hex(status).__str__())
        else:
            return image_raw8

    def __convert_to_special_pixelformat(self, pixelformat , convert_type, channel_order, pixel_bit_depth, valid_bits, flip):
        """
        :brief      convert mono_packed to raw8
        :return:    RAWImage object
        """
        if pixel_bit_depth == GxPixelSizeEntry.BPP8:
            valid_bits = min(valid_bits, DxValidBit.BIT0_7)
        elif pixel_bit_depth == GxPixelSizeEntry.BPP10:
            valid_bits = min(valid_bits, DxValidBit.BIT2_9)
        elif pixel_bit_depth == GxPixelSizeEntry.BPP12:
            valid_bits = min(valid_bits, DxValidBit.BIT4_11)
        elif pixel_bit_depth == GxPixelSizeEntry.BPP14:
            valid_bits = min(valid_bits, DxValidBit.BIT6_13)
        elif pixel_bit_depth == GxPixelSizeEntry.BPP16:
            valid_bits = min(valid_bits, DxValidBit.BIT8_15)
        elif pixel_bit_depth == GxPixelSizeEntry.BPP24:
            valid_bits = min(valid_bits, DxValidBit.BIT0_7)
        else:
            print("ImageProc.__convert_to_special_pixelformat: not support")
            return None

        status, handle = dx_image_format_convert_create()
        if status != DxStatus.OK:
            raise UnexpectedError("dx_image_format_convert_create failure, Error code:%s" % hex(status).__str__())

        status = dx_image_format_convert_set_output_pixel_format(handle, pixelformat)
        if status != DxStatus.OK:
            raise UnexpectedError(
                "dx_image_format_convert_set_output_pixel_format failure, Error code:%s" % hex(status).__str__())

        status = dx_image_format_convert_set_valid_bits(handle, valid_bits)
        if status != DxStatus.OK:
            raise UnexpectedError("image_format_convert_set_valid_bits failure, Error code:%s" % hex(status).__str__())

        status = dx_image_format_convert_set_alpha_value(handle, channel_order)
        if status != DxStatus.OK:
            raise UnexpectedError("image_format_convert_set_alpha_value failure, Error code:%s" % hex(status).__str__())

        status = dx_image_format_convert_set_interpolation_type(handle, convert_type)
        if status != DxStatus.OK:
            raise UnexpectedError("image_format_convert_set_interpolation_type failure, Error code:%s" % hex(status).__str__())

        status, buffer_size_c = dx_image_format_convert_get_buffer_size_for_conversion(handle, pixelformat,
                                                                                       self.frame_data.width, self.frame_data.height)
        if status != DxStatus.OK:
            raise UnexpectedError("dx_image_format_convert_get_buffer_size_for_conversion failure, Error code:%s" % hex(status).__str__())

        image = None
        frame_data = GxFrameData()
        frame_data.status = self.frame_data.status
        frame_data.width = self.frame_data.width
        frame_data.height = self.frame_data.height
        frame_data.pixel_format = pixelformat
        frame_data.image_size = buffer_size_c
        frame_data.frame_id = self.frame_data.frame_id
        frame_data.timestamp = self.frame_data.timestamp
        frame_data.image_buf = None

        if pixelformat == GxPixelFormatEntry.RGB8:
            image = RGBImage(frame_data)
        else:
            image = RawImage(frame_data)

        status = dx_image_format_convert(handle, self.frame_data.image_buf, self.frame_data.image_size, image.frame_data.image_buf,
                                         image.frame_data.image_size, self.frame_data.pixel_format, self.frame_data.width, self.frame_data.height, flip)
        if status != DxStatus.OK:
            raise UnexpectedError("image_format_convert failure, Error code:%s" % hex(status).__str__())

        status = dx_image_format_convert_destroy(handle)
        if status != DxStatus.OK:
            raise UnexpectedError("image_format_convert_destroy failure, Error code:%s" % hex(status).__str__())

        return image

    def __raw8_to_rgb(self, raw8_image, convert_type, pixel_color_filter, flip):
        """
        :brief      convert raw8 to RGB
        :param      raw8_image          RAWImage object, bit depth is 8bit
        :param      convert_type:       Bayer convert type, See detail in DxBayerConvertType
        :param      pixel_color_filter: pixel color filter, See detail in DxPixelColorFilter
        :param      flip:               Output image flip flag
                                        True: turn the image upside down
                                        False: do not flip
        :return:    RAWImage object
        """
        frame_data = GxFrameData()
        frame_data.status = raw8_image.frame_data.status
        frame_data.width = raw8_image.frame_data.width
        frame_data.height = raw8_image.frame_data.height
        frame_data.pixel_format = GxPixelFormatEntry.RGB8_PLANAR
        frame_data.image_size = raw8_image.frame_data.width * raw8_image.frame_data.height * 3
        frame_data.frame_id = raw8_image.frame_data.frame_id
        frame_data.timestamp = raw8_image.frame_data.timestamp
        # frame_data.buf_id = self.frame_data.buf_id
        frame_data.image_buf = None
        image_rgb = RGBImage(frame_data)

        status = dx_raw8_to_rgb24(raw8_image.frame_data.image_buf, image_rgb.frame_data.image_buf,
                                  raw8_image.frame_data.width, raw8_image.frame_data.height,
                                  convert_type, pixel_color_filter, flip)

        if status != DxStatus.OK:
            raise UnexpectedError("RawImage.convert: failed, error code:%s" % hex(status).__str__())

        return image_rgb

    def __raw8_to_rgb_ex(self, raw8_image, convert_type, pixel_color_filter, flip, channel_order):
        """
        :brief      convert raw8 to RGB with chosen RGB channel order
        :param      raw8_image          RAWImage object, bit depth is 8bit
        :param      convert_type:       Bayer convert type, See detail in DxBayerConvertType
        :param      pixel_color_filter: pixel color filter, See detail in DxPixelColorFilter
        :param      flip:               Output image flip flag
                                        True: turn the image upside down
                                        False: do not flip
        :param      channel_order:      RGB channel order of output image
        :return:    RAWImage object
        """
        frame_data = GxFrameData()
        frame_data.status = raw8_image.frame_data.status
        frame_data.width = raw8_image.frame_data.width
        frame_data.height = raw8_image.frame_data.height
        frame_data.image_size = raw8_image.frame_data.width * raw8_image.frame_data.height * 3
        frame_data.frame_id = raw8_image.frame_data.frame_id
        frame_data.timestamp = raw8_image.frame_data.timestamp
        # frame_data.buf_id = self.frame_data.buf_id
        if channel_order == DxRGBChannelOrder.ORDER_RGB:
            frame_data.pixel_format = GxPixelFormatEntry.RGB8
        else:
            frame_data.pixel_format = GxPixelFormatEntry.BGR8
        frame_data.image_buf = None
        image_rgb = RGBImage(frame_data)

        status = dx_raw8_to_rgb24_ex(raw8_image.frame_data.image_buf, image_rgb.frame_data.image_buf,
                                     raw8_image.frame_data.width, raw8_image.frame_data.height,
                                     convert_type, pixel_color_filter, flip, channel_order)

        if status != DxStatus.OK:
            raise UnexpectedError("RawImage.convert: failed, error code:%s" % hex(status).__str__())

        return image_rgb

    def rgb8_to_numpy_array(self):
        frame_data = GxFrameData()
        frame_data.status = self.frame_data.status
        frame_data.width = self.frame_data.width
        frame_data.height = self.frame_data.height
        frame_data.pixel_format = GxPixelFormatEntry.RGB8
        frame_data.image_size = self.frame_data.image_size
        frame_data.frame_id = self.frame_data.frame_id
        frame_data.timestamp = self.frame_data.timestamp
        frame_data.image_buf = self.frame_data.image_buf
        image_rgb = RGBImage(frame_data)

        return image_rgb.get_numpy_array()


    def __raw8_pixel_format_rotate_90(self, pixel_format, direct):
        """
        :brief      Rotate pixel format by 90 or -90 degrees
        :param      pixel_format    Image format
        :param      direct          90 or -90
        :return:    success: rotated pixel format
                    failed: -1
        """
        if pixel_format & PIXEL_BIT_MASK != GX_PIXEL_8BIT:
            print("__raw8_pixel_format_rotate_90.pixel_format only support raw8")
            return -1

        if direct != 90 and direct != -90:
            print("__raw8_pixel_format_rotate_90.direct only support 90 or -90")
            return -1

        if pixel_format == GxPixelFormatEntry.MONO8:
            return GxPixelFormatEntry.MONO8

        if (pixel_format == GxPixelFormatEntry.BAYER_GR8 and direct == 90) or \
                (pixel_format == GxPixelFormatEntry.BAYER_GB8 and direct == -90):
            return GxPixelFormatEntry.BAYER_BG8

        if (pixel_format == GxPixelFormatEntry.BAYER_RG8 and direct == 90) or \
                (pixel_format == GxPixelFormatEntry.BAYER_BG8 and direct == -90):
            return GxPixelFormatEntry.BAYER_GR8

        if (pixel_format == GxPixelFormatEntry.BAYER_GB8 and direct == 90) or \
                (pixel_format == GxPixelFormatEntry.BAYER_GR8 and direct == -90):
            return GxPixelFormatEntry.BAYER_RG8

        if (pixel_format == GxPixelFormatEntry.BAYER_BG8 and direct == 90) or \
                (pixel_format == GxPixelFormatEntry.BAYER_RG8 and direct == -90):
            return GxPixelFormatEntry.BAYER_GB8

        return -1

    def __raw8_pixel_format_mirror(self, pixel_format, mirror_mode):
        """
        :brief      Mirror pixel format
        :param      pixel_format:   Image format
        :param      mirror_mode:    DxImageMirrorMode
        :return:    success: mirror pixel format
                    failed: -1
        """
        if pixel_format & PIXEL_BIT_MASK != GX_PIXEL_8BIT:
            print("__raw8_pixel_format_mirror.pixel_format only support raw8")
            return -1

        if mirror_mode not in (DxImageMirrorMode.VERTICAL_MIRROR, DxImageMirrorMode.HORIZONTAL_MIRROR):
            print("mirror_mode only support VERTICAL_MIRROR or HORIZONTAL_MIRROR")
            return -1

        if pixel_format == GxPixelFormatEntry.MONO8:
            return GxPixelFormatEntry.MONO8

        if (pixel_format == GxPixelFormatEntry.BAYER_GR8 and mirror_mode == DxImageMirrorMode.HORIZONTAL_MIRROR) or \
                (pixel_format == GxPixelFormatEntry.BAYER_GB8 and mirror_mode == DxImageMirrorMode.VERTICAL_MIRROR):
            return GxPixelFormatEntry.BAYER_RG8

        if (pixel_format == GxPixelFormatEntry.BAYER_RG8 and mirror_mode == DxImageMirrorMode.HORIZONTAL_MIRROR) or \
                (pixel_format == GxPixelFormatEntry.BAYER_BG8 and mirror_mode == DxImageMirrorMode.VERTICAL_MIRROR):
            return GxPixelFormatEntry.BAYER_GR8

        if (pixel_format == GxPixelFormatEntry.BAYER_GB8 and mirror_mode == DxImageMirrorMode.HORIZONTAL_MIRROR) or \
                (pixel_format == GxPixelFormatEntry.BAYER_GR8 and mirror_mode == DxImageMirrorMode.VERTICAL_MIRROR):
            return GxPixelFormatEntry.BAYER_BG8

        if (pixel_format == GxPixelFormatEntry.BAYER_BG8 and mirror_mode == DxImageMirrorMode.HORIZONTAL_MIRROR) or \
                (pixel_format == GxPixelFormatEntry.BAYER_RG8 and mirror_mode == DxImageMirrorMode.VERTICAL_MIRROR):
            return GxPixelFormatEntry.BAYER_GB8

        return -1

    def convert(self, mode, flip=False, valid_bits=DxValidBit.BIT8_15,
                convert_type=DxBayerConvertType.NEIGHBOUR, channel_order=DxRGBChannelOrder.ORDER_RGB):
        """
        :brief      Image format convert
        :param      mode:           "RAW8":     convert raw16 RAWImage object to raw8 RAWImage object
                                    "RGB":   convert raw8 RAWImage object to RGBImage object
        :param      flip:           Output image flip flag
                                    True: turn the image upside down
                                    False: do not flip
        :param      valid_bits:     Data valid digit, See detail in DxValidBit, raw8 don't this param
        :param      convert_type:   Bayer convert type, See detail in DxBayerConvertType
        :param      channel_order:  RGB channel order of output image
        :return:    return image object according to mode parameter
        """
        if self.frame_data.status != GxFrameStatusList.SUCCESS:
            print("RawImage.convert: This is a incomplete image")
            return None

        if not isinstance(flip, bool):
            raise ParameterTypeError("RawImage.convert: "
                                     "Expected flip type is bool, not %s" % type(flip))

        if not isinstance(convert_type, INT_TYPE):
            raise ParameterTypeError("RawImage.convert: "
                                     "Expected convert_type type is int, not %s" % type(convert_type))

        if not isinstance(channel_order, INT_TYPE):
            raise ParameterTypeError("RawImage.convert: "
                                     "Expected channel_order type is int, not %s" % type(channel_order))

        if not isinstance(valid_bits, INT_TYPE):
            raise ParameterTypeError("RawImage.convert: "
                                     "Expected valid_bits type is int, not %s" % type(valid_bits))

        if not isinstance(mode, str):
            raise ParameterTypeError("RawImage.convert: "
                                     "Expected mode type is str, not %s" % type(mode))

        convert_type_dict = dict((name, getattr(DxBayerConvertType, name))
                                 for name in dir(DxBayerConvertType) if not name.startswith('__'))
        if convert_type not in convert_type_dict.values():
            print("RawImage.convert: convert_type out of bounds, %s" % convert_type_dict.__str__())
            return None

        valid_bits_dict = dict((name, getattr(DxValidBit, name))
                               for name in dir(DxValidBit) if not name.startswith('__'))
        if valid_bits not in valid_bits_dict.values():
            print("RawImage.convert: valid_bits out of bounds, %s" % valid_bits_dict.__str__())
            return None

        pixel_bit_depth = _InterUtility.get_bit_depth(self.frame_data.pixel_format)
        if (self.frame_data.pixel_format in (GxPixelFormatEntry.RGB8, GxPixelFormatEntry.BGR8)):
            if mode == "RAW8":
                raise ParameterTypeError("Unsupported pixel format conversion.")
            elif mode == "RGB":
                if self.frame_data.pixel_format == GxPixelFormatEntry.BGR8:
                    image_rgb = self.__convert_to_special_pixelformat(GxPixelFormatEntry.RGB8, convert_type,
                                                                      channel_order, pixel_bit_depth, valid_bits, flip)
                    return image_rgb
                else:
                    frame_data = GxFrameData()
                    frame_data.status = self.frame_data.status
                    frame_data.width = self.frame_data.width
                    frame_data.height = self.frame_data.height
                    frame_data.pixel_format = self.frame_data.pixel_format
                    frame_data.image_size = self.frame_data.image_size
                    frame_data.frame_id = self.frame_data.frame_id
                    frame_data.timestamp = self.frame_data.timestamp
                    frame_data.image_buf = self.frame_data.image_buf
                    image = RGBImage(frame_data)
                    return image
            else:
                print('''RawImage.convert: mode="%s", isn't support''' % mode)
                return None


        if (pixel_bit_depth < GxPixelSizeEntry.BPP8 or pixel_bit_depth > GxPixelSizeEntry.BPP16):
            print("RawImage.convert: This pixel format is not support")
            return None

        if mode == "RAW8":
            if flip is True:
                print('''RawImage.convert: mode="RAW8" don't support flip=True''')
                return None

            dest_pixel_format = Utility.get_convert_dest_8bit_pixel_format(self.frame_data.pixel_format)
            if dest_pixel_format == GxPixelFormatEntry.UNDEFINED:
                raise UnexpectedError("__convert_to_raw8 get dest pixel format failure")

            image_raw8 = self.__convert_to_special_pixelformat(dest_pixel_format, convert_type, channel_order,
                                                               pixel_bit_depth, valid_bits, flip)
            return image_raw8
        elif mode == "RGB":
            image_rgb = self.__convert_to_special_pixelformat(GxPixelFormatEntry.RGB8, convert_type, channel_order,
                                                              pixel_bit_depth, valid_bits, flip)
            return image_rgb
        else:
            print('''RawImage.convert: mode="%s", isn't support''' % mode)
            return None

    def is_color_cam(self):
        pixel_color_filter = _InterUtility.get_pixel_color_filter(self.frame_data.pixel_format)
        if (pixel_color_filter > 0) or \
                (self.frame_data.pixel_format in (GxPixelFormatEntry.RGB8, GxPixelFormatEntry.BGR8, GxPixelFormatEntry.YUV422_8, GxPixelFormatEntry.YUV422_8_UYVY)):
            return True
        else:
            return False

    def get_output_pixel_format(self):
        return self.frame_data.pixel_format

    def defective_pixel_correct(self):
        """
        :brief      Auto raw defective pixel correct,Support image from Raw8 to Raw16, the bit number is actual
                    bit number, when it is more than 8, the actual bit can be every number between 9 to 16.
                    And if image format is packed, you need convert it to Raw16.
                    This function should be used in each frame.
        :return:    None
        """
        pixel_bit_depth = _InterUtility.get_bit_depth(self.frame_data.pixel_format)
        status = dx_auto_raw_defective_pixel_correct(self.frame_data.image_buf, self.frame_data.width,
                                                     self.frame_data.height, pixel_bit_depth)

        if status != DxStatus.OK:
            raise UnexpectedError("RawImage.defective_pixel_correct: failed, error code:%s" % hex(status).__str__())

    def raw8_rotate_90_cw(self):
        """
        :brief      To rotate the 8-bit image clockwise by 90 degrees
        :return     RAWImage object
        """
        if self.frame_data.pixel_format & PIXEL_BIT_MASK != GX_PIXEL_8BIT:
            raise InvalidParameter("RawImage.raw8_rotate_90_cw only support 8bit image")

        frame_data = GxFrameData()
        frame_data.status = self.frame_data.status
        frame_data.width = self.frame_data.height
        frame_data.height = self.frame_data.width
        frame_data.pixel_format = self.__raw8_pixel_format_rotate_90(self.frame_data.pixel_format, 90)
        if frame_data.pixel_format == -1:
            raise UnexpectedError("Rotate pixel format %s failed" % hex(self.frame_data.pixel_format).__str__())

        frame_data.image_size = self.frame_data.image_size
        frame_data.frame_id = self.frame_data.frame_id
        frame_data.timestamp = self.frame_data.timestamp
        # frame_data.buf_id = self.frame_data.buf_id
        frame_data.image_buf = None
        rotate_image = RawImage(frame_data)

        status = dx_raw8_rotate_90_cw(self.frame_data.image_buf, rotate_image.frame_data.image_buf,
                                      self.frame_data.width, self.frame_data.height)

        if status != DxStatus.OK:
            raise UnexpectedError("RawImage.raw8_rotate_90_cw: failed, error code:%s" % hex(status).__str__())

        return rotate_image

    def raw8_rotate_90_ccw(self):
        """
        :brief      To rotate the 8-bit image clockwise by -90 degrees
        :return     RAWImage object
        """
        if self.frame_data.pixel_format & PIXEL_BIT_MASK != GX_PIXEL_8BIT:
            raise InvalidParameter("RawImage.raw8_rotate_90_ccw only support 8bit image")

        frame_data = GxFrameData()
        frame_data.status = self.frame_data.status
        frame_data.width = self.frame_data.height
        frame_data.height = self.frame_data.width
        frame_data.pixel_format = self.__raw8_pixel_format_rotate_90(self.frame_data.pixel_format, -90)
        if frame_data.pixel_format == -1:
            raise UnexpectedError("Rotate pixel format %s failed" % hex(self.frame_data.pixel_format).__str__())

        frame_data.image_size = self.frame_data.image_size
        frame_data.frame_id = self.frame_data.frame_id
        frame_data.timestamp = self.frame_data.timestamp
        # frame_data.buf_id = self.frame_data.buf_id
        frame_data.image_buf = None
        rotate_image = RawImage(frame_data)

        status = dx_raw8_rotate_90_ccw(self.frame_data.image_buf, rotate_image.frame_data.image_buf,
                                       self.frame_data.width, self.frame_data.height)

        if status != DxStatus.OK:
            raise UnexpectedError("RawImage.raw8_rotate_90_ccw: failed, error code:%s" % hex(status).__str__())

        return rotate_image

    def brightness(self, factor):
        """
        :brief      Brightness adjustment (mono8)
        :param      factor:    factor, range(-150 ~ 150)
        :return:    None
        """
        if not isinstance(factor, INT_TYPE):
            raise ParameterTypeError("RawImage.brightness: "
                                     "Expected factor type is int, not %s" % type(factor))

        if self.frame_data.pixel_format != GxPixelFormatEntry.MONO8:
            raise InvalidParameter("RawImage.brightness only support mono8 image")

        status = dx_brightness(self.frame_data.image_buf, self.frame_data.image_buf, self.frame_data.image_size, factor)

        if status != DxStatus.OK:
            raise UnexpectedError("RawImage.brightness: failed, error code:%s" % hex(status).__str__())

    def contrast(self, factor):
        """
        :brief      Contrast adjustment (mono8)
        :param      factor:    factor, range(-50 ~ 100)
        :return:    None
        """
        if not isinstance(factor, INT_TYPE):
            raise ParameterTypeError("RawImage.contrast: "
                                     "Expected factor type is int, not %s" % type(factor))

        if self.frame_data.pixel_format != GxPixelFormatEntry.MONO8:
            raise InvalidParameter("RawImage.contrast only support mono8 image")

        status = dx_contrast(self.frame_data.image_buf, self.frame_data.image_buf, self.frame_data.image_size, factor)

        if status != DxStatus.OK:
            raise UnexpectedError("RawImage.contrast: failed, error code:%s" % hex(status).__str__())

    def mirror(self, mirror_mode):
        """
        :brief      Image mirror(Raw8 or 8bit image)
        :param      mirror_mode:    mirror mode [reference DxImageMirrorMode]
        :return     RAWImage object
        """
        if not isinstance(mirror_mode, INT_TYPE):
            raise ParameterTypeError("RawImage.mirror: "
                                     "Expected mirror_mode type is int, not %s" % type(mirror_mode))

        if self.frame_data.pixel_format & PIXEL_BIT_MASK != GX_PIXEL_8BIT:
            raise InvalidParameter("RawImage.mirror only support raw8 or mono8")

        frame_data = GxFrameData()
        frame_data.status = self.frame_data.status
        frame_data.width = self.frame_data.width
        frame_data.height = self.frame_data.height
        frame_data.pixel_format = self.__raw8_pixel_format_mirror(self.frame_data.pixel_format, mirror_mode)
        if frame_data.pixel_format == -1:
            raise UnexpectedError("Rotate pixel format %s failed" % hex(self.frame_data.pixel_format).__str__())

        frame_data.image_size = self.frame_data.image_size
        frame_data.frame_id = self.frame_data.frame_id
        frame_data.timestamp = self.frame_data.timestamp
        # frame_data.buf_id = self.frame_data.buf_id
        frame_data.image_buf = None
        mirror_image = RawImage(frame_data)

        status = dx_image_mirror(self.frame_data.image_buf, mirror_image.frame_data.image_buf, self.frame_data.width,
                                 self.frame_data.height, mirror_mode)

        if status != DxStatus.OK:
            raise UnexpectedError("RawImage.mirror: failed, error code:%s" % hex(status).__str__())

        return mirror_image

    '''
    def raw8_image_process(self, color_img_process_param):
        """
        :brief  Raw8 image process
        :param  color_img_process_param:  image process param, refer to DxColorImgProcess
        :return img_rgb
        """
        if self.frame_data.pixel_format & PIXEL_BIT_MASK != GX_PIXEL_8BIT or \
                self.frame_data.pixel_format == GxPixelFormatEntry.MONO8:
            raise ParameterTypeError("RawImage.raw8_image_process only support bayer raw8")

        if not isinstance(color_img_process_param, DxColorImgProcess):
            raise ParameterTypeError("RawImage.raw8_image_process img_process_param must be DxColorImgProcess type")

        color_img_process_param.check_param_type()

        frame_data = GxFrameData()
        frame_data.status = self.frame_data.status
        frame_data.width = self.frame_data.width
        frame_data.height = self.frame_data.height
        frame_data.pixel_format = GxPixelFormatEntry.RGB8_PLANAR
        frame_data.image_size = self.frame_data.image_size * 3
        frame_data.frame_id = self.frame_data.frame_id
        frame_data.timestamp = self.frame_data.timestamp
        # frame_data.buf_id = self.frame_data.buf_id
        frame_data.image_buf = None
        image_rgb = RGBImage(frame_data)

        status = dx_raw8_image_process(self.frame_data.image_buf, image_rgb.frame_data.image_buf,
                                       self.frame_data.width, self.frame_data.height, color_img_process_param)

        if status != DxStatus.OK:
            raise UnexpectedError("RawImage.raw8_image_process: failed, error code:%s" % hex(status).__str__())

        return image_rgb

    def mono8_image_process(self, mono_img_process_param):
        """
        :brief  mono8 image process
        :param  mono_img_process_param:  image process param, refer to DxMonoImgProcess
        :return img_mono
        """
        if self.frame_data.pixel_format != GxPixelFormatEntry.MONO8:
            raise ParameterTypeError("RawImage.mono8_image_process only support mono8")

        if not isinstance(mono_img_process_param, DxMonoImgProcess):
            raise ParameterTypeError("RawImage.mono8_image_process img_process_param must be DxMonoImgProcess type")

        mono_img_process_param.check_param_type()

        frame_data = GxFrameData()
        frame_data.status = self.frame_data.status
        frame_data.width = self.frame_data.width
        frame_data.height = self.frame_data.height
        frame_data.pixel_format = self.frame_data.pixel_format
        frame_data.image_size = self.frame_data.image_size
        frame_data.frame_id = self.frame_data.frame_id
        frame_data.timestamp = self.frame_data.timestamp
        # frame_data.buf_id = self.frame_data.buf_id
        frame_data.image_buf = None
        image_mono = RawImage(frame_data)

        status = dx_mono8_image_process(self.frame_data.image_buf, image_mono.frame_data.image_buf,
                                        self.frame_data.width, self.frame_data.height, mono_img_process_param)

        if status != DxStatus.OK:
            raise UnexpectedError("RawImage.mono8_image_process: failed, error code:%s" % hex(status).__str__())

        return image_mono
    '''

    def get_ffc_coefficients(self, dark_img=None, target_value=None):
        """
        :brief  Get Flat Field Correction Coefficients
                (only support raw8 raw10 raw12)
        :param  dark_img:           dark image, type should be RawImage
        :param  target_value:       correction target Value
        :return ffc_coefficients:   flat field correction coefficients Buffer
        """
        if dark_img is not None:
            _InterUtility.check_type(dark_img, RawImage, "dark_img", "Utility", "get_ffc_coefficients")

        if target_value is not None:
            _InterUtility.check_type(target_value, INT_TYPE, "target_value", "Utility", "get_ffc_coefficients")

        actual_bits = _InterUtility.get_bit_depth(self.frame_data.pixel_format)
        if actual_bits not in (GxPixelSizeEntry.BPP8, GxPixelSizeEntry.BPP10, GxPixelSizeEntry.BPP12):
            raise InvalidParameter("Utility.get_ffc_coefficients only support raw8, raw10, raw12")

        if dark_img is None:
            status, ffc_coefficients, _ = dx_get_ffc_coefficients(self.frame_data.image_buf,
                                                                  None,
                                                                  actual_bits,
                                                                  _InterUtility.get_pixel_color_filter(
                                                                      self.frame_data.pixel_format),
                                                                  self.frame_data.width, self.frame_data.height,
                                                                  target_value)
        else:
            if self.frame_data.width != dark_img.get_width() or \
                    self.frame_data.height != dark_img.get_height() or \
                    self.frame_data.pixel_format != dark_img.get_pixel_format():
                raise InvalidParameter("Utility.get_ffc_coefficients, the width/height/format of raw image and dark "
                                       "image is different")

            status, ffc_coefficients, _ = dx_get_ffc_coefficients(self.frame_data.image_buf,
                                                                  dark_img.frame_data.image_buf,
                                                                  actual_bits,
                                                                  _InterUtility.get_pixel_color_filter(
                                                                      self.frame_data.pixel_format),
                                                                  self.frame_data.width, self.frame_data.height,
                                                                  target_value)

        if status != DxStatus.OK:
            raise UnexpectedError("Utility.get_ffc_coefficients failure, Error code:%s" % hex(status).__str__())

        return Buffer(ffc_coefficients)

    def flat_field_correction(self, ffc_coefficients):
        """
        :brief      Flat Field Correction Process
        :param      ffc_coefficients:   Flat field correction coefficients
        :return:    None
        """
        actual_bits = _InterUtility.get_bit_depth(self.frame_data.pixel_format)
        if actual_bits not in (GxPixelSizeEntry.BPP8, GxPixelSizeEntry.BPP10, GxPixelSizeEntry.BPP12):
            raise InvalidParameter("Utility.get_ffc_coefficients only support raw8, raw10, raw12")
        _InterUtility.check_type(ffc_coefficients, Buffer, "ffc_coefficients", "RawImage", "flat_field_correction")
        status = dx_flat_field_correction(self.frame_data.image_buf, self.frame_data.image_buf, actual_bits,
                                          self.frame_data.width, self.frame_data.height, ffc_coefficients)
        if status != DxStatus.OK:
            raise UnexpectedError("Utility.flat_field_correction failure, Error code:%s" % hex(status).__str__())

    def get_numpy_array(self):
        """
        :brief      Return data as a numpy.Array type with dimension Image.height * Image.width
        :return:    numpy.Array objects
        """
        if self.frame_data.status != GxFrameStatusList.SUCCESS:
            print("RawImage.get_numpy_array: This is a incomplete image")
            return None

        image_size = self.frame_data.width * self.frame_data.height

        if self.frame_data.pixel_format & PIXEL_BIT_MASK == GX_PIXEL_8BIT:
            image_np = numpy.frombuffer(self.__image_array, dtype=numpy.ubyte, count=image_size). \
                reshape(self.frame_data.height, self.frame_data.width)
        elif self.frame_data.pixel_format & PIXEL_BIT_MASK == GX_PIXEL_16BIT:
            image_np = numpy.frombuffer(self.__image_array, dtype=numpy.uint16, count=image_size). \
                reshape(self.frame_data.height, self.frame_data.width)
        elif self.frame_data.pixel_format == GxPixelFormatEntry.RGB8:
            image_np = numpy.frombuffer(self.__image_array, dtype=numpy.ubyte, count=image_size * 3). \
                reshape(self.frame_data.height, self.frame_data.width, 3)
        elif self.frame_data.pixel_format == GxPixelFormatEntry.BGR8:
            image_np = numpy.frombuffer(self.__image_array, dtype=numpy.ubyte, count=image_size * 3). \
            reshape(self.frame_data.height, self.frame_data.width, 3)
        elif self.frame_data.pixel_format in (GxPixelFormatEntry.MONO10_PACKED, GxPixelFormatEntry.MONO12_PACKED):
            image_np = numpy.frombuffer(self.__image_array, dtype=numpy.ubyte, count=image_size). \
            reshape(self.frame_data.height, self.frame_data.width)
        else:
            image_np = None

        return image_np

    def get_data(self):
        """
        :brief      get Raw data
        :return:    raw data[string]
        """
        image_str = string_at(self.__image_array, self.frame_data.image_size)
        return image_str

    def get_chunkdata(self):
        """
        :brief      get Raw data
        :return:    raw data[string]
        """
        if self.frame_data.pixel_format & PIXEL_BIT_MASK == GX_PIXEL_8BIT:
            imagedata_size = self.frame_data.width * self.frame_data.height
        elif self.frame_data.pixel_format & PIXEL_BIT_MASK == GX_PIXEL_16BIT:
            imagedata_size = self.frame_data.width * self.frame_data.height * 2
        elif self.frame_data.pixel_format & PIXEL_BIT_MASK == GX_PIXEL_12BIT:
            imagedata_size = int(self.frame_data.width * self.frame_data.height * 1.5)
        elif self.frame_data.pixel_format & PIXEL_BIT_MASK == GX_PIXEL_24BIT:
            imagedata_size = self.frame_data.width * self.frame_data.height * 3
        else:
            imagedata_size = 0

        chunkdata_str = string_at(self.frame_data.image_buf+imagedata_size, self.frame_data.image_size - imagedata_size )
        return chunkdata_str

    def save_raw(self, file_path):
        """
        :brief      save raw data
        :param      file_path:      file path
        :return:    None
        """
        if not isinstance(file_path, str):
            raise ParameterTypeError("RawImage.save_raw: "
                                     "Expected file_path type is str, not %s" % type(file_path))

        try:
            fp = open(file_path, "wb")
            fp.write(self.__image_array)
            fp.close()
        except Exception as error:
            raise UnexpectedError("RawImage.save_raw:%s" % error)

    def get_status(self):
        """
        :brief      get raw data status
        :return:    status
        """
        return self.frame_data.status

    def get_width(self):
        """
        :brief      get width of raw data
        :return:    width
        """
        return self.frame_data.width

    def get_height(self):
        """
        :brief     get height of raw data
        :return:
        """
        return self.frame_data.height

    def get_pixel_format(self):
        """
        :brief      Get image pixel format
        :return:    pixel format
        """
        return self.frame_data.pixel_format

    def get_image_size(self):
        """
        :brief      Get raw data size
        :return:    size
        """
        return self.frame_data.image_size

    def get_frame_id(self):
        """
        :brief      Get  frame id of raw data
        :return:    frame id
        """
        return self.frame_data.frame_id

    def get_timestamp(self):
        """
        :brief      Get timestamp of raw data
        :return:    timestamp
        """
        return self.frame_data.timestamp

    def get_user_param(self):
        """
        :brief      Get  user param of raw data
        :return:    user param
        """
        return self.user_param

class Utility:
    def __init__(self):
        pass

    @staticmethod
    def get_gamma_lut(gamma=1):
        """
        :brief   Calculating gamma lookup table (RGB24)
        :param   gamma:  gamma param,range(0.1 ~ 10)
        :return: gamma_lut buffer
        """
        if not (isinstance(gamma, (INT_TYPE, float))):
            raise ParameterTypeError("Utility.get_gamma_lut: "
                                     "Expected gamma type is float, not %s" % type(gamma))

        if (gamma < GAMMA_MIN) or (gamma > GAMMA_MAX):
            print("Utility.get_gamma_lut: gamma out of bounds, range:[0.1, 10.0]")
            return None

        status, gamma_lut, gamma_lut_len = dx_get_gamma_lut(gamma)
        if status != DxStatus.OK:
            print("Utility.get_gamma_lut: get gamma lut failure, Error code:%s" % hex(status).__str__())
            return None

        return Buffer(gamma_lut)

    @staticmethod
    def get_contrast_lut(contrast=0):
        """
        :brief   Calculating contrast lookup table (RGB24)
        :param   contrast:   contrast param,range(-50 ~ 100)
        :return: contrast_lut buffer
        """
        if not (isinstance(contrast, INT_TYPE)):
            raise ParameterTypeError("Utility.get_contrast_lut: "
                                     "Expected contrast type is int, not %s" % type(contrast))

        if (contrast < CONTRAST_MIN) or (contrast > CONTRAST_MAX):
            print("Utility.get_contrast_lut: contrast out of bounds, range:[-50, 100]")
            return None

        status, contrast_lut, contrast_lut_len = dx_get_contrast_lut(contrast)
        if status != DxStatus.OK:
            print("Utility.get_contrast_lut: get contrast lut failure, Error code:%s" % hex(status).__str__())
            return None

        return Buffer(contrast_lut)

    @staticmethod
    def get_lut(contrast=0, gamma=1, lightness=0):
        """
        :brief      Calculating lookup table of 8bit image
        :param      contrast:   contrast param, range(-50 ~ 100)
        :param      gamma:      gamma param, range(0.1 ~ 10)
        :param      lightness:  lightness param, range(-150 ~ 150)
        :return:    lut buffer
        """
        if not (isinstance(contrast, INT_TYPE)):
            raise ParameterTypeError("Utility.get_lut: "
                                     "Expected contrast type is int, not %s" % type(contrast))

        if not (isinstance(gamma, (INT_TYPE, float))):
            raise ParameterTypeError("Utility.get_lut: "
                                     "Expected gamma type is float, not %s" % type(gamma))

        if not (isinstance(lightness, INT_TYPE)):
            raise ParameterTypeError("Utility.get_lut: "
                                     "Expected lightness type is int, not %s" % type(lightness))

        status, lut, lut_length = dx_get_lut(contrast, gamma, lightness)
        if status != DxStatus.OK:
            print("Utility.get_lut: get lut failure, Error code:%s" % hex(status).__str__())
            return None

        return Buffer(lut)

    @staticmethod
    def calc_cc_param(color_correction_param, saturation=64):
        """
        :brief      calculating array of image processing color adjustment
        :param      color_correction_param: color correction param address(get from camera)
        :param      saturation:             saturation factor,Range(0~128)
        :return:    cc param buffer
        """
        if not (isinstance(color_correction_param, INT_TYPE)):
            raise ParameterTypeError("Utility.calc_cc_param: Expected color_correction_param "
                                     "type is int, not %s" % type(color_correction_param))

        if not (isinstance(saturation, INT_TYPE)):
            raise ParameterTypeError("Utility.calc_cc_param: "
                                     "Expected saturation type is int, not %s" % type(saturation))

        status, cc_param = dx_calc_cc_param(color_correction_param, saturation)
        if status != DxStatus.OK:
            print("Utility.calc_cc_param: calc correction param failure, Error code:%s" % hex(status).__str__())
            return None

        return Buffer(cc_param)

    @staticmethod
    def calc_user_set_cc_param(color_transform_factor, saturation=64):
        """
        :brief      calculating array of image processing color adjustment
        :param      color_transform_factor: color correction param address(user set),
                                            type should be list or tuple, size = 3*3=9
        :param      saturation:             saturation factor,Range(0~128)
        :return:    cc param buffer
        """
        _InterUtility.check_type(color_transform_factor, (list, tuple), "color_transform_factor",
                                 "Utility", "calc_user_set_cc_param")
        if len(color_transform_factor) != COLOR_TRANSFORM_MATRIX_SIZE:
            raise InvalidParameter("Utility.calc_user_set_cc_param  "
                                   "color_transform_factor should be list or tuple, length = 9")

        status, cc_param = dx_calc_user_set_cc_param(color_transform_factor, saturation)
        if status != DxStatus.OK:
            print("Utility.calc_user_set_cc_param: calc correction param failure, "
                  "Error code:%s" % hex(status).__str__())
            return None

        return Buffer(cc_param)


    @staticmethod
    def __is_bayer(pixel_format):
        bayer_gr8_id = (GxPixelFormatEntry.BAYER_GR8 & PIXEL_ID_MASK)
        bayer_bg12_id = (GxPixelFormatEntry.BAYER_BG12 & PIXEL_ID_MASK)

        bayer_gr14_id = (GxPixelFormatEntry.BAYER_GR14 & PIXEL_ID_MASK)
        bayer_bg14_id = (GxPixelFormatEntry.BAYER_BG14 & PIXEL_ID_MASK)

        bayer_gr16_id = (GxPixelFormatEntry.BAYER_GR16 & PIXEL_ID_MASK)
        bayer_bg16_id = (GxPixelFormatEntry.BAYER_BG16 & PIXEL_ID_MASK)
        if ((pixel_format & PIXEL_ID_MASK) >= bayer_gr8_id) and ((pixel_format & PIXEL_ID_MASK) <= bayer_bg12_id):
            return True
        elif ((pixel_format & PIXEL_ID_MASK) >= bayer_gr14_id) and ((pixel_format & PIXEL_ID_MASK) <= bayer_bg14_id):
            return True
        elif ((pixel_format & PIXEL_ID_MASK) >= bayer_gr16_id) and ((pixel_format & PIXEL_ID_MASK) <= bayer_bg16_id):
            return True

        return False

    @staticmethod
    def __pixel_suffix(pixel_format):
        return (pixel_format & PIXEL_ID_MASK)

    @staticmethod
    def __is_bayer_packed(pixel_format):
        if (Utility.__pixel_suffix(pixel_format) >= Utility.__pixel_suffix(GxPixelFormatEntry.BAYER_BG10_P)) \
                and (Utility.__pixel_suffix(pixel_format) <= Utility.__pixel_suffix(GxPixelFormatEntry.BAYER_RG12_P)):
            return True
        elif (Utility.__pixel_suffix(pixel_format) >= Utility.__pixel_suffix(GxPixelFormatEntry.BAYER_GR14_P)) \
                and (Utility.__pixel_suffix(pixel_format) <= Utility.__pixel_suffix(GxPixelFormatEntry.BAYER_BG14_P)):
            return True
        elif (Utility.__pixel_suffix(pixel_format) >= Utility.__pixel_suffix(GxPixelFormatEntry.BAYER_BG10_P)) \
                and (Utility.__pixel_suffix(pixel_format) <= Utility.__pixel_suffix(GxPixelFormatEntry.BAYER_RG12_P)):
            return True
        elif (Utility.__pixel_suffix(pixel_format) >= Utility.__pixel_suffix(GxPixelFormatEntry.BAYER_GR10_PACKED)) \
                and (Utility.__pixel_suffix(pixel_format) <= Utility.__pixel_suffix(GxPixelFormatEntry.BAYER_BG12_PACKED)):
            return True

        return False


    @staticmethod
    def is_gray(pixel_format):
        if (pixel_format & PIXEL_COLOR_MASK) != PIXEL_MONO:
            return False
        elif (pixel_format & PIXEL_COLOR_MASK) == PIXEL_COLOR:
            return False
        elif (Utility.__is_bayer(pixel_format)):
            return False
        elif (Utility.__is_bayer_packed(pixel_format)):
            return False

        else:
            return True

    @staticmethod
    def get_convert_dest_8bit_pixel_format(src_pixel_format):
        """
        :brief      Calculate pixel color filter based on pixel format
        :param      pixel_format
        :return:    pixel color filter
        """
        gr_pixel = (GxPixelFormatEntry.BAYER_GR10, GxPixelFormatEntry.BAYER_GR10_P,
                    GxPixelFormatEntry.BAYER_GR12, GxPixelFormatEntry.BAYER_GR12_P,
                    GxPixelFormatEntry.BAYER_GR14, GxPixelFormatEntry.BAYER_GR14_P,
                    GxPixelFormatEntry.BAYER_GR16, GxPixelFormatEntry.BAYER_GR10_PACKED,
                    GxPixelFormatEntry.BAYER_GR12_PACKED, GxPixelFormatEntry.BAYER_GR8)

        rg_pixel = (GxPixelFormatEntry.BAYER_RG10, GxPixelFormatEntry.BAYER_RG10_P,
                    GxPixelFormatEntry.BAYER_RG12, GxPixelFormatEntry.BAYER_RG12_P,
                    GxPixelFormatEntry.BAYER_RG14, GxPixelFormatEntry.BAYER_RG14_P,
                    GxPixelFormatEntry.BAYER_RG16, GxPixelFormatEntry.BAYER_RG10_PACKED,
                    GxPixelFormatEntry.BAYER_RG12_PACKED, GxPixelFormatEntry.BAYER_RG8)

        gb_pixel = (GxPixelFormatEntry.BAYER_GB10, GxPixelFormatEntry.BAYER_GB10_P,
                    GxPixelFormatEntry.BAYER_GB12, GxPixelFormatEntry.BAYER_GB12_P,
                    GxPixelFormatEntry.BAYER_GB14, GxPixelFormatEntry.BAYER_GB14_P,
                    GxPixelFormatEntry.BAYER_GB16, GxPixelFormatEntry.BAYER_GB10_PACKED,
                    GxPixelFormatEntry.BAYER_GB12_PACKED, GxPixelFormatEntry.BAYER_GB8)

        bg_pixel = (GxPixelFormatEntry.BAYER_BG10, GxPixelFormatEntry.BAYER_BG10_P,
                    GxPixelFormatEntry.BAYER_BG12, GxPixelFormatEntry.BAYER_BG12_P,
                    GxPixelFormatEntry.BAYER_BG14, GxPixelFormatEntry.BAYER_BG14_P,
                    GxPixelFormatEntry.BAYER_BG16, GxPixelFormatEntry.BAYER_BG10_PACKED,
                    GxPixelFormatEntry.BAYER_BG12_PACKED, GxPixelFormatEntry.BAYER_BG8)

        mono_pixel = (GxPixelFormatEntry.MONO10, GxPixelFormatEntry.MONO12,
                      GxPixelFormatEntry.MONO14, GxPixelFormatEntry.MONO16,
                      GxPixelFormatEntry.MONO10_PACKED, GxPixelFormatEntry.MONO12_PACKED,
                      GxPixelFormatEntry.MONO10_P, GxPixelFormatEntry.MONO12_P,
                      GxPixelFormatEntry.MONO14_P, GxPixelFormatEntry.MONO8)

        if src_pixel_format in gr_pixel:
            return GxPixelFormatEntry.BAYER_GR8
        elif src_pixel_format in rg_pixel:
            return GxPixelFormatEntry.BAYER_RG8
        elif src_pixel_format in gb_pixel:
            return GxPixelFormatEntry.BAYER_GB8
        elif src_pixel_format in bg_pixel:
            return GxPixelFormatEntry.BAYER_BG8
        elif src_pixel_format in mono_pixel:
            return GxPixelFormatEntry.MONO8
        elif src_pixel_format == GxPixelFormatEntry.R8:
            return GxPixelFormatEntry.R8
        elif src_pixel_format == GxPixelFormatEntry.G8:
            return GxPixelFormatEntry.G8
        elif src_pixel_format == GxPixelFormatEntry.B8:
            return GxPixelFormatEntry.B8
        else:
            return GxPixelFormatEntry.UNDEFINED

class _InterUtility:
    def __init__(self):
        pass

    @staticmethod
    def check_type(var, var_type, var_name="", class_name="", func_name=""):
        """
        :chief  check type
        """
        if not isinstance(var, var_type):
            if not isinstance(var_type, tuple):
                raise ParameterTypeError("{} {}: Expected {} type is {}, not {}".format(class_name,
                                                                                        func_name, var_name,
                                                                                        var_type.__name__,
                                                                                        type(var).__name__))
            else:
                type_name = ""
                for i, name in enumerate(var_type):
                    type_name = type_name + name.__name__
                    if i != len(var_type) - 1:
                        type_name = type_name + ", "
                raise ParameterTypeError("{} {}: Expected {} type is ({}), not {}".format(class_name,
                                                                                          func_name, var_name,
                                                                                          type_name,
                                                                                          type(var).__name__))

    @staticmethod
    def get_pixel_color_filter(pixel_format):
        """
        :brief      Calculate pixel color filter based on pixel format
        :param      pixel_format
        :return:    pixel color filter
        """
        gr_tup = (GxPixelFormatEntry.BAYER_GR8, GxPixelFormatEntry.BAYER_GR10,
                  GxPixelFormatEntry.BAYER_GR12, GxPixelFormatEntry.BAYER_GR16,
                  GxPixelFormatEntry.BAYER_GR10_PACKED, GxPixelFormatEntry.BAYER_GR12_PACKED,
                  GxPixelFormatEntry.BAYER_GR10_P, GxPixelFormatEntry.BAYER_GR12_P,
                  GxPixelFormatEntry.BAYER_GR14, GxPixelFormatEntry.BAYER_GR14_P)

        rg_tup = (GxPixelFormatEntry.BAYER_RG8, GxPixelFormatEntry.BAYER_RG10,
                  GxPixelFormatEntry.BAYER_RG12, GxPixelFormatEntry.BAYER_RG16,
                  GxPixelFormatEntry.BAYER_RG10_PACKED, GxPixelFormatEntry.BAYER_RG12_PACKED,
                  GxPixelFormatEntry.BAYER_RG10_P, GxPixelFormatEntry.BAYER_RG12_P,
                  GxPixelFormatEntry.BAYER_RG14, GxPixelFormatEntry.BAYER_RG14_P)

        gb_tup = (GxPixelFormatEntry.BAYER_GB8, GxPixelFormatEntry.BAYER_GB10,
                  GxPixelFormatEntry.BAYER_GB12, GxPixelFormatEntry.BAYER_GB16,
                  GxPixelFormatEntry.BAYER_GB10_PACKED, GxPixelFormatEntry.BAYER_GB12_PACKED,
                  GxPixelFormatEntry.BAYER_GB10_P, GxPixelFormatEntry.BAYER_GB12_P,
                  GxPixelFormatEntry.BAYER_GB14, GxPixelFormatEntry.BAYER_GB14_P)

        bg_tup = (GxPixelFormatEntry.BAYER_BG8, GxPixelFormatEntry.BAYER_BG10,
                  GxPixelFormatEntry.BAYER_BG12, GxPixelFormatEntry.BAYER_BG16,
                  GxPixelFormatEntry.BAYER_BG10_PACKED, GxPixelFormatEntry.BAYER_BG12_PACKED,
                  GxPixelFormatEntry.BAYER_BG10_P, GxPixelFormatEntry.BAYER_BG12_P,
                  GxPixelFormatEntry.BAYER_BG14, GxPixelFormatEntry.BAYER_BG14_P)

        mono_tup = (GxPixelFormatEntry.MONO8, GxPixelFormatEntry.MONO8_SIGNED,
                    GxPixelFormatEntry.MONO10, GxPixelFormatEntry.MONO12,
                    GxPixelFormatEntry.MONO14, GxPixelFormatEntry.MONO16,
                    GxPixelFormatEntry.MONO10_PACKED, GxPixelFormatEntry.MONO12_PACKED,
                    GxPixelFormatEntry.MONO10_P, GxPixelFormatEntry.MONO12_P,
                    GxPixelFormatEntry.MONO14_P)

        if pixel_format in gr_tup:
            return DxPixelColorFilter.GR
        elif pixel_format in rg_tup:
            return DxPixelColorFilter.RG
        elif pixel_format in gb_tup:
            return DxPixelColorFilter.GB
        elif pixel_format in bg_tup:
            return DxPixelColorFilter.BG
        elif pixel_format in mono_tup:
            return DxPixelColorFilter.NONE
        else:
            return -1

    @staticmethod
    def get_bit_depth(pixel_format):
        """
        :brief      Calculate pixel depth based on pixel format
        :param      pixel_format
        :return:    pixel depth
        """
        bpp8_tup = (GxPixelFormatEntry.YUV422_8, GxPixelFormatEntry.YUV422_8_UYVY)

        bpp10_tup = (GxPixelFormatEntry.MONO10, GxPixelFormatEntry.BAYER_GR10, GxPixelFormatEntry.BAYER_RG10,
                     GxPixelFormatEntry.BAYER_GB10, GxPixelFormatEntry.BAYER_BG10, GxPixelFormatEntry.MONO10_PACKED,
                     GxPixelFormatEntry.BAYER_GR10_P, GxPixelFormatEntry.BAYER_RG10_P, GxPixelFormatEntry.BAYER_GB10_P,
                     GxPixelFormatEntry.BAYER_BG10_P, GxPixelFormatEntry.BAYER_RG10_PACKED,
                     GxPixelFormatEntry.BAYER_GR10_PACKED, GxPixelFormatEntry.BAYER_GB10_PACKED,
                     GxPixelFormatEntry.BAYER_BG10_PACKED, GxPixelFormatEntry.MONO10_P)

        bpp12_tup = (GxPixelFormatEntry.MONO12, GxPixelFormatEntry.BAYER_GR12, GxPixelFormatEntry.BAYER_RG12,
                     GxPixelFormatEntry.BAYER_GB12, GxPixelFormatEntry.BAYER_BG12, GxPixelFormatEntry.MONO12_PACKED,
                     GxPixelFormatEntry.BAYER_GR12_P, GxPixelFormatEntry.BAYER_RG12_P, GxPixelFormatEntry.BAYER_GB12_P,
                     GxPixelFormatEntry.BAYER_BG12_P, GxPixelFormatEntry.BAYER_RG12_PACKED,
                     GxPixelFormatEntry.BAYER_GR12_PACKED, GxPixelFormatEntry.BAYER_GB12_PACKED,
                     GxPixelFormatEntry.BAYER_BG12_PACKED, GxPixelFormatEntry.MONO12_P)

        bpp14_tup = (GxPixelFormatEntry.MONO14, GxPixelFormatEntry.MONO14_P,
                     GxPixelFormatEntry.BAYER_GR14, GxPixelFormatEntry.BAYER_RG14,
                     GxPixelFormatEntry.BAYER_GB14, GxPixelFormatEntry.BAYER_BG14,
                     GxPixelFormatEntry.BAYER_GR14_P, GxPixelFormatEntry.BAYER_RG14_P,
                     GxPixelFormatEntry.BAYER_BG14_P, GxPixelFormatEntry.BAYER_GB14_P)

        bpp16_tup = (GxPixelFormatEntry.MONO16, GxPixelFormatEntry.BAYER_GR16, GxPixelFormatEntry.BAYER_RG16,
                     GxPixelFormatEntry.BAYER_GB16, GxPixelFormatEntry.BAYER_BG16)

        if ((pixel_format & PIXEL_BIT_MASK) == GX_PIXEL_8BIT) or (pixel_format in bpp8_tup):
            return GxPixelSizeEntry.BPP8
        elif pixel_format in bpp10_tup:
            return GxPixelSizeEntry.BPP10
        elif pixel_format in bpp12_tup:
            return GxPixelSizeEntry.BPP12
        elif pixel_format in bpp14_tup:
            return GxPixelSizeEntry.BPP14
        elif pixel_format in bpp16_tup:
            return GxPixelSizeEntry.BPP16
        elif (pixel_format & PIXEL_BIT_MASK) == GX_PIXEL_24BIT:
            return GxPixelSizeEntry.BPP24
        elif (pixel_format & PIXEL_BIT_MASK) == GX_PIXEL_48BIT:
            return GxPixelSizeEntry.BPP48
        else:
            return -1

class DxColorImgProcess:
    def __init__(self):
        self.defective_pixel_correct = False  # bool
        self.denoise = False  # bool
        self.sharpness = False  # bool
        self.accelerate = False  # bool
        self.cc_param = None  # Buffer
        self.sharp_factor = 0  # float
        self.pro_lut = None  # Buffer
        self.convert_type = DxBayerConvertType.NEIGHBOUR  # DxBayerConvertType
        self.color_filter_layout = DxPixelColorFilter.RG  # DxPixelColorFilter
        self.flip = False  # bool

    def check_param_type(self):
        """
        :chief  check param type
        """
        _InterUtility.check_type(self.defective_pixel_correct, bool, "defective_pixel_correct",
                    "DxColorImgProcess", "check_param_type")

        _InterUtility.check_type(self.denoise, bool, "denoise",
                    "DxColorImgProcess", "check_param_type")

        _InterUtility.check_type(self.sharpness, bool, "sharpness",
                    "DxColorImgProcess", "check_param_type")

        _InterUtility.check_type(self.accelerate, bool, "accelerate",
                    "DxColorImgProcess", "check_param_type")

        _InterUtility.check_type(self.cc_param, (Buffer, type(None)), "cc_param",
                    "DxColorImgProcess", "check_param_type")

        _InterUtility.check_type(self.sharp_factor, (float, INT_TYPE), "sharp_factor",
                    "DxColorImgProcess", "check_param_type")

        _InterUtility.check_type(self.pro_lut, (Buffer, type(None)), "pro_lut",
                    "DxColorImgProcess", "check_param_type")

        _InterUtility.check_type(self.convert_type, INT_TYPE, "convert_type",
                    "DxColorImgProcess", "check_param_type")

        _InterUtility.check_type(self.color_filter_layout, INT_TYPE, "color_filter_layout",
                    "DxColorImgProcess", "check_param_type")

        _InterUtility.check_type(self.flip, bool, "flip",
                    "DxColorImgProcess", "check_param_type")


class DxMonoImgProcess:
    def __init__(self):
        self.defective_pixel_correct = False  # bool
        self.sharpness = False  # bool
        self.accelerate = False  # bool
        self.sharp_factor = 0  # float
        self.pro_lut = None  # Buffer

    def check_param_type(self):
        """
        :chief  check param type
        """
        _InterUtility.check_type(self.defective_pixel_correct, bool, "defective_pixel_correct",
                    "DxMonoImgProcess", "check_param_type")

        _InterUtility.check_type(self.sharpness, bool, "sharpness",
                    "DxMonoImgProcess", "check_param_type")

        _InterUtility.check_type(self.accelerate, bool, "accelerate",
                    "DxMonoImgProcess", "check_param_type")

        _InterUtility.check_type(self.sharp_factor, (float, INT_TYPE), "sharp_factor",
                    "DxMonoImgProcess", "check_param_type")

        _InterUtility.check_type(self.pro_lut, (Buffer, type(None)), "pro_lut",
                    "DxMonoImgProcess", "check_param_type")

