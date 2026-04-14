#!/usr/bin/python
# -*- coding:utf-8 -*-
# -*-mode:python ; tab-width:4 -*- ex:set tabstop=4 shiftwidth=4 expandtab: -*-

import numpy
from gxipy.gxwrapper import *
from gxipy.dxwrapper import *
from gxipy.ImageProc import *
from gxipy.gxiapi import *
from gxipy.StatusProcessor import *
import types

if sys.version_info.major > 2:
    INT_TYPE = int
else:
    INT_TYPE = (int, long)

class Feature_s:
    def __init__(self, handle, feature_name):
        """
        :brief  Constructor for instance initialization
        :param handle:          Interface featrue control handle/Device local layer feature control/Device remote layer featrure control/Device stream layer feature control
        :param feature_name:    Feature node name
        """
        self.__handle = handle
        self.__feature_name = feature_name

class IntFeature_s(Feature_s):
    def __init__(self, handle, feature_name):
        """
        :brief  Constructor for instance initialization
        :param handle:          Interface featrue control handle/Device local layer feature control/Device remote layer featrure control/Device stream layer feature control
        :param feature_name:    Feature node name
        """
        Feature_s.__init__( self, handle, feature_name)
        self.__handle = handle
        self.__feature_name = feature_name

    def __range_dicts(self, feature_value):
        """
        :brief      Convert feature info to list
        :param feature_value:   Int type feature info
        :return:    Feature info list
        """
        range_dicts = {
            "value"     : feature_value.value,
            "min"       : feature_value.min,
            "max"       : feature_value.max,
            "inc"       : feature_value.inc,
            "reserved"  : array_decoding( feature_value.reserved),
        }
        return  range_dicts

    def get_range(self):
        """
        :brief      Getting integer range
        :return:    integer range dictionary
        """
        status, int_feature_info = gx_get_int_feature(self.__handle, self.__feature_name)
        StatusProcessor.process(status, 'IntFeature_s', 'get_range')

        return self.__range_dicts( int_feature_info)

    def get(self):
        """
        :brief      Getting value of Enum feature
        :return:    enum_value:     enum value
                    enum_str:       string for enum description
        """
        status, int_feature_info = gx_get_int_feature(self.__handle, self.__feature_name)
        StatusProcessor.process(status, 'IntFeature_s', 'get')

        return int_feature_info.value

    def set(self, int_value):
        """
        :brief      Setting integer value
        :param      int_value:  Set value
        :return:    None
        """
        if not isinstance(int_value, INT_TYPE):
            raise ParameterTypeError("IntFeature_s.set: "
                                     "Expected int_value type is int, not %s" % type(int_value))

        status = gx_set_int_feature_value(self.__handle, self.__feature_name, int_value)
        StatusProcessor.process(status, 'IntFeature_s', 'set')

class EnumFeature_s(Feature_s):
    def __init__(self, handle, feature_name):
        """
        :brief  Constructor for instance initialization
        :param handle:          Interface featrue control handle/Device local layer feature control/Device remote layer featrure control/Device stream layer feature control
        :param feature_name:    Feature node name
        """
        Feature_s.__init__( self, handle, feature_name)
        self.__handle = handle
        self.__feature_name = feature_name

    def __range_dicts(self, feature_value):
        enum_dict = []
        for index in range(feature_value.supported_number):
            enum_dict.append({
                "value"     : feature_value.supported_value[index].cur_value,
                "symbolic"  : string_decoding( feature_value.supported_value[index].cur_symbolic),
            })
        return  enum_dict

    def get_range(self):
        """
        :brief      Getting range of Enum feature
        :return:    enum_dict:    enum range dictionary
        """
        status, enum_feature_info = gx_get_enum_feature( self.__handle, self.__feature_name)
        StatusProcessor.process(status, 'FeatureControl', 'gx_get_enum_feature')

        return self.__range_dicts( enum_feature_info)

    def get(self):
        """
        :brief      Getting value of Enum feature
        :return:    enum_value:     enum value
                    enum_str:       string for enum description
        """
        status, enum_feature_info = gx_get_enum_feature(self.__handle, self.__feature_name)
        StatusProcessor.process(status, 'FeatureControl', 'gx_get_enum_feature')

        return enum_feature_info.cur_value.cur_value, string_decoding( enum_feature_info.cur_value.cur_symbolic)

    def set(self, enum_value):
        """
        :brief      Setting enum value
        :param      enum_value
        :return:    None
        """
        if isinstance(enum_value, int):
            status = gx_set_enum_feature_value(self.__handle, self.__feature_name, enum_value)
            StatusProcessor.process(status, 'EnumFeature_s', 'set')
        elif isinstance(enum_value, str):
            status = gx_set_enum_feature_value_string( self.__handle, self.__feature_name, enum_value)
            StatusProcessor.process(status, 'EnumFeature_s', 'set')
        else:
            raise ParameterTypeError("EnumFeature_s.set: "
                                     "Expected enum_value type is int or string, not %s" % type(enum_value))

