#!/usr/bin/python
# -*-mode:python ; tab-width:4 -*- ex:set tabstop=4 shiftwidth=4 expandtab: -*-
# -*- coding:utf-8 -*-

from ctypes import *
import ctypes
import sys
import os

NODE_FEATURE_RESERVED_16 = 16

if sys.platform == 'linux2' or sys.platform == 'linux':
    try:
        dll = CDLL('/usr/lib/libgxiapi.so')
    except OSError:
        print("Cannot find libgxiapi.so.")
else:
    try:
        env_dist = os.environ
        GeniCam_AddPath32 = str(env_dist["GALAXY_GENICAM_ROOT"]) + r"\bin\Win32_i86"
        GeniCam_AddPath64 = str(env_dist["GALAXY_GENICAM_ROOT"]) + r"\bin\Win64_x64"
        GxiApi_AddPath32 = str(env_dist["GALAXY_GENICAM_ROOT"]).split("GenICam")[0] + r"\APIDll\Win32"
        GxiApi_AddPath64 = str(env_dist["GALAXY_GENICAM_ROOT"]).split("GenICam")[0] + r"\APIDll\Win64"

        if (sys.version_info.major == 3 and sys.version_info.minor >= 8) or (sys.version_info.major > 3):
            os.add_dll_directory(GeniCam_AddPath32)
            os.add_dll_directory(GxiApi_AddPath32)

            # 32bit system has no GeniCam_AddPath64/GxiApi_AddPath64
            if os.path.exists(GeniCam_AddPath64):
                os.add_dll_directory(GeniCam_AddPath64)
            if os.path.exists(GxiApi_AddPath64):
                os.add_dll_directory(GxiApi_AddPath64)
            
            dll = WinDLL('GxIAPI.dll', winmode=0)
        else:
            dll = WinDLL('GxIAPI.dll')
    except OSError:
        print('Cannot find GxIAPI.dll.')


# Error code
class GxStatusList:
    SUCCESS = 0	                # Success
    ERROR = -1                  # There is a unspecified internal error that is not expected to occur
    NOT_FOUND_TL = -2           # The TL library cannot be found
    NOT_FOUND_DEVICE = -3       # The device is not found
    OFFLINE = -4                # The current device is in a offline state
    INVALID_PARAMETER = -5      # Invalid parameter, Generally the pointer is NULL or the input IP and
                                # Other parameter formats are invalid
    INVALID_HANDLE = -6         # Invalid handle
    INVALID_CALL = -7           # The interface is invalid, which refers to software interface logic error
    INVALID_ACCESS = -8         # The function is currently inaccessible or the device access mode is incorrect
    NEED_MORE_BUFFER = -9       # The user request buffer is insufficient: the user input buffersize during
                                # the read operation is less than the actual need
    ERROR_TYPE = -10            # The type of FeatureID used by the user is incorrect,
                                # such as an integer interface using a floating-point function code
    OUT_OF_RANGE = -11          # The value written by the user is crossed
    NOT_IMPLEMENTED = -12       # This function is not currently supported
    NOT_INIT_API = -13          # There is no call to initialize the interface
    TIMEOUT = -14               # Timeout error
    REPEAT_OPENED = -1004       # The device has been opened

    def __init__(self):
        pass

#Interface CXP type info
class GXCxpInterfaceInfo(Structure):
    _fields_ = [
        ('interface_id', c_char*64),           # Interface ID
        ('display_name', c_char*64),           # Display Name
        ('serial_number', c_char*64),          # Serial Number
        ('init_flag', c_uint),                 # Init Flag
        ('reserved', c_uint*65),               # Reserved
    ]
    def __str__(self):
        return "GXCxpInterfaceInfo\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)

#Interface GEV type info
class GXGevInterfaceInfo(Structure):
    _fields_ = [
        ('interface_id', c_char * 64),         # Interface ID
        ('display_name', c_char * 64),         # Display Name
        ('serial_number', c_char * 64),        # Serial Number
        ('description', c_char * 256),         # Description
        ('init_flag', c_uint),                 # Init Flag
        ('reserved', c_uint*63),               # Reserved
    ]
    def __str__(self):
        return "GXGevInterfaceInfo\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)

#Interface U3V type info
class GXU3vInterfaceInfo(Structure):
    _fields_ = [
        ('interface_id', c_char*64),           # Interface ID
        ('display_name', c_char*64),           # Display Name
        ('serial_number', c_char*64),          # Serial Number
        ('description', c_char*256),           # Description
        ('reserved', c_uint*64),               # Reserved
    ]
    def __str__(self):
        return "GXU3vInterfaceInfo\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)

#Interface USB type info
class GXUsbInterfaceInfo(Structure):
    _fields_ = [
        ('interface_id', c_char * 64),         # Interface ID
        ('display_name', c_char * 64),         # Display Name
        ('serial_number', c_char * 64),        # Serial Number
        ('description', c_char * 256),         # Description
        ('reserved', c_uint*64),               # Reserved
    ]
    def __str__(self):
        return "GXUsbInterfaceInfo\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)

# Interface Special info
class GXInterfacSpecialInfo(Union):
    _fields_ = [
        ("CXP_interface_info", GXCxpInterfaceInfo),   # CXP Type
        ("GEV_interface_info", GXGevInterfaceInfo),   # Gev Type
        ("U3V_interface_info", GXU3vInterfaceInfo),   # U3V Type
        ("USB_interface_info", GXUsbInterfaceInfo),   # USB Type
        ("reserved", c_uint*64),                      # Reserved
    ]
    def __str__(self):
        return "_GXInterfacSpecialInfo_\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)

# Interface info
class GXInterfaceInfo(Structure):
    _fields_ = [
        ('TLayer_type', c_int),         # TLayer Type
        ('reserved', c_int*4),          # Reserved
        ('IF_info', GXInterfacSpecialInfo),
    ]
    def __str__(self):
        return "GXInterfaceInfo\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)

class GxRegisterStackEntry(Structure):
    _fields_ = [
        ('address'  , c_ulonglong),     # Address of the register
        ('buffer'   , c_void_p),        # Pointer to the buffer containing the data
        ('size'     , c_uint),          # Number of bytes to read
    ]

    def __str__(self):
        return "GxRegisterStackEntry\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)

class GxOpenMode:
    SN = 0	                   # Opens the device via a serial number
    IP = 1                     # Opens the device via an IP address
    MAC = 2                    # Opens the device via a MAC address
    INDEX = 3                  # Opens the device via a serial number(Start from 1)
    USER_ID = 4                # Opens the device via user defined ID

    def __init__(self):
        pass


class GxFrameMask:
    TYPE_MASK = 0xF0000000
    LEVEL_MASK = 0x0F000000
    
    def __init__(self):
        pass


class GxNodeAccessMode:
    MODE_NI     = 0             # Not implemented
    MODE_NA     = 1             # Not read and write
    MODE_WO     = 2             # Only write
    MODE_RO     = 3             # Only read
    MODE_RW     = 4             # Read and Write
    MODE_UNDEF  = 5             # Unknown


class GxFeatureType:
    INT = 0x10000000            # Integer type
    FLOAT = 0X20000000          # Floating point type
    ENUM = 0x30000000           # Enum type
    BOOL = 0x40000000           # Boolean type
    STRING = 0x50000000         # String type
    BUFFER = 0x60000000         # Block data type
    COMMAND = 0x70000000        # Command type

    def __init__(self):
        pass


class GxFeatureLevel:
    REMOTE_DEV = 0x00000000     # RemoteDevice Layer
    TL = 0x01000000             # TL Layer
    IF = 0x02000000             # Interface Layer
    DEV = 0x03000000            # Device Layer
    DS = 0x04000000             # DataStream Layer

    def __init__(self):
        pass


