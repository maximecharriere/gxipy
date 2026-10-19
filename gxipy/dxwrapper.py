#!/usr/bin/python
# -*- coding:utf-8 -*-
# -*-mode:python ; tab-width:4 -*- ex:set tabstop=4 shiftwidth=4 expandtab: -*-
#

from ctypes import *
import sys
import os

if sys.platform == 'linux2' or sys.platform == 'linux':
    if os.path.exists('/usr/lib/libdximageproc.so') : 
        filepath = '/usr/lib/libdximageproc.so'
    else:
        filepath = '/usr/lib/libgxiapi.so'
    try:
        dll = CDLL(filepath)
    except OSError:
        print('Cannot find libdximageproc.so or libgxiapi.so.')
else:
    try:
        if (sys.version_info.major == 3 and sys.version_info.minor >= 8) or (sys.version_info.major > 3):
            dll = WinDLL('DxImageProc.dll', winmode=0)
        else:
            dll = WinDLL('DxImageProc.dll')
    except OSError:
        print('Cannot find DxImageProc.dll.')

def string_encoding(string):
    """
    :breif      Python3.X: String encoded as bytes
    :param      string
    :return:
    """
    if sys.version_info.major == 3:
        string = string.encode()
    return string

# image format handle
class DxImageFormatConvertHandle:

    def __init__(self):
        pass

# status  definition
class DxStatus:
    OK = 0                               # Operation is successful
    PARAMETER_INVALID = -101             # Invalid input parameter
    PARAMETER_OUT_OF_BOUND = -102        # The input parameter is out of bounds
    NOT_ENOUGH_SYSTEM_MEMORY = -103      # System out of memory
    NOT_FIND_DEVICE = -104               # not find device
    STATUS_NOT_SUPPORTED = -105          # operation is not supported
    CPU_NOT_SUPPORT_ACCELERATE = -106    # CPU does not support acceleration
  
    def __init__(self):
        pass

# Bayer layout
class DxPixelColorFilter:
    NONE = 0                                # Isn't bayer format
    RG = 1                                  # The first row starts with RG
    GB = 2                                  # The first line starts with GB
    GR = 3                                  # The first line starts with GR
    BG = 4                                  # The first line starts with BG

    def __init__(self):
        pass
            

# image actual bits
class DxActualBits:
    BITS_8 = 8               # 8bit
    BITS_10 = 10             # 10bit
    BITS_12 = 12             # 12bit
    BITS_14 = 14             # 14bit
    BITS_16 = 16             # 16bit

    def __init__(self):
        pass

# image mirror method
class DxImageMirrorMethod:
    HORIZONTAL_MIRROR = 0
    VERTICAL_MIRROR = 1

    def __init__(self):
        pass

# mono8 image process structure
class MonoImgProcess(Structure):
    _fields_ = [
        ('defective_pixel_correct',     c_bool),        # Pixel correct switch
        ('sharpness',                   c_bool),        # Sharpness switch
        ('accelerate',                  c_bool),        # Accelerate switch
        ('sharp_factor',                c_float),       # Sharpen the intensity factor
        ('pro_lut',                     c_void_p),      # Lookup table
        ('lut_length',                  c_uint16),      # Lut Buffer length
        ('array_reserved',              c_ubyte * 32),  # Reserved
    ]

    def __str__(self):
        return "MonoImgProcess\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)


# Raw8 Image process structure
class ColorImgProcess(Structure):
    _fields_ = [
        ('defective_pixel_correct',     c_bool),        # Pixel correct switch
        ('denoise',                     c_bool),        # Noise reduction switch
        ('sharpness',                   c_bool),        # Sharpness switch
        ('accelerate',                  c_bool),        # Accelerate switch
        ('arr_cc',                      c_void_p),      # Color processing parameters
        ('cc_buf_length',               c_uint8),       # Color processing parameters length(sizeof(VxInt16)*9)
        ('sharp_factor',                c_float),       # Sharpen the intensity factor
        ('pro_lut',                     c_void_p),      # Lookup table
        ('lut_length',                  c_uint16),      # The length of the lookup table
        ('cv_type',                     c_uint),        # Interpolation algorithm
        ('layout',                      c_uint),        # Bayer format
        ('flip',                        c_bool),        # Image flip flag
        ('array_reserved',              c_ubyte * 32),  # Reserved
    ]

    def __str__(self):
        return "ColorImgProcess\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)


# Field correction process structure
class FieldCorrectionProcess(Structure):
    _fields_ = [
        ('bright_buf',                  c_void_p),      # Bright image buffer
        ('dark_buf',                    c_void_p),      # Dark image buffer
        ('width',                       c_uint32),      # image width
        ('height',                      c_uint32),      # image height
        ('actual_bits',                 c_uint),        # image actual bits
        ('bayer_type',                  c_uint),        # Bayer Type
    ]

    def __str__(self):
        return "FieldCorrectionProcess\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)


# color transform factor
class ColorTransformFactor(Structure):
    _fields_ = [
        ('fGain00', c_float),   # red   contribution to the red   pixel (multiplicative factor)
        ('fGain01', c_float),   # green contribution to the red   pixel (multiplicative factor)
        ('fGain02', c_float),   # blue  contribution to the red   pixel (multiplicative factor)
        ('fGain10', c_float),   # red   contribution to the green pixel (multiplicative factor)
        ('fGain11', c_float),   # green contribution to the green pixel (multiplicative factor)
        ('fGain12', c_float),   # blue  contribution to the green pixel (multiplicative factor)
        ('fGain20', c_float),   # red   contribution to the blue  pixel (multiplicative factor)
        ('fGain21', c_float),   # green contribution to the blue  pixel (multiplicative factor)
        ('fGain22', c_float),   # blue  contribution to the blue  pixel (multiplicative factor)
    ]

    def __str__(self):
        return "ColorTransformFactor\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)

# Field correction process structure
class StaticDefectCorrection(Structure):
    _fields_ = [
        ('width',                       c_uint32),      # image width
        ('height',                      c_uint32),      # image height
        ('OffsetX',                     c_uint32),      # image off x
        ('OffSetY',                     c_uint32),      # image off y
        ('WidthMax',                    c_uint32),      # image width max
        ('bayer_type',                  c_uint),        # Bayer Type
        ('actual_bits',                 c_uint),        # image actual bits
    ]

    def __str__(self):
        return "FieldCorrectionProcess\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)

# Field correction process structure
class FlatFieldCorrectionParameter(Structure):
    _fields_ = [
        ('bright_buf',                  c_void_p),      # Bright image buffer
        ('dark_buf',                    c_void_p),      # Dark image buffer
        ('pixel_format',                c_uint),        # pixel format
        ('width',                       c_int32),      # image width
        ('height',                      c_int32),      # image height
        ('block_size',                  c_int32),      # block size
        ('expected_gray',               c_int32),      # FFC expected gray value
        ('array_reserved',              c_int32 * 64),  # Reserved
    ]

    def __str__(self):
        return "FlatFieldCorrectionParameter\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)