class FloatFeature_s(Feature_s):
    def __init__(self, handle, feature_name):
        """
        :brief  Constructor for instance initialization
        :param handle:          Interface featrue control handle/Device local layer feature control/Device remote layer featrure control/Device stream layer feature control
        :param feature_name:    Feature node name
        """
        Feature_s.__init__( self, handle, feature_name)
        self.__handle = handle
        self.__feature_name = feature_name

    def __range_dict(self, feature_value):
        """
        :brief      Convert GxFloatRange to dictionary
        :param      float_range:  GxFloatRange
        :return:    range_dicts
        """
        range_dicts = {
            "cur_value"     : feature_value.cur_value,
            "min"           : feature_value.min,
            "max"           : feature_value.max,
            "inc"           : feature_value.inc,
            "inc_is_valid"  : feature_value.inc_is_valid,
            "unit"          : string_decoding( feature_value.unit),
            "reserved"      : array_decoding( feature_value.reserved),
        }
        return range_dicts

    def get_range(self):
        """
        :brief      Getting float range
        :return:    float range dictionary
        """
        status, float_feature_info = gx_get_float_feature(self.__handle, self.__feature_name)
        StatusProcessor.process(status, 'FloatFeature_s', 'get_range')
        return self.__range_dict( float_feature_info)

    def get(self):
        """
        :brief      Getting float value
        :return:    float value
        """
        status, float_feature_info = gx_get_float_feature(self.__handle, self.__feature_name)
        StatusProcessor.process(status, 'FloatFeature_s', 'get_range')
        return float_feature_info.cur_value

    def set(self, float_value):
        """
        :brief      Setting float value
        :param      float_value
        :return:    None
        """
        if not isinstance(float_value, float):
            raise ParameterTypeError("FloatFeature_s.set: "
                                     "Expected float_value type is float, not %s" % type(float_value))

        status = gx_set_float_feature_value(self.__handle, self.__feature_name, float_value)
        StatusProcessor.process(status, 'FloatFeature_s', 'set')

class BoolFeature_s(Feature_s):
    def __init__(self, handle, feature_name):
        """
        :brief  Constructor for instance initialization
        :param handle:          Interface featrue control handle/Device local layer feature control/Device remote layer featrure control/Device stream layer feature control
        :param feature_name:    Feature node name
        """
        Feature_s.__init__( self, handle, feature_name)
        self.__handle = handle
        self.__feature_name = feature_name

    def get(self):
        """
        :brief      Getting bool value
        :return:    bool value[bool]
        """
        status, bool_feature_value = gx_get_bool_feature( self.__handle, self.__feature_name)
        StatusProcessor.process(status, 'BoolFeature_s', 'get')
        return  bool_feature_value

    def set(self, bool_value):
        """
        :brief      Setting bool value
        :param      bool_value[bool]
        :return:    None
        """
        if not isinstance(bool_value, bool):
            raise ParameterTypeError("BoolFeature_s.set: "
                                     "Expected bool_value type is bool, not %s" % type(bool_value))

        status = gx_set_bool_feature_value( self.__handle, self.__feature_name, bool_value)
        StatusProcessor.process(status, 'BoolFeature_s', 'set')