class GxFeatureID:
    # ---------------Device Information Section---------------------------
    STRING_DEVICE_VENDOR_NAME = 0x50000000                 # The name of the device's vendor
    STRING_DEVICE_MODEL_NAME = 0x50000001                  # The model name of the device
    STRING_DEVICE_FIRMWARE_VERSION = 0x50000002            # The version of the device's firmware and software
    STRING_DEVICE_VERSION = 0x50000003                     # The version of the device
    STRING_DEVICE_SERIAL_NUMBER = 0x50000004               # A serial number for device
    STRING_FACTORY_SETTING_VERSION = 0x50000006            # The version of the device's Factory Setting
    STRING_DEVICE_USER_ID = 0x50000007                     # A user programmable string
    INT_DEVICE_LINK_SELECTOR = 0x10000008                  # Selects which Link of the device to control
    ENUM_DEVICE_LINK_THROUGHPUT_LIMIT_MODE = 0x30000009    # DeviceLinkThroughputLimit switch
    INT_DEVICE_LINK_THROUGHPUT_LIMIT = 0x1000000a          # Limits the maximum bandwidth of the data
    INT_DEVICE_LINK_CURRENT_THROUGHPUT = 0x1000000b        # Current bandwidth of the data
    COMMAND_DEVICE_RESET = 0x7000000c                      # Device reset
    INT_TIMESTAMP_TICK_FREQUENCY = 0x1000000d              # Timestamp tick frequency
    COMMAND_TIMESTAMP_LATCH = 0x7000000e                   # Timestamp latch
    COMMAND_TIMESTAMP_RESET = 0x7000000f                   # Timestamp reset
    COMMAND_TIMESTAMP_LATCH_RESET = 0x70000010             # Timestamp latch reset
    INT_TIMESTAMP_LATCH_VALUE = 0x10000011                 # The value of timestamp latch
    STRING_DEVICE_PHY_VERSION = 0x50000012                 # Device network chip version
    ENUM_DEVICE_TEMPERATURE_SELECTOR = 0x30000013          # Device temperature selection, reference GxDeviceTemperatureSelectorEntry
    FLOAT_DEVICE_TEMPERATURE = 0x20000014                  # Device temperature
    STRING_DEVICE_ISP_FIRMWARE_VERSION = 0x50000015        # The version of device's ISP firmware
    ENUM_LOWPOWER_MODE = 0x30000016                        # Low power consumption mode,refer
    ENUM_CLOSE_CCD = 0x30000017                            # Close CCD
    STRING_PRODUCTION_CODE = 0x50000018                    # Production code
    STRING_DEVICE_ORIGINAL_NAME = 0x50000019               # Original name
    INT_REVISION = 0x1000001a                              # CXP protocol version
    INT_VERSIONS_SUPPORTED = 0x1000001b                    # Supported CXP protocol versions
    INT_VERSION_USED = 0x1000001c                          # Use version
    BOOL_TEC_ENABLE = 0x4000001d                           # TEC switch
    FLOAT_TEC_TARGET_TEMPERATURE = 0x2000001e              # TEC target temperature
    BOOL_FAN_ENABLE = 0x4000001f                           # Fan switch
    INT_TEMPERATURE_DETECTION_STATUS = 0x10000020          # Temperature state detection
    INT_FAN_SPEED = 0x10000021                             # Fan speed
    FLOAT_DEVICE_HUMIDITY = 0x10000022                     # Equipment humidity
    FLOAT_DEVICE_PRESSURE = 0x10000023                     # Equipment air pressure
    INT_AIR_CHANGE_DETECTION_STATUS = 0x10000024           # Ventilation status detection
    INT_AIR_TIGHTNESS_DETECTION_STATUS = 0x10000025        # Airtightness state detection
    ENUM_DEVICE_SCAN_TYPE = 0x30000026                     # Device scanning mode

    # ---------------ImageFormat Section----------------------------------
    INT_SENSOR_WIDTH = 0x100003e8                           # The actual width of the camera's sensor in pixels
    INT_SENSOR_HEIGHT = 0x100003e9                          # The actual height of the camera's sensor in pixels
    INT_WIDTH_MAX = 0x100003ea                              # Width max[read_only]
    INT_HEIGHT_MAX = 0x100003eb                             # Height max[read_only]
    INT_OFFSET_X = 0x100003ec                               # The X offset for the area of interest
    INT_OFFSET_Y = 0x100003ed                               # The Y offset for the area of interest
    INT_WIDTH = 0x100003ee                                  # the width of the area of interest in pixels
    INT_HEIGHT = 0x100003ef                                 # the height of the area of interest in pixels
    INT_BINNING_HORIZONTAL = 0x100003f0                     # Horizontal pixel Binning
    INT_BINNING_VERTICAL = 0x100003f1                       # Vertical pixel Binning
    INT_DECIMATION_HORIZONTAL = 0x100003f2                  # Horizontal pixel sampling
    INT_DECIMATION_VERTICAL = 0x100003f3                    # Vertical pixel sampling
    ENUM_PIXEL_SIZE = 0x300003f4                            # Pixel depth, Reference GxPixelSizeEntry
    ENUM_PIXEL_COLOR_FILTER = 0x300003f5                    # Bayer format, Reference GxPixelColorFilterEntry
    ENUM_PIXEL_FORMAT = 0x300003f6                          # Pixel format, Reference GxPixelFormatEntry
    BOOL_REVERSE_X = 0x400003f7                             # Horizontal flipping
    BOOL_REVERSE_Y = 0x400003f8                             # Vertical flipping
    ENUM_TEST_PATTERN = 0x300003f9                          # Test pattern, Reference GxTestPatternEntry
    ENUM_TEST_PATTERN_GENERATOR_SELECTOR = 0x300003fa       # The source of test pattern, reference GxTestPatternGeneratorSelectorEntry
    ENUM_REGION_SEND_MODE = 0x300003fb                      # ROI region output mode, reference GxRegionSendModeEntry
    ENUM_REGION_MODE = 0x300003fc                           # ROI region output switch
    ENUM_REGION_SELECTOR = 0x300003fd                       # ROI region select, reference GxRegionSelectorEntry
    INT_CENTER_WIDTH = 0x100003fe                           # Window width
    INT_CENTER_HEIGHT = 0x100003ff                          # Window height
    ENUM_BINNING_HORIZONTAL_MODE = 0x30000400               # Binning horizontal mode, reference GxBinningHorizontalModeEntry
    ENUM_BINNING_VERTICAL_MODE = 0x30000401                 # Binning vertical mode, reference GxBinningVerticalModeEntry
    ENUM_SENSOR_SHUTTER_MODE = 0x30000402                   # Sensor shutter mode, reference GxSensorShutterModeEntry
    INT_DECIMATION_LINENUMBER = 0x10000403                  # The line number of decimation
    INT_SENSOR_DECIMATION_HORIZONTAL = 0x10000404           # Sensor Horizontal pixel sampling
    INT_SENSOR_DECIMATION_VERTICAL = 0x10000405             # Sensor Vertical pixel sampling
    ENUM_SENSOR_SELECTOR = 0x30000406                       # selector current sonsor
    INT_CURRENT_SENSOR_WIDTH = 0x10000407                   # current sonsor width
    INT_CURRENT_SENSOR_HEIGHT = 0x10000408                  # current sonsor height
    INT_CURRENT_SENSOR_OFFSETX = 0x10000409                 # current sonsor offset X
    INT_CURRENT_SENSOR_OFFSETY = 0x1000040a                 # current sonsor offset Y
    INT_CURRENT_SENSOR_WIDTHMAX = 0x1000040b                # current sonsor width max
    INT_CURRENT_SENSOR_HEIGHTMAX = 0x1000040c               # current sonsor height max
    ENUM_SENSOR_BIT_DEPTH = 0x3000040d                      # Sensor Bit Depth
    BOOL_WATERMARK_ENABLE = 0x4000040e                      # Watermark

    # ---------------TransportLayer Section-------------------------------
    INT_PAYLOAD_SIZE = 0x100007d0                           # Size of images in byte
    BOOL_GEV_CURRENT_IP_CONFIGURATION_LLA = 0x400007d1      # (Only GEVDevice)IP configuration by LLA.
    BOOL_GEV_CURRENT_IP_CONFIGURATION_DHCP = 0x400007d2     # (Only GEVDevice)IP configuration by DHCP
    BOOL_GEV_CURRENT_IP_CONFIGURATION_PERSISTENT_IP = 0x400007d3   # (Only GEVDevice)IP configuration by PersistentIP
    INT_ESTIMATED_BANDWIDTH = 0x100007d4                    # (Only GEVDevice)Estimated Bandwidth in Bps
    INT_GEV_HEARTBEAT_TIMEOUT = 0x100007d5                  # (Only GEVDevice)The heartbeat timeout in milliseconds
    INT_GEV_PACKET_SIZE = 0x100007d6                        # (Only GEVDevice)The packet size in bytes for each packet
    INT_GEV_PACKET_DELAY = 0x100007d7                       # (Only GEVDevice)A delay between the transmission of each packet
    INT_GEV_LINK_SPEED = 0x100007d8                         # (Only GEVDevice)The connection speed in Mbps
    ENUM_DEVICE_TAP_GEOMETRY = 0x300007d9                   # Equipment geometry

    # ---------------AcquisitionTrigger Section---------------------------
    ENUM_ACQUISITION_MODE = 0x30000bb8                      # The mode of acquisition, reference GxAcquisitionModeEntry
    COMMAND_ACQUISITION_START = 0x70000bb9                  # The command for starts the acquisition of images
    COMMAND_ACQUISITION_STOP = 0x70000bba                   # The command for stop the acquisition of images
    INT_ACQUISITION_SPEED_LEVEL = 0x10000bbb                # (Only U2Device)The level for acquisition speed
    INT_ACQUISITION_FRAME_COUNT = 0x10000bbc                # (Only U2Device)Number of frames to acquire in MultiFrame Acquisition mode.
    ENUM_TRIGGER_MODE = 0x30000bbd                          # Trigger mode switch
    COMMAND_TRIGGER_SOFTWARE = 0x70000bbe                   # The command for generates a software trigger signal
    ENUM_TRIGGER_ACTIVATION = 0x30000bbf                    # Trigger polarity, Reference GxTriggerActivationEntry
    ENUM_TRIGGER_SWITCH = 0x30000bc0                        # (Only U2Device)The switch of External trigger
    FLOAT_EXPOSURE_TIME = 0x20000bc1                        # Exposure time
    ENUM_EXPOSURE_AUTO = 0x30000bc2                         # Exposure auto
    FLOAT_TRIGGER_FILTER_RAISING = 0x20000bc3               # The Value of rising edge triggered filter
    FLOAT_TRIGGER_FILTER_FALLING = 0x20000bc4               # The Value of falling edge triggered filter
    ENUM_TRIGGER_SOURCE = 0x30000bc5                        # Trigger source, Reference GxTriggerSourceEntry
    ENUM_EXPOSURE_MODE = 0x30000bc6                         # Exposure mode, Reference GxExposureModeEntry
    ENUM_TRIGGER_SELECTOR = 0x30000bc7                      # Trigger type, Reference GxTriggerSelectorEntry
    FLOAT_TRIGGER_DELAY = 0x20000bc8                        # The trigger delay in microsecond
    ENUM_TRANSFER_CONTROL_MODE = 0x30000bc9                 # The control method for the transfers, Reference GxTransferControlModeEntry
    ENUM_TRANSFER_OPERATION_MODE = 0x30000bca               # The operation method for the transfers, Reference GxTransferOperationModeEntry
    COMMAND_TRANSFER_START = 0x70000bcb                     # Starts the streaming of data blocks out of the device
    INT_TRANSFER_BLOCK_COUNT = 0x10000bcc                   # The number of data Blocks that the device should stream before stopping
    BOOL_FRAMESTORE_COVER_ACTIVE = 0x40000bcd               # The switch for frame cover
    ENUM_ACQUISITION_FRAME_RATE_MODE = 0x30000bce           # The switch for Control frame rate
    FLOAT_ACQUISITION_FRAME_RATE = 0x20000bcf               # The value for Control frame rate
    FLOAT_CURRENT_ACQUISITION_FRAME_RATE = 0x20000bd0       # The maximum allowed frame acquisition rate
    ENUM_FIXED_PATTERN_NOISE_CORRECT_MODE = 0x30000bd1      # The switch of fixed pattern noise correct
    INT_ACQUISITION_BURST_FRAME_COUNT = 0x10000bd6          # The acquisition burst frame count
    ENUM_ACQUISITION_STATUS_SELECTOR = 0x30000bd7           # The selector of acquisition status, reference GxAcquisitionStatusSelectorEntry
    BOOL_ACQUISITION_STATUS = 0x40000bd8                    # The acquisition status
    FLOAT_EXPOSURE_DELAY = 0x2000765c                       # The exposure delay
    FLOAT_EXPOSURE_OVERLAP_TIME_MAX = 0x2000765d            # Maximum overlap exposure time
    ENUM_EXPOSURE_TIME_MODE = 0x3000765e                    # Exposure time mode, reference GxExposureTimeModeEntry
    INT_FRAME_BUFFER_COUNT = 0x10004651                     # Frame memory depth
    COMMAND_FRAME_BUFFER_FLUSH = 0x70004652                 # Empty the frame save
    ENUM_ACQUISITION_BURST_MODE = 0x3000765F                # Burst acquisition mode
    ENUM_OVERLAP_MODE = 0x30007660                          # overlap mode
    ENUM_MULTISOURCE_SELECTOR = 0x30007661                  # MultiSourceSelector
    BOOL_MULTISOURCE_ENABLE = 0x40007662                    # MultiSource Trigger Enable
    BOOL_TRIGGER_CACHE_ENABLE = 0x40007663                  # Trigger Cache Enable

    # ----------------DigitalIO Section-----------------------------------
    ENUM_USER_OUTPUT_SELECTOR = 0x30000fa0                  # selects user settable output signal, Reference GxUserOutputSelectorEntry
    BOOL_USER_OUTPUT_VALUE = 0x40000fa1                     # The state of the output signal
    ENUM_USER_OUTPUT_MODE = 0x30000fa2                      # (Only U2Device)UserIO output mode, Reference GxUserOutputModeEntry
    ENUM_STROBE_SWITCH = 0x30000fa3                         # (Only U2Device)Strobe switch
    ENUM_LINE_SELECTOR = 0x30000fa4                         # Line selector, Reference GxLineSelectorEntry
    ENUM_LINE_MODE = 0x30000fa5                             # Line mode, Reference GxLineModeEntry
    BOOL_LINE_INVERTER = 0x40000fa6                         # Pin level reversal
    ENUM_LINE_SOURCE = 0x30000fa7                           # line source, Reference GxLineSourceEntry
    BOOL_LINE_STATUS = 0x40000fa8                           # line status
    INT_LINE_STATUS_ALL = 0x10000fa9                        # all line status
    FLOAT_PULSE_WIDTH = 0x20000faa                          # IO pulse width
    INT_LINE_RANGE = 0x10000fab                             # flash line ragne
    INT_LINE_DELAY = 0x10000fac                             # flash line delay
    INT_LINE_FILTER_RAISING_EDGE = 0x10000fad               # Pin rising edge filtering
    INT_LINE_FILTER_FALLING_EDGE = 0x10000fae               # Pin falling edge filtering

    # ----------------AnalogControls Section------------------------------
    ENUM_GAIN_AUTO = 0x30001388                             # gain auto, Reference GxAutoEntry
    ENUM_GAIN_SELECTOR = 0x30001389                         # selects gain channel, Reference GxGainSelectorEntry
    ENUM_BLACK_LEVEL_AUTO = 0x3000138b                      # Black level auto, Reference GxAutoEntry
    ENUM_BLACK_LEVEL_SELECTOR = 0x3000138c                  # Black level channel, Reference GxBlackLevelSelectEntry
    ENUM_BALANCE_WHITE_AUTO = 0x3000138e                    # Balance white auto, Reference GxAutoEntry
    ENUM_BALANCE_RATIO_SELECTOR = 0x3000138f                # selects Balance white channel, Reference GxBalanceRatioSelectorEntry
    FLOAT_BALANCE_RATIO = 0x20001390                        # Balance white channel ratio
    ENUM_COLOR_CORRECT = 0x30001391                         # Color correct switch
    ENUM_DEAD_PIXEL_CORRECT = 0x30001392                    # Pixel correct switch
    FLOAT_GAIN = 0x20001393                                 # gain value
    FLOAT_BLACK_LEVEL = 0x20001394                          # Black level value
    BOOL_GAMMA_ENABLE = 0x40001395                          # Gamma enable bit
    ENUM_GAMMA_MODE = 0x30001396                            # Gamma mode, reference GxGammaModeEntry
    FLOAT_GAMMA = 0x20001397                                # The value of Gamma
    INT_DIGITAL_SHIFT = 0x10001398                          # bit select
    ENUM_LIGHT_SOURCE_PRESET = 0x30001399                   # Light source preset, Reference GxLightSourcePresetEntry
    BOOL_BLACKLEVEL_CALIB_STATUS = 0x4000139a               # BlackLevelCalibStatus
    INT_BLACKLEVEL_CALIB_VALUE = 0x1000139b                 # BlackLevelCalibValue
    FLOAT_PGA_GAIN = 0x2000139c                             # PGAGain

    # ---------------CustomFeature Section--------------------------------
    INT_ADC_LEVEL = 0x10001770                              # (Only U2Device)AD conversion level
    INT_H_BLANKING = 0x10001771                             # (Only U2Device)Horizontal blanking
    INT_V_BLANKING = 0x10001772                             # (Only U2Device)Vertical blanking
    STRING_USER_PASSWORD = 0x50001773                       # (Only U2Device)User encrypted zone cipher
    STRING_VERIFY_PASSWORD = 0x50001774                     # (Only U2Device)User encrypted zone check cipher
    BUFFER_USER_DATA = 0x60001775                           # (Only U2Device)User encrypted area content
    INT_GRAY_VALUE = 0x10001776                             # Expected gray value
    ENUM_AA_LIGHT_ENVIRONMENT = 0x30001777                  # (Only U2Device)Gain auto, Exposure auto, Light environment type,
                                                            # Reference GxAALightEnvironmentEntry
    INT_AAROI_OFFSETX = 0x10001778                          # The X offset for the rect of interest in pixels for 2A
    INT_AAROI_OFFSETY = 0x10001779                          # The Y offset for the rect of interest in pixels for 2A
    INT_AAROI_WIDTH = 0x1000177a                            # The width offset for the rect of interest in pixels for 2A
    INT_AAROI_HEIGHT = 0x1000177b                           # The height offset for the rect of interest in pixels for 2A
    FLOAT_AUTO_GAIN_MIN = 0x2000177c                        # Automatic gain minimum
    FLOAT_AUTO_GAIN_MAX = 0x2000177d                        # Automatic gain maximum
    FLOAT_AUTO_EXPOSURE_TIME_MIN = 0x2000177e               # Automatic exposure minimum
    FLOAT_AUTO_EXPOSURE_TIME_MAX = 0x2000177f               # Automatic exposure maximum
    BUFFER_FRAME_INFORMATION = 0x60001780                   # (Only U2Device)Image frame information
    INT_CONTRAST_PARAM = 0x10001781                         # Contrast parameter
    FLOAT_GAMMA_PARAM = 0x20001782                          # Gamma parameter
    INT_COLOR_CORRECTION_PARAM = 0x10001783                 # Color correction param
    ENUM_IMAGE_GRAY_RAISE_SWITCH = 0x30001784               # (Only U2Device)Image gray raise switch
    ENUM_AWB_LAMP_HOUSE = 0x30001785                        # Automatic white balance light source
                                                            # Reference GxAWBLampHouseEntry
    INT_AWBROI_OFFSETX = 0x10001786                         # Offset_X of automatic white balance region
    INT_AWBROI_OFFSETY = 0x10001787                         # Offset_Y of automatic white balance region
    INT_AWBROI_WIDTH = 0x10001788                           # Width of automatic white balance region
    INT_AWBROI_HEIGHT = 0x10001789                          # Height of automatic white balance region
    ENUM_SHARPNESS_MODE = 0x3000178a                        # Sharpness switch
    FLOAT_SHARPNESS = 0x2000178b                            # Sharpness value
    ENUM_USER_DATA_FIELD_SELECTOR = 0x3000178c              # User selects the flash data field
                                                            # Reference GxUserDataFieldSelectorEntry for area selection
    BUFFER_USER_DATA_FIELD_VALUE = 0x6000178d               # User data field content
    ENUM_FLAT_FIELD_CORRECTION = 0x3000178e                 # Flat field correction switch
    ENUM_NOISE_REDUCTION_MODE = 0x3000178f                  # Noise reduction switch
    FLOAT_NOISE_REDUCTION = 0x20001790                      # Noise reduction value
    BUFFER_FFCLOAD = 0x60001791                             # Get flat field correction parameters
    BUFFER_FFCSAVE = 0x60001792                             # Set flat field correction parameters
    ENUM_STATIC_DEFECT_CORRECTION = 0x30001793              # Static dead pixel correction switch

    ENUM_2D_NOISE_REDUCTION_MODE = 0x30001794               # 2d noise reduction mode
    ENUM_3D_NOISE_REDUCTION_MODE = 0x30001795               # 3d noise reduction mode
    COMMAND_CLOSE_ISP = 0x70001796                          # Close ISP
    BUFFER_STATIC_DEFECT_CORRECTION_VALUE_ALL = 0x60001797  # static defect conrrection value
    BUFFER_STATIC_DEFECT_CORRECTION_FLASH_VALUE = 0x60001798  # static defect conrrection flash value
    INT_STATIC_DEFECT_CORRECTION_FINISH = 0x10001799        # static defect conrrection finish
    BUFFER_STATIC_DEFECT_CORRECTION_INFO = 0x6000179a       # static defect conrrection Info
    COMMAND_STRIP_CALIBRATION_START = 0x7000179b            # Starts the strip calibration
    COMMAND_STRIP_CALIBRATION_STOP = 0x7000179c             # Ready to stop the strip calibration
    BUFFER_USER_DATA_FILED_VALUE_ALL = 0x6000179d           # Continuous user area content
    ENUM_SHADING_CORRECTION_MODE = 0x3000179e
    COMMAND_FFC_GENERATE = 0x7000179f                       # Generate flat field correction factor
    ENUM_FFC_GENERATE_STATUS = 0x700017a0                   # Level-field correction status
    ENUM_FFC_EXPECTED_GRAY_VALUE_ENABLE = 0x700017a1        # Level-field correction expected gray value enable
    INT_FFC_EXPECTED_GRAY = 0x100017a2                      # Flat-field correction expected gray value
    INT_FFC_COEFFICIENTS_SIZE = 0x100017a3                  # Level-field correction factor size
    BUFFER_FFC_VALUE_ALL = 0x600017a4                       # Level-field correction value
    ENUM_DSNU_SELECTOR = 0x700017a5                         # Selection of dark field correction coefficient
    COMMAND_DSNU_GENERATE = 0x700017a6                      # Generate dark field correction factor
    ENUM_DSNU_GENERATE_STATUS = 0x700017a7                  # Dark field correction status
    COMMAND_DSNU_SAVE = 0x700017a8                          # Save dark-field correction factor
    COMMAND_DSNU_LOAD = 0x700017a9                          # Load dark-field correction factor
    ENUM_PRNU_SELECTOR = 0x700017aa                         # Selection of bright field correction coefficient
    COMMAND_PRNU_GENERATE = 0x700017ab                      # Generate bright field correction factor
    ENUM_PRNU_GENERATE_STATUS = 0x700017ac                  # Bright-field correction status
    COMMAND_PRNU_SAVE = 0x700017ad                          # Save the bright field correction factor
    COMMAND_PRNU_LOAD = 0x700017ae                          # Loaded open field correction factor
    BUFFER_DATA_FIELD_VALUE_ALL = 0x600017bf                # Data field value
    INT_STATIC_DEFECT_CORRECTION_CALIB_STATUS = 0x100017b0  # Static bad point calibration status
    INT_FFC_FACTORY_STATUS = 0x100017b1                     # Level-field correction status detection
    INT_DSNU_FACTORY_STATUS = 0x100017b2                    # Detection of dark-field correction state
    INT_PRNU_FACTORY_STATUS = 0x100017b3                    # Open field correction state detection
    BUFFER_DETECT = 0x100017b4                              # Buffer detection (CXP)
    ENUM_FFC_COEFFICIENT = 0x700017b5                       # Selection of flat field correction coefficient
    BUFFER_FFCFLASH_LOAD = 0x700017b6                       # Load the flat field correction coefficient
    BUFFER_FFCFLASH_SAVE = 0x700017b7                       # Save the flat field correction coefficient

    # ---------------UserSetControl Section-------------------------------
    ENUM_USER_SET_SELECTOR = 0x30001b58                     # Parameter group selection, Reference GxUserSetEntry
    COMMAND_USER_SET_LOAD = 0x70001b59                      # Load parameter group
    COMMAND_USER_SET_SAVE = 0x70001b5a                      # Save parameter group
    ENUM_USER_SET_DEFAULT = 0x30001b5b                      # Startup parameter group, Reference GxUserSetEntry
    INT_DATA_FIELD_VALUE_ALL_USED_STATUS = 0x10001b5c       # Factory status of user data area

    # ---------------Event Section----------------------------------------
    ENUM_EVENT_SELECTOR = 0x30001f40                        # Event source select, Reference GxEventSelectorEntry
    ENUM_EVENT_NOTIFICATION = 0x30001f41                    # Switch of the notification to the host application of the occurrence of the selected Event.
    INT_EVENT_EXPOSURE_END = 0x10001f42                     # Exposure end event
    INT_EVENT_EXPOSURE_END_TIMESTAMP = 0x10001f43           # The timestamp of Exposure end event
    INT_EVENT_EXPOSURE_END_FRAME_ID = 0x10001f44            # The frame id of Exposure end event
    INT_EVENT_BLOCK_DISCARD = 0x10001f45                    # Block discard event
    INT_EVENT_BLOCK_DISCARD_TIMESTAMP = 0x10001f46          # The timestamp of Block discard event
    INT_EVENT_OVERRUN = 0x10001f47                          # Event queue overflow event
    INT_EVENT_OVERRUN_TIMESTAMP = 0x10001f48                # The timestamp of event queue overflow event
    INT_EVENT_FRAME_START_OVER_TRIGGER = 0x10001f49         # Trigger signal shield event
    INT_EVENT_FRAME_START_OVER_TRIGGER_TIMESTAMP = 0x10001f4a   # The timestamp of trigger signal shield event
    INT_EVENT_BLOCK_NOT_EMPTY = 0x10001f4b                  # Frame memory not empty event
    INT_EVENT_BLOCK_NOT_EMPTY_TIMESTAMP = 0x10001f4c        # The timestamp of frame memory not empty event
    INT_EVENT_INTERNAL_ERROR = 0x10001f4d                   # Internal erroneous event
    INT_EVENT_INTERNAL_ERROR_TIMESTAMP = 0x10001f4e         # The timestamp of internal erroneous event
    INT_EVENT_FRAMEBURSTSTART_OVERTRIGGER = 0x10001f4f      # Frame burst start overtrigger event ID
    INT_EVENT_FRAMEBURSTSTART_OVERTRIGGER_FRAMEID = 0x10001f50   # Frame burst start overtrigger event frame ID
    INT_EVENT_FRAMEBURSTSTART_OVERTRIGGER_TIMESTAMP = 0x10001f51 # Frame burst start overtrigger event timestamp
    INT_EVENT_FRAMESTART_WAIT = 0x10001f52                  # Frame start wait event ID
    INT_EVENT_FRAMESTART_WAIT_TIMESTAMP = 0x10001f53        # Frame start wait event timestamp
    INT_EVENT_FRAMEBURSTSTART_WAIT = 0x10001f54             # Frame burst start wait event ID
    INT_EVENT_FRAMEBURSTSTART_WAIT_TIMESTAMP = 0x10001f55   # Frame burst start wait event timestamp
    INT_EVENT_BLOCK_DISCARD_FRAMEID= 0x10001f56             # Data block discard event frame ID
    INT_EVENT_FRAMESTART_OVERTRIGGER_FRAMEID = 0x10001f57   # Frame start wait overtrigger event frame ID
    INT_EVENT_BLOCK_NOT_EMPTY_FRAMEID = 0x10001f58          # Data block not empty event frame ID
    INT_EVENT_FRAMESTART_WAIT_FRAMEID = 0x10001f59          # Frame start wait event frame ID
    INT_EVENT_FRAMEBURSTSTART_WAIT_FRAMEID = 0x10001f5a     # Frame burst start wait event frame ID
    ENUM_EVENT_SIMPLE_MODE = 0x30001f5b                     # event block ID enable

    # ---------------LUT Section------------------------------------------
    ENUM_LUT_SELECTOR = 0x30002328                          # Select lut, Reference GxLutSelectorEntry
    BUFFER_LUT_VALUE_ALL = 0x60002329                       # Lut data
    BOOL_LUT_ENABLE = 0x4000232a                            # Lut enable bit
    INT_LUT_INDEX = 0x1000232b                              # Lut index
    INT_LUT_VALUE = 0x1000232c                              # Lut value
    INT_LUT_FACTORY_STATUS = 0x1000232d                     # Lookup table factory status

    # ---------------ChunkData Section------------------------------------
    BOOL_CHUNK_MODE_ACTIVE = 0x40002711                     # Enable frame information
    ENUM_CHUNK_SELECTOR = 0x30002712                        # Select frame information channel, Reference GxChunkSelectorEntry
    BOOL_CHUNK_ENABLE = 0x40002713                          # Enable single frame information channel

    # ---------------Color Transformation Control-------------------------
    ENUM_COLOR_TRANSFORMATION_MODE = 0x30002af8             # Color transformation mode, Reference GxColorTransformationModeEntry
    BOOL_COLOR_TRANSFORMATION_ENABLE = 0x40002af9           # Color transformation enable bit
    ENUM_COLOR_TRANSFORMATION_VALUE_SELECTOR = 0x30002afa   # The selector of color transformation value, Reference GxColorTransformationValueSelectorEntry
    FLOAT_COLOR_TRANSFORMATION_VALUE = 0x20002afb           # The value of color transformation
    ENUM_SATURATION_MODE = 0x30002afc                       # Saturation switch
    INT_SATURATION = 0x10002afd                             # Saturation value

    # ---------------CounterAndTimerControl Section-----------------------
    ENUM_TIMER_SELECTOR = 0x30002ee0                        # Selects which Counter to configure, Refer to GxTimerSelectorEntry
    FLOAT_TIMER_DURATION = 0x20002ee1                       # Sets the duration (in microseconds) of the Timer pulse.
    FLOAT_TIMER_DELAY = 0x20002ee2                          # Sets the duration (in microseconds) of the delay to apply at the reception of a trigger before starting the Timer.
    ENUM_TIMER_TRIGGER_SOURCE = 0x30002ee3                  # Selects the source of the trigger to start the Timer, Refer to GxTimerTriggerSourceEntry
    ENUM_COUNTER_SELECTOR = 0x30002ee4                      # Selects which Counter to configure, Refer to GxCounterSelectorEntry
    ENUM_COUNTER_EVENT_SOURCE = 0x30002ee5                  # Select the events that will be the source to increment the Counter, Refer to GxCounterEventSourceEntry
    ENUM_COUNTER_RESET_SOURCE = 0x30002ee6                  # Selects the signals that will be the source to reset the Counter, Refer to GxCounterResetSourceEntry
    ENUM_COUNTER_RESET_ACTIVATION = 0x30002ee7              # Selects the Activation mode of the Counter Reset Source signal, Refer to GxCounterResetActivationEntry
    COMMAND_COUNTER_RESET = 0x70002ee8                      # Does a software reset of the selected Counter and starts it.
    ENUM_COUNTER_TRIGGER_SOURCE = 0x30002ee9                # Counter trigger source, Reference GxCounterTriggerSourceEntry
    INT_COUNTER_DURATION = 0x10002eea                       # Counter duration value
    ENUM_TIMER_TRIGGER_ACTIVATION = 0x30002eeb              # Timer Trigger Activation, reference GxTimerTriggerActivationEntry
    INT_COUNTER_VALUE = 0x10002eec                          # counter value

    # ---------------RemoveParameterLimitControl Section------------------
    ENUM_REMOVE_PARAMETER_LIMIT = 0x300032c8                # Remove paremeter range restriction switch

    # ---------------HDRControl Section-----------------------------------
    ENUM_HDR_MODE = 0x300036b0                              # HDR switch
    INT_HDR_TARGET_LONG_VALUE = 0x100036b1                  # Bright field expectations
    INT_HDR_TARGET_SHORT_VALUE = 0x100036b2                 # dark field expectations
    INT_HDR_TARGET_MAIN_VALUE = 0x100036b3                  # Convergence expectations

    # ---------------MultiGrayControl Section-----------------------------------
    ENUM_MGC_MODE = 0x30003a99                              # Multi-frame grey scale control mode
    INT_MGC_SELECTOR = 0x10003a9a                           # Multiframe grey color selection
    FLOAT_MGC_EXPOSURE_TIME = 0x20003a9b                    # Multi-frame grey time exposure time
    FLOAT_MGC_GAIN = 0x20003a9c                             # Multiframe grey gain

    # ---------------ImageQualityControl Section-----------------------------------
    BUFFER_STRIPED_CALIBRATION_INFO = 0x60003e81            # Fringe calibration information
    FLOAT_CONTRAST = 0x20003e82                             # Contrast
    ENUM_HOTPIXEL_CORRECTION = 0x30003e83                   # Hotpixel correction

    # ---------------GyroControl Section-----------------------------------
    BUFFER_IMU_DATA = 0x60004269                            # IMU data
    ENUM_IMU_CONFIG_ACC_RANGE = 0x3000426a                  # IMU config acc range
    ENUM_IMU_CONFIG_ACC_ODR_LOW_PASS_FILTER_SWITCH = 0x3000426b  # IMU config acc odr low pass filter switch
    ENUM_IMU_CONFIG_ACC_ODR = 0x3000426c                    # IMU config acc odr
    ENUM_IMU_CONFIG_ACC_ODR_LOW_PASS_FILTER_FREQUENCY = 0x3000426d  # imu config acc odr low pass filter frequency
    ENUM_IMU_CONFIG_GYRO_XRANGE = 0x3000426f                # imu config gyro Xrange
    ENUM_IMU_CONFIG_GYRO_YRANGE = 0x30004270                # imu config gyro Yrange
    ENUM_IMU_CONFIG_GYRO_ZRANGE = 0x30004271                # imu config gyro Zrange
    ENUM_IMU_CONFIG_GYRO_ODR_LOW_PASS_FILTER_SWITCH = 0x30004272  # imu config gyro odr low pass filter switch
    ENUM_IMU_CONFIG_GYRO_ODR = 0x30004273                   # imu config gyro odr
    ENUM_IMU_CONFIG_GYRO_ODR_LOW_PASS_FILTER_FREQUENCY = 0x30004274  # imu config gyro odr low pass filter frequency
    FLOAT_IMU_ROOM_TEMPERATURE = 0x20004275                 # imu room temperature
    ENUM_IMU_TEMPERATURE_ODR = 0x30004276                   # imu temperature odr

    # ---------------SerialPortControl Section-----------------------------------
    ENUM_SERIALPORT_SELECTOR = 0x30004a39                   # Serial port selection
    ENUM_SERIALPORT_SOURCE = 0x30004a3a                     # Serial port input source
    ENUM_SERIALPORT_BAUDRATE = 0x30004a3b                   # Serial baud rate
    INT_SERIALPORT_DATA_BITS = 0x10004a3c                   # Serial port data bit
    ENUM_SERIALPORT_STOP_BITS = 0x30004a3d                  # Serial port stop bit
    ENUM_SERIALPORT_PARITY = 0x30004a3e                     # Serial port parity
    INT_TRANSMIT_QUEUE_MAX_CHARACTER_COUNT = 0x10004a3f     # Maximum number of characters in transmission queue
    INT_TRANSMIT_QUEUE_CURRENT_CHARACTER_COUNT = 0x10004a40  # Current number of characters in the transmission queue
    INT_RECEIVE_QUEUE_MAX_CHARACTER_COUNT = 0x10004a41      # Maximum number of characters in receive queue
    INT_RECEIVE_QUEUE_CURRENT_CHARACTER_COUNT = 0x10004a42  # Current number of characters in the receive queue
    INT_RECEIVE_FRAMING_ERROR_COUNT = 0x10004a43            # Received frame error count
    INT_RECEIVE_PARITY_ERROR_COUNT = 0x10004a44             # Receive parity error count
    COMMAND_RECEIVE_QUEUE_CLEAR = 0x70004a45                # Queue Clear
    BUFFER_SERIALPORT_DATA = 0x60004a46                     # serial data
    INT_SERIALPORT_DATA_LENGTH = 0x10004a47                 # Serial port data length
    INT_SERIAL_PORT_DETECTION_STATUS = 0x10004a48           # Serial port status detection

    # ---------------CoaXPress Section-------------------------------------------
    ENUM_CXP_LINK_CONFIGURATION = 0x30004e21                # Connection configuration
    ENUM_CXP_LINK_CONFIGURATION_PREFERRED = 0x30004e22      # Preset connection configuration
    ENUM_CXP_LINK_CONFIGURATION_STATUS = 0x30004e23         # CXP connection configuration status
    INT_IMAGE1_STREAM_ID = 0x10004e24                       # First image flow ID
    ENUM_CXP_CONNECTION_SELECTOR = 0x30004e25               # Connection selection
    ENUM_CXP_CONNECTION_TEST_MODE = 0x30004e26              # Connection test mode
    INT_CXP_CONNECTION_TEST_ERROR_COUNT = 0x10004e27        # Connection test error count
    INT_CXP_CONNECTION_TEST_PACKET_RX_COUNT = 0x10004e28    # Number of connection test packets received
    INT_CXP_CONNECTION_TEST_PACKET_TX_COUNT = 0x10004e29    # Number of connection test packets sent

    # ---------------SequencerControl Section-----------------------------------
    ENUM_SEQUENCER_MODE = 0x30005209                        # Sequencer mode
    ENUM_SEQUENCER_CONFIGURATION_MODE = 0x3000520a          # Sequencer configuration mode
    ENUM_SEQUENCER_FEATURE_SELECTOR = 0x3000520b            # Sequencer function selector
    BOOL_SEQUENCER_FEATURE_ENABLE = 0x4000520c              # Sequencer function enabled
    INT_SEQUENCER_SET_SELECTOR = 0x1000520d                 # Sequencer setting selector
    INT_SEQUENCER_SET_COUNT = 0x1000520e                    # Sequencer count
    INT_SEQUENCER_SET_ACTIVE = 0x1000520f                   # Sequencer settings active
    COMMAND_SEQUENCER_SET_RESET = 0x70005210                # Sequencer setting reset
    INT_SEQUENCER_PATH_SELECTOR = 0x10005211                # Sequencer payh selection
    INT_SEQUENCER_SET_NEXT = 0x10005212                     # Sequencer Next
    ENUM_SEQUENCER_TRIGGER_SOURCE = 0x30005213              # Sequencer Trigger
    COMMAND_SEQUENCER_SET_SAVE = 0x70005214                 # Sequencer Save
    COMMAND_SEQUENCER_SET_LOAD = 0x70005215                 # Sequencer Load

    # ---------------EnoderControl Section--------------------------------------
    ENUM_ENCODER_SELECTOR = 0x300055f1                      # Encoder selector
    ENUM_ENCODER_DIRECTION = 0x300055f2                     # Encoder direction
    INT_ENCODER_VALUE = 0x100055f3                          # Decoder value
    ENUM_ENCODER_SOURCEA = 0x300055f4                       # Encoder phase A input
    ENUM_ENCODER_SOURCEB = 0x300055f5                       # Encoder phase B input
    ENUM_ENCODER_MODE = 0x300055f6                          # Encoder Mode

    # ---------------Device Feature---------------------------------------
    INT_COMMAND_TIMEOUT = 0x13000000                        # (Only GEVDevice)The time of command timeout
    INT_COMMAND_RETRY_COUNT = 0x13000001                    # (Only GEVDevice)Command retry times

    # ---------------DataStream Feature-----------------------------------
    INT_ANNOUNCED_BUFFER_COUNT = 0x14000000                 # The number of Buffer declarations
    INT_DELIVERED_FRAME_COUNT = 0x14000001                  # Number of received frames (including remnant frames)
    INT_LOST_FRAME_COUNT = 0x14000002                       # Number of lost frames caused by buffer deficiency
    INT_INCOMPLETE_FRAME_COUNT = 0x14000003                 # Number of residual frames received
    INT_DELIVERED_PACKET_COUNT = 0x14000004                 # The number of packets received
    INT_RESEND_PACKET_COUNT = 0x14000005                    # (Only GEVDevice)Number of retransmission packages
    INT_RESCUED_PACKET_COUNT = 0x14000006                   # (Only GEVDevice)Retransmission success package number
    INT_RESEND_COMMAND_COUNT = 0x14000007                   # (Only GEVDevice)Retransmission command times
    INT_UNEXPECTED_PACKET_COUNT = 0x14000008                # (Only GEVDevice)Exception packet number
    INT_MAX_PACKET_COUNT_IN_ONE_BLOCK = 0x14000009          # (Only GEVDevice)Data block maximum retransmission number
    INT_MAX_PACKET_COUNT_IN_ONE_COMMAND = 0x1400000a        # (Only GEVDevice)The maximum number of packets contained in one command
    INT_RESEND_TIMEOUT = 0x1400000b                         # (Only GEVDevice)Retransmission timeout time
    INT_MAX_WAIT_PACKET_COUNT = 0x1400000c                  # (Only GEVDevice)Maximum waiting packet number
    ENUM_RESEND_MODE = 0x3400000d                           # (Only GEVDevice)Retransmission mode switch
    INT_MISSING_BLOCK_ID_COUNT = 0x1400000e                 # (Only GEVDevice)BlockID lost number
    INT_BLOCK_TIMEOUT = 0x1400000f                          # (Only GEVDevice)Data block timeout time
    INT_STREAM_TRANSFER_SIZE = 0x14000010                   # (Only U3VDevice)Data block size
    INT_STREAM_TRANSFER_NUMBER_URB = 0x14000011             # (Only U3VDevice)Number of data blocks
    INT_MAX_NUM_QUEUE_BUFFER = 0x14000012                   # (Only GEVDevice)The maximum Buffer number of the collection queue
    INT_PACKET_TIMEOUT = 0x14000013                         # (Only GEVDevice)Packet timeout time
    INT_SOCKET_BUFFER_SIZE = 0x14000014                     # (Only GEVDevice)Socket buffer size in kilobytes
    ENUM_STOP_ACQUISITION_MODE = 0x34000015                 # (Only U3VDevice)Stop acquisition mode Reference GxStopAcquisitionModeEntry
    ENUM_STREAM_BUFFER_HANDLING_MODE = 0x34000016           # Buffer handling mode Reference GxDSStreamBufferHandlingModeEntry

    def __init__(self):
        pass