if hasattr(dll, 'DxGetLut'):
    def dx_get_lut(contrast_param, gamma, lightness):
        """
        :brief calculating lookup table of 8bit image
        :param contrast_param:  contrast param,range(-50~100)
        :param gamma:           gamma param,range(0.1~10)
        :param lightness:       lightness param,range(-150~150)
        :return: status         State return value, See detail in DxStatus
                 lut            lookup table
                 lut_length     lookup table length(unit:byte)
        """
        contrast_param_c = c_int32()
        contrast_param_c.value = contrast_param

        gamma_c = c_double()
        gamma_c.value = gamma

        lightness_c = c_int32()
        lightness_c.value = lightness

        lut_length_c = c_uint16()
        lut_length_c.value = 0

        # Get length of the lookup table
        dll.DxGetLut(contrast_param_c, gamma_c, lightness_c, None, byref(lut_length_c))

        # Create buff to get LUT data
        lut_c = (c_uint8 * lut_length_c.value)()
        status = dll.DxGetLut(contrast_param_c, gamma_c, lightness_c,  byref(lut_c), byref(lut_length_c))

        return status, lut_c, lut_length_c.value

CC_PARAM_ARRAY_LEN = 18

if hasattr(dll, "DxCalcCCParam"):
    def dx_calc_cc_param(color_cc_param, saturation):
        """
        :brief  calculating array of image processing color adjustment
        :param  color_cc_param:     color correction param address(get from camera)
        :param  saturation:         saturation factor,Range(0~128)
        :return: status:            State return value, See detail in DxStatus
                 cc_param:          color adjustment calculating array
        """
        color_cc_param_c = c_int64()
        color_cc_param_c.value = color_cc_param

        saturation_c = c_int16()
        saturation_c.value = saturation

        length_c = c_uint8()
        # DxCalcCCParam length = sizeof(int16)*9 = 2 * 9 = 18
        length_c.value = CC_PARAM_ARRAY_LEN

        # Create buff to get cc data
        cc_param_c = (c_int16 * length_c.value)()

        status = dll.DxCalcCCParam(color_cc_param_c, saturation_c, byref(cc_param_c), length_c)

        return status, cc_param_c


if hasattr(dll, "DxCalcUserSetCCParam"):
    def dx_calc_user_set_cc_param(color_transform_factor, saturation):
        """
        :brief  calculating array of image processing color adjustment
        :param  color_transform_factor:     color correction param address(user set),
                                            type should be list or tuple, size = 3*3=9
        :param  saturation:                 saturation factor,Range(0~128)
        :return: status:                    State return value, See detail in DxStatus
                 cc_param:                  color adjustment calculating array
        """
        color_transform_factor_c = ColorTransformFactor()
        color_transform_factor_c.fGain00 = color_transform_factor[0]
        color_transform_factor_c.fGain01 = color_transform_factor[1]
        color_transform_factor_c.fGain02 = color_transform_factor[2]
        color_transform_factor_c.fGain10 = color_transform_factor[3]
        color_transform_factor_c.fGain11 = color_transform_factor[4]
        color_transform_factor_c.fGain12 = color_transform_factor[5]
        color_transform_factor_c.fGain20 = color_transform_factor[6]
        color_transform_factor_c.fGain21 = color_transform_factor[7]
        color_transform_factor_c.fGain22 = color_transform_factor[8]

        saturation_c = c_int16()
        saturation_c.value = saturation

        length_c = c_uint8()
        # DxCalcCCParam length = sizeof(int16)*9 = 2 * 9 = 18
        length_c.value = CC_PARAM_ARRAY_LEN

        # Create buff to get cc data
        cc_param_c = (c_int16 * length_c.value)()

        status = dll.DxCalcUserSetCCParam(byref(color_transform_factor_c), saturation_c, byref(cc_param_c), length_c)

        return status, cc_param_c


if hasattr(dll, "DxGetGammatLut"):
    def dx_get_gamma_lut(gamma_param):
        """
        :brief  calculating gamma lookup table (RGB24)
        :param  gamma_param:    gamma param,range(0.1 ~ 10)
        :return: status:        State return value, See detail in DxStatus
                gamma_lut:      gamma lookup table
                lut_length:     gamma lookup table length(unit:byte)
        """
        gamma_param_c = c_double()
        gamma_param_c.value = gamma_param

        lut_length_c = c_int()
        status = dll.DxGetGammatLut(gamma_param_c, None, byref(lut_length_c))

        gamma_lut = (c_ubyte * lut_length_c.value)()
        status = dll.DxGetGammatLut(gamma_param_c, byref(gamma_lut), byref(lut_length_c))

        return status, gamma_lut, lut_length_c.value


if hasattr(dll, "DxGetContrastLut"):
    def dx_get_contrast_lut(contrast_param):
        """
        :brief  ccalculating contrast lookup table (RGB24)
        :param  contrast_param: contrast param,range(-50 ~ 100)
        :return: status:       State return value, See detail in DxStatus
                 contrast_lut: contrast lookup table
                 lut_length:   contrast lookup table length(unit:byte)
        """
        contrast_param_c = c_int()
        contrast_param_c.value = contrast_param

        lut_length_c = c_int()
        status = dll.DxGetContrastLut(contrast_param_c, None, byref(lut_length_c))

        contrast_lut = (c_ubyte * lut_length_c.value)()
        status = dll.DxGetContrastLut(contrast_param_c, byref(contrast_lut), byref(lut_length_c))

        return status, contrast_lut, lut_length_c.value


if hasattr(dll, 'DxRaw8toRGB24'):
    def dx_raw8_to_rgb24(input_address, output_address, width, height, convert_type, bayer_type, flip):
        """
        :brief  Convert Raw8 to Rgb24
        :param input_address:      The input raw image buff address, buff size = width * height
        :param output_address:     The output rgb image buff address, buff size = width * height * 3
        :param width:           Image width
        :param height:          Image height
        :param convert_type:    Bayer convert type, See detail in DxBayerConvertType
        :param bayer_type:      pixel color filter, See detail in DxPixelColorFilter
        :param flip:            Output image flip flag
                                True: turn the image upside down
                                False: do not flip
        :return: status         State return value, See detail in DxStatus
                 data_array     Array of output images, buff size = width * height * 3
        """
        width_c = c_uint32()
        width_c.value = width

        height_c = c_uint32()
        height_c.value = height

        convert_type_c = c_uint()
        convert_type_c.value = convert_type

        bayer_type_c = c_uint()
        bayer_type_c.value = bayer_type

        flip_c = c_bool()
        flip_c.value = flip

        input_address_p = c_void_p()
        input_address_p.value = input_address

        output_address_p = c_void_p()
        output_address_p.value = output_address

        status = dll.DxRaw8toRGB24(input_address_p, output_address_p,
                                   width_c, height_c, convert_type_c, bayer_type_c, flip_c)
        return status


