#!/usr/bin/python
# -*- coding:utf-8 -*-
# -*-mode:python ; tab-width:4 -*- ex:set tabstop=4 shiftwidth=4 expandtab: -*-


import numpy
from gxipy.gxwrapper import *
from gxipy.dxwrapper import *
from gxipy.gxiapi import *
from gxipy.gxidef import *
from gxipy.ImageProc import *
import types

if sys.version_info.major > 2:
    INT_TYPE = int
else:
    INT_TYPE = (int, long)

class Decompressor:
    def __init__(self):
        self.decompressor_handle = None

    def __new__(cls, *args, **kw):
        return object.__new__(cls, *args)

    def __del__(self):
        if self.decompressor_handle is not None:
            status = dx_decompression_destroy(self.decompressor_handle)
            if status != DxStatus.OK:
                raise UnexpectedError(
                    "dx_decompression_destroy failure, Error code:%s" % hex(status).__str__())
            self.decompressor_handle = None

    def decompression(self, compression_address, compression_address_size, decompression_address,
                      decompression_address_size, img_pixel_format, img_width, img_height, compression_method):
        """
        :brief  decompression image

        :param  compression_address                 [in]            compression image address
        :param  compression_address_size        	[in]            compression image buffer size
        :param  decompression_address               [out]         decompression image address
        :param  decompression_address_size          [in|out]     decompression image buffer size
        :param  img_pixel_format                    [in]              Image pixel format
        :param  img_width                           [in]              Image width
        :param  img_height                          [in]              Image height
        :param  compression_method                  [in]             compression method

        :return void
        """

        if compression_address is None:
            raise ParameterTypeError("compression_address is NULL pointer.")

        if decompression_address is None:
            raise ParameterTypeError("decompression_address is NULL pointer.")

        if not isinstance(img_width, INT_TYPE):
            raise ParameterTypeError("img_width param must be int type.")

        if not isinstance(img_height, INT_TYPE):
            raise ParameterTypeError("img_height param must be int type.")

        if not (isinstance(img_pixel_format, INT_TYPE)):
            raise ParameterTypeError("img_fixel_format must to be GxPixelFormatEntry's element.")

        if not (isinstance(decompression_address_size, INT_TYPE)):
            raise ParameterTypeError("decompression_address_length must to be int type.")

        if not (isinstance(compression_method, INT_TYPE)):
            raise ParameterTypeError("compression_method must to be int type.")

        self.__check_handle()

        status = dx_decompression(self.decompressor_handle, compression_address, compression_address_size,
                                  decompression_address, decompression_address_size, img_pixel_format, img_width,
                                img_height, compression_method)
        if status != DxStatus.OK:
            raise UnexpectedError("dx_decompression failure, Error code:%s" % hex(status).__str__())

    def __check_handle(self):
        """
        :brief  The transformation handle is initialized the first time it is called
        :return NONE
        """
        if self.decompressor_handle is None:
            status, handle = dx_decompression_create()
            if status != DxStatus.OK:
                raise UnexpectedError("dx_decompression_create failure, Error code:%s" % hex(status).__str__())
            self.decompressor_handle = handle