class GxDeviceIPInfo(Structure):
    _fields_ = [
        ('device_id', c_char * 68),         # The unique identifier of the device.
        ('mac', c_char * 32),               # MAC address
        ('ip', c_char * 32),                # IP address
        ('subnet_mask', c_char * 32),       # Subnet mask
        ('gateway', c_char * 32),           # Gateway
        ('nic_mac', c_char * 32),           # The MAC address of the corresponding NIC(Network Interface Card).
        ('nic_ip', c_char * 32),            # The IP of the corresponding NIC
        ('nic_subnet_mask', c_char * 32),   # The subnet mask of the corresponding NIC
        ('nic_gateWay', c_char * 32),       # The Gateway of the corresponding NIC
        ('nic_description', c_char * 132),  # The description of the corresponding NIC
        ('reserved', c_char * 512),         # Reserved 512 bytes
    ]

    def __str__(self):
        return "GxDeviceIPInfo\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)


class GxDeviceBaseInfo(Structure):
    _fields_ = [
        ('vendor_name', c_char*32),         # Vendor name
        ('model_name', c_char*32),          # TModel name
        ('serial_number', c_char*32),       # Serial number
        ('display_name', c_char*132),       # Display name
        ('device_id', c_char*68),           # The unique identifier of the device.
        ('user_id', c_char*68),             # User's custom name
        ('access_status', c_int),           # Access status that is currently supported by the device
                                            # Refer to GxAccessStatus
        ('device_class', c_int),            # Device type. Such as USB2.0, GEV.
        ('reserved', c_char*300),           # Reserved 300 bytes
    ]

    def __str__(self):
        return "GxDeviceBaseInfo\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)