if hasattr(dll, 'DxRaw8toRGB24Ex'):
    def dx_raw8_to_rgb24_ex(input_address, output_address, width, height, convert_type, bayer_type, flip, channel_order):
        """
        :brief  Convert Raw8 to Rgb24
        :param input_address:      The input raw image buff address, buff size = width * height
        :param output_address:     The output rgb image buff address, buff size = width * height * 3
        :param width:           Image width
        :param height:          Image height
        :param convert_type:    Bayer convert type, See detail in DxBayerConvertType
        :param bayer_type:      pixel color filter, See detail in DxPixelColorFilter
        :param flip:            Output image flip flag
                                True: turn the image upside down
                                False: do not flip
        :param channel_order:   RGB channel order of output image
        :return: status         State return value, See detail in DxStatus
                 data_array     Array of output images, buff size = width * height * 3
        """
        width_c = c_uint32()
        width_c.value = width

        height_c = c_uint32()
        height_c.value = height

        convert_type_c = c_uint()
        convert_type_c.value = convert_type

        bayer_type_c = c_uint()
        bayer_type_c.value = bayer_type

        flip_c = c_bool()
        flip_c.value = flip

        channel_order_c = c_uint()
        channel_order_c.value = channel_order

        input_address_p = c_void_p()
        input_address_p.value = input_address

        output_address_p = c_void_p()
        output_address_p.value = output_address

        status = dll.DxRaw8toRGB24Ex(input_address_p, output_address_p,
                                   width_c, height_c, convert_type_c, bayer_type_c, flip_c, channel_order_c)
        return status


if hasattr(dll, 'DxRaw16toRaw8'):
    def dx_raw16_to_raw8(input_address, out_address, width, height, valid_bits):
        """
        :brief  Raw16 converted to Raw8
        :param  input_address:     The input image buff address, buff size = width * height * 2
        :param  out_address:       The output image buff address, buff size = width * height
        :param  width:          Image width
        :param  height:         Image height
        :param  valid_bits:     Data valid digit, See detail in DxValidBit
        :return: status         State return value, See detail in DxStatus
                 data_array     Array of output images, buff size = width * height
        """
        width_c = c_uint32()
        width_c.value = width

        height_c = c_uint32()
        height_c.value = height

        valid_bits_c = c_uint()
        valid_bits_c.value = valid_bits

        input_address_p = c_void_p()
        input_address_p.value = input_address

        out_address_p = c_void_p()
        out_address_p.value = out_address

        status = dll.DxRaw16toRaw8(input_address_p, out_address_p,
                                   width_c, height_c, valid_bits_c)
        return status


if hasattr(dll, 'DxRotate90CW8B'):
    def dx_raw8_rotate_90_cw(input_address, out_address, width, height):
        """
        :brief  To rotate the 8-bit image clockwise by 90 degrees
        :param  input_address:     The input image buff address, buff size = width * height
        :param  out_address:       The output image buff address, buff size = width * height
        :param  width:          Image width
        :param  height:         Image height
        :return: status         State return value, See detail in DxStatus
                 data_array     Array of output images, buff size = width * height
        """
        width_c = c_uint32()
        width_c.value = width

        height_c = c_uint32()
        height_c.value = height

        input_address_p = c_void_p()
        input_address_p.value = input_address

        out_address_p = c_void_p()
        out_address_p.value = out_address

        status = dll.DxRotate90CW8B(input_address_p, out_address_p,
                                   width_c, height_c)
        return status


if hasattr(dll, 'DxRotate90CCW8B'):
    def dx_raw8_rotate_90_ccw(input_address, out_address, width, height):
        """
        :brief  To rotate the 8-bit image counter clockwise by 90 degrees
        :param  input_address:     The input image buff address, buff size = width * height
        :param  out_address:       The output image buff address, buff size = width * height
        :param  width:          Image width
        :param  height:         Image height
        :return: status         State return value, See detail in DxStatus
                 data_array     Array of output images, buff size = width * height
        """
        width_c = c_uint32()
        width_c.value = width

        height_c = c_uint32()
        height_c.value = height

        input_address_p = c_void_p()
        input_address_p.value = input_address

        out_address_p = c_void_p()
        out_address_p.value = out_address

        status = dll.DxRotate90CCW8B(input_address_p, out_address_p,
                                   width_c, height_c)
        return status


if hasattr(dll, "DxImageImprovment"):
    def dx_image_improvement(input_address, output_address, width, height,
                             color_correction_param, contrast_lut, gamma_lut):
        """
        :brief      image quality improvement
        :param      input_address:              input buffer address, buff size = width * height *3
        :param      output_address:             input buffer address, buff size = width * height *3
        :param      width:                      image width
        :param      height:                     image height
        :param      color_correction_param:     color correction param(get from camera)
        :param      contrast_lut:               contrast lookup table
        :param      gamma_lut:                  gamma lookup table
        :return:    status                      State return value, See detail in DxStatus
                    data_array                  Array of output images, buff size = width * height * 3
        """
        width_c = c_uint32()
        width_c.value = width

        height_c = c_uint32()
        height_c.value = height

        input_address_p = c_void_p()
        input_address_p.value = input_address

        output_address_p = c_void_p()
        output_address_p.value = output_address

        color_correction_param_c = c_int64()
        color_correction_param_c.value = color_correction_param

        status = dll.DxImageImprovment(input_address_p, output_address_p, width_c, height_c,
                                       color_correction_param_c, contrast_lut, gamma_lut)
        return status

if hasattr(dll, "DxImageImprovmentEx"):
    def dx_image_improvement_ex(input_address, output_address, width, height,
                                color_correction_param, contrast_lut, gamma_lut, channel_order):
        """
        :brief      image quality improvement
        :param      input_address:              input buffer address, buff size = width * height *3
        :param      output_address:             input buffer address, buff size = width * height *3
        :param      width:                      image width
        :param      height:                     image height
        :param      color_correction_param:     color correction param(get from camera)
        :param      contrast_lut:               contrast lookup table
        :param      gamma_lut:                  gamma lookup table
        :param      channel_order:              RGB channel order of output image
        :return:    status                      State return value, See detail in DxStatus
                    data_array                  Array of output images, buff size = width * height * 3
        """
        width_c = c_uint32()
        width_c.value = width

        height_c = c_uint32()
        height_c.value = height

        input_address_p = c_void_p()
        input_address_p.value = input_address

        output_address_p = c_void_p()
        output_address_p.value = output_address

        color_correction_param_c = c_int64()
        color_correction_param_c.value = color_correction_param

        channel_order_c = c_uint()
        channel_order_c.value = channel_order

        status = dll.DxImageImprovmentEx(input_address_p, output_address_p, width_c, height_c,
                                         color_correction_param_c, contrast_lut, gamma_lut, channel_order_c)
        return status


if hasattr(dll, "DxBrightness"):
    def dx_brightness(input_address, output_address, image_size, factor):
        """
        :brief      Brightness adjustment (RGB24 or mono8)
        :param      input_address:          input buffer address
        :param      output_address:         output buffer address
        :param      image_size:             image size
        :param      factor:                 brightness factor,range(-150 ~ 150)
        :return:    status:                 State return value, See detail in DxStatus
        """
        image_size_c = c_uint32()
        image_size_c.value = image_size

        factor_c = c_int32()
        factor_c.value = factor

        input_address_p = c_void_p()
        input_address_p.value = input_address

        output_address_p = c_void_p()
        output_address_p.value = output_address

        status = dll.DxBrightness(input_address_p, output_address_p, image_size_c, factor_c)
        return status