class StringFeature_s(Feature_s):
    def __init__(self, handle, feature_name):
        """
        :brief  Constructor for instance initialization
        :param handle:          Interface featrue control handle/Device local layer feature control/Device remote layer featrure control/Device stream layer feature control
        :param feature_name:    Feature node name
        """
        Feature_s.__init__( self, handle, feature_name)
        self.__handle = handle
        self.__feature_name = feature_name

    def get_string_max_length(self):
        """
        :brief      String max length
        :return:    Max length
        """
        status, string_value = gx_get_string_feature( self.__handle, self.__feature_name)
        StatusProcessor.process(status, 'StringFeature_s', 'get_string_max_length')
        return  string_value.max_length

    def get(self):
        """
        :brief      Getting string value
        :return:    strings
        """
        status, string_value = gx_get_string_feature(self.__handle, self.__feature_name)
        StatusProcessor.process(status, 'StringFeature_s', 'get')
        return string_decoding( string_value.cur_value)

    def set(self, input_string):
        """
        :brief      Setting string value
        :param      input_string[string]
        :return:    None
        """
        if not isinstance(input_string, str):
            raise ParameterTypeError("StringFeature_s.set: "
                                     "Expected input_string type is string, not %s" % type(input_string))

        status = gx_set_string_feature_value( self.__handle, self.__feature_name, input_string)
        StatusProcessor.process(status, 'StringFeature_s', 'set')

class CommandFeature_s(Feature_s):
    def __init__(self, handle, feature_name):
        """
        :brief  Constructor for instance initialization
        :param handle:          Interface featrue control handle/Device local layer feature control/Device remote layer featrure control/Device stream layer feature control
        :param feature_name:    Feature node name
        """
        Feature_s.__init__( self, handle, feature_name)
        self.__handle = handle
        self.__feature_name = feature_name

    def send_command(self):
        """
        :brief      Sending command
        :return:    None
        """
        status = gx_feature_send_command(self.__handle, self.__feature_name)
        StatusProcessor.process(status, 'CommandFeature_s', 'send_command')


class RegisterFeature_s(Feature_s):
    def __init__(self, handle, feature_name):
        """
        :brief  Constructor for instance initialization
        :param handle:          Interface featrue control handle/Device local layer feature control/Device remote layer featrure control/Device stream layer feature control
        :param feature_name:    Feature node name
        """
        Feature_s.__init__( self, handle, feature_name)
        self.__handle = handle
        self.__feature_name = feature_name

    def get_register_length(self):
        """
        :brief      Getting buffer length
        :return:    length:     buffer length
        """
        status, register_feature_length = gx_get_register_feature_length(self.__handle, self.__feature_name)
        StatusProcessor.process(status, 'RegisterFeature_s', 'get_register_length')
        return register_feature_length

    def get_buffer(self):
        """
        :brief      Getting buffer data
        :return:    Buffer object
        """
        status, register_feature_value = gx_get_register_feature_value(self.__handle, self.__feature_name)
        StatusProcessor.process(status, 'RegisterFeature_s', 'get_buffer')
        return Buffer(register_feature_value)

    def set_buffer(self, buf):
        """
        :brief      Setting buffer data
        :param      buf:    Buffer object
        :return:    None
        """
        if not isinstance(buf, Buffer):
            raise ParameterTypeError("RegisterFeature_s.set_buffer: "
                                     "Expected buff type is Buffer, not %s" % type(buf))

        max_length = self.get_register_length()
        if buf.get_length() > max_length:
            print("RegisterFeature_s.set_buffer: "
                  "buff length out of bounds, %s.length_max:%s" % (self.__feature_name, max_length))

            raise UnexpectedError("buff length out of bounds, %s.length_max:%d" % (self.__feature_name, max_length))

        status = gx_set_register_feature_value(self.__handle, self.__feature_name,buf.get_ctype_array(), buf.get_length())
        StatusProcessor.process(status, 'RegisterFeature_s', 'set_buffer')