class GxOpenParam(Structure):
    _fields_ = [
        ('content',             c_char_p),
        ('open_mode',           c_uint),
        ('access_mode',         c_uint),
    ]

    def __str__(self):
        return "GxOpenParam\n%s" % "\n".join( "%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)


# The data structure definitions for collection in Windows and Linux are different, so it is necessary to distinguish between them here.
if sys.platform != 'linux2' and sys.platform != 'linux':
    class GxFrameCallbackParam(Structure):
        _fields_ = [
            ('user_param_index',    c_void_p),      # User private data
            ('status',              c_int),         # The return state of the image
            ('image_buf',           c_void_p),      # Image buff address
            ('image_size',          c_int),         # Image data size, Including frame information
            ('width',               c_int),         # Image width
            ('height',              c_int),         # Image height
            ('pixel_format',        c_int),         # Image PixFormat
            ('frame_id',            c_ulonglong),   # The frame id of the image
            ('timestamp',           c_ulonglong),   # Time stamp of image
            ('reserved',            c_int),         # Reserved
        ]

        def __str__(self):
            return "GxFrameCallbackParam\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)


    class GxFrameData(Structure):
        _fields_ = [
            ('status', c_int),                      # The return state of the image
            ('image_buf', c_void_p),                # Image buff address
            ('width', c_int),                       # Image width
            ('height', c_int),                      # Image height
            ('pixel_format', c_int),                # Image PixFormat
            ('image_size', c_int),                  # Image data size, Including frame information
            ('frame_id', c_ulonglong),              # The frame id of the image
            ('timestamp', c_ulonglong),             # Time stamp of image
            ('user_param', c_void_p),               # User param
            ('reserved',  c_int),                   # Reserved

            ('buf_id', c_ulonglong),                # Image buff ID (for dq_buf)
        ]

        def __str__(self):
            return "GxFrameData\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)

    class GxFrameBuffer(ctypes.Structure):
        _fields_ = [
            ('frame_id', c_ulonglong),              # The frame id of the image
            ('timestamp', c_ulonglong),             # Time stamp of image
            ('buf_id', c_ulonglong),                # Image buff ID
            ('image_buf', c_ulonglong),                # Image buff address
            ('status', c_uint),                     # The return state of the image
            ('width', c_uint),                      # Image width
            ('height', c_uint),                     # Image height
            ('pixel_format', c_uint),               # Image PixFormat
            ('image_size', c_uint),                 # Image data size, Including frame information
            ('offset_x', c_uint),                   # X-direction offset of the image
            ('offset_y', c_uint),                   # Y-direction offset of the image
            ('user_param', c_void_p),               # User param
            ('reserved', c_uint),                   # Reserved
        ]

        def __str__(self):
            return "GxFrameBuffer\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)
else:
    class GxFrameCallbackParam(Structure):
        _fields_ = [
            ('user_param_index',    c_void_p),      # User private data
            ('status',              c_int),         # The return state of the image
            ('image_buf',           c_void_p),      # Image buff address
            ('image_size',          c_int),         # Image data size, Including frame information
            ('width',               c_int),         # Image width
            ('height',              c_int),         # Image height
            ('pixel_format',        c_int),         # Image PixFormat
            ('frame_id',            c_ulonglong),   # The frame id of the image
            ('timestamp',           c_ulonglong),   # Time stamp of image
            ('offset_x',            c_int),         # X-direction offset of the image
            ('offset_y',            c_int),         # Y-direction offset of the image
            ('reserved',            c_int),         # Reserved
        ]

        def __str__(self):
            return "GxFrameCallbackParam\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)


    class GxFrameData(Structure):
        _fields_ = [
            ('status',              c_int),         # The return state of the image
            ('image_buf',           c_void_p),      # Image buff address
            ('width',               c_int),         # Image width
            ('height',              c_int),         # Image height
            ('pixel_format',        c_int),         # Image PixFormat
            ('image_size',          c_int),         # Image data size, Including frame information
            ('frame_id',            c_ulonglong),   # The frame id of the image
            ('timestamp',           c_ulonglong),   # Time stamp of image
            ('offset_x',            c_int),         # X-direction offset of the image
            ('offset_y',            c_int),         # Y-direction offset of the image
            ('reserved',            c_int),         # Reserved
            # Reserved

            ('buf_id', c_ulonglong),                # Image buff ID (for dq_buf)
        ]

        def __str__(self):
            return "GxFrameData\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)

    class GxFrameBuffer(ctypes.Structure):
        _fields_ = [
            ('status',              c_uint),        # The return state of the image
            ('image_buf',           c_void_p),      # Image buff address
            ('width',               c_uint),        # Image width
            ('height',              c_uint),        # Image height
            ('pixel_format',        c_uint),        # Image PixFormat
            ('image_size',          c_uint),        # Image data size, Including frame information
            ('frame_id',            c_ulonglong),   # The frame id of the image
            ('timestamp',           c_ulonglong),   # Time stamp of image
            ('buf_id',              c_ulonglong),   # Image buff ID
            ('offset_x',            c_uint),        # X-direction offset of the image
            ('offset_y',            c_uint),        # Y-direction offset of the image
            ('user_param',          c_void_p),      # User param
            ('reserved', c_uint),                   # Reserved
        ]

        def __str__(self):
            return "GxFrameBuffer\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)

class GxIntFeatrue(Structure):
    _fields_ = [
        ('value', c_int64),
        ('min', c_int64),
        ('max', c_int64),
        ('inc', c_int64),
        ('reserved', c_int32*NODE_FEATURE_RESERVED_16),
    ]
    def __str__(self):
        return "GxIntFeatrue\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)

class GxEnumValue(Structure):
    _fields_ = [
        ('cur_value'    ,   c_int64),                   # Enumerate subkey values
        ('cur_symbolic' ,   c_char * 128),              # Enumeration sub item description
        ('reserved'     ,   c_int32 * 4),               # Reserved
    ]
    def __str__(self):
        return "GxEnumValue\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)

class GxEnumFeatrue( Structure):
    _fields_ = [
        ('cur_value'        ,   GxEnumValue),           # Current enumeration value
        ('supported_number' ,   c_int64),               # Number of enumerated subitems
        ('supported_value'  ,   GxEnumValue * 128),     # Info of enumerated subitems
        ('reserved'         ,   c_int32 * 16),          # Reserved
    ]
    def __str__(self):
        return "GxEnumFeatrue\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)

class GxFloatFeature( Structure):
    _fields_ = [
        ('cur_value'        ,   c_double),               # Float feature current value
        ('min'              ,   c_double),               # Floating point minimum
        ('max'              ,   c_double),               # Floating point max
        ('inc'              ,   c_double),               # Floating point step size
        ('inc_is_valid'     ,   c_bool),                # Whether the floating point step size is valid
        ('unit'             ,   c_char * 8),            # Floating point units
        ('reserved'         ,   c_int32 * 16),          # Reserved
    ]
    def __str__(self):
        return "GxFloatFeature\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)

class GxStringFeature( Structure):
    _fields_ = [
        ('cur_value'    , c_char * 256),        # String feature current value
        ('max_length'   , c_int64),             # String feature max length
        ('reserved'     , c_int32 * 4),         # Reserved
    ]
    def __str__(self):
        return "GxStringFeature\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)

class GxRegisterStackEntry(Structure):
     _fields_ = [
         ('address',            c_ulonglong),     #Address of the register
         ('buffer',             c_void_p),       #Pointer to the buffer containing the data
         ('size',               c_uint),         #Number of bytes to read
     ]

     def __str__(self):
         return "GxRegisterStackEntry\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)

# The following structures have been abandoned
class GxIntRange(Structure):
    _fields_ = [
        ('min',                 c_ulonglong),
        ('max',                 c_ulonglong),
        ('inc',                 c_ulonglong),
        ('reserved',            c_int * 8),
    ]

    def __str__(self):
        return "GxIntRange\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)


class GxFloatRange(Structure):
    _fields_ = [
        ('min',                 c_double),
        ('max',                 c_double),
        ('inc',                 c_double),
        ('unit',                c_char * 8),
        ('inc_is_valid',        c_bool),
        ('reserved',            c_char * 31),
    ]

    def __str__(self):
        return "GxFloatRange\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)


class GxEnumDescription(Structure):
    _fields_ = [
        ('value',               c_longlong),    # Enum value
        ('symbolic',            c_char * 64),   # Character description
        ('reserved',            c_int * 8),
    ]

    def __str__(self):
        return "GxEnumDescription\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)

class GxRegisterStackEntry(Structure):
     _fields_ = [
         ('address',            c_ulonglong),     #Address of the register
         ('buffer',             c_void_p),       #Pointer to the buffer containing the data
         ('size',               c_uint),         #Number of bytes to read
     ]

     def __str__(self):
         return "GxRegisterStackEntry\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)

class GxActionCommandResult(Structure):
    _fields_ = [
        ('device_ip', c_char * 16),  # ip of device
        ('status', c_int32),  # status of ack
    ]

    def __str__(self):
        return "GxActionCommandResult\n%s" % "\n".join("%s:\t%s" % (n, getattr(self, n[0])) for n in self._fields_)


if hasattr(dll, 'GXSetLogType'):
    def gx_set_log_type(log_type):
        """
        :brief      Set whether logs of the specified type can be sent
        :param      log_type:           log type,See detail in GxLogTypeList
                                        Type: Int
        :return:    status:             State return value, See detail in GxStatusList
        """
        log_type_c = c_uint()
        log_type_c.value = log_type

        status = dll.GXSetLogType(log_type)

        return status

if hasattr(dll, 'GXGetLogType'):
    def gx_get_log_type():
        """
        :brief      Gets whether logs of a specified type can be sent
        :param      log_type:           log type,See detail in GxLogTypeList
                                        Type: Int
        :return:    status:             State return value, See detail in GxStatusList
        """
        log_type_c = c_uint()

        status = dll.GXGetLogType(byref(log_type_c))

        return status,log_type_c.value

if hasattr(dll, 'GXInitLib'):
    def gx_init_lib():
        """
        :brief      Initialize the device library for some resource application operations
        :return:    None
        """
        return dll.GXInitLib()


if hasattr(dll, 'GXCloseLib'):
    def gx_close_lib():
        """
        :brief      Close the device library to release resources.
        :return:    None
        """
        return dll.GXCloseLib()


if hasattr(dll, 'GXGetLastError'):
    def gx_get_last_error(size=1024):
        """
        :brief      To get the latest error descriptions information of the program
        :param      size:           string buff length(size=1024)
                                    Type: Int, Minnum: 0
        :return:    status:         State return value, See detail in GxStatusList
                    err_code:       Return the last error code
                    err_content:    the latest error descriptions information of the program
        """
        err_code = c_int()
        err_content_buff = create_string_buffer(size)

        content_size = c_size_t()
        content_size.value = size

        status = dll.GXGetLastError(byref(err_code), byref(err_content_buff), byref(content_size))
        err_content = string_at(err_content_buff, content_size.value-1)

        return status, err_code.value, string_decoding(err_content)


if hasattr(dll, 'GXUpdateDeviceList'):
    def gx_update_device_list(time_out=200):
        """
        :brief      Enumerating currently all available devices in subnet and gets the number of devices.
        :param      time_out:           The timeout time of enumeration (unit: ms).
                                        Type: Int, Minimum:0
        :return:    status:             State return value, See detail in GxStatusList
                    device_num:         The number of devices
        """
        time_out_c = c_uint()
        time_out_c.value = time_out

        device_num = c_uint()
        status = dll.GXUpdateDeviceList(byref(device_num), time_out_c)
        return status, device_num.value


if hasattr(dll, 'GXUpdateAllDeviceList'):
    def gx_update_all_device_list(time_out=200):
        """
        :brief      Enumerating currently all available devices in entire network and gets the number of devices
        :param      time_out:           The timeout time of enumeration (unit: ms).
                                        Type: Int, Minimum: 0
        :return:    status:             State return value, See detail in GxStatusList
                    device_num:         The number of devices
        """
        time_out_c = c_uint()
        time_out_c.value = time_out

        device_num = c_uint()
        status = dll.GXUpdateAllDeviceList(byref(device_num), time_out_c)
        return status, device_num.value

if hasattr(dll, 'GXUpdateAllDeviceListEx'):
    def gx_update_device_list_ex(device_type,time_out=2000):
        """
        :brief      Enumerating all available ntype type devices.
        :param      ntype:              enumerat ntype type device
        :param      time_out:           The timeout time of enumeration (unit: ms).
                                        Type: Int, Minimum:0
        :return:    status:             State return value, See detail in GxStatusList
                    device_num:         The number of devices
        """
        device_type_c = c_uint()
        device_type_c.value = device_type

        time_out_c = c_uint()
        time_out_c.value = time_out

        device_num = c_uint()
        status = dll.GXUpdateAllDeviceListEx(device_type_c, byref(device_num), time_out_c)
        return status, device_num.value

if hasattr(dll, 'GXGetInterfaceNum'):
    def gx_get_interface_number():
        """
        :brief      To get the basic information of all the devices
        :return:    status:             State return value, See detail in GxStatusList
                    interface_number_c:     The interface number
        """
        interface_number_c = c_size_t()
        status = dll.GXGetInterfaceNum(byref(interface_number_c))
        return status, interface_number_c.value

if hasattr(dll, 'GXGetInterfaceInfo'):
    def gx_get_interface_info(interface_num):
        """
        :brief      To get the basic information of all the devices
        :param      interface_num:      The number of interface
                                        Type: Int, Minimum: 0
        :return:    status:             State return value, See detail in GxStatusList
                    device_ip_info:     The structure pointer of the device information(GxDeviceIPInfo)
        """
        interface_info = GXInterfaceInfo()

        buf_size_c = c_size_t()
        buf_size_c.value = interface_num

        status = dll.GXGetInterfaceInfo(buf_size_c,byref(interface_info))
        return status, interface_info

if hasattr(dll, 'GXGetInterfaceHandle'):
    def gx_get_interface_handle(interface_num):
        """
        :brief      To get the basic information of all the devices
        :param      interface_num:      The number of interface
                                        Type: Int, Minimum: 0
        :return:    status:             State return value, See detail in GxStatusList
                    handle_size_c:      The interface handle
        """
        index_c = c_uint()
        index_c.value = interface_num

        handle_size_c = c_void_p()

        status = dll.GXGetInterfaceHandle(index_c, byref(handle_size_c))
        return status, handle_size_c.value

if hasattr(dll, 'GXGetAllDeviceBaseInfo'):
    def gx_get_all_device_base_info(devices_num):
        """
        :brief      To get the basic information of all the devices
        :param      devices_num:        The number of devices
                                        Type: Int, Minimum: 0
        :return:    status:             State return value, See detail in GxStatusList
                    device_ip_info:     The structure pointer of the device information(GxDeviceIPInfo)
        """
        devices_info = (GxDeviceBaseInfo * devices_num)()

        buf_size_c = c_size_t()
        buf_size_c.value = sizeof(GxDeviceBaseInfo) * devices_num

        status = dll.GXGetAllDeviceBaseInfo(byref(devices_info), byref(buf_size_c))
        return status, devices_info
        

if hasattr(dll, 'GXGetDeviceIPInfo'):
    def gx_get_device_ip_info(index):
        """
        :brief      To get the network information of the device.
        :param      index:              Device index
                                        Type: Int, Minimum: 1
        :return:    status:             State return value, See detail in GxStatusList
                    device_ip_info:     The structure pointer of the device information(GxDeviceIPInfo)
        """
        index_c = c_uint()
        index_c.value = index

        device_ip_info = GxDeviceIPInfo()
        status = dll.GXGetDeviceIPInfo(index_c, byref(device_ip_info))

        return status, device_ip_info


if hasattr(dll, 'GXOpenDeviceByIndex'):
    def gx_open_device_by_index(index):
        """
        :brief      Open the device by a specific Index(1, 2, 3, ...)
        :param      index:          Device index
                                    Type: Int, Minimum: 1
        :return:    status:         State return value, See detail in GxStatusList
                    handle:         The device handle returned by the interface
        """
        index_c = c_uint()
        index_c.value = index

        handle_c = c_void_p()
        status = dll.GXOpenDeviceByIndex(index_c, byref(handle_c))
        return status, handle_c.value


if hasattr(dll, 'GXOpenDevice'):
    def gx_open_device(open_param):
        """
        :brief      Open the device by a specific unique identification, such as: SN, IP, MAC, Index etc.
        :param      open_param:     The open device parameter which is configurated by the user.
                                    Type: GxOpenParam
        :return:    status:         State return value, See detail in GxStatusList
                    handle:         The device handle returned by the interface
        """
        handle = c_void_p()
        status = dll.GXOpenDevice(byref(open_param), byref(handle))
        return status, handle.value


if hasattr(dll, 'GXCloseDevice'):
    def gx_close_device(handle):
        """
        :brief      Specify the device handle to close the device
        :param      handle:     The device handle that the user specified to close.
                                Type: Long, Greater than 0
        :return:    status:     State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        status = dll.GXCloseDevice(handle_c)
        return status


if hasattr(dll, 'GXGetParentInterfaceFromDev'):
    def gx_get_parent_interface_from_device(handle):
        """
        :brief      Specify the device handle to close the device
        :param      handle:     The device handle that the user specified to close.
                                Type: Long, Greater than 0
        :return:    status:     State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        interface_handle_c = c_void_p()

        status = dll.GXGetParentInterfaceFromDev(handle_c, byref(interface_handle_c))
        return status, interface_handle_c.value


if hasattr(dll, 'GXGetLocalDeviceHandleFromDev'):
    def gx_local_device_handle_from_device(handle):
        """
        :brief      Get device local layer handle
        :param      handle:     The device handle
        :return:    status:     State return value, See detail in GxStatusList
                                device local layer handle
        """
        handle_c = c_void_p()
        handle_c.value = handle

        local_device_handle_c = c_void_p()

        status = dll.GXGetLocalDeviceHandleFromDev(handle_c, byref(local_device_handle_c))
        return status, local_device_handle_c.value


if hasattr(dll, 'GXGetDataStreamNumFromDev'):
    def gx_data_stream_number_from_device(handle):
        """
        :brief      Get device stream number
        :param      handle:     The device handle that the user specified to get stream number.
                                Type: Long, Greater than 0
        :return:    status:     State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        stream_number = c_uint32()

        status = dll.GXGetDataStreamNumFromDev(handle_c, byref( stream_number))
        return status,stream_number.value


if hasattr(dll, 'GXGetPayLoadSize'):
    def gx_get_payload_size(handle):
        """
        :brief      Get device stream payload size
        :param      handle:     The device stream layer payload size
        :return:    status:     State return value, See detail in GxStatusList
                                stream payload size
        """
        handle_c = c_void_p()
        handle_c.value = handle

        stream_payload_size = c_uint32()

        status = dll.GXGetPayLoadSize(handle_c, byref( stream_payload_size))
        return status,stream_payload_size.value


if hasattr(dll, 'GXGetDataStreamHandleFromDev'):
    def gx_get_data_stream_handle_from_device(handle,stream_index):
        """
        :brief      Get device stream handle
        :param      handle:     The device handle that the user specified to get stream number.
                                Type: Long, Greater than 0
        :param      stream_index:stream index.
        :return:    status:     State return value, See detail in GxStatusList
                                stream handle
        """
        handle_c = c_void_p()
        handle_c.value = handle
        stream_number = c_uint32()
        stream_number.value = stream_index
        stream_handle_c = c_void_p()

        status = dll.GXGetDataStreamHandleFromDev(handle_c, stream_number, byref(stream_handle_c))
        return status, stream_handle_c.value


if hasattr(dll, 'GXFeatureSave'):
    def gx_feature_save(handle,file_path):
        """
        :brief      Save the current handle parameter of the camera to the configuration file.
        :param      handle:     The handle of the device feature each layer
                                Type: Long, Greater than 0
        :return:    status:     State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle
        file_path_c = create_string_buffer(string_encoding(file_path))

        status = dll.GXFeatureSave(handle_c, file_path_c)
        return status


if hasattr(dll, 'GXFeatureLoad'):
    def gx_feature_load(handle, file_path, b_verify):
        """
        :brief      Load the configuration file for the camera
        :param      handle:     The handle of the device feature each layer
                                Type: Long, Greater than 0
        :param      file_path:  The path that load user parameter group.
                                Type: char*
        :return:    status:     State return value
        """
        handle_c = c_void_p()
        handle_c.value = handle

        file_path_c = create_string_buffer(string_encoding(file_path))

        b_verify_c = c_bool()
        b_verify_c.value = b_verify

        status = dll.GXFeatureLoad(handle_c,file_path,b_verify_c)
        return status


if hasattr(dll, 'GXGetNodeAccessMode'):
    def gx_get_node_access_mode(handle, feature_name):
        """
        :brief      To get the access information of the feature node
        :param      handle:         The handle that the device each layer
                                    Type: Long, Greater than 0
        :param      feature_name:   The feature_name that node feature name.
                                    Type: char*
        :return:    status:         State return value
                                    feature node access mode
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_name_c = create_string_buffer(string_encoding(feature_name))

        node_access_mode_c = c_int()
        node_access_mode_c.value = GxNodeAccessMode.MODE_UNDEF

        status = dll.GXGetNodeAccessMode(handle_c, feature_name_c, byref(node_access_mode_c))
        return status,node_access_mode_c.value


if hasattr(dll, 'GXGetIntValue'):
    def gx_get_int_feature(handle, feature_name):
        """
        :brief      Get int type feature value
        :param      handle:     The handle of the device each layer.
                                Type: Long, Greater than 0
        :param      feature_name:The feature node name.
                                Type: char*
        :return:    status:     State return value
                                int feature info
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_name_c = create_string_buffer(string_encoding(feature_name))

        int_feature_c = GxIntFeatrue()

        status = dll.GXGetIntValue(handle_c,feature_name_c, byref(int_feature_c))
        return status,int_feature_c


if hasattr(dll, 'GXSetIntValue'):
    def gx_set_int_feature_value(handle, feature_name, feature_value):
        """
        :brief      Set int type feature value
        :param      handle:     TThe handle of the device each layer.
                                Type: Long, Greater than 0
        :param      feature_name:The feature node name.
                                Type: char*
        :param      featrue_value:The feature node value.
                                Type: int
        :return:    status:     State return value
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_name_c = create_string_buffer(string_encoding(feature_name))

        feature_value_c = c_int64()
        feature_value_c.value = feature_value

        status = dll.GXSetIntValue(handle_c,feature_name_c, feature_value_c)
        return status


if hasattr(dll, 'GXGetEnumValue'):
    def gx_get_enum_feature(handle, feature_name):
        """
        :brief      Get enum type feature info
        :param      handle:     The handle of the device each layer.
                                Type: Long, Greater than 0
        :param      feature_name:The feature node name.
                                Type: char*
        :return:    status:     State return value
                                enum info
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_name_c = create_string_buffer(string_encoding(feature_name))

        enum_feature_c = GxEnumFeatrue()

        status = dll.GXGetEnumValue(handle_c,feature_name_c, byref(enum_feature_c))
        return status,enum_feature_c


if hasattr(dll, 'GXSetEnumValue'):
    def gx_set_enum_feature_value(handle, feature_name, featue_value):
        """
        :brief      Set enum type feature value
        :param      handle:     The handle of the device each layer.
                                Type: Long, Greater than 0
        :param      feature_name:The feature node name.
                                Type: char*
        :param      featrue_value:The feature node value.
                                Type: string
        :return:    status:     State return value
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_name_c = create_string_buffer(string_encoding(feature_name))

        featue_value_c = c_int64()
        featue_value_c.value = featue_value

        status = dll.GXSetEnumValue(handle_c,feature_name_c, featue_value_c)
        return status


if hasattr(dll, 'GXSetEnumValueByString'):
    def gx_set_enum_feature_value_string(handle, feature_name, feature_value):
        """
        :brief      Set enum type feature value
        :param      handle:     The handle of the device each layer.
                                Type: Long, Greater than 0
        :param      feature_name:The feature node name.
                                Type: char*
        :param      featrue_value:The feature node value.
                                Type: string
        :return:    status:     State return value
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_name_c = create_string_buffer(string_encoding(feature_name))
        feature_value_c = create_string_buffer( string_encoding( feature_value))

        status = dll.GXSetEnumValueByString(handle_c,feature_name_c, feature_value_c)
        return status


if hasattr(dll, 'GXGetFloatValue'):
    def gx_get_float_feature(handle, feature_name):
        """
        :brief      Get float type feature value
        :param      handle:     The handle of the device each layer.
                                Type: Long, Greater than 0
        :param      feature_name:The feature node name.
                                Type: char*
        :return:    status:     State return value
                                float value
        """
        handle_c = c_void_p()
        handle_c.value = handle
        feature_name_c = create_string_buffer(string_encoding(feature_name))
        float_feature_c = GxFloatFeature()

        status = dll.GXGetFloatValue(handle_c,feature_name_c, byref(float_feature_c))
        return status,float_feature_c


if hasattr(dll, 'GXSetFloatValue'):
    def gx_set_float_feature_value(handle, feature_name, featue_value):
        """
        :brief      Set float type feature value
        :param      handle:     The handle of the device each layer.
                                Type: Long, Greater than 0
        :param      feature_name:The feature node name.
                                Type: char*
        :param      featrue_value:The feature node value.
                                Type: float
        :return:    status:     State return value
        """
        handle_c = c_void_p()
        handle_c.value = handle
        feature_name_c = create_string_buffer(string_encoding(feature_name))
        featue_value_c = c_double()
        featue_value_c.value = featue_value

        status = dll.GXSetFloatValue(handle_c,feature_name_c, featue_value_c)
        return status


if hasattr(dll, 'GXGetBoolValue'):
    def gx_get_bool_feature(handle, feature_name):
        """
        :brief      Get bool type feature value
        :param      handle:     The handle of the device each layer.
                                Type: Long, Greater than 0
        :param      feature_name:The feature node name.
                                Type: char*
        :return:    status:     State return value
                                bool value
        """
        handle_c = c_void_p()
        handle_c.value = handle
        feature_name_c = create_string_buffer(string_encoding(feature_name))
        bool_feature_c = c_bool()

        status = dll.GXGetBoolValue(handle_c,feature_name_c, byref(bool_feature_c))
        return status,bool_feature_c.value


if hasattr(dll, 'GXSetBoolValue'):
    def gx_set_bool_feature_value(handle, feature_name, featue_value):
        """
        :brief      Set bool type feature value
        :param      handle:     The handle of the device each layer.
                                Type: Long, Greater than 0
        :param      feature_name:The feature node name.
                                Type: char*
        :param      featue_value:The feature node value.
                                Type: bool
        :return:    status:     State return value
        """
        handle_c = c_void_p()
        handle_c.value = handle
        feature_name_c = create_string_buffer(string_encoding(feature_name))
        featue_value_c = c_bool()
        featue_value_c.value = featue_value

        status = dll.GXSetBoolValue(handle_c,feature_name_c, featue_value)
        return status


if hasattr(dll, 'GXGetStringValue'):
    def gx_get_string_feature(handle, feature_name):
        """
        :brief      Get string type feature info
        :param      handle:     The handle of the device each layer.
                                Type: Long, Greater than 0
        :param      feature_name:The feature node name.
                                Type: char*
        :return:    status:     State return value
                                string info
        """
        handle_c = c_void_p()
        handle_c.value = handle
        feature_name_c = create_string_buffer(string_encoding(feature_name))
        string_feature_c = GxStringFeature()

        status = dll.GXGetStringValue(handle_c,feature_name_c, byref(string_feature_c))
        return status,string_feature_c


if hasattr(dll, 'GXSetStringValue'):
    def gx_set_string_feature_value(handle, feature_name, featue_value):
        """
        :brief      Set string type feature value
        :param      handle:     The handle of the device each layer.
                                Type: Long, Greater than 0
        :param      feature_name:The feature node name.
                                Type: char*
        :param      featue_value:The feature node value.
                                Type: char*
        :return:    status:     State return value
        """
        handle_c = c_void_p()
        handle_c.value = handle
        feature_name_c = create_string_buffer(string_encoding( feature_name))
        featue_value_c = create_string_buffer( string_encoding( featue_value))

        status = dll.GXSetStringValue(handle_c,feature_name_c, featue_value_c)
        return status


if hasattr(dll, 'GXSetCommandValue'):
    def gx_feature_send_command(handle, feature_name):
        """
        :brief      Send the command
        :param      handle:     The handle of the device each layer.
                                Type: Long, Greater than 0
        :param      feature_name:The feature node name.
                                Type: char*
        :return:    status:     State return value
        """
        handle_c = c_void_p()
        handle_c.value = handle
        feature_name_c = create_string_buffer(string_encoding(feature_name))

        status = dll.GXSetCommandValue(handle_c,feature_name_c)
        return status


if hasattr(dll, 'GXGetRegisterLength'):
    def gx_get_register_feature_length(handle, feature_name):
        """
        :brief      Get register type feature length
        :param      handle:     The handle of the device each layer.
                                Type: Long, Greater than 0
        :param      feature_name:The feature node name.
                                Type: char*
        :return:    status:     State return value
                                Feature length
        """
        handle_c = c_void_p()
        handle_c.value = handle
        feature_name_c = create_string_buffer(string_encoding(feature_name))
        featue_value_c = c_size_t()

        status = dll.GXGetRegisterLength(handle_c,feature_name_c, byref(featue_value_c))
        return status,featue_value_c.value


if hasattr(dll, 'GXGetRegisterValue'):
    def gx_get_register_feature_value(handle, feature_name):
        """
        :brief      Specify the device handle to close the device
        :param      handle:     The handle of the device each layer.
                                Type: Long, Greater than 0
        :param      feature_name:The feature name.
                                Type: char*
        :return:    status:     State return value, See detail in GxStatusList
                                Buffer data
        """
        handle_c = c_void_p()
        handle_c.value = handle
        feature_name_c = create_string_buffer(string_encoding(feature_name))

        feature_size_c = c_size_t()
        status = dll.GXGetRegisterValue( handle_c, feature_name_c, None, byref( feature_size_c))

        buff_c = (c_ubyte * feature_size_c.value)()

        status = dll.GXGetRegisterValue(handle_c,feature_name_c, byref(buff_c), byref(feature_size_c))
        return status,buff_c


if hasattr(dll, 'GXSetRegisterValue'):
    def gx_set_register_feature_value(handle, feature_name, buff, buff_size):
        """
        :brief      Specify the device handle to close the device
        :param      handle:     The handle of the device each layer.
                                Type: Long, Greater than 0
        :param      feature_name: feature node name
                                Type: char*
        :param      buff:       Set user data
                                Type: buffer*
        :param      buff_size:  User data size
                                Type: size_t*
        :return:    status:     State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle
        feature_name_c = create_string_buffer(string_encoding(feature_name))

        featue_value_c = c_int64()
        featue_value_c.value = buff_size

        status = dll.GXSetRegisterValue(handle_c,feature_name_c, buff, featue_value_c)
        return status


if hasattr(dll, 'GXFeatureLoad'):
    def gx_feature_load(handle, file_path, verify):
        """
        :brief      Specify the device handle to close the device
        :param      handle:     The handle of the device each layer.
                                Type: Long, Greater than 0
        :param      file_path:  The path that load user parameter group.
                                Type: char*
        :return:    status:     State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle
        file_path_c = create_string_buffer(string_encoding(file_path))
        verify_c = c_bool()
        verify_c.value = verify

        status = dll.GXFeatureLoad(handle_c,file_path_c, verify_c)
        return status


if hasattr(dll, 'GXFeatureSave'):
    def gx_feature_save(handle, file_path):
        """
        :brief      Specify the device handle to close the device
        :param      handle:     The handle of the device each layer.
                                Type: Long, Greater than 0
        :param      file_path:  The path that load user parameter group.
                                Type: char*
        :return:    status:     State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle
        file_path_c = create_string_buffer(string_encoding(file_path))

        status = dll.GXFeatureSave(handle_c,file_path_c)
        return status


if hasattr(dll, 'GXReadPort'):
    def gx_read_port(handle, address, size):
        """
        :brief      Read data for user specified register.
        :param      handle:     The handle of the device each layer.
                                Type: Long, Greater than 0
        :param      address:    Register address
                                Type: ulonglong
        :param      buff:       Output data buff
                                Type: int*
        :param      size:       User data size
                                Type: char*
        :return:    status:     State return value, See detail in GxStatusList
                    size:       Returns the length of the actual read register
        """
        handle_c = c_void_p()
        handle_c.value = handle

        address_c = c_ulonglong()
        address_c.value = address

        buff_c = c_int()

        size_c = c_uint()
        size_c.value = size

        status = dll.GXReadPort(handle_c,address_c, byref( buff_c), byref( size_c))
        return status, buff_c.value


if hasattr(dll, 'GXWritePort'):
    def gx_writer_port(handle, address, buff, size):
        """
        :brief      Writes user specified data to a user specified register.
        :param      handle:     The handle of the device each layer.
                                Type: Long, Greater than 0
        :param      address:    Register address
                                Type: ulonglong
        :param      buff:       User data
                                Type: int*
        :param      size:       User data size
                                Type: char*
        :return:    status:     State return value
        """
        handle_c = c_void_p()
        handle_c.value = handle

        address_c = c_ulonglong()
        address_c.value = address

        size_c = c_uint()
        size_c.value = size

        buff_c = c_int()
        buff_c.value = buff

        status = dll.GXWritePort(handle_c, address_c, byref(buff_c), byref(size_c))
        return status


if hasattr(dll, 'GXReadPortStacked'):
    def gx_read_port_stacked(handle, entries, size):
        """
        :brief      Batch reads the value of the user-specified register (Registers with command values of 4 bytes only)
        :param      handle:     The handle of the device each layer.
                                Type: Long, Greater than 0
        :param      entries:    [in]Batch read register addresses and values
                                [out]Read the data to the corresponding register
                                Type: void*
        :param      size:       [in]Read the number of device registers
                                [out]The number of registers that were successfully read
                                Type: size_t*
        :return:    status:     State return value
        """
        handle_c = c_void_p()
        handle_c.value = handle

        size_c = c_uint()
        size_c.value = size

        status = dll.GXReadPortStacked(handle_c,entries, byref(size_c))
        return status


if hasattr(dll, 'GXWritePortStacked'):
    def gx_writer_port_stacked(handle, entries, size):
        """
        :brief      Batch reads the value of the user-specified register (Registers with command values of 4 bytes only)
        :param      handle:     [in]The handle of the device each layer.
                                Type: Long, Greater than 0
        :param      entries:    [in]The address and value of the batch write register
                                Type: void*
        :param      size:       [in]Sets the number of device registers
                                [out]The number of registers that were successfully written
                                Type: size_t*
        :return:    status:     State return value
        """
        handle_c = c_void_p()
        handle_c.value = handle

        size_c = c_uint()
        size_c.value = size

        status = dll.GXWritePortStacked(handle_c,entries, byref(size_c))
        return status


FEATURE_CALL_CHAR = CFUNCTYPE(None, c_char_p, py_object)
if hasattr(dll, 'GXRegisterFeatureCallbackByString'):
    def gx_register_feature_call_back_by_string(handle, call_back, feature_name, args):
        """
        :brief      Specify the device handle to close the device
        :param      handle:     The handle of the device each layer.
                                Type: Long, Greater than 0
        :param      file_path:  The path that load user parameter group.
                                Type: char*
        :return:    status:     State return value
                                call back handle object
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_name_c = create_string_buffer(string_encoding(feature_name))

        call_back_handle = c_void_p()

        status = dll.GXRegisterFeatureCallbackByString(handle_c, ctypes.py_object(args), call_back, feature_name_c, byref(call_back_handle))
        return status, call_back_handle.value


if hasattr(dll, 'GXUnregisterFeatureCallbackByString'):
    def gx_unregister_feature_call_back_by_string(handle, feature_name, call_back_handle):
        """
        :brief      Specify the device handle to close the device
        :param      handle:     The handle of the device each layer.
                                Type: Long, Greater than 0
        :param      feature_name:  The feature name of the device each layer.
                                Type: char*
        :return:    status:     State return value
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_name_c = create_string_buffer(string_encoding(feature_name))

        call_back_handle_c = c_void_p()
        call_back_handle_c.value = call_back_handle

        status = dll.GXUnregisterFeatureCallbackByString(handle_c, feature_name_c, call_back_handle_c)
        return status


if hasattr(dll, 'GXRegisterBuffer'):
    def gx_register_buffer(handle, user_buf, user_param):
        """
        :brief      Register extern capture buffer
        :param      handle:         The handle of the device each layer.
        :param      user_buf:       User alloc buffer.
        :param      user_param:     User parameter.
        :return:    status:         State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        address_of_buffer = ctypes.addressof(user_buf)
        size_of_buffer = len(user_buf)

        status = dll.GXRegisterBuffer(handle_c, ctypes.cast(address_of_buffer, ctypes.c_void_p),
                                      ctypes.c_size_t(size_of_buffer), ctypes.py_object(user_param))
        return status


if hasattr(dll, 'GXUnRegisterBuffer'):
    def gx_unregister_buffer(handle, user_buf):
        """
        :brief      UnRegister extern capture buffer
        :param      handle:         The handle of the device each layer.
        :param      user_buf:       User alloc buffer.
        :return:    status:         State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        address_of_buffer = ctypes.addressof(user_buf)

        status = dll.GXUnRegisterBuffer(handle_c, ctypes.cast(address_of_buffer, ctypes.c_void_p))
        return status

if hasattr(dll, 'GXGetDevicePersistentIpAddress'):
    def gx_get_device_persistent_ip_address(handle, ip_length=16, subnet_mask_length=16, default_gateway_length=16):
        """
        :brief      Get the persistent IP information of the device
        :param      handle:                 The handle of the device
        :param      ip_length:              The character string length of the device persistent IP address.
        :param      subnet_mask_length:     The character string length of the device persistent subnet mask.
        :param      default_gateway_length: The character string length of the device persistent gateway
        :return:    status:                 State return value, See detail in GxStatusList
                    ip:                     The device persistent IP address(str)
                    subnet_mask:            The device persistent subnet mask(str)
                    default_gateway:        The device persistent gateway
        """
        handle_c = c_void_p()
        handle_c.value = handle

        ip_length_c = c_uint()
        ip_length_c.value = ip_length
        ip_c = create_string_buffer(ip_length)

        subnet_mask_length_c = c_uint()
        subnet_mask_length_c.value = subnet_mask_length
        subnet_mask_c = create_string_buffer(subnet_mask_length)

        default_gateway_length_c = c_uint()
        default_gateway_length_c.value = default_gateway_length
        default_gateway_c = create_string_buffer(default_gateway_length)

        status = dll.GXGetDevicePersistentIpAddress(handle_c, byref(ip_c), byref(ip_length_c),
                                                    byref(subnet_mask_c), byref(subnet_mask_length_c),
                                                    byref(default_gateway_c), byref(default_gateway_length_c))

        ip = string_at(ip_c, ip_length_c.value-1)
        subnet_mask = string_at(subnet_mask_c, subnet_mask_length_c.value-1)
        default_gateway = string_at(default_gateway_c, default_gateway_length_c.value-1)

        return status, string_decoding(ip), string_decoding(subnet_mask), string_decoding(default_gateway)

if hasattr(dll, 'GXSetDevicePersistentIpAddress'):
    def gx_set_device_persistent_ip_address(handle, ip, subnet_mask, default_gate_way):
        """
        :brief      Set the persistent IP information of the device
        :param      handle:             The handle of the device
        :param      ip:                 The persistent IP character string of the device(str)
        :param      subnet_mask:        The persistent subnet mask character string of the device(str)
        :param      default_gate_way:   The persistent gateway character string of the device(str)
        :return:    status:             State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        ip_c = create_string_buffer(string_encoding(ip))
        subnet_mask_c = create_string_buffer(string_encoding(subnet_mask))
        default_gate_way_c = create_string_buffer(string_encoding(default_gate_way))

        status = dll.GXSetDevicePersistentIpAddress(handle_c, byref(ip_c), byref(subnet_mask_c),
                                                    byref(default_gate_way_c))
        return status


if hasattr(dll, 'GXGetFeatureName'):
    def gx_get_feature_name(handle, feature_id):
        """
        :brief      Get the string description for the feature code
        :param      handle:         The handle of the device
                                    Type: Long, Greater than 0
        :param      feature_id:     The feature code ID
                                    Type: Int, Greater than 0
        :return:    status:         State return value, See detail in GxStatusList
                    name:           The string description for the feature code
        """
        handle_c = c_void_p()
        handle_c.value = handle
        feature_id_c = c_int()
        feature_id_c.value = feature_id

        size_c = c_size_t()
        status = dll.GXGetFeatureName(handle_c, feature_id_c, None, byref(size_c))

        name_buff = create_string_buffer(size_c.value)
        status = dll.GXGetFeatureName(handle_c, feature_id_c, byref(name_buff), byref(size_c))

        name = string_at(name_buff, size_c.value-1)
        return status, string_decoding(name)


if hasattr(dll, 'GXIsImplemented'):
    def gx_is_implemented(handle, feature_id):
        """
        :brief      Inquire the current camera whether support a special feature.
        :param      handle:         The handle of the device
                                    Type: Long, Greater than 0
        :param      feature_id:     The feature code ID
                                    Type: int, Greater than 0
        :return:    status:         State return value, See detail in GxStatusList
                    is_implemented: To return the result whether is support this feature
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_id_c = c_int()
        feature_id_c.value = feature_id

        is_implemented = c_bool()
        status = dll.GXIsImplemented(handle_c, feature_id_c, byref(is_implemented))
        return status, is_implemented.value


if hasattr(dll, 'GXIsReadable'):
    def gx_is_readable(handle, feature_id):
        """
        :brief      Inquire if a feature code is currently readable
        :param      handle:             The handle of the device
                                        Type: Long, Greater than 0
        :param      feature_id:         The feature code ID
                                        Type: int, Greater than 0
        :return:    status:             State return value, See detail in GxStatusList
                    is_readable:        To return the result whether the feature code ID is readable
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_id_c = c_int()
        feature_id_c.value = feature_id

        is_readable = c_bool()
        status = dll.GXIsReadable(handle_c, feature_id_c, byref(is_readable))
        return status, is_readable.value


if hasattr(dll, 'GXIsWritable'):
    def gx_is_writable(handle, feature_id):
        """
        :brief      Inquire if a feature code is currently writable
        :param      handle:             The handle of the device.
                                        Type: Long, Greater than 0
        :param      feature_id:         The feature code ID
                                        Type: int, Greater than 0
        :return:    status:             State return value, See detail in GxStatusList
                    is_writeable:       To return the result whether the feature code ID is writable(Bool)
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_id_c = c_int()
        feature_id_c.value = feature_id

        is_writeable = c_bool()
        status = dll.GXIsWritable(handle_c, feature_id_c, byref(is_writeable))
        return status, is_writeable.value


if hasattr(dll, 'GXGetIntRange'):
    def gx_get_int_range(handle, feature_id):
        """
        :brief      To get the minimum value, maximum value and steps of the int type
        :param      handle:         The handle of the device.
                                    Type: Long, Greater than 0
        :param      feature_id:     The feature code ID
                                    Type: int, Greater than 0
        :return:    status:         State return value, See detail in GxStatusList
                    int_range:      The structure of range description(GxIntRange)
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_id_c = c_int()
        feature_id_c.value = feature_id

        int_range = GxIntRange()
        status = dll.GXGetIntRange(handle_c, feature_id_c, byref(int_range))
        return status, int_range


if hasattr(dll, 'GXGetInt'):
    def gx_get_int(handle, feature_id):
        """
        :brief      Get the current value of the int type.
        :param      handle:         The handle of the device
                                    Type: Long, Greater than 0
        :param      feature_id:     The feature code ID
                                    Type: int, Greater than 0
        :return:    status:         State return value, See detail in GxStatusList
                    int_value:      Get the current value of the int type
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_id_c = c_int()
        feature_id_c.value = feature_id

        int_value = c_int64()
        status = dll.GXGetInt(handle_c, feature_id_c, byref(int_value))
        return status, int_value.value


if hasattr(dll, 'GXSetInt'):
    def gx_set_int(handle, feature_id, int_value):
        """
        :brief      Set the value of int type
        :param      handle:         The handle of the device
                                    Type: Long, Greater than 0
        :param      feature_id:     The feature code ID.
                                    Type: int, Greater than 0
        :param      int_value:      The value that the user will set
                                    Type: long, minnum:0
        :return:    status:         State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_id_c = c_int()
        feature_id_c.value = feature_id

        value_c = c_int64()
        value_c.value = int_value

        status = dll.GXSetInt(handle_c, feature_id_c, value_c)
        return status


if hasattr(dll, 'GXGetFloatRange'):
    def gx_get_float_range(handle, feature_id):
        """
        :brief      To get the minimum value, maximum value, stepsand unit of the float type
        :param      handle:         The handle of the device
                                    Type: Long, Greater than 0
        :param      feature_id:     The feature code ID
                                    Type: int, Greater than 0
        :return:    status:         State return value, See detail in GxStatusList
                    float_range:    The description structure(GxFloatRange)
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_id_c = c_int()
        feature_id_c.value = feature_id

        float_range = GxFloatRange()
        status = dll.GXGetFloatRange(handle_c, feature_id_c, byref(float_range))
        return status, float_range


if hasattr(dll, 'GXSetFloat'):
    def gx_set_float(handle, feature_id, float_value):
        """
        :brief      Set the value of float type
        :param      handle:         The handle of the device
                                    Type: Long, Greater than 0
        :param      feature_id:     The feature code ID
                                    Type: int, Greater than 0
        :param      float_value:    The float value that the user will set
                                    Type: double
        :return:    status:         State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_id_c = c_int()
        feature_id_c.value = feature_id

        value_c = c_double()
        value_c.value = float_value

        status = dll.GXSetFloat(handle_c, feature_id_c, value_c)
        return status


if hasattr(dll, 'GXGetFloat'):
    def gx_get_float(handle, feature_id):
        """
        :brief      Get the value of float type
        :param      handle:         The handle of the device
                                    Type: Long, Greater than 0
        :param      feature_id:     The feature code ID
                                    Type: int, Greater than 0
        :return:    status:         State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_id_c = c_int()
        feature_id_c.value = feature_id

        float_value = c_double()
        status = dll.GXGetFloat(handle_c, feature_id_c, byref(float_value))

        return status, float_value.value


if hasattr(dll, 'GXGetEnumEntryNums'):
    def gx_get_enum_entry_nums(handle, feature_id):
        """
        :brief      Get the number of the options for the enumeration item
        :param      handle:         The handle of the device
                                    Type: Long, Greater than 0
        :param      feature_id:     The feature code ID
                                    Type: int, Greater than 0
        :return:    status:         State return value, See detail in GxStatusList
                    enum_num:       The number of the options for the enumeration item
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_id_c = c_int()
        feature_id_c.value = feature_id

        enum_nums = c_uint()
        status = dll.GXGetEnumEntryNums(handle_c, feature_id_c, byref(enum_nums))
        return status, enum_nums.value


if hasattr(dll, 'GXGetEnumDescription'):
    def gx_get_enum_description(handle, feature_id, enum_num):
        """
        :brief      To get the description information of the enumerated type values
                    the number of enumerated items and the value and descriptions of each item
                    please reference GxEnumDescription.
        :param      handle:             The handle of the device
                                        Type: Long, Greater than 0
        :param      feature_id:         The feature code ID
                                        Type: int, Greater than 0
        :param      enum_num:           The number of enumerated information
                                        Type: int, Greater than 0
        :return:    status:             State return value, See detail in GxStatusList
                    enum_description:   Enumerated information array(GxEnumDescription)
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_id_c = c_int()
        feature_id_c.value = feature_id

        buf_size_c = c_size_t()
        buf_size_c.value = sizeof(GxEnumDescription) * enum_num

        enum_description = (GxEnumDescription * enum_num)()
        status = dll.GXGetEnumDescription(handle_c, feature_id_c, byref(enum_description), byref(buf_size_c))
        return status, enum_description


if hasattr(dll, 'GXGetEnum'):
    def gx_get_enum(handle, feature_id):
        """
        :brief      To get the current enumeration value
        :param      handle:         The handle of the device
                                    Type: Long, Greater than 0
        :param      feature_id:     The feature code ID
                                    Type: int, Greater than 0
        :return:    status:         State return value, See detail in GxStatusList
                    enum_value:     Get the current enumeration value
        """
        handle_c = c_void_p()
        handle_c.value = handle
        feature_id_c = c_int()
        feature_id_c.value = feature_id

        enum_value = c_int64()
        status = dll.GXGetEnum(handle_c, feature_id_c, byref(enum_value))

        return status, enum_value.value


if hasattr(dll, 'GXSetEnum'):
    def gx_set_enum(handle, feature_id, enum_value):
        """
        :brief      Set the enumeration value
        :param      handle:         The handle of the device
                                    Type: Long, Greater than 0
        :param      feature_id:     The feature code ID
                                    Type: int, Greater than 0
        :param      enum_value:     Set the enumeration value
                                    Type: int
        :return:    status:         State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_id_c = c_int()
        feature_id_c.value = feature_id

        value_c = c_int64()
        value_c.value = enum_value

        status = dll.GXSetEnum(handle_c, feature_id_c, value_c)
        return status


if hasattr(dll, 'GXGetBool'):
    def gx_get_bool(handle, feature_id):
        """
        :brief      Get the value of bool type
        :param      handle:         The handle of the device
                                    Type: Long, Greater than 0
        :param      feature_id:     The feature code ID
                                    Type: int, Greater than 0
        :return:    status:         State return value, See detail in GxStatusList
                    boot_value:     the value of bool type
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_id_c = c_int()
        feature_id_c.value = feature_id

        boot_value = c_bool()
        status = dll.GXGetBool(handle_c, feature_id_c, byref(boot_value))
        return status, boot_value.value


if hasattr(dll, 'GXSetBool'):
    def gx_set_bool(handle, feature_id, bool_value):
        """
        :brief      Set the value of bool type
        :param      handle:         The handle of the device
                                    Type: Long, Greater than 0
        :param      feature_id:     The feature code ID
                                    Type: int, Greater than 0
        :param      bool_value:     The bool value that the user will set
                                    Type: Bool
        :return:    status:         State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_id_c = c_int()
        feature_id_c.value = feature_id

        value_c = c_bool()
        value_c.value = bool_value

        status = dll.GXSetBool(handle_c, feature_id_c, value_c)
        return status


if hasattr(dll, 'GXGetStringLength'):
    def gx_get_string_length(handle, feature_id):
        """
        :brief      Get the current value length of the character string type. Unit: byte
        :param      handle:             The handle of the device
                                        Type: Long, Greater than 0
        :param      feature_id:         The feature code ID
                                        Type: int, Greater than 0
        :return:    status:             State return value, See detail in GxStatusList
                    string_length:      the current value length of the character string type
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_id_c = c_int()
        feature_id_c.value = feature_id

        string_length = c_size_t()
        status = dll.GXGetStringLength(handle_c, feature_id_c, byref(string_length))

        return status, string_length.value - 1


if hasattr(dll, 'GXGetStringMaxLength'):
    def gx_get_string_max_length(handle, feature_id):
        """
        :brief      Get the maximum length of the string type value,  Unit: byte
        :param      handle:             The handle of the device
                                        Type: Long, Greater than 0
        :param      feature_id:         The feature code ID
                                        Type: int, Greater than 0
        :return:    status:             State return value, See detail in GxStatusList
                    string_max_length:  the maximum length of the string type value
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_id_c = c_int()
        feature_id_c.value = feature_id

        string_max_length = c_size_t()
        status = dll.GXGetStringMaxLength(handle_c, feature_id, byref(string_max_length))

        return status, string_max_length.value - 1


if hasattr(dll, 'GXGetString'):
    def gx_get_string(handle, feature_id):
        """
        :brief      Get the content of the string type value
        :param      handle:         The handle of the device
                                    Type: Long, Greater than 0
        :param      feature_id:     The feature code ID
                                    Type: int, Greater than 0
        :return:    status:         State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_id_c = c_int()
        feature_id_c.value = feature_id

        size_c = c_size_t()
        status = dll.GXGetString(handle_c, feature_id_c, None, byref(size_c))

        content_c = create_string_buffer(size_c.value)
        status = dll.GXGetString(handle_c, feature_id_c, byref(content_c), byref(size_c))

        content = string_at(content_c, size_c.value-1)
        return status, string_decoding(content)


if hasattr(dll, 'GXSetString'):
    def gx_set_string(handle, feature_id, content):
        """
        :brief      Set the content of the string value
        :param      handle:         The handle of the device
                                    Type: Long, Greater than 0
        :param      feature_id:     The feature code ID
                                    Type: int, Greater than 0
        :param      content:        The string will be setting(str)
                                    Type: str
        :return:    status:         State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_id_c = c_int()
        feature_id_c.value = feature_id

        content_c = create_string_buffer(string_encoding(content))

        status = dll.GXSetString(handle_c, feature_id_c, byref(content_c))
        return status


if hasattr(dll, 'GXGetBufferLength'):
    def gx_get_buffer_length(handle, feature_id):
        """
        :brief      Get the length of the chunk data and the unit is byte,
                    the user can apply the buffer based on the length obtained,
                    and then call the gx_get_buffer to get the chunk data.
        :param      handle:         The handle of the device
                                    Type: Long, Greater than 0
        :param      feature_id:     The feature code ID
                                    Type: int, Greater than 0
        :return:    status:         State return value, See detail in GxStatusList
                    buff_length:    Buff length, Unit: byte
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_id_c = c_int()
        feature_id_c.value = feature_id

        buff_length = c_size_t()
        status = dll.GXGetBufferLength(handle_c, feature_id_c, byref(buff_length))
        return status, buff_length.value


if hasattr(dll, 'GXGetBuffer'):
    def gx_get_buffer(handle, feature_id):
        """
        :brief      Get the chunk data
        :param      handle:         The handle of the device
                                    Type: Long, Greater than 0
        :param      feature_id:     The feature code ID
                                    Type: int, Greater than 0
        :return:    status:         State return value, See detail in GxStatusList
                    buff:           chunk data
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_id_c = c_int()
        feature_id_c.value = feature_id

        buff_length_c = c_size_t()
        status = dll.GXGetBuffer(handle_c, feature_id_c, None, byref(buff_length_c))

        buff_c = (c_ubyte * buff_length_c.value)()
        status = dll.GXGetBuffer(handle_c, feature_id_c, byref(buff_c), byref(buff_length_c))
        return status, buff_c


if hasattr(dll, 'GXSetBuffer'):
    def gx_set_buffer(handle, feature_id, buff, buff_size):
        """
        :brief      Set the chunk data
        :param      handle:         The handle of the device
        :param      feature_id:     The feature code ID
                                    Type: long, Greater than 0
        :param      buff:           chunk data buff
                                    Type: Ctype array
        :param      buff_size:      chunk data buff size
                                    Type: int, Greater than 0
        :return:    status:         State return value, See detail in GxStatusList
        """

        handle_c = c_void_p()
        handle_c.value = handle

        feature_id_c = c_int()
        feature_id_c.value = feature_id

        buff_size_c = c_size_t()
        buff_size_c.value = buff_size

        status = dll.GXSetBuffer(handle_c, feature_id_c, buff, buff_size_c)
        return status


if hasattr(dll, 'GXSendCommand'):
    def gx_send_command(handle, feature_id):
        """
        :brief      Send the command
        :param      handle:         The handle of the device
                                    Type: long, Greater than 0
        :param      feature_id:     The feature code ID.
                                    Type: int, Greater than 0
        :return:    status:         State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_id_c = c_int()
        feature_id_c.value = feature_id

        status = dll.GXSendCommand(handle_c, feature_id_c)
        return status


CAP_CALL = CFUNCTYPE(None, POINTER(GxFrameCallbackParam))
if hasattr(dll, 'GXRegisterCaptureCallback'):
    def gx_register_capture_callback(handle, cap_call):
        """
        :brief      Register the capture callback function
        :param      handle:         The handle of the device
        :param      cap_call:       The callback function that the user will register(@ CAP_CALL)
        :return:    status:         State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        status = dll.GXRegisterCaptureCallback(handle_c, None, cap_call)
        return status


if hasattr(dll, 'GXUnregisterCaptureCallback'):
    def gx_unregister_capture_callback(handle):
        """
        :brief      Unregister the capture callback function
        :param      handle:         The handle of the device
        :return:    status:         State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        status = dll.GXUnregisterCaptureCallback(handle_c)
        return status


if hasattr(dll, 'GXGetImage'):
    def gx_get_image(handle, frame_data, time_out=200):
        """
        :brief      After starting acquisition, you can call this function to get images directly.
                    Noting that the interface can not be mixed with the callback capture mode.
        :param      handle:         The handle of the device
                                    Type: Long, Greater than 0
        :param      frame_data:     [out]User introduced to receive the image data
                                    Type: GxFrameData
        :param      time_out:       The timeout time of capture image.(unit: ms)
                                    Type: int, minnum: 0
        :return:    status:         State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        time_out_c = c_uint()
        time_out_c.value = time_out

        status = dll.GXGetImage(handle_c, byref(frame_data), time_out_c)
        return status

if hasattr(dll, "GXDQBuf"):
    def gx_dq_buf(handle, pp_frame_buffer, time_out = 200):
        """
        :brief      After starting acquisition, you can call this function to get images directly.
                    Noting that the interface can not be mixed with the callback capture mode.
        :param      handle:         The handle of the device
                                    Type: Long, Greater than 0
        :param      pp_frame_buffer:[out]User introduced to receive the image data
                                    Type: Secondary pointer
        :param      time_out:       The timeout time of capture image.(unit: ms)
                                    Type: int, minnum: 0
        :return:    status:         State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        time_out_c = c_uint()
        time_out_c.value = time_out

        dll.GXDQBuf.argtypes = [c_void_p, ctypes.POINTER(ctypes.POINTER(GxFrameBuffer)), c_uint]
        dll.GXDQBuf.restype = c_int

        status = dll.GXDQBuf(handle_c, pp_frame_buffer, time_out_c)
        return status

if hasattr(dll, "GXQBuf"):
    def gx_q_buf(handle, p_frame_buffer):
        """
        :brief      Call this interface to return after using the cache
        :param      handle:         The handle of the device
                                    Type: Long, Greater than 0
        :param      p_frame_buffer: [out]User introduced to receive the image data
                                    Type: First level pointer
        :return:    status:         State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        dll.GXQBuf.argtypes = [c_void_p, ctypes.POINTER(GxFrameBuffer)]
        dll.GXQBuf.restype = c_int

        status = dll.GXQBuf(handle_c, p_frame_buffer)
        return status

if hasattr(dll, 'GXFlushQueue'):
    def gx_flush_queue(handle):
        """
        :brief      Empty the cache image in the image output queue.
        :param      handle:     The handle of the device
                                Type: Long, Greater than 0
        :return:    status:     State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        status = dll.GXFlushQueue(handle_c)
        return status


OFF_LINE_CALL = CFUNCTYPE(None, c_void_p)
if hasattr(dll, 'GXRegisterDeviceOfflineCallback'):
    def gx_register_device_offline_callback(handle, call_back):
        """
        :brief      At present, the mercury GIGE camera provides the device offline notification event mechanism,
                    the user can call this interface to register the event handle callback function
        :param      handle:             The handle of the device
        :param      call_back:          The user event handle callback function(@ OFF_LINE_CALL)
        :return:    status:             State return value, See detail in GxStatusList
                    call_back_handle:   The handle of offline callback function
                                        the handle is used for unregistering the callback function
        """
        handle_c = c_void_p()
        handle_c.value = handle

        call_back_handle = c_void_p()

        status = dll.GXRegisterDeviceOfflineCallback(handle_c, None, call_back, byref(call_back_handle))
        return status, call_back_handle.value


if hasattr(dll, 'GXUnregisterDeviceOfflineCallback'):
    def gx_unregister_device_offline_callback(handle, call_back_handle):
        """
        :brief      Unregister event handle callback function
        :param      handle:             The handle of the device
        :param      call_back_handle:   The handle of device offline callback function
        :return:    status:             State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        call_back_handle_c = c_void_p()
        call_back_handle_c.value = call_back_handle

        status = dll.GXUnregisterDeviceOfflineCallback(handle_c, call_back_handle_c)
        return status



if hasattr(dll, 'GXFlushEvent'):
    def gx_flush_event(handle):
        """
        :brief      Empty the device event, such as the frame exposure to end the event data queue
        :param      handle:    The handle of the device
        :return:    status:     State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        status = dll.GXFlushEvent(handle_c)
        return status


if hasattr(dll, 'GXGetEventNumInQueue'):
    def gx_get_event_num_in_queue(handle):
        """
        :brief      Get the number of the events in the current remote device event queue cache.
        :param      handle:     The handle of the device
        :return:    status:     State return value, See detail in GxStatusList
                    event_num:  event number.
        """
        handle_c = c_void_p()
        handle_c.value = handle

        event_num = c_uint()

        status = dll.GXGetEventNumInQueue(handle_c, byref(event_num))
        return status, event_num.value


FEATURE_CALL = CFUNCTYPE(None, c_uint, py_object)
if hasattr(dll, 'GXRegisterFeatureCallback'):
    def gx_register_feature_callback(handle, call_back, feature_id, args):
        """
        :brief      Register device attribute update callback function.
                    When the current value of the device property has updated, or the accessible property is changed,
                    call this callback function.
        :param      handle:             The handle of the device
        :param      call_back:          The user event handle callback function(@ FEATURE_CALL)
        :param      feature_id:         The feature code ID
        :return:    status:             State return value, See detail in GxStatusList
                    call_back_handle:   The handle of property update callback function,
                                        to unregister the callback function.
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_id_c = c_int()
        feature_id_c.value = feature_id

        call_back_handle = c_void_p()
        status = dll.GXRegisterFeatureCallback(handle_c, ctypes.py_object(args), call_back, feature_id_c, byref(call_back_handle))

        return status, call_back_handle.value


if hasattr(dll, 'GXUnregisterFeatureCallback'):
    """
    """
    def gx_unregister_feature_callback(handle, feature_id, call_back_handle):
        """
        :brief      Unregister device attribute update callback function
        :param      handle:             The handle of the device
        :param      feature_id:         The feature code ID
        :param      call_back_handle:   Handle of property update callback function
        :return:    status:             State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        feature_id_c = c_int()
        feature_id_c.value = feature_id

        call_back_handle_c = c_void_p()
        call_back_handle_c.value = call_back_handle

        status = dll.GXUnregisterFeatureCallback(handle_c, feature_id_c, call_back_handle_c)
        return status

if hasattr(dll, 'GXExportConfigFile'):
    def gx_export_config_file(handle, file_path):
        """
        :brief      Export the current parameter of the camera to the configuration file.
        :param      handle:         The handle of the device
                                    Type: Long, Greater than 0
        :param      file_path:      The path of the configuration file that to be generated
                                    Type: str
        :return:    status:         State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        file_path_c = create_string_buffer(string_encoding(file_path))
        status = dll.GXExportConfigFile(handle_c, byref(file_path_c))

        return status


if hasattr(dll, 'GXImportConfigFile'):
    def gx_import_config_file(handle, file_path, verify):
        """
        :brief      Import the configuration file for the camera
        :param      handle:         The handle of the device
                                    Type: Long, Greater than 0
        :param      file_path:      The path of the configuration file(str)
                                    Type: str
        :param      verify:         If this value is true, all imported values will be read out
                                    to check whether they are consistent.
        :return:    status:         State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        verify_c = c_bool()
        verify_c.value = verify

        file_path_c = create_string_buffer(string_encoding(file_path))
        status = dll.GXImportConfigFile(handle_c, byref(file_path_c), verify_c)
        return status


if hasattr(dll, 'GXReadRemoteDevicePort'):
    def gx_read_remote_device_port(handle, address, buff, size):
        """
        :brief      Read data for user specified register.
        :param      handle:     The handle of the device
        :param      address:    Register address
        :param      buff:       Output data buff
        :param      size:       Buff size
        :return:    status:     State return value, See detail in GxStatusList
                    size:       Returns the length of the actual read register
        """
        handle_c = c_void_p()
        handle_c.value = handle

        address_c = c_ulonglong()
        address_c.value = address

        size_c = c_uint()
        size_c.value = size

        status = dll.GXReadRemoteDevicePort(handle_c, address_c, byref(buff), byref(size_c))
        return status, buff


if hasattr(dll, 'GXWriteRemoteDevicePort'):
    def gx_write_remote_device_port(handle, address, buff, size):
        """
        :brief      Writes user specified data to a user specified register.
        :param      handle:     The handle of the device
        :param      address:    Register address
        :param      buff:       User data
        :param      size:       User data size
        :return:    status:     State return value, See detail in GxStatusList
                    size:       Returns the length of the actual write register
        """
        handle_c = c_void_p()
        handle_c.value = handle

        address_c = c_ulonglong()
        address_c.value = address

        size_c = c_uint()
        size_c.value = size

        buff_c = c_int()
        buff_c.value = buff

        status = dll.GXWriteRemoteDevicePort(handle_c, address_c, byref(buff_c), byref(size_c))
        return status, size_c.value


if hasattr(dll, 'GXGigEIpConfiguration'):
    def gx_gige_ip_configuration(mac_address, ipconfig_flag, ip_address, subnet_mask, default_gateway, user_id):
        """
        "brief      Configure the static IP address of the camera
        :param      mac_address:        The MAC address of the device(str)
        :param      ipconfig_flag:      IP Configuration mode(GxIPConfigureModeList)
        :param      ip_address:         The IP address to be set(str)
        :param      subnet_mask:        The subnet mask to be set(str)
        :param      default_gateway:    The default gateway to be set(str)
        :param      user_id:            The user-defined name to be set(str)
        :return:    status:             State return value, See detail in GxStatusList
        """
        mac_address_c = create_string_buffer(string_encoding(mac_address))
        ip_address_c = create_string_buffer(string_encoding(ip_address))
        subnet_mask_c = create_string_buffer(string_encoding(subnet_mask))
        default_gateway_c = create_string_buffer(string_encoding(default_gateway))
        user_id_c = create_string_buffer(string_encoding(user_id))

        status = dll.GXGigEIpConfiguration(mac_address_c, ipconfig_flag,
                                           ip_address_c, subnet_mask_c,
                                           default_gateway_c, user_id_c)
        return status


if hasattr(dll, 'GXGigEForceIp'):
    def gx_gige_force_ip(mac_address, ip_address, subnet_mask, default_gate_way):
        """
        :brief      Execute the Force IP
        :param      mac_address:        The MAC address of the device(str)
        :param      ip_address:         The IP address to be set(str)
        :param      subnet_mask:        The subnet mask to be set(str)
        :param      default_gate_way:   The default gateway to be set(str)
        :return:    status:             State return value, See detail in GxStatusList
        """
        mac_address_c = create_string_buffer(string_encoding(mac_address))
        ip_address_c = create_string_buffer(string_encoding(ip_address))
        subnet_mask_c = create_string_buffer(string_encoding(subnet_mask))
        default_gate_way_c = create_string_buffer(string_encoding(default_gate_way))

        status = dll.GXGigEForceIp(mac_address_c, ip_address_c, subnet_mask_c, default_gate_way_c)
        return status


if hasattr(dll, 'GXGigEResetDevice'):
    def gx_gige_reset_device(mac_address, reset_device_mode):
        """
        :brief      Reconnection/Reset
        :param      mac_address:        The MAC address of the device(str)
        :param      reset_device_mode:  Reconnection mode, refer to GxResetDeviceModeEntry
        :return:    status:             State return value, See detail in GxStatusList
        """
        mac_address_c = create_string_buffer(string_encoding(mac_address))
        reset_device_mode_c = c_uint()
        reset_device_mode_c.value = reset_device_mode

        status = dll.GXGigEResetDevice(mac_address_c, reset_device_mode_c)
        return status


if hasattr(dll, 'GXSetAcqusitionBufferNumber'):
    def gx_set_acquisition_buffer_number(handle, buffer_num):
        """
        :brief      Users Set Acquisition buffer Number
        :param      handle:         The handle of the device
                                    Type: Long, Greater than 0
        :param      buffer_num:     Acquisition buffer Number
                                    Type: int, Greater than 0
        :return:    status:         State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        buffer_num_c = c_uint64()
        buffer_num_c.value = buffer_num

        status = dll.GXSetAcqusitionBufferNumber(handle_c, buffer_num_c)
        return status

if hasattr(dll,'GXReadRemoteDevicePortStacked'):
    def gx_set_read_remote_device_port_stacked(handle, entries, size):
        """
        :brief      Batch reads the value of the user-specified register (Registers with command values of 4 bytes only)
        :entries             [in]Batch read register addresses and values
                             [out]Read the data to the corresponding register
        :size                [in]Read the number of device registers
                             [out]The number of registers that were successfully read
        :return:    status:  State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        size_c = c_uint()
        size_c.value = size

        status = dll.GXReadRemoteDevicePortStacked(handle_c, entries, byref(size_c))
        return status


if hasattr(dll,'GXWriteRemoteDevicePortStacked'):
    def gx_set_write_remote_device_port_stacked(handle, entries, size):
        """
        :brief      Batch reads the value of the user-specified register (Registers with command values of 4 bytes only)
        :entries      [in]The address and value of the batch write register
        :size         [in]Sets the number of device registers
                      [out]The number of registers that were successfully written
        :return:      status:  State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        size_c = c_uint()
        size_c.value = size
        
        status = dll.GXWriteRemoteDevicePortStacked(handle_c, entries, byref(size_c))
        return status

if hasattr(dll, 'GXGigEIssueActionCommand'):
    def gx_issue_action_command(device_key, group_key, group_mask, broadcast_address, special_address, time_out,
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
        :expect_ack_st           [out]The user allocates memory to return the expected ack status to the device.

        :return:  status:  State return value, See detail in GxStatusList
        """
        dest_ip_c = create_string_buffer(string_encoding(broadcast_address))

        if special_address is not None:
            special_ip_c = create_string_buffer(string_encoding(special_address))
        else:
            special_ip_c = None

        expect_ack_c = c_uint32()
        expect_ack_c.value = expect_ack_number_res

        expect_ack_st = (GxActionCommandResult * expect_ack_number_res)()
        status = dll.GXGigEIssueActionCommand(device_key, group_key, group_mask, dest_ip_c,
                                              special_ip_c, time_out, byref(expect_ack_c), expect_ack_st)

        actual_ack_list = []
        for i in range(expect_ack_c.value):
            actual_ack_list.append({
                'status': expect_ack_st[i].status,
                'device_ip': string_decoding(expect_ack_st[i].device_ip),
            })
        return status, actual_ack_list

if hasattr(dll, 'GXGigEIssueScheduledActionCommand'):
    def gx_issue_scheduled_action_command(device_key, group_key, group_mask, action_time, broadcast_address,
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
        :expect_ack_st           [out]The user allocates memory to return the expected ack status to the device.

        :return:  status:  State return value, See detail in GxStatusList
        """
        dest_ip_c = create_string_buffer(string_encoding(broadcast_address))

        if special_address is not None:
            special_ip_c = create_string_buffer(string_encoding(special_address))
        else:
            special_ip_c = None

        action_time_c = c_uint64()
        action_time_c.value = action_time

        expect_ack_c = c_uint32()
        expect_ack_c.value = expect_ack_number_res

        expect_ack_st = (GxActionCommandResult * expect_ack_number_res)()

        status = dll.GXGigEIssueScheduledActionCommand(device_key, group_key, group_mask, action_time_c, dest_ip_c,
                                                       special_ip_c, time_out, byref(expect_ack_c), expect_ack_st)

        actual_ack_list = []
        for i in range(expect_ack_c.value):
            actual_ack_list.append({
                'status': expect_ack_st[i].status,
                'device_ip': string_decoding(expect_ack_st[i].device_ip),
            })
        return status, actual_ack_list

'''
if hasattr(dll, 'GXStreamOn'):
    def gx_stream_on(handle):
        """
        :brief      Start acquisition
        :param      handle:     The handle of the device
        :return:    status:     State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        status = dll.GXStreamOn(handle_c)
        return status


if hasattr(dll, 'GXDQBuf'):
    def gx_dequeue_buf(handle, time_out):
        """
        :brief      Get a image
                    After the image processing is completed, the gx_queue_buf interface needs to be called
                    otherwise the collection will not be able to continue.
        :param      handle:             The handle of the device
        :param      time_out:           The timeout time of capture image.(unit: ms)
        :return:    status:             State return value, See detail in GxStatusList
                    frame_data:         Image data
                    frame_data_p:       Image buff address
        """
        handle_c = c_void_p()
        handle_c.value = handle

        time_out_c = c_uint()
        time_out_c.value = time_out

        frame_data_p = c_void_p()
        status = dll.GXDQBuf(handle_c, byref(frame_data_p), time_out_c)

        frame_data = GxFrameData()
        memmove(addressof(frame_data), frame_data_p.value, sizeof(frame_data))
        return status, frame_data, frame_data_p.value


if hasattr(dll, 'GXQBuf'):
    def gx_queue_buf(handle, frame_data_p):
        """
        :brief      Put an image Buff back to the GxIAPI library and continue to be used for collection.
        :param      handle:         The handle of the device
        :param      frame_data_p:   Image buff address
        :return:    status:         State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        frame_data_p_p = c_void_p()
        frame_data_p_p.value = frame_data_p

        status = dll.GXQBuf(handle_c, frame_data_p_p)
        return status
        

if hasattr(dll, 'GXDQAllBufs'):
    def gx_dequeue_all_bufs(handle, buff_num, time_out):
        """
        :brief      Get images
                    After the image processing is completed, the gx_queue_all_bufs interface needs to be called
                    otherwise the collection will not be able to continue.
        :param      handle:         The handle of the device
        :param      buff_num:       The number of images expected to be obtained
        :param      time_out:       The timeout time of capture image.(unit: ms)
        :return:    status:         State return value, See detail in GxStatusList
                    frame_data:     Image data arrays
                    frame_count:    The number of images that are actually returned
        """
        handle_c = c_void_p()
        handle_c.value = handle

        time_out_c = c_uint()
        time_out_c.value = time_out

        frame_data_p = (c_void_p * buff_num)()
        frame_count_c = c_uint()

        status = dll.GXDQAllBufs(handle_c, frame_data_p, buff_num, byref(frame_count_c), time_out_c)
        frame_data = (GxFrameData * buff_num)()

        for i in range(buff_num):
            memmove(addressof(frame_data[i]), frame_data_p[i], sizeof(GxFrameData))

        return status, frame_data, frame_count_c.value


if hasattr(dll, 'GXQAllBufs'):
    def gx_queue_all_bufs(handle):
        """
        :brief      The image data Buf is returned to the GxIAPI library and used for collection.
        :param      handle:     The handle of the device
        :return:    status:     State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        status = dll.GXQAllBufs(handle_c)
        return status


if hasattr(dll, 'GXStreamOff'):
    def gx_stream_off(handle):
        """
        :brief      Stop acquisition
        :param      handle:     The handle of the device
        :return:    status:     State return value, See detail in GxStatusList
        """
        handle_c = c_void_p()
        handle_c.value = handle

        status = dll.GXStreamOff(handle_c)
        return status
'''

def array_decoding(int_array_c):
    """
    :breif      Python3.X: int array
    :param      int_array_c :   uint_c[]
    :return:    int_array   :   python array
    """
    int_array = []
    for index in range( len( int_array_c)):
        int_array.append( int_array_c[index])
    return int_array

def string_encoding(string):
    """
    :breif      Python3.X: String encoded as bytes
    :param      string
    :return:
    """
    if sys.version_info.major == 3:
        string = string.encode()
    return string


def string_decoding(string):
    """
    :brief      Python3.X: bytes decoded as string
    :param      string
    :return:
    """
    if sys.platform == 'linux2' or sys.platform == 'linux':
        try:
            string = string.decode()
        except UnicodeDecodeError:
            string = string.decode("gbk")
    else:
        try:
            string = string.decode("gbk")
        except UnicodeDecodeError:
            string = string.decode()
    return string


def range_check(value, min_value, max_value, inc_value=0):
    """
    :brief      Determine if the input parameter is within range
    :param      value:       input value
    :param      min_value:   max value
    :param      max_value:   min value
    :param      inc_value:   step size, default=0
    :return:    True/False
    """
    if value < min_value:
        return False
    elif value > max_value:
        return False
    elif (inc_value != 0) and (value != int(value / inc_value) * inc_value):
        return False
    return True