if hasattr(dll, "DxContrast"):
    def dx_contrast(input_address, output_address, image_size, factor):
        """
        :brief      Contrast adjustment (RGB24 or mono8)
        :param      input_address:          input buffer address
        :param      output_address:         output buffer address
        :param      image_size:             image size
        :param      factor:                 contrast factor,range(-50 ~ 100)
        :return:    status:                 State return value, See detail in DxStatus
        """
        image_size_c = c_uint32()
        image_size_c.value = image_size

        factor_c = c_int32()
        factor_c.value = factor

        input_address_p = c_void_p()
        input_address_p.value = input_address

        output_address_p = c_void_p()
        output_address_p.value = output_address

        status = dll.DxContrast(input_address_p, output_address_p, image_size_c, factor_c)
        return status


if hasattr(dll, "DxSaturation"):
    def dx_saturation(input_address, output_address, image_size, factor):
        """
        :brief      Saturation adjustment (RGB24)
        :param      input_address:          input buffer address, buff size = width * height * 3
        :param      output_address:         output buffer address, buff size = width * height * 3        
        :param      image_size:             image size (width * height)
        :param      factor:                 saturation factor,range(0 ~ 128)
        :return:    status:                 State return value, See detail in DxStatus
        """
        image_size_c = c_uint32()
        image_size_c.value = image_size

        factor_c = c_int32()
        factor_c.value = factor

        input_address_p = c_void_p()
        input_address_p.value = input_address

        output_address_p = c_void_p()
        output_address_p.value = output_address

        status = dll.DxSaturation(input_address_p, output_address_p, image_size_c, factor_c)
        return status


if hasattr(dll, "DxAutoRawDefectivePixelCorrect"):
    def dx_auto_raw_defective_pixel_correct(inout_address, width, height, bit_num):
        """
        :brief      Auto raw defective pixel correct,Support image from Raw8 to Raw16, the bit number is actual
                    bit number, when it is more than 8, the actual bit can be every number between 9 to 16.
                    And if image format is packed, you need convert it to Raw16.
                    This function should be used in each frame.
        :param      inout_address:          input & output buffer address
        :param      width:                  image width
        :param      height:                 image height
        :param      bit_num:                image bit number (for example:if image 10bit, nBitNum = 10,
                                                                          if image 12bit, nBitNum = 12,
                                                                          range:8 ~ 16)
        :return:    status:                 State return value, See detail in DxStatus
        """
        width_c = c_uint32()
        width_c.value = width

        height_c = c_uint32()
        height_c.value = height

        bit_num_c = c_int32()
        bit_num_c.value = bit_num

        inout_address_p = c_void_p()
        inout_address_p.value = inout_address

        status = dll.DxAutoRawDefectivePixelCorrect(inout_address_p, width_c, height_c, bit_num_c)
        return status


if hasattr(dll, "DxSharpen24B"):
    def dx_sharpen_24b(input_address, output_address, width, height, factor):
        """
        :brief      Sharpen adjustment (RGB24)
        :param      input_address:          input buffer address, buff size = width * height * 3
        :param      output_address:         output buffer address, buff size = width * height * 3
        :param      width:                  image width
        :param      height:                 image height
        :param      factor:                 sharpen factor, range(0.1~5.0)
        :return:    status:                 State return value, See detail in DxStatus
        """
        width_c = c_uint32()
        width_c.value = width

        height_c = c_uint32()
        height_c.value = height

        input_address_p = c_void_p()
        input_address_p.value = input_address

        output_address_p = c_void_p()
        output_address_p.value = output_address

        factor_c = c_float()
        factor_c.value = factor

        status = dll.DxSharpen24B(input_address_p, output_address_p, width_c, height_c, factor_c)
        return status


if hasattr(dll, "DxGetWhiteBalanceRatio"):
    def dx_get_white_balance_ratio(input_address, width, height):
        """
        :brief      Get white balance ratios(RGB24), In order to calculate accurately, the camera should
                    shoot objective "white" area,or input image is white area.
        :param      input_address:          input buffer address, buff size = width * height * 3
        :param      width:                  image width
        :param      height:                 image height
        :return:    status:                 State return value, See detail in DxStatus
                    (r_ratio, g_ratio, b_ratio):    rgb ratio tuple
        """
        width_c = c_uint32()
        width_c.value = width

        height_c = c_uint32()
        height_c.value = height

        input_address_p = c_void_p()
        input_address_p.value = input_address

        r_ratio_c = c_double()
        r_ratio_c.value = 0

        g_ratio_c = c_double()
        g_ratio_c.value = 0

        b_ratio_c = c_double()
        b_ratio_c.value = 0

        status = dll.DxGetWhiteBalanceRatio(input_address_p, width_c, height_c, byref(r_ratio_c),
                                            byref(g_ratio_c), byref(b_ratio_c))

        return status, (r_ratio_c.value, g_ratio_c.value, b_ratio_c.value)


if hasattr(dll, "DxImageMirror"):
    def dx_image_mirror(input_address, output_address, width, height, mirror_mode):
        """
        :brief      image mirror(raw8)
        :param      input_address:          input buffer address
        :param      output_address:         output buffer address
        :param      width:                  image width
        :param      height:                 image height
        :param      mirror_mode:            mirror mode
        :return:    status:                 State return value, See detail in DxStatus
        """
        width_c = c_uint32()
        width_c.value = width

        height_c = c_uint32()
        height_c.value = height

        mirror_mode_c = c_uint()
        mirror_mode_c.value = mirror_mode

        input_address_p = c_void_p()
        input_address_p.value = input_address

        output_address_p = c_void_p()
        output_address_p.value = output_address

        status = dll.DxImageMirror(input_address_p, output_address_p, width_c, height_c, mirror_mode_c)

        return status

if hasattr(dll, "DxRaw8ImgProcess"):
    def dx_raw8_image_process(input_address, output_address, width, height, color_img_process_param):
        """
        :brief  Raw8 image process
        :param  input_address:              input buffer address, buff size = width * height
        :param  output_address:             output buffer address, buff size = width * height * 3
        :param  width:                      image width
        :param  height:                     image height
        :param  color_img_process_param:    Raw8 image process param, refer to DxColorImgProcess
        """
        input_address_p = c_void_p()
        input_address_p.value = input_address

        output_address_p = c_void_p()
        output_address_p.value = output_address

        width_c = c_uint32()
        width_c.value = width

        height_c = c_uint32()
        height_c.value = height

        color_img_process_param_c = ColorImgProcess()
        color_img_process_param_c.defective_pixel_correct = color_img_process_param.defective_pixel_correct
        color_img_process_param_c.denoise = color_img_process_param.denoise
        color_img_process_param_c.sharpness = color_img_process_param.sharpness
        color_img_process_param_c.accelerate = color_img_process_param.accelerate
        if color_img_process_param.cc_param is None:
            color_img_process_param_c.arr_cc = None
            color_img_process_param_c.cc_buf_length = 0
        else:
            color_img_process_param_c.arr_cc = addressof(color_img_process_param.cc_param.get_ctype_array())
            color_img_process_param_c.cc_buf_length = color_img_process_param.cc_param.get_length()
        color_img_process_param_c.sharp_factor = color_img_process_param.sharp_factor
        if color_img_process_param.pro_lut is None:
            color_img_process_param_c.pro_lut = None
            color_img_process_param_c.lut_length = 0
        else:
            color_img_process_param_c.pro_lut = addressof(color_img_process_param.pro_lut.get_ctype_array())
            color_img_process_param_c.lut_length = color_img_process_param.pro_lut.get_length()
        color_img_process_param_c.cv_type = color_img_process_param.convert_type
        color_img_process_param_c.layout = color_img_process_param.color_filter_layout
        color_img_process_param_c.flip = color_img_process_param.flip

        status = dll.DxRaw8ImgProcess(input_address_p, output_address_p, width_c,
                                      height_c, byref(color_img_process_param_c))

        return status


