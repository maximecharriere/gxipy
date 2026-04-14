#!/usr/bin/python
# -*- coding:utf-8 -*-
# -*-mode:python ; tab-width:4 -*- ex:set tabstop=4 shiftwidth=4 expandtab: -*-


import numpy
from numpy.compat import long

from gxipy.Device import Device
from gxipy.gxwrapper import *
from gxipy.dxwrapper import *
from gxipy.gxidef import *
from gxipy.gxiapi import *
from gxipy.StatusProcessor import *
from gxipy.Interface import *
from gxipy.Device import *
from gxipy.ImageFormatConvert import *
from gxipy.ImageProcess import *
from gxipy.Exception import *
import types

if sys.version_info.major > 2:
    INT_TYPE = int
else:
    INT_TYPE = (int, long)


class DeviceManager(object):
    __instance_num = 0

    def set_log_type(self, log_type):
        """
        :brief      Set whether logs of the specified type can be sent
        :param      log_type:   log type,See detail in GxLogTypeList
        :return:    status:     State return value, See detail in GxStatusList
        """
        if not isinstance(log_type, INT_TYPE):
            raise ParameterTypeError("DeviceManager.set_log_type: "
                                     "Expected log type is int, not %s" % type(log_type))

        status = gx_set_log_type(log_type)
        StatusProcessor.process(status, 'DeviceManager', 'set_log_type')

    def get_log_type(self):
        """
        :brief      Gets whether logs of the specified type can be sent
        :return:    status:      State return value, See detail in GxStatusList
                    log_type:    log type,See detail in GxLogTypeList
        """
        status, log_type = gx_get_log_type()
        StatusProcessor.process(status, 'DeviceManager', 'get_log_type')
        self.__log_type = log_type

        return self.__log_type

    def __new__(cls, *args, **kw):
        cls.__instance_num += 1
        status = gx_init_lib()
        StatusProcessor.process(status, 'DeviceManager', 'init_lib')
        return object.__new__(cls, *args)

    def __init__(self):
        self.__device_num = 0
        self.__device_info_list = []
        self.__interface_info_list = []
        self.__interface_num = 0

    def __del__(self):
        self.__class__.__instance_num -= 1
        if self.__class__.__instance_num <= 0:
            status = gx_close_lib()
            StatusProcessor.process(status, 'DeviceManager', 'close_lib')

    def __create_device(self, device_class, device_handle):
        status, interface_handle = gx_get_parent_interface_from_device(device_handle)
        StatusProcessor.process(status, 'DeviceManager', '__create_device')

        index = 0
        for interface_item in self.__interface_info_list:
            if interface_item['handle'] == interface_handle:
                break
            ++index

        if device_class == GxDeviceClassList.U3V:
            return U3VDevice(device_handle, Interface(interface_handle, self.__interface_info_list[index]))
        elif device_class == GxDeviceClassList.USB2:
            return U2Device(device_handle, Interface(interface_handle, self.__interface_info_list[index]))
        elif device_class == GxDeviceClassList.GEV:
            return GEVDevice(device_handle, Interface(interface_handle, self.__interface_info_list[index]))
        elif device_class == GxDeviceClassList.CXP:
            return Device(device_handle, Interface(interface_handle, self.__interface_info_list[index]))
        else:
            raise NotFoundDevice("DeviceManager.__create_device: Does not support this device type.")

    def __get_device_info_list(self, base_info, ip_info, num):
        """
        :brief      Convert GxDeviceBaseInfo and GxDeviceIPInfo to device info list
        :param      base_info:  device base info list[GxDeviceBaseInfo]
        :param      ip_info:    device ip info list[GxDeviceIPInfo]
        :param      num:        device number
        :return:    device info list
        """
        device_info_list = []
        for i in range(num):
            device_info_list.append({
                'index': i + 1,
                'vendor_name': string_decoding(base_info[i].vendor_name),
                'model_name': string_decoding(base_info[i].model_name),
                'sn': string_decoding(base_info[i].serial_number),
                'display_name': string_decoding(base_info[i].display_name),
                'device_id': string_decoding(base_info[i].device_id),
                'user_id': string_decoding(base_info[i].user_id),
                'access_status': base_info[i].access_status,
                'device_class': base_info[i].device_class,
                'mac': string_decoding(ip_info[i].mac),
                'ip': string_decoding(ip_info[i].ip),
                'subnet_mask': string_decoding(ip_info[i].subnet_mask),
                'gateway': string_decoding(ip_info[i].gateway),
                'nic_mac': string_decoding(ip_info[i].nic_mac),
                'nic_ip': string_decoding(ip_info[i].nic_ip),
                'nic_subnet_mask': string_decoding(ip_info[i].nic_subnet_mask),
                'nic_gateWay': string_decoding(ip_info[i].nic_gateWay),
                'nic_description': string_decoding(ip_info[i].nic_description)
            })

        return device_info_list

    def __get_interface_info_list(self):
        """
        :brief      Get GXInterfaceInfo and Convert GXInterfaceInfo to interface info list
        :return:    interface info list
        """
        status,interface_number = gx_get_interface_number()
        StatusProcessor.process(status, 'DeviceManager', '__get_interface_info_list')

        interface_info_list = []
        for nindex in range(interface_number):
            status, interface_info = gx_get_interface_info(nindex+1)
            StatusProcessor.process(status, 'DeviceManager', '__get_interface_info_list')

            status, interface_handle = gx_get_interface_handle(nindex+1)
            StatusProcessor.process(status, 'DeviceManager', '__get_interface_info_list')

            if GxTLClassList.TL_TYPE_CXP == interface_info.TLayer_type:
                interface_info_list.append({
                    'handle'       : interface_handle,
                    'type'         : GxTLClassList.TL_TYPE_CXP,
                    'display_name' : string_decoding( interface_info.IF_info.CXP_interface_info.display_name),
                    'interface_id' : string_decoding( interface_info.IF_info.CXP_interface_info.interface_id),
                    'serial_number': string_decoding( interface_info.IF_info.CXP_interface_info.serial_number),
                    'description'  : '',
                    'init_flag'    : interface_info.IF_info.CXP_interface_info.init_flag,
                    'reserved'     : array_decoding(interface_info.IF_info.CXP_interface_info.reserved),
                })
            elif GxTLClassList.TL_TYPE_GEV == interface_info.TLayer_type:
                interface_info_list.append({
                    'handle'        : interface_handle,
                    'type'          : GxTLClassList.TL_TYPE_GEV,
                    'display_name'  : string_decoding( interface_info.IF_info.GEV_interface_info.display_name),
                    'interface_id'  : string_decoding(interface_info.IF_info.GEV_interface_info.interface_id),
                    'serial_number' : string_decoding(interface_info.IF_info.GEV_interface_info.serial_number),
                    'description'   : string_decoding(interface_info.IF_info.GEV_interface_info.description),
                    'init_flag'     : interface_info.IF_info.GEV_interface_info.init_flag,
                    'reserved'      : array_decoding(interface_info.IF_info.GEV_interface_info.reserved),
                })
            elif GxTLClassList.TL_TYPE_U3V == interface_info.TLayer_type:
                interface_info_list.append({
                    'handle'        : interface_handle,
                    'type'          : GxTLClassList.TL_TYPE_U3V,
                    'display_name'  : string_decoding( interface_info.IF_info.U3V_interface_info.display_name),
                    'interface_id'  : string_decoding(interface_info.IF_info.U3V_interface_info.interface_id),
                    'serial_number' : string_decoding(interface_info.IF_info.U3V_interface_info.serial_number),
                    'description'   : string_decoding(interface_info.IF_info.U3V_interface_info.description),
                    'init_flag'     : 0,
                    'reserved'      : array_decoding(interface_info.IF_info.U3V_interface_info.reserved),
                })
            elif GxTLClassList.TL_TYPE_USB == interface_info.TLayer_type:
                interface_info_list.append({
                    'handle'        : interface_handle,
                    'type'          : GxTLClassList.TL_TYPE_USB,
                    'display_name'  : string_decoding( interface_info.IF_info.USB_interface_info.display_name),
                    'interface_id'  : string_decoding(interface_info.IF_info.USB_interface_info.interface_id),
                    'serial_number' : string_decoding(interface_info.IF_info.USB_interface_info.serial_number),
                    'description'   : string_decoding(interface_info.IF_info.USB_interface_info.description),
                    'init_flag'     : 0,
                    'reserved'      : array_decoding(interface_info.IF_info.USB_interface_info.reserved),
                })
            else:
                interface_info_list.append({
                    'handle'        : 0,
                    'type'          : GxTLClassList.TL_TYPE_UNKNOWN,
                    'display_name'  : string_decoding(''),
                    'interface_id'  : '',
                    'serial_number' : '',
                    'description'   : '',
                    'init_flag'     : 0,
                    'reserved'      : [],
                })
        return interface_number,interface_info_list


    def __get_ip_info(self, base_info_list, dev_mum):
        """
        :brief      Get the network information
        """

        ip_info_list = []
        for i in range(dev_mum):
            if base_info_list[i].device_class == GxDeviceClassList.GEV:
                status, ip_info = gx_get_device_ip_info(i + 1)
                StatusProcessor.process(status, 'DeviceManager', '__get_ip_info')
                ip_info_list.append(ip_info)
            else:
                ip_info_list.append(GxDeviceIPInfo())

        return ip_info_list

    def update_device_list(self, timeout=200):
        """
        :brief      enumerate the same network segment devices
        :param      timeout:    Enumeration timeout, range:[0, 0xFFFFFFFF]
        :return:    dev_num:    device number
                    device_info_list: all device info list
        """
        if not isinstance(timeout, INT_TYPE):
            raise ParameterTypeError("DeviceManager.update_device_list: "
                                     "Expected timeout type is int, not %s" % type(timeout))

        if (timeout < 0) or (timeout > UNSIGNED_INT_MAX):
            print("DeviceManager.update_device_list: "
                  "timeout out of bounds, timeout: minimum=0, maximum=%s" % hex(UNSIGNED_INT_MAX).__str__())
            return 0, None

        status, dev_num = gx_update_device_list(timeout)
        StatusProcessor.process(status, 'DeviceManager', 'update_device_list')

        self.__interface_num, self.__interface_info_list = self.__get_interface_info_list()

        status, base_info_list = gx_get_all_device_base_info(dev_num)
        StatusProcessor.process(status, 'DeviceManager', 'update_device_list')

        ip_info_list = self.__get_ip_info(base_info_list, dev_num)
        self.__device_num = dev_num
        self.__device_info_list = self.__get_device_info_list(base_info_list, ip_info_list, dev_num)

        return self.__device_num, self.__device_info_list

    def update_device_list_ex(self, tl_type, timeout=2000):
        """
        :brief      Enumerate the device_type type devices
        :param      tl_type:device type
        :param      timeout:    Enumeration timeout, range:[0, 0xFFFFFFFF]
        :return:    dev_num:    device number
                    device_info_list: all device info list
        """
        if not isinstance(timeout, INT_TYPE):
            raise ParameterTypeError("DeviceManager.update_device_list: "
                                     "Expected timeout type is int, not %s" % type(timeout))

        if (timeout < 0) or (timeout > UNSIGNED_INT_MAX):
            print("DeviceManager.update_device_list: "
                  "timeout out of bounds, timeout: minimum=0, maximum=%s" % hex(UNSIGNED_INT_MAX).__str__())
            return 0, None

        status, dev_num = gx_update_device_list_ex(tl_type, timeout)
        StatusProcessor.process(status, 'DeviceManager', 'update_device_list_ex')

        self.__interface_num, self.__interface_info_list = self.__get_interface_info_list()

        status, base_info_list = gx_get_all_device_base_info(dev_num)
        StatusProcessor.process(status, 'DeviceManager', 'update_device_list_ex')

        ip_info_list = self.__get_ip_info(base_info_list, dev_num)
        self.__device_num = dev_num
        self.__device_info_list = self.__get_device_info_list(base_info_list, ip_info_list, dev_num)

        return self.__device_num, self.__device_info_list

    def update_all_device_list(self, timeout=200):
        """
        :brief      Enumerate devices on different network segments
        :param      timeout:    Enumeration timeout, range:[0, 0xFFFFFFFF]
        :return:    dev_num:    device number
                    device_info_list:   all device info list
        """
        if not isinstance(timeout, INT_TYPE):
            raise ParameterTypeError("DeviceManager.update_all_device_list: "
                                     "Expected timeout type is int, not %s" % type(timeout))

        if (timeout < 0) or (timeout > UNSIGNED_INT_MAX):
            print("DeviceManager.update_all_device_list: "
                  "timeout out of bounds, timeout: minimum=0, maximum=%s" % hex(UNSIGNED_INT_MAX).__str__())
            return 0, None

        status, dev_num = gx_update_all_device_list(timeout)
        StatusProcessor.process(status, 'DeviceManager', 'update_all_device_list')

        self.__interface_num, self.__interface_info_list = self.__get_interface_info_list()

        status, base_info_list = gx_get_all_device_base_info(dev_num)
        StatusProcessor.process(status, 'DeviceManager', 'update_all_device_list')

        ip_info_list = self.__get_ip_info(base_info_list, dev_num)
        self.__device_num = dev_num
        self.__device_info_list = self.__get_device_info_list(base_info_list, ip_info_list, dev_num)

        return self.__device_num, self.__device_info_list

    def get_interface_number(self):
        """
        :brief      Get device number
        :return:    device number
        """
        return self.__interface_num

    def get_interface_info(self):
        """
        :brief      Get device number
        :return:    device number
        """
        return self.__interface_info_list

    def get_interface(self, index):
        """
        :brief      Get device number
        :return:    device number
        """
        if not isinstance(index, INT_TYPE):
            raise ParameterTypeError("DeviceManager.get_interface: "
                                     "Expected index type is int, not %s" % type(index))

        if index < 1:
            print("DeviceManager.get_interface: index must start from 1")
            return None
        elif index > UNSIGNED_INT_MAX:
            print("DeviceManager.get_interface: index maximum: %s" % hex(UNSIGNED_INT_MAX).__str__())
            return None

        if self.__interface_num < index:
            # Re-update the device
            self.update_device_list()
            if self.__interface_num < index:
                raise NotFoundDevice("DeviceManager.get_interface: invalid index")

        status, interface_handle = gx_get_interface_handle(index)
        StatusProcessor.process(status, 'DeviceManager', 'get_interface')

        return Interface(interface_handle, self.__interface_info_list[index - 1])

    def get_device_number(self):
        """
        :brief      Get device number
        :return:    device number
        """
        return self.__device_num

    def get_device_info(self):
        """
        :brief      Get all device info
        :return:    info_dict:      device info list
        """
        return self.__device_info_list

    def open_device_by_index(self, index, access_mode=GxAccessMode.CONTROL):
        """
        :brief      open device by index
                    USB3 device return U3VDevice object
                    USB2 device return U2Device object
                    GEV  device return GEVDevice object
        :param      index:          device index must start from 1
        :param      access_mode:    the access of open device
        :return:    Device object
        """
        if not isinstance(index, INT_TYPE):
            raise ParameterTypeError("DeviceManager.open_device_by_index: "
                                     "Expected index type is int, not %s" % type(index))

        if not isinstance(access_mode, INT_TYPE):
            raise ParameterTypeError("DeviceManager.open_device_by_index: "
                                     "Expected access_mode type is int, not %s" % type(access_mode))

        if index < 1:
            print("DeviceManager.open_device_by_index: index must start from 1")
            return None
        elif index > UNSIGNED_INT_MAX:
            print("DeviceManager.open_device_by_index: index maximum: %s" % hex(UNSIGNED_INT_MAX).__str__())
            return None

        access_mode_dict = dict(
            (name, getattr(GxAccessMode, name)) for name in dir(GxAccessMode) if not name.startswith('__'))
        if access_mode not in access_mode_dict.values():
            print("DeviceManager.open_device_by_index: "
                  "access_mode out of bounds, %s" % access_mode_dict.__str__())
            return None

        if self.__device_num < index:
            # Re-update the device
            self.update_device_list()
            if self.__device_num < index:
                raise NotFoundDevice("DeviceManager.open_device_by_index: invalid index")

        # open devices by index
        open_param = GxOpenParam()
        open_param.content = string_encoding(str(index))
        open_param.open_mode = GxOpenMode.INDEX
        open_param.access_mode = access_mode
        status, handle = gx_open_device(open_param)
        StatusProcessor.process(status, 'DeviceManager', 'open_device_by_index')

        # get device class
        device_class = self.__device_info_list[index - 1]["device_class"]

        return self.__create_device(device_class, handle)

    def __get_device_class_by_sn(self, sn):
        """
        :brief:     1.find device by sn in self.__device_info_list
                    2.return different objects according to device class
        :param      sn:      device serial number
        :return:    device class
        """
        for index in range(self.__device_num):
            if self.__device_info_list[index]["sn"] == sn:
                return self.__device_info_list[index]["device_class"]

        # don't find this id in device base info list
        return -1

    def open_device_by_sn(self, sn, access_mode=GxAccessMode.CONTROL):
        """
        :brief      open device by serial number(SN)
                    USB3 device return U3VDevice object
                    USB2 device return U2Device object
                    GEV device return GEVDevice object
        :param      sn:             device serial number, type: str
        :param      access_mode:    the mode of open device[GxAccessMode]
        :return:    Device object
        """
        if not isinstance(sn, str):
            raise ParameterTypeError("DeviceManager.open_device_by_sn: "
                                     "Expected sn type is str, not %s" % type(sn))

        if not isinstance(access_mode, INT_TYPE):
            raise ParameterTypeError("DeviceManager.open_device_by_sn: "
                                     "Expected access_mode type is int, not %s" % type(access_mode))

        access_mode_dict = dict(
            (name, getattr(GxAccessMode, name)) for name in dir(GxAccessMode) if not name.startswith('__'))
        if access_mode not in access_mode_dict.values():
            print("DeviceManager.open_device_by_sn: "
                  "access_mode out of bounds, %s" % access_mode_dict.__str__())
            return None

        # get device class from self.__device_info_list
        device_class = self.__get_device_class_by_sn(sn)
        if device_class == -1:
            # Re-update the device
            self.update_device_list()
            device_class = self.__get_device_class_by_sn(sn)
            if device_class == -1:
                # don't find this sn
                raise NotFoundDevice("DeviceManager.open_device_by_sn: Not found device")

        # open devices by sn
        open_param = GxOpenParam()
        open_param.content = string_encoding(sn)
        open_param.open_mode = GxOpenMode.SN
        open_param.access_mode = access_mode
        status, handle = gx_open_device(open_param)
        StatusProcessor.process(status, 'DeviceManager', 'open_device_by_sn')

        return self.__create_device(device_class, handle)

    def __get_device_class_by_user_id(self, user_id):
        """
        :brief:     1.find device according to sn in self.__device_info_list
                    2.return different objects according to device class
        :param      user_id:        user ID
        :return:    device class
        """
        for index in range(self.__device_num):
            if self.__device_info_list[index]["user_id"] == user_id:
                return self.__device_info_list[index]["device_class"]

        # don't find this id in device base info list
        return -1

    def open_device_by_user_id(self, user_id, access_mode=GxAccessMode.CONTROL):
        """
        :brief      open device by user defined name
                    USB3 device return U3VDevice object
                    GEV  device return GEVDevice object
        :param      user_id:        user defined name, type:str
        :param      access_mode:    the mode of open device[GxAccessMode]
        :return:    Device object
        """
        if not isinstance(user_id, str):
            raise ParameterTypeError("DeviceManager.open_device_by_user_id: "
                                     "Expected user_id type is str, not %s" % type(user_id))
        elif user_id.__len__() == 0:
            raise InvalidParameter("DeviceManager.open_device_by_user_id: Don't support user_id's length is 0")

        if not isinstance(access_mode, INT_TYPE):
            raise ParameterTypeError("DeviceManager.open_device_by_user_id: "
                                     "Expected access_mode type is int, not %s" % type(access_mode))

        access_mode_dict = dict(
            (name, getattr(GxAccessMode, name)) for name in dir(GxAccessMode) if not name.startswith('__'))
        if access_mode not in access_mode_dict.values():
            print("DeviceManager.open_device_by_user_id: access_mode out of bounds, %s" % access_mode_dict.__str__())
            return None

        # get device class from self.__device_info_list
        device_class = self.__get_device_class_by_user_id(user_id)
        if device_class == -1:
            # Re-update the device
            self.update_device_list()
            device_class = self.__get_device_class_by_user_id(user_id)
            if device_class == -1:
                # don't find this user_id
                raise NotFoundDevice("DeviceManager.open_device_by_user_id: Not found device")

        # open device by user_id
        open_param = GxOpenParam()
        open_param.content = string_encoding(user_id)
        open_param.open_mode = GxOpenMode.USER_ID
        open_param.access_mode = access_mode
        status, handle = gx_open_device(open_param)
        StatusProcessor.process(status, 'DeviceManager', 'open_device_by_user_id')

        return self.__create_device(device_class, handle)

    def open_device_by_ip(self, ip, access_mode=GxAccessMode.CONTROL):
        """
        :brief      open device by device ip address
        :param      ip:             device ip address, type:str
        :param      access_mode:    the mode of open device[GxAccessMode]
        :return:    GEVDevice object
        """
        if not isinstance(ip, str):
            raise ParameterTypeError("DeviceManager.open_device_by_ip: "
                                     "Expected ip type is str, not %s" % type(ip))

        if not isinstance(access_mode, INT_TYPE):
            raise ParameterTypeError("DeviceManager.open_device_by_ip: "
                                     "Expected access_mode type is int, not %s" % type(access_mode))

        access_mode_dict = dict(
            (name, getattr(GxAccessMode, name)) for name in dir(GxAccessMode) if not name.startswith('__'))
        if access_mode not in access_mode_dict.values():
            print("DeviceManager.open_device_by_ip: access_mode out of bounds, %s" % access_mode_dict.__str__())
            return None

        # open device by ip
        open_param = GxOpenParam()
        open_param.content = string_encoding(ip)
        open_param.open_mode = GxOpenMode.IP
        open_param.access_mode = access_mode
        status, handle = gx_open_device(open_param)
        StatusProcessor.process(status, 'DeviceManager', 'open_device_by_ip')

        return self.__create_device(GxDeviceClassList.GEV, handle)

    def open_device_by_mac(self, mac, access_mode=GxAccessMode.CONTROL):
        """
        :brief      open device by device mac address
        :param      mac:            device mac address, type:str
        :param      access_mode:    the mode of open device[GxAccessMode]
        :return:    GEVDevice object
        """
        if not isinstance(mac, str):
            raise ParameterTypeError("DeviceManager.open_device_by_mac: "
                                     "Expected mac type is str, not %s" % type(mac))

        if not isinstance(access_mode, INT_TYPE):
            raise ParameterTypeError("DeviceManager.open_device_by_mac: "
                                     "Expected access_mode type is int, not %s" % type(access_mode))

        access_mode_dict = dict(
            (name, getattr(GxAccessMode, name)) for name in dir(GxAccessMode) if not name.startswith('__'))
        if access_mode not in access_mode_dict.values():
            print("DeviceManager.open_device_by_mac: access_mode out of bounds, %s" % access_mode_dict.__str__())
            return None

        # open device by ip
        open_param = GxOpenParam()
        open_param.content = string_encoding(mac)
        open_param.open_mode = GxOpenMode.MAC
        open_param.access_mode = access_mode
        status, handle = gx_open_device(open_param)
        StatusProcessor.process(status, 'DeviceManager', 'open_device_by_mac')

        return self.__create_device(GxDeviceClassList.GEV, handle)

    def gige_reset_device(self, mac_address, reset_device_mode):
        """
        :brief      Reconnection/Reset
        :param      mac_address:        The MAC address of the device(str)
        :param      reset_device_mode:  Reconnection mode, refer to GxResetDeviceModeEntry
        :return:    None
        """
        _InterUtility.check_type(mac_address, str, "mac_address", "DeviceManager", "gige_reset_device")
        _InterUtility.check_type(reset_device_mode, int, "reset_device_mode", "DeviceManager", "gige_reset_device")
        status = gx_gige_reset_device(mac_address, reset_device_mode)
        StatusProcessor.process(status, 'DeviceManager', 'gige_reset_device')

    def gige_force_ip(self, mac_address, ip_address, subnet_mask, default_gate_way):
        """
        :brief      Execute the Force IP
        :param      mac_address:        The MAC address of the device(str)
        :param      ip_address:         Reconnection mode, refer to GxResetDeviceModeEntry
        :param      subnet_mask:        The MAC address of the device(str)
        :param      default_gate_way:  Reconnection mode, refer to GxResetDeviceModeEntry
        :return:    None
        """
        _InterUtility.check_type(mac_address, str, "mac_address", "DeviceManager", "gige_force_ip")
        _InterUtility.check_type(ip_address, str, "ip_address", "DeviceManager", "gige_force_ip")
        _InterUtility.check_type(subnet_mask, str, "subnet_mask", "DeviceManager", "gige_force_ip")
        _InterUtility.check_type(default_gate_way, str, "default_gate_way", "DeviceManager", "gige_force_ip")
        status = gx_gige_force_ip(mac_address, ip_address, subnet_mask, default_gate_way)
        StatusProcessor.process(status, 'DeviceManager', 'gige_force_ip')

    def gige_ip_configuration(self, mac_address, ipconfig_flag, ip_address, subnet_mask, default_gateway, user_id):
        """
        :brief      Execute the Force IP
        :param      mac_address:        The MAC address of the device(str)
        :param      ipconfig_flag:         Reconnection mode, refer to GxResetDeviceModeEntry
        :param      ip_address:        The MAC address of the device(str)
        :param      subnet_mask:         Reconnection mode, refer to GxResetDeviceModeEntry
        :param      default_gateway:        The MAC address of the device(str)
        :param      user_id:  Reconnection mode, refer to GxResetDeviceModeEntry
        :return:    None
        """
        _InterUtility.check_type(mac_address, str, "mac_address", "DeviceManager", "gige_ip_configuration")
        _InterUtility.check_type(ipconfig_flag, int, "ipconfig_flag", "DeviceManager", "gige_ip_configuration")
        _InterUtility.check_type(ip_address, str, "ip_address", "DeviceManager", "gige_ip_configuration")
        _InterUtility.check_type(subnet_mask, str, "subnet_mask", "DeviceManager", "gige_ip_configuration")
        _InterUtility.check_type(default_gateway, str, "default_gateway", "DeviceManager", "gige_ip_configuration")
        _InterUtility.check_type(user_id, str, "user_id", "DeviceManager", "gige_ip_configuration")
        status = gx_gige_ip_configuration(mac_address, ipconfig_flag, ip_address, subnet_mask, default_gateway, user_id)
        StatusProcessor.process(status, 'DeviceManager', 'gige_ip_configuration')

    def create_image_format_convert(self):
        """
        :brief      create new convert pointer
        :return:    GxImageFormatConvert
        """
        image_format_convert = ImageFormatConvert()
        return image_format_convert

    def create_image_process(self):
        """
        :brief      create image process
        :return:    GxImageFormatConvert
        """
        image_process = ImageProcess()
        return image_process

    def issue_action_command(self, device_key, group_key, group_mask, broadcast_address, special_address, time_out,
                             expect_ack_number_res):
        """
        :brief                 Send normal action command
        :device_key            [in]ACK_COMMAND protocol: Key to identify the device
        :group_key             [in]ACK_COMMAND protocol: Key to identify the group
        :group_mask            [in]ACK_COMMAND protocol: Key to identify the group
        :broadcast_address     [in] Broadcast address entered by the user
        :special_address       [in] Optional parameter user specifies which network port to send
        :time_out              [in] time out
        :expect_ack_number_res [in]The expected number of acks returned
                               [out]The actual number of acks returned

        :return:  status:  State return value, See detail in GxStatusList
        """

        _InterUtility.check_type(device_key, INT_TYPE, "device_key", "DeviceManager", "issue_action_command")
        _InterUtility.check_type(group_key, INT_TYPE, "group_key", "DeviceManager", "issue_action_command")
        _InterUtility.check_type(group_mask, INT_TYPE, "group_mask", "DeviceManager", "issue_action_command")
        _InterUtility.check_type(broadcast_address, str, "broadcast_address", "DeviceManager", "issue_action_command")

        _InterUtility.check_type(time_out, INT_TYPE, "time_out", "DeviceManager", "issue_action_command")
        _InterUtility.check_type(expect_ack_number_res, INT_TYPE, "expect_ack_number_res", "DeviceManager",
                                 "issue_action_command")

        status, actual_ack_list = gx_issue_action_command(device_key, group_key, group_mask, broadcast_address, special_address,
                                                time_out, expect_ack_number_res)


        StatusProcessor.process(status, 'DeviceManager', 'issue_action_command')
        return actual_ack_list

    def issue_scheduled_action_command(self, device_key, group_key, group_mask, action_time, broadcast_address,
                                       special_address, time_out,
                                       expect_ack_number_res):
        """
        :brief                 Send normal action command
        :device_key            [in]ACK_COMMAND protocol: Key to identify the device
        :group_key             [in]ACK_COMMAND protocol: Key to identify the group
        :group_mask            [in]ACK_COMMAND protocol: Key to identify the group
        :action_time           [in]ACK_COMMAND protocol: Time to execute the planned action command
        :broadcast_address     [in] Broadcast address entered by the user
        :special_address       [in] Optional parameter user specifies which network port to send
        :time_out              [in] time out
        :expect_ack_number_res [in]The expected number of acks returned
                               [out]The actual number of acks returned

        :return:  status:  State return value, See detail in GxStatusList
        """

        _InterUtility.check_type(device_key, INT_TYPE, "device_key", "DeviceManager", "issue_scheduled_action_command")
        _InterUtility.check_type(group_key, INT_TYPE, "group_key", "DeviceManager", "issue_scheduled_action_command")
        _InterUtility.check_type(group_mask, INT_TYPE, "group_mask", "DeviceManager", "issue_scheduled_action_command")
        _InterUtility.check_type(broadcast_address, str, "broadcast_address", "DeviceManager", "issue_scheduled_action_command")

        _InterUtility.check_type(time_out, INT_TYPE, "time_out", "DeviceManager", "issue_scheduled_action_command")
        _InterUtility.check_type(action_time, INT_TYPE, "action_time", "DeviceManager", "issue_scheduled_action_command")
        _InterUtility.check_type(expect_ack_number_res, INT_TYPE, "expect_ack_number_res", "DeviceManager", "issue_scheduled_action_command")

        status, actual_ack_list = gx_issue_scheduled_action_command(device_key, group_key, group_mask, action_time, broadcast_address,
                                                   special_address,
                                                   time_out, expect_ack_number_res)
        StatusProcessor.process(status, 'DeviceManager', 'issue_scheduled_action_command')
        return actual_ack_list

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


