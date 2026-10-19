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

class FlatFieldCorrection:
    def __init__(self):
        self.flat_field_correction_handle = None

    def __new__(cls, *args, **kw):
        return object.__new__(cls, *args)

    def __del__(self):
        if self.flat_field_correction_handle is not None:
            status = dx_ffc_destroy(self.flat_field_correction_handle)
            if status != DxStatus.OK:
                raise UnexpectedError(
                    "dx_ffc_destroy failure, Error code:%s" % hex(status).__str__())
            self.flat_field_correction_handle = None

    def set_frame_count(self, frame_count):
        """
        :brief  Set flat field correction frame count
        :param  handle                  [in] flat field correction handle
        :param  nFFCFrameCount          [in] flat field correction frame count
        """
        if not (isinstance(frame_count, INT_TYPE)):
            raise ParameterTypeError("frame_count must to be INT_TYPE element.")

        self.__check_handle()
        status = dx_set_frame_count(self.flat_field_correction_handle, frame_count)
        if status != DxStatus.OK:
            raise UnexpectedError("dx_set_frame_count failure, Error code:%s" % hex(status).__str__())

    def get_coefficients_size(self, ffc_param):
        """
        :brief  Calculate flat field correction coefficients size
        :param  handle                       [in] flat field correction handle
        :param  ffc_param                  [in] flat field correction parameter
        :return status,CoefficientsSize
        """
        if not (isinstance(ffc_param, FlatFieldCorrectionParameter)):
            raise ParameterTypeError("ffc_param must to be FlatFieldCorrectionParameter element.")

        self.__check_handle()
        status, coefficients_size = dx_ffc_get_coefficients_size(self.flat_field_correction_handle, ffc_param)
        if status != DxStatus.OK:
            raise UnexpectedError("dx_ffc_get_coefficients_size failure, Error code:%s" % hex(status).__str__())
        return coefficients_size

    def calculate(self, ffc_param, coefficients_buffer, coefficients_buffer_size):
        """
        :brief  Calculate flat field correction coefficients size
        :param  handle                       [in] flat field correction handle
        :param  ffc_param                  [in] flat field correction parameter
        :param  coefficients_buffer        [out] flat field correction coefficients
        :param  coefficients_buffer_size    [in] flat field correction coefficients size
        """
        if not (isinstance(ffc_param, FlatFieldCorrectionParameter)):
            raise ParameterTypeError("ffc_param must to be FlatFieldCorrectionParameter element.")

        if coefficients_buffer is None:
            raise ParameterTypeError("coefficients_buffer is NULL pointer.")

        if not (isinstance(coefficients_buffer_size, INT_TYPE)):
            raise ParameterTypeError("coefficients_buffer_size must to be INT_TYPE element.")

        self.__check_handle()
        status = dx_ffc_calculate(self.flat_field_correction_handle, ffc_param, coefficients_buffer, coefficients_buffer_size)
        if status != DxStatus.OK:
            raise UnexpectedError("dx_ffc_calculate failure, Error code:%s" % hex(status).__str__())

    def flat_field_correction(self, input_address, output_address, actual_bits, width, height, coefficients_buffer, coefficients_buffer_size):
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
        if input_address is None:
            raise ParameterTypeError("input_address is NULL pointer.")

        if output_address is None:
            raise ParameterTypeError("output_address is NULL pointer.")

        if coefficients_buffer is None:
            raise ParameterTypeError("coefficients_buffer is NULL pointer.")

        if not (isinstance(actual_bits, INT_TYPE)):
            raise ParameterTypeError("actual_bits must to be DxActualBits element.")

        if not (isinstance(width, INT_TYPE)):
            raise ParameterTypeError("width must to be INT_TYPE element.")

        if not (isinstance(height, INT_TYPE)):
            raise ParameterTypeError("height must to be INT_TYPE element.")

        if not (isinstance(coefficients_buffer_size, INT_TYPE)):
            raise ParameterTypeError("coefficients_buffer_size must to be INT_TYPE element.")

        self.__check_handle()
        status = dx_flat_field_correction(input_address, output_address, actual_bits, width, height, coefficients_buffer, coefficients_buffer_size)
        if status != DxStatus.OK:
            raise UnexpectedError("dx_flat_field_correction failure, Error code:%s" % hex(status).__str__())

    def __check_handle(self):
        """
        :brief  The transformation handle is initialized the first time it is called
        :return NONE
        """
        if self.flat_field_correction_handle is None:
            status, handle = dx_ffc_create()
            if status != DxStatus.OK:
                raise UnexpectedError("dx_ffc_create failure, Error code:%s" % hex(status).__str__())
            self.flat_field_correction_handle = handle