if hasattr(dll, "DxMono8ImgProcess"):
    def dx_mono8_image_process(input_address, output_address, width, height, mono_img_process_param):
        """
        :brief  mono8 image process
        :param  input_address:              input buffer address, buff size = width * height
        :param  output_address:             output buffer address, buff size = width * height
        :param  width:                      image width
        :param  height:                     image height
        :param  mono_img_process_param:     mono8 image process param, refer to DxMonoImgProcess
        """
        input_address_p = c_void_p()
        input_address_p.value = input_address

        output_address_p = c_void_p()
        output_address_p.value = output_address

        width_c = c_uint32()
        width_c.value = width

        height_c = c_uint32()
        height_c.value = height

        mono_img_process_param_c = MonoImgProcess()
        mono_img_process_param_c.defective_pixel_correct = mono_img_process_param.defective_pixel_correct
        mono_img_process_param_c.sharpness = mono_img_process_param.sharpness
        mono_img_process_param_c.accelerate = mono_img_process_param.accelerate
        mono_img_process_param_c.sharp_factor = mono_img_process_param.sharp_factor
        if mono_img_process_param.pro_lut is None:
            mono_img_process_param_c.pro_lut = None
            mono_img_process_param_c.lut_length = 0
        else:
            mono_img_process_param_c.pro_lut = addressof(mono_img_process_param.pro_lut.get_ctype_array())
            mono_img_process_param_c.lut_length = mono_img_process_param.pro_lut.get_length()

        status = dll.DxMono8ImgProcess(input_address_p, output_address_p, width_c,
                                       height_c, byref(mono_img_process_param_c))

        return status

if hasattr(dll, 'DxGetFFCCoefficients'):
    def dx_get_ffc_coefficients(bright_img, dark_img, actual_bits, bayer_type, width, height, target_value):
        """
        :brief  Get Flat Field Correction Coefficients
                (only support raw8 raw10 raw12)
        :param  bright_img:         bright image
        :param  dark_img:           dark image
        :param  actual_bits:        image actual bits
        :param  bayer_type:         bayer type
        :param  width:              image width
        :param  height:             image height
        :param  target_value:       correction target Value
        :return status:             State return value, See detail in DxStatus
                ffc_coefficients:   flat field correction coefficients Buffer
                ffc_coefficients_length:  flat field correction coefficients Buffer length
        """
        field_correction_process_c = FieldCorrectionProcess()
        field_correction_process_c.bright_buf = bright_img
        field_correction_process_c.dark_buf = dark_img
        field_correction_process_c.width = width
        field_correction_process_c.height = height
        field_correction_process_c.actual_bits = actual_bits
        field_correction_process_c.bayer_type = bayer_type

        ffc_coefficients_len_c = c_int()
        ffc_coefficients_len_c.value = 0

        if target_value is None:
            # Get length of ffc coefficients
            dll.DxGetFFCCoefficients(field_correction_process_c, None, byref(ffc_coefficients_len_c), None)

            # Create buff to get coefficients data
            ffc_coefficients_c = (c_ubyte * ffc_coefficients_len_c.value)()
            status = dll.DxGetFFCCoefficients(field_correction_process_c, byref(ffc_coefficients_c),
                                              byref(ffc_coefficients_len_c), None)
        else:
            target_value_c = c_int()
            target_value_c.value = target_value

            # Get length of ffc coefficients
            dll.DxGetFFCCoefficients(field_correction_process_c, None, byref(ffc_coefficients_len_c),
                                     byref(target_value_c))

            # Create buff to get coefficients data
            ffc_coefficients_c = (c_ubyte * ffc_coefficients_len_c.value)()
            status = dll.DxGetFFCCoefficients(field_correction_process_c, byref(ffc_coefficients_c),
                                              byref(ffc_coefficients_len_c), byref(target_value_c))

        return status, ffc_coefficients_c, ffc_coefficients_len_c.value

if hasattr(dll, "DxRaw12PackedToRaw16"):
    def dx_raw12_packed_to_raw16(input_address, output_address, width, height):
        """
        :brief  Convert Raw12Packed to Raw16
        :param      input_address:          input buffer address, buff size = width * height
        :param      output_address:         output buffer address, buff size = width * height
        :param      width:                  image width
        :param      height:                 image height
        :return:    status:                 State return value, See detail in DxStatus
        """
        input_address_p = c_void_p()
        input_address_p.value = input_address

        output_address_p = c_void_p()
        output_address_p.value = output_address

        width_c = c_uint32()
        width_c.value = width

        height_c = c_uint32()
        height_c.value = height

        status = dll.DxRaw12PackedToRaw16(input_address_p, output_address_p, width_c, height_c)

        return status

if hasattr(dll, "DxRaw10PackedToRaw16"):
    def dx_raw10_packed_to_raw16(input_address, output_address, width, height):
        """
        :brief  Convert Raw10Packed to Raw16
        :param      input_address:          input buffer address, buff size = width * height
        :param      output_address:         output buffer address, buff size = width * height
        :param      width:                  image width
        :param      height:                 image height
        :return:    status:                 State return value, See detail in DxStatus
        """
        input_address_p = c_void_p()
        input_address_p.value = input_address

        output_address_p = c_void_p()
        output_address_p.value = output_address

        width_c = c_uint32()
        width_c.value = width

        height_c = c_uint32()
        height_c.value = height

        status = dll.DxRaw10PackedToRaw16(input_address_p, output_address_p, width_c, height_c)

        return status

if hasattr(dll, "DxRGB48toRGB24"):
    def dx_rgb48_to_rgb24(input_address, output_address, width, height, valid_bit):
        """
        :brief  Convert RGB48 to RGB24
        :param      input_address:          input buffer address, buff size = width * height
        :param      output_address:         output buffer address, buff size = width * height
        :param      width:                  image width
        :param      height:                 image height
        :param      valid_bit:             image valid bit
        :return:    status:                 State return value, See detail in DxStatus
        """
        input_address_p = c_void_p()
        input_address_p.value = input_address

        output_address_p = c_void_p()
        output_address_p.value = output_address

        width_c = c_uint32()
        width_c.value = width

        height_c = c_uint32()
        height_c.value = height

        valid_bit_c = c_uint()
        valid_bit_c.value = valid_bit

        status = dll.DxRGB48toRGB24(input_address_p, output_address_p, width_c, height_c, valid_bit_c)

        return status

if hasattr(dll, 'DxRaw16toRGB48'):
    def dx_raw16_to_rgb48(input_address, output_address, width, height, actual_bits, convert_type, bayer_type, flip):
        """
        :brief  Convert Raw16 to RGB48
        :param input_address:      The input raw image buff address, buff size = width * height
        :param output_address:     The output rgb image buff address, buff size = width * height * 3
        :param width:              Image width
        :param height:             Image height
        :param  actual_bits:       image actual bits
        :param convert_type:       Bayer convert type, See detail in DxBayerConvertType
        :param bayer_type:         pixel color filter, See detail in DxPixelColorFilter
        :param flip:               Output image flip flag
                                   True: turn the image upside down
                                   False: do not flip
        :return: status            State return value, See detail in DxStatus
                 data_array        Array of output images, buff size = width * height * 3
        """
        input_address_p = c_void_p()
        input_address_p.value = input_address

        output_address_p = c_void_p()
        output_address_p.value = output_address

        width_c = c_uint32()
        width_c.value = width

        height_c = c_uint32()
        height_c.value = height

        actual_bits_c = c_uint()
        actual_bits_c.value = actual_bits

        convert_type_c = c_uint()
        convert_type_c.value = convert_type

        bayer_type_c = c_uint()
        bayer_type_c.value = bayer_type

        flip_c = c_bool()
        flip_c.value = flip

        status = dll.DxRaw16toRGB48(input_address_p, output_address_p,
                                    width_c, height_c, actual_bits_c, convert_type_c, bayer_type_c, flip_c)
        return status

if hasattr(dll, 'DxRaw8toARGB32'):
    def dx_raw8_to_rgb32(input_address, output_address, width, height, stride, convert_type, bayer_type, flip, alpha):
        """
        :brief  Convert Raw8 to ARGB32
        :param input_address:      The input raw image buff address, buff size = width * height
        :param output_address:     The output rgb image buff address, buff size = width * height * 3
        :param width:              Image width
        :param height:             Image height
        :param  stride:            Android surface stride
        :param convert_type:       Bayer convert type, See detail in DxBayerConvertType
        :param bayer_type:         pixel color filter, See detail in DxPixelColorFilter
        :param flip:               Output image flip flag
                                   True: turn the image upside down
                                   False: do not flip
        :param  alpha:            value of channel Alpha
        :return: status            State return value, See detail in DxStatus
                 data_array        Array of output images, buff size = width * height * 3
        """
        input_address_p = c_void_p()
        input_address_p.value = input_address

        output_address_p = c_void_p()
        output_address_p.value = output_address

        width_c = c_uint32()
        width_c.value = width

        height_c = c_uint32()
        height_c.value = height

        stride_c = c_uint32()
        stride_c.value = stride

        convert_type_c = c_uint()
        convert_type_c.value = convert_type

        bayer_type_c = c_uint()
        bayer_type_c.value = bayer_type

        flip_c = c_bool()
        flip_c.value = flip

        alpha_c = c_uint32()
        alpha_c.value = alpha

        status = dll.DxRaw8toARGB32(input_address_p, output_address_p,
                                    width_c, height_c, stride_c, convert_type_c, bayer_type_c, flip_c, alpha_c)
        return status

if hasattr(dll, 'DxStaticDefectCorrection'):
    def dx_static_defect_correction(input_address, output_address, defect_correction, defect_pos_buffer_address,
                                    defect_pos_buffer_size):
        """
        :brief Image defect pixel correction
        :param input_address:                      The input raw image buff address, buff size = width * height
        :param output_address:                     The output rgb image buff address, buff size = width * height * 3
        :param defect_correction:                  Image parameter used to do defect correction
        :param defect_pos_buffer_address:          Defect Pixel position file buffer
        :param  defect_pos_buffer_size:            Defect Pixel position file buffer size

        :return: status                            State return value, See detail in DxStatus
                 data_array                        Array of output images, buff size = width * height * 3
        """
        input_address_p = c_void_p()
        input_address_p.value = input_address

        output_address_p = c_void_p()
        output_address_p.value = output_address

        defect_correction_c = defect_correction

        defect_pos_buffer_address_p = c_void_p()
        defect_pos_buffer_address_p.value = defect_pos_buffer_address

        defect_pos_buffer_size_c = c_uint32()
        defect_pos_buffer_size_c.value = defect_pos_buffer_size

        status = dll.DxStaticDefectCorrection(input_address_p, output_address_p,
                                              defect_correction_c, defect_pos_buffer_address_p,
                                              defect_pos_buffer_size_c)
        return status

if hasattr(dll, 'DxCalcCameraLutBuffer'):
    def dx_calc_camera_lut_buffer(contrast_param, gamma, light_ness, lut_address,
                                  lut_length_address):
        """
        :brief calculating lookup table of camera
        :param contrast_param:                      contrast param,range(-50~100)
        :param gamma:                               gamma param,range(0.1~10)
        :param light_ness:                          lightness param,range(-150~150)
        :param lut_address:                         lookup table
        :param  lut_length_address:                 lookup table length(unit:byte)

        Lookup table length should be obtained through the interface GXGetBufferLength.
        """
        contrast_param_c = c_int32()
        contrast_param_c.value = contrast_param

        gamma_c = c_double()
        gamma_c.value = gamma

        lightness_c = c_int32()
        lightness_c.value = light_ness

        lut_address_c = c_void_p()
        lut_address_c.value = lut_address

        status = dll.DxCalcCameraLutBuffer(contrast_param_c, gamma_c,
                                           lightness_c, lut_address_c,
                                           lut_length_address)
        return status

if hasattr(dll, 'DxReadLutFile'):
    def dx_read_lut_file(lut_file_path, lut_address, lut_length_address):
        """
        :brief read lut file
        :param lut_file_path:                        Lut file path. Lut file(xxx.lut) can be obtained from Lut
                                 Create Tool Plugin,which can be get by select Plugin->Lut
                                 Create Tool Plugin from the menu bar in GalaxyView.
        :param lut_address:                          Lookup table. Users need to apply for memory in advance.The
                                 memory size is also lookup table length(nLutLength),should be
                                 obtained through the interface GXGetBufferLength,
                                 e.g. GXGetBufferLength(m_hDevice, GX_BUFFER_LUT_VALUEALL,&nLutLength),
        :param lut_length_address:                   Lookup table length(unit:byte),which should be obtained through
                                 the interface GXGetBufferLength, e.g.
                                 GXGetBufferLength(m_hDevice, GX_BUFFER_LUT_VALUEALL,&nLutLength),
        :return: status                            State return value, See detail in DxStatus
                 data_array                        Array of output images, buff size = width * height * 3
        """

        lut_address_p = c_void_p()
        lut_address_p.value = lut_address

        status = dll.DxReadLutFile(lut_file_path, lut_address_p,
                                   lut_length_address)
        return status

if hasattr(dll, 'DxImageFormatConvertCreate'):
    def dx_image_format_convert_create():
        """
        :brief Create handle for Image Format Convert
        :param  handle          [in] Image Format convert handle
        """
        handle = c_void_p()
        status = dll.DxImageFormatConvertCreate(pointer(handle))
        return status, handle

if hasattr(dll, 'DxImageFormatConvertDestroy'):
    def dx_image_format_convert_destroy(handle):
        """
        :brief Destroy handle for Image Format Convert
        :param  handle          [in] Image Format convert handle
        """
        status = dll.DxImageFormatConvertDestroy(handle)
        return status

if hasattr(dll, 'DxImageFormatConvert'):
    def dx_image_format_convert(handle, input_address, input_length, output_address, output_length, fixel_format, width,
                                height, flip):
        """
        :brief Image Format Convert Process
        """
        input_address_p = c_void_p()
        input_address_p.value = input_address

        output_address_p = c_void_p()
        output_address_p.value = output_address

        width_c = c_uint32()
        width_c.value = width

        height_c = c_uint32()
        height_c.value = height


        fixel_format_c = c_uint()
        fixel_format_c.value = fixel_format

        flip_c = c_bool()
        flip_c.value = flip

        status = dll.DxImageFormatConvert(handle, input_address_p, input_length, output_address_p,
                                          output_length, fixel_format_c, width_c, height_c, flip_c)
        return status

if hasattr(dll, 'DxImageFormatConvertSetOutputPixelFormat'):
    def dx_image_format_convert_set_output_pixel_format(handle, pixel_format):
        """
        :brief Set Bayer Pixel Format Convert Type
        :param  handle          [in] Image Format convert handle
        :param  pixel_format   [in] Pixel Format
        """

        pixel_format_c = c_uint()
        pixel_format_c.value = pixel_format

        status = dll.DxImageFormatConvertSetOutputPixelFormat(handle, pixel_format_c)
        return status

if hasattr(dll, 'DxImageFormatConvertSetAlphaValue'):
    def dx_image_format_convert_set_alpha_value(handle, alpha_value):
        """
        :brief Set Bayer Pixel Format Convert Type
        :param  handle          [in] Image Format convert handle
        :param  alpha_value     [in] Alpha channel value(range of 0~255)
        """

        alpha_value_c = c_uint()
        alpha_value_c.value = alpha_value

        status = dll.DxImageFormatConvertSetAlphaValue(handle, alpha_value_c)
        return status

if hasattr(dll, 'DxImageFormatConvertSetInterpolationType'):
    def dx_image_format_convert_set_interpolation_type(handle, cvt_type):
        """
        :brief Set Bayer Pixel Format Convert Type
        :param  handle          [in] Image Format convert handle
        :param  cvt_type       [in] Bayer Pixel Format convert RGB type
        """

        status = dll.DxImageFormatConvertSetInterpolationType(handle, cvt_type)
        return status

if hasattr(dll, 'DxImageFormatConvertSetValidBits'):
    def dx_image_format_convert_set_valid_bits(handle, valid_bits):
        """
        :brief Set Valid Bits
        :param  handle          [in] Image Format convert handle
        :param  valid_bits     [in] Valid Bits value
        """

        status = dll.DxImageFormatConvertSetValidBits(handle, valid_bits)
        return status

if hasattr(dll, 'DxImageFormatConvertGetOutputPixelFormat'):
    def dx_image_format_convert_get_output_pixel_format(handle):
        """
        :brief Set Output Pixel type
        :param  handle          [in] Image Format convert handle
        :param  pixel_format   [out] Pixel Format
        """

        pixel_format_c = c_uint()

        status = dll.DxImageFormatConvertGetOutputPixelFormat(handle, byref(pixel_format_c))
        return status, pixel_format_c.value

if hasattr(dll, 'DxImageFormatConvertGetBufferSizeForConversion'):
    def dx_image_format_convert_get_buffer_size_for_conversion(handle, pixel_format, width, height):
        """
        :brief Set Output Pixel type
        :param  handle          [in] Image Format convert handle
        :param  pixel_format    [in]   Pixel Format
        :param  width           [in]   Image Width
        :param  height          [in]   Image Height
        :param  buffer_size_address     [out]  Image buffer size
        """
        pixel_format_c = c_uint()
        pixel_format_c.value = pixel_format

        width_c = c_uint()
        width_c.value = width

        height_c = c_uint()
        height_c.value = height

        buffer_size_c = c_int()

        status = dll.DxImageFormatConvertGetBufferSizeForConversion(handle, pixel_format_c, width_c,
                                                                    height_c, byref(buffer_size_c))
        return status, buffer_size_c.value

if hasattr(dll, "DxRotate90CW8B"):
    def dx_rotate_90_cw8b(input_address, output_address, width, height):
        """
        :brief  To rotate the 8-bit image clockwise by 90 degrees
        :param  pInputBuffer  	[in] input buffer
        :param  pOutputBuffer	[out]output buffer(new buffer)
        :param  nWidth        	[in] image width
        :param  nHeight       	[in] image height

        :return emStatus
        """
        input_address_p = c_void_p()
        input_address_p.value = input_address

        output_address_p = c_void_p()
        output_address_p.value = output_address

        width_c = c_uint32()
        width_c.value = width

        height_c = c_uint32()
        height_c.value = height

        status = dll.DxRotate90CW8B(input_address_p, output_address_p, width_c, height_c)

        return status

if hasattr(dll, "DxRotate90CCW8B"):
    def dx_rotate_90_ccw8b(input_address, output_address, width, height):
        """
        :brief  To rotate the 8-bit image counter by 90 degrees
        :param  pInputBuffer  	[in] input buffer
        :param  pOutputBuffer	[out]output buffer(new buffer)
        :param  nWidth        	[in] image width
        :param  nHeight       	[in] image height

        :return emStatus
        """
        input_address_p = c_void_p()
        input_address_p.value = input_address

        output_address_p = c_void_p()
        output_address_p.value = output_address

        width_c = c_uint32()
        width_c.value = width

        height_c = c_uint32()
        height_c.value = height

        status = dll.DxRotate90CCW8B(input_address_p, output_address_p, width_c, height_c)

        return status

if hasattr(dll, "DxRotate90CW16B"):
    def dx_rotate_90_cw16b(input_address, output_address, width, height):
        """
        :brief  To rotate the 16-bit image clockwise by 90 degrees
        :param  pInputBuffer  	[in] input buffer
        :param  pOutputBuffer	[out]output buffer(new buffer)
        :param  nWidth        	[in] image width
        :param  nHeight       	[in] image height

        :return emStatus
        """
        input_address_p = c_void_p()
        input_address_p.value = input_address

        output_address_p = c_void_p()
        output_address_p.value = output_address

        width_c = c_uint32()
        width_c.value = width

        height_c = c_uint32()
        height_c.value = height

        status = dll.DxRotate90CW16B(input_address_p, output_address_p, width_c, height_c)

        return status

if hasattr(dll, "DxRotate90CCW16B"):
    def dx_rotate_90_ccw16b(input_address, output_address, width, height):
        """
        :brief  To rotate the 16-bit image counter by 90 degrees
        :param  pInputBuffer  	[in] input buffer
        :param  pOutputBuffer	[out]output buffer(new buffer)
        :param  nWidth        	[in] image width
        :param  nHeight       	[in] image height

        :return emStatus
        """
        input_address_p = c_void_p()
        input_address_p.value = input_address

        output_address_p = c_void_p()
        output_address_p.value = output_address

        width_c = c_uint32()
        width_c.value = width

        height_c = c_uint32()
        height_c.value = height

        status = dll.DxRotate90CCW16B(input_address_p, output_address_p, width_c, height_c)

        return status

if hasattr(dll, "DxImageMirror16B"):
    def dx_image_mirror_16b(input_address, output_address, width, height, mirro_mode):
        """
        :brief  image mirror(Raw16 or 16bit image)
        :param  pInputBuff   	[in] input buffer
        :param  pOutputBuf      [out]output buffer
        :param  nWidth          [in] image width
        :param  nHeight         [in] image height
        :param  emMirrorMode    [in] mirror mode

        :return emStatus
        """
        input_address_p = c_void_p()
        input_address_p.value = input_address

        output_address_p = c_void_p()
        output_address_p.value = output_address

        width_c = c_uint32()
        width_c.value = width

        height_c = c_uint32()
        height_c.value = height

        status = dll.DxImageMirror16B(input_address_p, output_address_p, width_c, height_c, mirro_mode)

        return status

if hasattr(dll, 'DxFFCCreate'):
    def dx_ffc_create():
        """
        :brief Create handle for flat field correction
        :param  phandle          [out] flat field correction handle
        """
        handle = c_void_p()
        status = dll.DxFFCCreate(pointer(handle))
        return status, handle

if hasattr(dll, 'DxFFCDestroy'):
    def dx_ffc_destroy(handle):
        """
        :brief Destroy handle for flat field correction
        :param  handle          [in] flat field correction handle
        """
        status = dll.DxFFCDestroy(handle)
        return status

if hasattr(dll, "DxFFCSetFrameCount"):
    def dx_set_frame_count(handle, ffc_frame_count):
        """
        :brief  Set flat field correction frame count
        :param  handle                  [in] flat field correction handle
        :param  nFFCFrameCount          [in] flat field correction frame count
        :return emStatus
        """
        ffc_frame_count_c = c_uint16()
        ffc_frame_count_c.value = ffc_frame_count

        status = dll.DxFFCSetFrameCount(handle, ffc_frame_count_c)

        return status

if hasattr(dll, "DxFFCGetCoefficientsSize"):
    def dx_ffc_get_coefficients_size(handle, ffc_param):
        """
        :brief  Calculate flat field correction coefficients size
        :param  handle                       [in] flat field correction handle
        :param  ffc_param                  [in] flat field correction parameter
        :return status,CoefficientsSize
        """
        coefficients_size = c_int32()
        status = dll.DxFFCGetCoefficientsSize(handle, byref(ffc_param), byref(coefficients_size))
        return status, coefficients_size.value

if hasattr(dll, "DxFFCCalculate"):
    def dx_ffc_calculate(handle, ffc_param, coefficients_buffer, coefficients_buffer_size):
        """
        :brief  Calculate flat field correction coefficients size
        :param  handle                       [in] flat field correction handle
        :param  ffc_param                  [in] flat field correction parameter
        :param  coefficients_buffer        [out] flat field correction coefficients
        :param  coefficients_buffer_size    [in] flat field correction coefficients size
        """
        coefficients_size_c = c_int32()
        coefficients_size_c.value = coefficients_buffer_size

        output_address_p = c_void_p()
        output_address_p.value = coefficients_buffer

        status = dll.DxFFCCalculate(handle, byref(ffc_param), output_address_p, byref(coefficients_size_c))
        return status

if hasattr(dll, "DxFlatFieldCorrection"):
    def dx_flat_field_correction(input_address, output_address, actual_bits, width, height, coefficients_buffer, coefficients_buffer_size):
        """
        :brief  Flat Field Correction Process
        :param  input_address    	  [in]        Image in
        :param  output_address    	  [out]       Image out
        :param  actual_bits           [in]        Image actual cits
        :param  width             [in]        Image width
        :param  heidht            [in]        Image height
        :param  coefficients_buffer      [in]        Flat field correction coefficients
        :param  coefficients_buffer_size              [in]        Flat field correction coefficients(byte)
        """
        coefficients_size_c = c_int32()
        coefficients_size_c.value = coefficients_buffer_size

        input_address_p = c_void_p()
        input_address_p.value = input_address

        output_address_p = c_void_p()
        output_address_p.value = output_address

        coefficients_buffer_p = c_void_p()
        coefficients_buffer_p.value = coefficients_buffer

        width_c = c_uint32()
        width_c.value = width

        height_c = c_uint32()
        height_c.value = height

        actual_bits_c = c_uint()
        actual_bits_c.value = actual_bits

        status = dll.DxFlatFieldCorrection(input_address_p, output_address_p, actual_bits_c, width_c, height_c, coefficients_buffer_p,
                                         byref(coefficients_size_c))
        return status

    if hasattr(dll, 'DxDecompressionCreate'):
        def dx_decompression_create():
            """
            :brief create decompression handle

            :param  handle           [out]   decompression handle

            :return status
            """
            handle = c_void_p()
            status = dll.DxDecompressionCreate(pointer(handle))
            return status, handle

    if hasattr(dll, 'DxDecompressionDestroy'):
        def dx_decompression_destroy( handle):
            """
            :brief destroy decompression handle

            :param  handle           [in]   decompression handle

            :return status
            """
            status = dll.DxDecompressionDestroy(handle)
            return status

    if hasattr(dll, 'DxDecompression'):
        def dx_decompression( handle, compression_image_address, compression_image_size, decompression_image_address,
                              decompression_image_address_size, img_pixel_format, img_width, img_height, compression_method ):
            """
            :brief decompression image

            :brief  decompression image

            :param  handle                                    [in]            decompression handle
            :param  compression_image_address                 [in]            compression image address
            :param  compression_image_size                    [in]            compression image buffer size
            :param  decompression_image_address               [out]         decompression image address
            :param  decompression_image_address_size          [in|out]     decompression image buffer size
            :param  img_pixel_format                          [in]              Image pixel format
            :param  img_width                                 [in]              Image width
            :param  img_height                                [in]              Image height
            :param  compression_method                        [in]             compression method

            :return status
            """
            compression_image_p = c_void_p()
            compression_image_p.value = compression_image_address

            compression_image_buffer_size_c = c_int32()
            compression_image_buffer_size_c.value = compression_image_size

            width_c = c_uint32()
            width_c.value = img_width

            height_c = c_uint32()
            height_c.value = img_height

            pixel_format_c = c_uint()
            pixel_format_c.value = img_pixel_format

            compression_method_c = c_int32()
            compression_method_c.value = compression_method

            decompression_image_p = c_void_p()
            decompression_image_p.value = decompression_image_address

            decompression_image_address_size_c = c_int32()
            decompression_image_address_size_c.value = decompression_image_address_size

            status = dll.DxDecompression(handle, compression_image_p, compression_image_buffer_size_c, decompression_image_p,
                                         byref(decompression_image_address_size_c), pixel_format_c, width_c, height_c, compression_method_c)
            return status