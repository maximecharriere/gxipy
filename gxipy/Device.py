#!/usr/bin/python
# -*- coding:utf-8 -*-
# -*-mode:python ; tab-width:4 -*- ex:set tabstop=4 shiftwidth=4 expandtab: -*-

import numpy
from gxipy.gxwrapper import *
from gxipy.dxwrapper import *
from gxipy.gxidef import *
from gxipy.gxiapi import *
from gxipy.StatusProcessor import *
from gxipy.Feature import *
from gxipy.FeatureControl import *
from gxipy.ImageProc import *
from gxipy.ImageProcessConfig import *
from gxipy.DataStream import *
import types

class Device:
    """
    The Camera class mainly encapsulates some common operations and function attributes,
    which are the operations and properties usually found in the camera.
    In addition, this class also encapsulates the common operations of  some functions in the C interface,
    such as SetInt, SetFloat, etc. Can not open to the user, so that when the subsequent addition of features,
    Python interface does not upgrade, or only the definition of the control code can support new features
    """

    def __init__(self, handle, interface_obj):
        """
        :brief  Constructor for instance initialization
        :param handle:  Device handle
        """
        self.__dev_handle = handle
        self.data_stream = []
        self.__interface_obj = interface_obj

        self.__c_offline_callback = OFF_LINE_CALL(self.__on_device_offline_callback)
        self.__py_offline_callback = None
        self.__offline_callback_handle = None

        self.__c_feature_callback = FEATURE_CALL(self.__on_device_feature_callback)
        self.__py_feature_callback = None

        self.__c_feature_callback_char = FEATURE_CALL_CHAR(self.__on_device_feature_callback_char)
        self.__py_feature_callback_char = None

        self.__color_correction_param = 0

        # Function code function is obsolete, please use string to obtain attribute value
        # ---------------Device Information Section--------------------------
        self.DeviceVendorName = StringFeature(self.__dev_handle, GxFeatureID.STRING_DEVICE_VENDOR_NAME)
        self.DeviceModelName = StringFeature(self.__dev_handle, GxFeatureID.STRING_DEVICE_MODEL_NAME)
        self.DeviceFirmwareVersion = StringFeature(self.__dev_handle, GxFeatureID.STRING_DEVICE_FIRMWARE_VERSION)
        self.DeviceVersion = StringFeature(self.__dev_handle, GxFeatureID.STRING_DEVICE_VERSION)
        self.DeviceSerialNumber = StringFeature(self.__dev_handle, GxFeatureID.STRING_DEVICE_SERIAL_NUMBER)
        self.FactorySettingVersion = StringFeature(self.__dev_handle, GxFeatureID.STRING_FACTORY_SETTING_VERSION)
        self.DeviceUserID = StringFeature(self.__dev_handle, GxFeatureID.STRING_DEVICE_USER_ID)
        self.DeviceLinkSelector = IntFeature(self.__dev_handle, GxFeatureID.INT_DEVICE_LINK_SELECTOR)
        self.DeviceLinkThroughputLimitMode = EnumFeature(self.__dev_handle,
                                                         GxFeatureID.ENUM_DEVICE_LINK_THROUGHPUT_LIMIT_MODE)
        self.DeviceLinkThroughputLimit = IntFeature(self.__dev_handle, GxFeatureID.INT_DEVICE_LINK_THROUGHPUT_LIMIT)
        self.DeviceLinkCurrentThroughput = IntFeature(self.__dev_handle, GxFeatureID.INT_DEVICE_LINK_CURRENT_THROUGHPUT)
        self.DeviceReset = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_DEVICE_RESET)
        self.TimestampTickFrequency = IntFeature(self.__dev_handle, GxFeatureID.INT_TIMESTAMP_TICK_FREQUENCY)
        self.TimestampLatch = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_TIMESTAMP_LATCH)
        self.TimestampReset = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_TIMESTAMP_RESET)
        self.TimestampLatchReset = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_TIMESTAMP_LATCH_RESET)
        self.TimestampLatchValue = IntFeature(self.__dev_handle, GxFeatureID.INT_TIMESTAMP_LATCH_VALUE)
        self.DevicePHYVersion = StringFeature(self.__dev_handle, GxFeatureID.STRING_DEVICE_PHY_VERSION)
        self.DeviceTemperatureSelector = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_DEVICE_TEMPERATURE_SELECTOR)
        self.DeviceTemperature = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_DEVICE_TEMPERATURE)
        self.DeviceIspFirmwareVersion = StringFeature(self.__dev_handle, GxFeatureID.STRING_DEVICE_ISP_FIRMWARE_VERSION)
        self.LowPowerMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_LOWPOWER_MODE)
        self.CloseCCD = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_CLOSE_CCD)
        self.ProductionCode = StringFeature(self.__dev_handle, GxFeatureID.STRING_PRODUCTION_CODE)
        self.DeviceOriginalName = StringFeature(self.__dev_handle, GxFeatureID.STRING_DEVICE_ORIGINAL_NAME)
        self.Revision = IntFeature(self.__dev_handle, GxFeatureID.INT_REVISION)
        self.VersionsSupported = IntFeature(self.__dev_handle, GxFeatureID.INT_VERSIONS_SUPPORTED)
        self.VersionUsed = IntFeature(self.__dev_handle, GxFeatureID.INT_VERSION_USED)
        self.TecEnable = BoolFeature(self.__dev_handle, GxFeatureID.BOOL_TEC_ENABLE)
        self.TecTargetTemperature = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_TEC_TARGET_TEMPERATURE)
        self.FanEnable = self.TecEnable = BoolFeature(self.__dev_handle, GxFeatureID.BOOL_FAN_ENABLE)
        self.TemperatureDetectionStatus = IntFeature(self.__dev_handle, GxFeatureID.INT_TEMPERATURE_DETECTION_STATUS)
        self.FanSpeed = IntFeature(self.__dev_handle, GxFeatureID.INT_FAN_SPEED)
        self.DeviceHumidity = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_DEVICE_HUMIDITY)
        self.DevicePressure = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_DEVICE_PRESSURE)
        self.AirChangeDetectionStatus = IntFeature(self.__dev_handle, GxFeatureID.INT_AIR_CHANGE_DETECTION_STATUS)
        self.AirTightnessDetectionStatus = IntFeature(self.__dev_handle, GxFeatureID.INT_AIR_TIGHTNESS_DETECTION_STATUS)
        self.DeviceScanType = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_DEVICE_SCAN_TYPE)

        # ---------------ImageFormat Section--------------------------------
        self.SensorWidth = IntFeature(self.__dev_handle, GxFeatureID.INT_SENSOR_WIDTH)
        self.SensorHeight = IntFeature(self.__dev_handle, GxFeatureID.INT_SENSOR_HEIGHT)
        self.WidthMax = IntFeature(self.__dev_handle, GxFeatureID.INT_WIDTH_MAX)
        self.HeightMax = IntFeature(self.__dev_handle, GxFeatureID.INT_HEIGHT_MAX)
        self.OffsetX = IntFeature(self.__dev_handle, GxFeatureID.INT_OFFSET_X)
        self.OffsetY = IntFeature(self.__dev_handle, GxFeatureID.INT_OFFSET_Y)
        self.Width = IntFeature(self.__dev_handle, GxFeatureID.INT_WIDTH)
        self.Height = IntFeature(self.__dev_handle, GxFeatureID.INT_HEIGHT)
        self.BinningHorizontal = IntFeature(self.__dev_handle, GxFeatureID.INT_BINNING_HORIZONTAL)
        self.BinningVertical = IntFeature(self.__dev_handle, GxFeatureID.INT_BINNING_VERTICAL)
        self.DecimationHorizontal = IntFeature(self.__dev_handle, GxFeatureID.INT_DECIMATION_HORIZONTAL)
        self.DecimationVertical = IntFeature(self.__dev_handle, GxFeatureID.INT_DECIMATION_VERTICAL)
        self.PixelSize = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_PIXEL_SIZE)
        self.PixelColorFilter = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_PIXEL_COLOR_FILTER)
        self.PixelFormat = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_PIXEL_FORMAT)
        self.ReverseX = BoolFeature(self.__dev_handle, GxFeatureID.BOOL_REVERSE_X)
        self.ReverseY = BoolFeature(self.__dev_handle, GxFeatureID.BOOL_REVERSE_Y)
        self.TestPattern = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_TEST_PATTERN)
        self.TestPatternGeneratorSelector = EnumFeature(self.__dev_handle,
                                                        GxFeatureID.ENUM_TEST_PATTERN_GENERATOR_SELECTOR)
        self.RegionSendMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_REGION_SEND_MODE)
        self.RegionMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_REGION_MODE)
        self.RegionSelector = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_REGION_SELECTOR)
        self.CenterWidth = IntFeature(self.__dev_handle, GxFeatureID.INT_CENTER_WIDTH)
        self.CenterHeight = IntFeature(self.__dev_handle, GxFeatureID.INT_CENTER_HEIGHT)
        self.BinningHorizontalMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_BINNING_HORIZONTAL_MODE)
        self.BinningVerticalMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_BINNING_VERTICAL_MODE)
        self.SensorShutterMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_SENSOR_SHUTTER_MODE)
        self.DecimationLineNumber = IntFeature(self.__dev_handle, GxFeatureID.INT_DECIMATION_LINENUMBER)
        self.SensorDecimationHorizontal = IntFeature(self.__dev_handle, GxFeatureID.INT_SENSOR_DECIMATION_HORIZONTAL)
        self.SensorDecimationVertical = IntFeature(self.__dev_handle, GxFeatureID.INT_SENSOR_DECIMATION_VERTICAL)
        self.SensorSelector = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_SENSOR_SELECTOR)
        self.CurrentSensorWidth = IntFeature(self.__dev_handle, GxFeatureID.INT_CURRENT_SENSOR_WIDTH)
        self.CurrentSensorHeight = IntFeature(self.__dev_handle, GxFeatureID.INT_CURRENT_SENSOR_HEIGHT)
        self.CurrentSensorOffsetX = IntFeature(self.__dev_handle, GxFeatureID.INT_CURRENT_SENSOR_OFFSETX)
        self.CurrentSensorOffsetY = IntFeature(self.__dev_handle, GxFeatureID.INT_CURRENT_SENSOR_OFFSETY)
        self.CurrentSensorWidthMax = IntFeature(self.__dev_handle, GxFeatureID.INT_CURRENT_SENSOR_WIDTHMAX)
        self.CurrectSensorHeightMax = IntFeature(self.__dev_handle, GxFeatureID.INT_CURRENT_SENSOR_HEIGHTMAX)
        self.SensorBitDepth = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_SENSOR_BIT_DEPTH)
        self.WatermarkEnable = BoolFeature(self.__dev_handle, GxFeatureID.BOOL_WATERMARK_ENABLE)

        # ---------------TransportLayer Section-------------------------------
        self.PayloadSize = IntFeature(self.__dev_handle, GxFeatureID.INT_PAYLOAD_SIZE)
        self.GevCurrentIPConfigurationLLA = BoolFeature(self.__dev_handle,
                                                        GxFeatureID.BOOL_GEV_CURRENT_IP_CONFIGURATION_LLA)
        self.GevCurrentIPConfigurationDHCP = BoolFeature(self.__dev_handle,
                                                         GxFeatureID.BOOL_GEV_CURRENT_IP_CONFIGURATION_DHCP)
        self.GevCurrentIPConfigurationPersistentIP = BoolFeature(self.__dev_handle,
                                                         GxFeatureID.BOOL_GEV_CURRENT_IP_CONFIGURATION_PERSISTENT_IP)
        self.EstimatedBandwidth = IntFeature(self.__dev_handle, GxFeatureID.INT_ESTIMATED_BANDWIDTH)
        self.GevHeartbeatTimeout = IntFeature(self.__dev_handle, GxFeatureID.INT_GEV_HEARTBEAT_TIMEOUT)
        self.GevSCPSPacketSize = IntFeature(self.__dev_handle, GxFeatureID.INT_GEV_PACKET_SIZE)
        self.GevSCPD = IntFeature(self.__dev_handle, GxFeatureID.INT_GEV_PACKET_DELAY)
        self.GevLinkSpeed = IntFeature(self.__dev_handle, GxFeatureID.INT_GEV_LINK_SPEED)
        self.DeviceTapGeometry = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_DEVICE_TAP_GEOMETRY)

        # ---------------AcquisitionTrigger Section---------------------------
        self.AcquisitionMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_ACQUISITION_MODE)
        self.AcquisitionStart = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_ACQUISITION_START)
        self.AcquisitionStop = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_ACQUISITION_STOP)
        self.TriggerMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_TRIGGER_MODE)
        self.TriggerSoftware = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_TRIGGER_SOFTWARE)
        self.TriggerActivation = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_TRIGGER_ACTIVATION)
        self.ExposureTime = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_EXPOSURE_TIME)
        self.ExposureAuto = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_EXPOSURE_AUTO)
        self.TriggerFilterRaisingEdge = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_TRIGGER_FILTER_RAISING)
        self.TriggerFilterFallingEdge = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_TRIGGER_FILTER_FALLING)
        self.TriggerSource = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_TRIGGER_SOURCE)
        self.ExposureMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_EXPOSURE_MODE)
        self.TriggerSelector = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_TRIGGER_SELECTOR)
        self.TriggerDelay = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_TRIGGER_DELAY)
        self.TransferControlMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_TRANSFER_CONTROL_MODE)
        self.TransferOperationMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_TRANSFER_OPERATION_MODE)
        self.TransferStart = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_TRANSFER_START)
        self.TransferBlockCount = IntFeature(self.__dev_handle, GxFeatureID.INT_TRANSFER_BLOCK_COUNT)
        self.FrameBufferOverwriteActive = BoolFeature(self.__dev_handle, GxFeatureID.BOOL_FRAMESTORE_COVER_ACTIVE)
        self.AcquisitionFrameRateMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_ACQUISITION_FRAME_RATE_MODE)
        self.AcquisitionFrameRate = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_ACQUISITION_FRAME_RATE)
        self.CurrentAcquisitionFrameRate = FloatFeature(self.__dev_handle,
                                                        GxFeatureID.FLOAT_CURRENT_ACQUISITION_FRAME_RATE)
        self.FixedPatternNoiseCorrectMode = EnumFeature(self.__dev_handle,
                                                        GxFeatureID.ENUM_FIXED_PATTERN_NOISE_CORRECT_MODE)
        self.AcquisitionBurstFrameCount = IntFeature(self.__dev_handle, GxFeatureID.INT_ACQUISITION_BURST_FRAME_COUNT)
        self.AcquisitionStatusSelector = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_ACQUISITION_STATUS_SELECTOR)
        self.AcquisitionStatus = BoolFeature(self.__dev_handle, GxFeatureID.BOOL_ACQUISITION_STATUS)
        self.ExposureDelay = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_EXPOSURE_DELAY)
        self.ExposureOverlapTimeMax = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_EXPOSURE_OVERLAP_TIME_MAX)
        self.ExposureTimeMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_EXPOSURE_TIME_MODE)
        self.FrameBufferCount = IntFeature(self.__dev_handle, GxFeatureID.INT_FRAME_BUFFER_COUNT)
        self.FrameBufferFlush = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_FRAME_BUFFER_FLUSH)
        self.AcquisitionBurstMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_ACQUISITION_BURST_MODE)
        self.OverlapMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_OVERLAP_MODE)
        self.MultiSourceSelector = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_MULTISOURCE_SELECTOR)
        self.MultiSourceEnable = BoolFeature(self.__dev_handle, GxFeatureID.BOOL_MULTISOURCE_ENABLE)
        self.TriggerCacheEnable = BoolFeature(self.__dev_handle, GxFeatureID.BOOL_TRIGGER_CACHE_ENABLE)

        # ----------------DigitalIO Section----------------------------------
        self.UserOutputSelector = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_USER_OUTPUT_SELECTOR)
        self.UserOutputValue = BoolFeature(self.__dev_handle, GxFeatureID.BOOL_USER_OUTPUT_VALUE)
        self.LineSelector = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_LINE_SELECTOR)
        self.LineMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_LINE_MODE)
        self.LineInverter = BoolFeature(self.__dev_handle, GxFeatureID.BOOL_LINE_INVERTER)
        self.LineSource = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_LINE_SOURCE)
        self.LineStatus = BoolFeature(self.__dev_handle, GxFeatureID.BOOL_LINE_STATUS)
        self.LineStatusAll = IntFeature(self.__dev_handle, GxFeatureID.INT_LINE_STATUS_ALL)
        self.PulseWidth = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_PULSE_WIDTH)
        self.LineRange = IntFeature(self.__dev_handle, GxFeatureID.INT_LINE_RANGE)
        self.LineDelay = IntFeature(self.__dev_handle, GxFeatureID.INT_LINE_DELAY)
        self.LineFilterRaisingEdge = IntFeature(self.__dev_handle, GxFeatureID.INT_LINE_FILTER_RAISING_EDGE)
        self.LineFilterFallingEdge = IntFeature(self.__dev_handle, GxFeatureID.INT_LINE_FILTER_FALLING_EDGE)

        # ----------------AnalogControls Section----------------------------
        self.GainAuto = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_GAIN_AUTO)
        self.GainSelector = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_GAIN_SELECTOR)
        self.BlackLevelAuto = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_BLACK_LEVEL_AUTO)
        self.BlackLevelSelector = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_BLACK_LEVEL_SELECTOR)
        self.BalanceWhiteAuto = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_BALANCE_WHITE_AUTO)
        self.BalanceRatioSelector = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_BALANCE_RATIO_SELECTOR)
        self.BalanceRatio = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_BALANCE_RATIO)
        self.DeadPixelCorrect = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_DEAD_PIXEL_CORRECT)
        self.Gain = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_GAIN)
        self.BlackLevel = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_BLACK_LEVEL)
        self.GammaEnable = BoolFeature(self.__dev_handle, GxFeatureID.BOOL_GAMMA_ENABLE)
        self.GammaMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_GAMMA_MODE)
        self.Gamma = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_GAMMA)
        self.DigitalShift = IntFeature(self.__dev_handle, GxFeatureID.INT_DIGITAL_SHIFT)
        self.LightSourcePreset = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_LIGHT_SOURCE_PRESET)
        self.BlackLevelCalibStatus = BoolFeature(self.__dev_handle, GxFeatureID.BOOL_BLACKLEVEL_CALIB_STATUS)
        self.BlackLevelCalibValue = IntFeature(self.__dev_handle, GxFeatureID.INT_BLACKLEVEL_CALIB_VALUE)
        self.PGAGain = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_PGA_GAIN)

        # ---------------CustomFeature Section------------------------------
        self.ExpectedGrayValue = IntFeature(self.__dev_handle, GxFeatureID.INT_GRAY_VALUE)
        self.AAROIOffsetX = IntFeature(self.__dev_handle, GxFeatureID.INT_AAROI_OFFSETX)
        self.AAROIOffsetY = IntFeature(self.__dev_handle, GxFeatureID.INT_AAROI_OFFSETY)
        self.AAROIWidth = IntFeature(self.__dev_handle, GxFeatureID.INT_AAROI_WIDTH)
        self.AAROIHeight = IntFeature(self.__dev_handle, GxFeatureID.INT_AAROI_HEIGHT)
        self.AutoGainMin = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_AUTO_GAIN_MIN)
        self.AutoGainMax = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_AUTO_GAIN_MAX)
        self.AutoExposureTimeMin = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_AUTO_EXPOSURE_TIME_MIN)
        self.AutoExposureTimeMax = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_AUTO_EXPOSURE_TIME_MAX)
        self.ContrastParam = IntFeature(self.__dev_handle, GxFeatureID.INT_CONTRAST_PARAM)
        self.GammaParam = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_GAMMA_PARAM)
        self.ColorCorrectionParam = IntFeature(self.__dev_handle, GxFeatureID.INT_COLOR_CORRECTION_PARAM)
        self.AWBLampHouse = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_AWB_LAMP_HOUSE)
        self.AWBROIOffsetX = IntFeature(self.__dev_handle, GxFeatureID.INT_AWBROI_OFFSETX)
        self.AWBROIOffsetY = IntFeature(self.__dev_handle, GxFeatureID.INT_AWBROI_OFFSETY)
        self.AWBROIWidth = IntFeature(self.__dev_handle, GxFeatureID.INT_AWBROI_WIDTH)
        self.AWBROIHeight = IntFeature(self.__dev_handle, GxFeatureID.INT_AWBROI_HEIGHT)
        self.SharpnessMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_SHARPNESS_MODE)
        self.Sharpness = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_SHARPNESS)
        self.DataFieldSelector = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_USER_DATA_FIELD_SELECTOR)
        self.DataFieldValue = BufferFeature(self.__dev_handle, GxFeatureID.BUFFER_USER_DATA_FIELD_VALUE)
        self.FlatFieldCorrection = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_FLAT_FIELD_CORRECTION)
        self.NoiseReductionMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_NOISE_REDUCTION_MODE)
        self.NoiseReduction = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_NOISE_REDUCTION)
        self.FFCLoad = BufferFeature(self.__dev_handle, GxFeatureID.BUFFER_FFCLOAD)
        self.FFCSave = BufferFeature(self.__dev_handle, GxFeatureID.BUFFER_FFCSAVE)
        self.StaticDefectCorrection = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_STATIC_DEFECT_CORRECTION)
        self.NoiseReductionMode2D = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_2D_NOISE_REDUCTION_MODE)
        self.NoiseReductionMode3D = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_3D_NOISE_REDUCTION_MODE)
        self.CloseISP = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_CLOSE_ISP)
        self.StaticDefectCorrectionValueAll = BufferFeature(self.__dev_handle,
                                                            GxFeatureID.BUFFER_STATIC_DEFECT_CORRECTION_VALUE_ALL)
        self.StaticDefectCorrectionFlashValue = BufferFeature(self.__dev_handle,
                                                              GxFeatureID.BUFFER_STATIC_DEFECT_CORRECTION_FLASH_VALUE)
        self.StaticDefectCorrectionFinish = IntFeature(self.__dev_handle,
                                                       GxFeatureID.INT_STATIC_DEFECT_CORRECTION_FINISH)
        self.StaticDefectCorrectionInfo = BufferFeature(self.__dev_handle,
                                                        GxFeatureID.BUFFER_STATIC_DEFECT_CORRECTION_INFO)
        self.StripCalibrationStart = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_STRIP_CALIBRATION_START)
        self.StripCalibrationStop = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_STRIP_CALIBRATION_STOP)
        self.UserDataFiledValueAll = BufferFeature(self.__dev_handle, GxFeatureID.BUFFER_USER_DATA_FILED_VALUE_ALL)
        self.ShadingCorrectionMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_SHADING_CORRECTION_MODE)
        self.FFCGenerate = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_FFC_GENERATE)
        self.FFCGenerateStatus = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_FFC_GENERATE_STATUS)
        self.FFCExpectedGrayValueEnable = EnumFeature(self.__dev_handle,
                                                      GxFeatureID.ENUM_FFC_EXPECTED_GRAY_VALUE_ENABLE)
        self.FFCExpectedGray = IntFeature(self.__dev_handle, GxFeatureID.INT_FFC_EXPECTED_GRAY)
        self.FFCCoeffinientsSize = IntFeature(self.__dev_handle, GxFeatureID.INT_FFC_COEFFICIENTS_SIZE)
        self.FFCValueAll = BufferFeature(self.__dev_handle, GxFeatureID.BUFFER_FFC_VALUE_ALL)
        self.DSNUSelector = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_DSNU_SELECTOR)
        self.DSNUGenerate = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_DSNU_GENERATE)
        self.DSNUGenerateStatus = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_DSNU_GENERATE_STATUS)
        self.DSNUSave = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_DSNU_SAVE)
        self.DSNULoad = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_DSNU_LOAD)
        self.PRNUSelector = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_PRNU_SELECTOR)
        self.PRNUGenerate = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_PRNU_GENERATE)
        self.PRNUGenerateStatus = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_PRNU_GENERATE_STATUS)
        self.PRNUSave = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_PRNU_SAVE)
        self.PRNULoad = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_PRNU_LOAD)
        self.DataFieldValueAll = BufferFeature(self.__dev_handle, GxFeatureID.BUFFER_USER_DATA_FILED_VALUE_ALL)
        self.StaticDefectCorrectionCalibStatus = IntFeature(self.__dev_handle,
                                                            GxFeatureID.INT_STATIC_DEFECT_CORRECTION_CALIB_STATUS)
        self.FFCFactoryStatus = IntFeature(self.__dev_handle, GxFeatureID.INT_FFC_FACTORY_STATUS)
        self.DSNUFactoryStatus = IntFeature(self.__dev_handle, GxFeatureID.INT_DSNU_FACTORY_STATUS)
        self.PRNUFactoryStatus = IntFeature(self.__dev_handle, GxFeatureID.INT_PRNU_FACTORY_STATUS)
        self.Detect = BufferFeature(self.__dev_handle, GxFeatureID.BUFFER_DETECT)
        self.FFCCoefficient = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_FFC_COEFFICIENT)
        self.FFCFlashLoad = BufferFeature(self.__dev_handle, GxFeatureID.BUFFER_FFCFLASH_LOAD)
        self.FFCFlashSave = BufferFeature(self.__dev_handle, GxFeatureID.BUFFER_FFCFLASH_SAVE)

        # ---------------UserSetControl Section-------------------------------
        self.UserSetSelector = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_USER_SET_SELECTOR)
        self.UserSetLoad = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_USER_SET_LOAD)
        self.UserSetSave = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_USER_SET_SAVE)
        self.UserSetDefault = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_USER_SET_DEFAULT)
        self.DataFieldValueAllUsedStatus = IntFeature(self.__dev_handle,
                                                      GxFeatureID.INT_DATA_FIELD_VALUE_ALL_USED_STATUS)

        # ---------------Event Section----------------------------------------
        self.EventSelector = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_EVENT_SELECTOR)
        self.EventNotification = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_EVENT_NOTIFICATION)
        self.EventExposureEnd = IntFeature(self.__dev_handle, GxFeatureID.INT_EVENT_EXPOSURE_END)
        self.EventExposureEndTimestamp = IntFeature(self.__dev_handle, GxFeatureID.INT_EVENT_EXPOSURE_END_TIMESTAMP)
        self.EventExposureEndFrameID = IntFeature(self.__dev_handle, GxFeatureID.INT_EVENT_EXPOSURE_END_FRAME_ID)
        self.EventBlockDiscard = IntFeature(self.__dev_handle, GxFeatureID.INT_EVENT_BLOCK_DISCARD)
        self.EventBlockDiscardTimestamp = IntFeature(self.__dev_handle, GxFeatureID.INT_EVENT_BLOCK_DISCARD_TIMESTAMP)
        self.EventOverrun = IntFeature(self.__dev_handle, GxFeatureID.INT_EVENT_OVERRUN)
        self.EventOverrunTimestamp = IntFeature(self.__dev_handle, GxFeatureID.INT_EVENT_OVERRUN_TIMESTAMP)
        self.EventFrameStartOvertrigger = IntFeature(self.__dev_handle, GxFeatureID.INT_EVENT_FRAME_START_OVER_TRIGGER)
        self.EventFrameStartOvertriggerTimestamp = IntFeature(self.__dev_handle,
                                                              GxFeatureID.INT_EVENT_FRAME_START_OVER_TRIGGER_TIMESTAMP)
        self.EventBlockNotEmpty = IntFeature(self.__dev_handle, GxFeatureID.INT_EVENT_BLOCK_NOT_EMPTY)
        self.EventBlockNotEmptyTimestamp = IntFeature(self.__dev_handle,
                                                      GxFeatureID.INT_EVENT_BLOCK_NOT_EMPTY_TIMESTAMP)
        self.EventInternalError = IntFeature(self.__dev_handle, GxFeatureID.INT_EVENT_INTERNAL_ERROR)
        self.EventInternalErrorTimestamp = IntFeature(self.__dev_handle, GxFeatureID.INT_EVENT_INTERNAL_ERROR_TIMESTAMP)
        self.EventFrameBurstStartOvertrigger = IntFeature(self.__dev_handle,
                                                          GxFeatureID.INT_EVENT_FRAMEBURSTSTART_OVERTRIGGER)
        self.EventFrameBurstStartOvertriggerFrameID = IntFeature(self.__dev_handle,
                                                                 GxFeatureID.INT_EVENT_FRAMEBURSTSTART_OVERTRIGGER_FRAMEID)
        self.EventFrameBurstStartOvertriggerTimestamp = IntFeature(self.__dev_handle,
                                                                   GxFeatureID.INT_EVENT_FRAMEBURSTSTART_OVERTRIGGER_TIMESTAMP)
        self.EventFrameStartWait = IntFeature(self.__dev_handle, GxFeatureID.INT_EVENT_FRAMESTART_WAIT)
        self.EventFrameStartWaitTimestamp = IntFeature(self.__dev_handle,
                                                       GxFeatureID.INT_EVENT_FRAMESTART_WAIT_TIMESTAMP)
        self.EventFrameBurstStartWait = IntFeature(self.__dev_handle, GxFeatureID.INT_EVENT_FRAMEBURSTSTART_WAIT)
        self.EventFrameBurstStartWaitTimestamp = IntFeature(self.__dev_handle,
                                                            GxFeatureID.INT_EVENT_FRAMEBURSTSTART_WAIT_TIMESTAMP)
        self.EventBlockDiscardFrameID = IntFeature(self.__dev_handle, GxFeatureID.INT_EVENT_BLOCK_DISCARD_FRAMEID)
        self.EventFrameStartOvertriggerFrameID = IntFeature(self.__dev_handle,
                                                            GxFeatureID.INT_EVENT_FRAMESTART_OVERTRIGGER_FRAMEID)
        self.EventBlockNotEmptyFrameID = IntFeature(self.__dev_handle, GxFeatureID.INT_EVENT_BLOCK_NOT_EMPTY_FRAMEID)
        self.EventFrameStartWaitFrameID = IntFeature(self.__dev_handle, GxFeatureID.INT_EVENT_FRAMESTART_WAIT_FRAMEID)
        self.EventFrameBurstStartWaitFrameID = IntFeature(self.__dev_handle,
                                                          GxFeatureID.INT_EVENT_FRAMEBURSTSTART_WAIT_FRAMEID)
        self.EventSimpleMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_EVENT_SIMPLE_MODE)

        # ---------------LUT Section------------------------------------------
        self.LUTSelector = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_LUT_SELECTOR)
        self.LUTValueAll = BufferFeature(self.__dev_handle, GxFeatureID.BUFFER_LUT_VALUE_ALL)
        self.LUTEnable = BoolFeature(self.__dev_handle, GxFeatureID.BOOL_LUT_ENABLE)
        self.LUTIndex = IntFeature(self.__dev_handle, GxFeatureID.INT_LUT_INDEX)
        self.LUTValue = IntFeature(self.__dev_handle, GxFeatureID.INT_LUT_VALUE)
        self.LUTFactoryStatus = IntFeature(self.__dev_handle, GxFeatureID.INT_LUT_FACTORY_STATUS)

        # ---------------ChunkData Section------------------------------------
        self.ChunkModeActive = BoolFeature(self.__dev_handle, GxFeatureID.BOOL_CHUNK_MODE_ACTIVE)
        self.ChunkSelector = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_CHUNK_SELECTOR)
        self.ChunkEnable = BoolFeature(self.__dev_handle, GxFeatureID.BOOL_CHUNK_ENABLE)

        # ---------------Color Transformation Control-------------------------
        self.ColorTransformationMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_COLOR_TRANSFORMATION_MODE)
        self.ColorTransformationEnable = BoolFeature(self.__dev_handle, GxFeatureID.BOOL_COLOR_TRANSFORMATION_ENABLE)
        self.ColorTransformationValueSelector = EnumFeature(self.__dev_handle,
                                                            GxFeatureID.ENUM_COLOR_TRANSFORMATION_VALUE_SELECTOR)
        self.ColorTransformationValue = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_COLOR_TRANSFORMATION_VALUE)
        self.SaturationMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_SATURATION_MODE)
        self.Saturation = IntFeature(self.__dev_handle, GxFeatureID.INT_SATURATION)

        # ---------------CounterAndTimerControl Section-----------------------
        self.TimerSelector = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_TIMER_SELECTOR)
        self.TimerDuration = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_TIMER_DURATION)
        self.TimerDelay = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_TIMER_DELAY)
        self.TimerTriggerSource = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_TIMER_TRIGGER_SOURCE)
        self.CounterSelector = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_COUNTER_SELECTOR)
        self.CounterEventSource = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_COUNTER_EVENT_SOURCE)
        self.CounterResetSource = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_COUNTER_RESET_SOURCE)
        self.CounterResetActivation = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_COUNTER_RESET_ACTIVATION)
        self.CounterReset = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_COUNTER_RESET)
        self.CounterTriggerSource = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_COUNTER_TRIGGER_SOURCE)
        self.CounterDuration = IntFeature(self.__dev_handle, GxFeatureID.INT_COUNTER_DURATION)
        self.TimerTriggerActivation = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_TIMER_TRIGGER_ACTIVATION)
        self.CounterValue = IntFeature(self.__dev_handle, GxFeatureID.INT_COUNTER_VALUE)

        # ---------------RemoveParameterLimitControl Section------------------
        self.RemoveParameterLimit = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_REMOVE_PARAMETER_LIMIT)

        # ---------------HDRControl Section------------------
        self.HDRMode = EnumFeature(self.__dev_handle,GxFeatureID.ENUM_HDR_MODE)
        self.HDRTargetLongValue = IntFeature(self.__dev_handle, GxFeatureID.INT_HDR_TARGET_LONG_VALUE)
        self.HDRTargetShortValue = IntFeature(self.__dev_handle, GxFeatureID.INT_HDR_TARGET_SHORT_VALUE)
        self.HDRTargetMainValue = IntFeature(self.__dev_handle, GxFeatureID.INT_HDR_TARGET_MAIN_VALUE)

        # ---------------MultiGrayControl Section------------------
        self.MGCMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_MGC_MODE)
        self.MGCSelector = IntFeature(self.__dev_handle, GxFeatureID.INT_MGC_SELECTOR)
        self.MGCExposureTime = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_MGC_EXPOSURE_TIME)
        self.MGCGain = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_MGC_GAIN)

        # ---------------ImageQualityControl Section------------------
        self.StripedCalibrationInfo = BufferFeature(self.__dev_handle, GxFeatureID.BUFFER_STRIPED_CALIBRATION_INFO)
        self.Contrast = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_CONTRAST)
        self.HotPixelCorrection = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_HOTPIXEL_CORRECTION)

        # ---------------GyroControl Section------------------
        self.IMUData = BufferFeature(self.__dev_handle, GxFeatureID.BUFFER_IMU_DATA)
        self.IMUConfigAccRange = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_IMU_CONFIG_ACC_RANGE)
        self.IMUConfigAccOdrLowPassFilterSwitch = EnumFeature(self.__dev_handle,
                                                        GxFeatureID.ENUM_IMU_CONFIG_ACC_ODR_LOW_PASS_FILTER_SWITCH)
        self.IMUConfigAccOdr = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_IMU_CONFIG_ACC_ODR)
        self.IMUConfigAccOdrLowPassFilterFrequency = EnumFeature(self.__dev_handle,
                                                        GxFeatureID.ENUM_IMU_CONFIG_ACC_ODR_LOW_PASS_FILTER_FREQUENCY)
        self.IMUConfigGyroXRange = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_IMU_CONFIG_GYRO_XRANGE)
        self.IMUConfigGyroYRange = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_IMU_CONFIG_GYRO_YRANGE)
        self.IMUConfigGyroZRange = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_IMU_CONFIG_GYRO_ZRANGE)
        self.IMUConfigGyroOdrLowPassFilterSwitch = EnumFeature(self.__dev_handle,
                                                        GxFeatureID.ENUM_IMU_CONFIG_GYRO_ODR_LOW_PASS_FILTER_SWITCH)
        self.IMUConfigGyroOdr = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_IMU_CONFIG_GYRO_ODR)
        self.IMUConfigGyroOdrLowPassFilterFrequency = EnumFeature(self.__dev_handle,
                                                        GxFeatureID.ENUM_IMU_CONFIG_GYRO_ODR_LOW_PASS_FILTER_FREQUENCY)
        self.IMURoomTemperature = FloatFeature(self.__dev_handle, GxFeatureID.FLOAT_IMU_ROOM_TEMPERATURE)
        self.IMUTemperatureOdr = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_IMU_TEMPERATURE_ODR)

        # ---------------FrameBufferControl Section------------------
        self.FrameBufferCount = IntFeature(self.__dev_handle, GxFeatureID.INT_FRAME_BUFFER_COUNT)
        self.FrameBufferFlush = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_FRAME_BUFFER_FLUSH)

        # ---------------SerialPortControl Section------------------
        self.DeviceSerialPortSelector = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_SERIALPORT_SELECTOR)
        self.SerialPortSource = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_SERIALPORT_SOURCE)
        self.DeviceSerialPortBaudRate = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_SERIALPORT_BAUDRATE)
        self.SerialPortDataBits = IntFeature(self.__dev_handle, GxFeatureID.INT_SERIALPORT_DATA_BITS)
        self.SerialPortStopBits = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_SERIALPORT_STOP_BITS)
        self.SerialPortParity = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_SERIALPORT_PARITY)
        self.TransmitQueueMaxCharacterCount = IntFeature(self.__dev_handle,
                                                         GxFeatureID.INT_TRANSMIT_QUEUE_MAX_CHARACTER_COUNT)
        self.TransmitQueueCurrentCharacterCount = IntFeature(self.__dev_handle,
                                                             GxFeatureID.INT_TRANSMIT_QUEUE_CURRENT_CHARACTER_COUNT)
        self.ReceiveQueueMaxCharacterCount = IntFeature(self.__dev_handle,
                                                        GxFeatureID.INT_RECEIVE_QUEUE_MAX_CHARACTER_COUNT)
        self.ReceiveQueueCurrentCharacterCount = IntFeature(self.__dev_handle,
                                                            GxFeatureID.INT_RECEIVE_QUEUE_CURRENT_CHARACTER_COUNT)
        self.ReceiveFramingErrorCount = IntFeature(self.__dev_handle, GxFeatureID.INT_RECEIVE_FRAMING_ERROR_COUNT)
        self.ReceiveParityErrorCount = IntFeature(self.__dev_handle, GxFeatureID.INT_RECEIVE_PARITY_ERROR_COUNT)
        self.ReceiveQueueClear = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_RECEIVE_QUEUE_CLEAR)
        self.SerialPortData = BufferFeature(self.__dev_handle, GxFeatureID.BUFFER_SERIALPORT_DATA)
        self.SerialPortDataLength = IntFeature(self.__dev_handle, GxFeatureID.INT_SERIALPORT_DATA_LENGTH)
        self.SerialPortDetectionStatus = IntFeature(self.__dev_handle, GxFeatureID.INT_SERIAL_PORT_DETECTION_STATUS)

        # ---------------CoaXPress Section------------------
        self.CxpLinkConfiguration = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_CXP_LINK_CONFIGURATION)
        self.CxpLinkConfigurationPreferred = EnumFeature(self.__dev_handle,
                                                         GxFeatureID.ENUM_CXP_LINK_CONFIGURATION_PREFERRED)
        self.CxpLinkConfigurationStatus = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_CXP_LINK_CONFIGURATION_STATUS)
        self.Image1StreamID = IntFeature(self.__dev_handle, GxFeatureID.INT_IMAGE1_STREAM_ID)
        self.CxpConnectionSelector = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_CXP_CONNECTION_SELECTOR)
        self.CxpConnectionTestMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_CXP_CONNECTION_TEST_MODE)
        self.CxpConnectionTestErrorCount = IntFeature(self.__dev_handle, GxFeatureID.INT_RECEIVE_FRAMING_ERROR_COUNT)
        self.CxpConnectionTestPacketRxCount = IntFeature(self.__dev_handle, GxFeatureID.INT_RECEIVE_FRAMING_ERROR_COUNT)
        self.CxpConnectionTestPacketTxCount = IntFeature(self.__dev_handle, GxFeatureID.INT_RECEIVE_FRAMING_ERROR_COUNT)

        # ---------------SequencerControl Section------------------
        self.SequencerMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_SEQUENCER_MODE)
        self.SequencerConfigurationMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_SEQUENCER_CONFIGURATION_MODE)
        self.SequencerFeatureSelector = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_SEQUENCER_FEATURE_SELECTOR)
        self.SequencerFeatureEnable = BoolFeature(self.__dev_handle, GxFeatureID.BOOL_SEQUENCER_FEATURE_ENABLE)
        self.SequencerSetSelector = IntFeature(self.__dev_handle, GxFeatureID.INT_SEQUENCER_SET_SELECTOR)
        self.SequencerSetCount = IntFeature(self.__dev_handle, GxFeatureID.INT_SEQUENCER_SET_COUNT)
        self.SequencerSetActive = IntFeature(self.__dev_handle, GxFeatureID.INT_SEQUENCER_SET_ACTIVE)
        self.SequencerSetReset = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_SEQUENCER_SET_RESET)
        self.SequencerPathSelector = IntFeature(self.__dev_handle, GxFeatureID.INT_SEQUENCER_PATH_SELECTOR)
        self.SequencerSetNext = IntFeature(self.__dev_handle, GxFeatureID.INT_SEQUENCER_SET_NEXT)
        self.SequencerTriggerSource = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_SEQUENCER_TRIGGER_SOURCE)
        self.SequencerSetSave = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_SEQUENCER_SET_SAVE)
        self.SequencerSetLoad = CommandFeature(self.__dev_handle, GxFeatureID.COMMAND_SEQUENCER_SET_LOAD)

        # ---------------EnoderControl Section------------------
        self.EncoderSelector = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_ENCODER_SELECTOR)
        self.EncoderDirection = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_ENCODER_DIRECTION)
        self.EncoderValue = IntFeature(self.__dev_handle, GxFeatureID.INT_ENCODER_VALUE)
        self.EncoderSourceA = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_ENCODER_SOURCEA)
        self.EncoderSourceB = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_ENCODER_SOURCEB)
        self.EncoderMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_ENCODER_MODE)
        self.__get_stream_handle()

    def __get_stream_handle(self):
        """
        :brief      Get stream handle and create stream object
        :return:
        """
        status, data_stream_num = gx_data_stream_number_from_device(self.__dev_handle)
        StatusProcessor.process(status, 'Device', '__get_stream_handle')

        for index in range(data_stream_num):
            status, stream_handle = gx_get_data_stream_handle_from_device(self.__dev_handle, index + 1)
            StatusProcessor.process(status, 'Device', '__get_stream_handle')

            self.data_stream.append(DataStream( self.__dev_handle, stream_handle))

    def get_stream_channel_num(self):
        """
        :brief      Get the number of stream channels supported by the current device.
        :return:    the number of stream channels
        """
        return len(self.data_stream)


    def get_parent_interface(self):
        """
        :brief      Get interface
        :return:    Interface
        """
        return  self.__interface_obj


    def close_device(self):
        """
        :brief      close device, close device handle
        :return:    None
        """
        status = gx_close_device(self.__dev_handle)
        StatusProcessor.process(status, 'Device', 'close_device')
        self.__dev_handle = None
        self.__py_offline_callback = None
        self.__offline_callback_handle = None
        self.__py_feature_callback = None
        self.__py_feature_callback_char = None

    def get_stream_number(self):
        """
        :brief      Get the number of stream channels supported by the current device.
        :return:    the number of stream channels
        """
        return len(self.__data_stream_handle)

    def get_stream(self, stream_index):
        """
        :brief      Get stream object
        :param stream_index:    stream index
        :return: stream object
        """
        if not isinstance(stream_index, INT_TYPE):
            raise ParameterTypeError("Device.get_stream: "
                                     "Expected stream_index type is int, not %s" % type(stream_index))

        if stream_index < 1:
            print("Device.get_stream: stream_index must start from 1")
            return None
        elif stream_index > UNSIGNED_INT_MAX:
            print("Device.get_stream: stream_index maximum: %s" % hex(len(self.data_stream)).__str__())
            return None

        if len( self.data_stream) < stream_index:
            raise NotFoundDevice("Device.get_stream: invalid index")

        return self.data_stream[stream_index - 1]

    def get_local_device_feature_control(self):
        """
        :brief      Get local device layer feature control object
        :return:    Local device layer feature control object
        """
        status, local_handle = gx_local_device_handle_from_device( self.__dev_handle)
        StatusProcessor.process(status, 'Device', 'register_device_offline_callback')
        feature_control = FeatureControl( local_handle)
        return  feature_control

    def get_remote_device_feature_control(self):
        """
        :brief      Get remote device layer feature control object
        :return:    Remote device layer feature control object
        """
        feature_control = FeatureControl( self.__dev_handle)
        return  feature_control

    def register_device_offline_callback(self, callback_func):
        """
        :brief      Register the device offline event callback function.
                    Interface is obsolete.
        :param      callback_func:  callback function
        :return:    none
        """
        if not isinstance(callback_func, types.FunctionType):
            raise ParameterTypeError("Device.register_device_offline_callback: "
                                     "Expected callback type is function not %s" % type(callback_func))

        status, offline_callback_handle = gx_register_device_offline_callback \
            (self.__dev_handle, self.__c_offline_callback)
        StatusProcessor.process(status, 'Device', 'register_device_offline_callback')

        # callback will not recorded when register callback failed.
        self.__py_offline_callback = callback_func
        self.__offline_callback_handle = offline_callback_handle

    def unregister_device_offline_callback(self):
        """
        :brief      Unregister the device offline event callback function.
                    Interface is obsolete.
        :return:    none
        """
        status = gx_unregister_device_offline_callback(self.__dev_handle, self.__offline_callback_handle)
        StatusProcessor.process(status, 'Device', 'unregister_device_offline_callback')
        self.__py_offline_callback = None
        self.__offline_callback_handle = None

    def __on_device_offline_callback(self, c_user_param):
        """
        :brief      Device offline event callback function with an unused c_void_p.
                    Interface is obsolete.
        :return:    none
        """
        self.__py_offline_callback()


    # The following interfaces are obsolete.
    def stream_on(self, stream_index = 0):
        """
        :brief      send start command, camera start transmission image data
                    Interface is obsolete.
        :return:    none
        """
        payload_size = self.data_stream[0].get_payload_size()
        self.data_stream[0].set_payload_size(payload_size)
        status = gx_send_command(self.__dev_handle, GxFeatureID.COMMAND_ACQUISITION_START)
        StatusProcessor.process(status, 'Device', 'stream_on')
        self.data_stream[0].set_acquisition_flag(True)

    def stream_off(self,stream_index = 0):
        """
        :brief      send stop command, camera stop transmission image data
                    Interface is obsolete.
        :return:    none
        """
        status = gx_send_command(self.__dev_handle, GxFeatureID.COMMAND_ACQUISITION_STOP)
        StatusProcessor.process(status, 'Device', 'stream_off')
        self.data_stream[0].set_acquisition_flag(False)

    def export_config_file(self, file_path):
        """
        :brief      Export the current configuration file
                    Interface is obsolete.
        :param      file_path:      file path(type: str)
        :return:    none
        """
        if not isinstance(file_path, str):
            raise ParameterTypeError("Device.export_config_file: "
                                     "Expected file_path type is str, not %s" % type(file_path))

        status = gx_export_config_file(self.__dev_handle, file_path)
        StatusProcessor.process(status, 'Device', 'export_config_file')

    def import_config_file(self, file_path, verify=False):
        """
        :brief      Imported configuration file
                    Interface is obsolete.
        :param      file_path:  file path(type: str)
        :param      verify:     If this value is true, all the imported values will be read out
                                and checked for consistency(type: bool)
        :return:    none
        """
        if not isinstance(file_path, str):
            raise ParameterTypeError("Device.import_config_file: "
                                     "Expected file_path type is str, not %s" % type(file_path))

        if not isinstance(verify, bool):
            raise ParameterTypeError("Device.import_config_file: "
                                     "Expected verify type is bool, not %s" % type(verify))

        status = gx_import_config_file(self.__dev_handle, file_path, verify)
        StatusProcessor.process(status, 'Device', 'import_config_file')

    def register_device_feature_callback(self, callback_func, feature_id, args):
        """
        :brief      Register the device feature event callback function.
        :param      callback_func:  callback function
        :param      feature_id:     feature id
        :return:    none
        """
        if not isinstance(callback_func, types.FunctionType):
            raise ParameterTypeError("Device.register_device_feature_callback: "
                                     "Expected callback type is function not %s" % type(callback_func))

        if feature_id not in vars(GxFeatureID).values():
            raise ParameterTypeError("Device.register_device_feature_callback: "
                                     "Expected feature id is in GxEventSectionEntry not %s" % feature_id)

        status, feature_callback_handle = gx_register_feature_callback \
            (self.__dev_handle, self.__c_feature_callback, feature_id, args)
        StatusProcessor.process(status, 'Device', 'register_device_feature_callback')

        # callback will not recorded when register callback failed.
        self.__py_feature_callback = callback_func
        return feature_callback_handle

    def register_device_feature_callback_by_string(self, callback_func, feature_name, args):
        """
        :brief      Register the device feature event callback function.
        :param      callback_func:  callback function
        :param      feature_id:     feature id
        :return:    none
        """
        if not isinstance(callback_func, types.FunctionType):
            raise ParameterTypeError("Device.register_device_feature_callback: "
                                     "Expected callback type is function not %s" % type(callback_func))

        if not isinstance(feature_name, str):
            raise ParameterTypeError("Device.register_device_feature_callback: "
                                     "Expected feature id is in GxEventSectionEntry not %s" % feature_name)

        status, feature_callback_handle = gx_register_feature_call_back_by_string \
            (self.__dev_handle, self.__c_feature_callback_char, feature_name, args)
        StatusProcessor.process(status, 'Device', 'register_device_feature_callback')

        # callback will not recorded when register callback failed.
        self.__py_feature_callback_char = callback_func
        return feature_callback_handle

    def unregister_device_feature_callback(self, feature_id, feature_callback_handle):
        """
        :brief      Unregister the device feature event callback function.
        :return:    none
        """
        if feature_id not in vars(GxFeatureID).values():
            raise ParameterTypeError("Device.unregister_device_feature_callback: "
                                     "Expected feature id is in GxEventSectionEntry not %s" % feature_id)

        status = gx_unregister_feature_callback(self.__dev_handle, feature_id, feature_callback_handle)
        StatusProcessor.process(status, 'Device', 'unregister_device_feature_callback')

        self.__py_feature_callback = None

    def unregister_device_feature_callback_by_string(self, feature_name, feature_callback_handle):
        """
        :brief      Unregister the device feature event callback function.
        :return:    none
        """
        if not isinstance(feature_name, str):
            raise ParameterTypeError("Device.unregister_device_feature_callback: "
                                     "Expected feature id is in GxEventSectionEntry not %s" % feature_name)

        status = gx_unregister_feature_call_back_by_string(self.__dev_handle, feature_name, feature_callback_handle)
        StatusProcessor.process(status, 'Device', 'unregister_device_feature_callback')

        self.__py_feature_callback_char = None

    def __on_device_feature_callback(self, c_feature_id, c_user_param):
        """
        :brief      Device feature event callback function with an unused c_void_p.
        :return:    none
        """
        self.__py_feature_callback(c_feature_id, c_user_param)

    def __on_device_feature_callback_char(self, c_feature_name, c_user_param):
        """
        :brief      Device feature event callback function with an unused c_void_p.
        :return:    none
        """
        self.__py_feature_callback_char(c_feature_name, c_user_param)

    def read_remote_device_port(self, address, buff, size):
        """
        :brief      Read Remote Regesiter
                    Interface is obsolete.
        :param      address:    The address of the register to be read(type: int)
        :param      bytearray:  The data to be read from register(type: buffer)
        :return:    Read Remote Regesiter Data Buff
        """
        if not isinstance(address, INT_TYPE):
            raise ParameterTypeError("Device.read_remote_device_port: "
                                     "Expected address type is int, not %s" % type(address))

        if not isinstance(size, INT_TYPE):
            raise ParameterTypeError("Device.read_remote_device_port: "
                                     "Expected size type is int, not %s" % type(size))

        status, read_result = gx_read_remote_device_port(self.__dev_handle, address, buff, size)
        StatusProcessor.process(status, 'Device', 'read_remote_device_port')

        return status

    def write_remote_device_port(self, address, buf, size):
        """
        :brief      Write remote register
                    Interface is obsolete.
        :param      address:    The address of the register to be written.(type: int)
        :param      bytearray:  The data to be written from user.(type: buffer)
        :return:    none
        """
        if not isinstance(address, INT_TYPE):
            raise ParameterTypeError("Device.write_remote_device_port: "
                                     "Expected address type is int, not %s" % type(address))

        status, r_size = gx_write_remote_device_port(self.__dev_handle, address, buf, size)
        StatusProcessor.process(status, 'Device', 'write_remote_device_port')

    def read_remote_device_port_stacked(self, entries, size):
        """
        :brief        Batch read the value of a user-specified register (only for registers with a command value of 4 bytes in length)
        :entries      [in]Batch read register addresses and values
                      [out]Read the data to the corresponding register
        :read_num     [in]Read the number of device registers
                      [out]The number of registers that were successfully read
        :return:    none
        """
        if not isinstance(size, INT_TYPE):
            raise ParameterTypeError("Device.set_read_remote_device_port_stacked: "
                                     "Expected size type is int, not %s" % type(size))

        status = gx_set_read_remote_device_port_stacked(self.__dev_handle, entries, size)
        StatusProcessor.process(status, 'Device', 'read_remote_device_port_stacked')

        return status

    def write_remote_device_port_stacked(self, entries, size):
        """
        :brief        Batch read the value of a user-specified register (only for registers with a command value of 4 bytes in length)
        :entries      [in]The address and value of the batch write register
        :read_num     [in]Sets the number of device registers
                      [out]The number of registers that were successfully written
        :return:    none
        """
        if not isinstance(size, INT_TYPE):
            raise ParameterTypeError("Device.set_read_remote_device_port_stacked: "
                                     "Expected size type is int, not %s" % type(size))

        status = gx_set_write_remote_device_port_stacked(self.__dev_handle, entries, size)
        StatusProcessor.process(status, 'Device', 'set_write_remote_device_port_stacked')

    def create_image_process_config(self):
        """
        :brief      Create an image processing configuration parameter object
        :return:    image processing configuration object
        """
        color_correction_param = self.__color_correction_param

        remote_feature_control = self.get_remote_device_feature_control()
        if (remote_feature_control.is_implemented("ColorCorrectionParam")):
            if remote_feature_control.is_readable("ColorCorrectionParam"):
                color_correction_param = remote_feature_control.get_int_feature("ColorCorrectionParam").get()
            else:
                raise UnexpectedError("ColorCorrectionParam does not support read")

        image_process_config = ImageProcessConfig(color_correction_param)
        return image_process_config  
   
    def set_device_persistent_ip_address(self, ip, subnet_mask, default_gate_way):
        """
        brief:  Set the persistent IP information of the device
        return: Success:    feature name
                Failed:     convert feature ID to string
        """
        status = gx_set_device_persistent_ip_address(self.__dev_handle, ip, subnet_mask, default_gate_way)
        StatusProcessor.process(status, 'Device', 'set_device_persistent_ip_address')

    def get_device_persistent_ip_address(self):
        """
        brief:  Set the persistent IP information of the device
        return: Success:    feature name
                Failed:     convert feature ID to string
        """
        status, ip, subnet_mask, default_gateway = gx_get_device_persistent_ip_address(self.__dev_handle)
        StatusProcessor.process(status, 'Device', 'get_device_persistent_ip_address')
        return status, ip, subnet_mask, default_gateway


class GEVDevice(Device):
    def __init__(self, handle, interface_obj):
        self.__dev_handle = handle
        Device.__init__(self, self.__dev_handle, interface_obj)
        self.GevCurrentIPConfigurationLLA = BoolFeature(self.__dev_handle,
                                                        GxFeatureID.BOOL_GEV_CURRENT_IP_CONFIGURATION_LLA)
        self.GevCurrentIPConfigurationDHCP = BoolFeature(self.__dev_handle,
                                                         GxFeatureID.BOOL_GEV_CURRENT_IP_CONFIGURATION_DHCP)
        self.GevCurrentIPConfigurationPersistentIP = BoolFeature(self.__dev_handle,
                                                                 GxFeatureID.BOOL_GEV_CURRENT_IP_CONFIGURATION_PERSISTENT_IP)
        self.EstimatedBandwidth = IntFeature(self.__dev_handle, GxFeatureID.INT_ESTIMATED_BANDWIDTH)
        self.GevHeartbeatTimeout = IntFeature(self.__dev_handle, GxFeatureID.INT_GEV_HEARTBEAT_TIMEOUT)
        self.GevSCPSPacketSize = IntFeature(self.__dev_handle, GxFeatureID.INT_GEV_PACKET_SIZE)
        self.GevSCPD = IntFeature(self.__dev_handle, GxFeatureID.INT_GEV_PACKET_DELAY)
        self.GevLinkSpeed = IntFeature(self.__dev_handle, GxFeatureID.INT_GEV_LINK_SPEED)
        self.DeviceCommandTimeout = IntFeature(self.__dev_handle, GxFeatureID.INT_COMMAND_TIMEOUT)
        self.DeviceCommandRetryCount = IntFeature(self.__dev_handle, GxFeatureID.INT_COMMAND_RETRY_COUNT)

class U3VDevice(Device):
    """
    The U3VDevice class inherits from the Device class. In addition to inheriting the properties of the Device,
    the U3V Device has special attributes such as bandwidth limitation, URBSetting, frame info, etc.
    """

    def __init__(self, handle, interface_obj):
        self.__dev_handle = handle
        Device.__init__(self, self.__dev_handle, interface_obj)


class U2Device(Device):
    """
    The U2Device class inherits from the Device class
    """

    def __init__(self, handle, interface_obj):
        self.__dev_handle = handle
        Device.__init__(self, self.__dev_handle, interface_obj)
        self.AcquisitionSpeedLevel = IntFeature(self.__dev_handle, GxFeatureID.INT_ACQUISITION_SPEED_LEVEL)
        self.AcquisitionFrameCount = IntFeature(self.__dev_handle, GxFeatureID.INT_ACQUISITION_FRAME_COUNT)
        self.TriggerSwitch = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_TRIGGER_SWITCH)
        self.UserOutputMode = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_USER_OUTPUT_MODE)
        self.StrobeSwitch = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_STROBE_SWITCH)
        self.ADCLevel = IntFeature(self.__dev_handle, GxFeatureID.INT_ADC_LEVEL)
        self.HBlanking = IntFeature(self.__dev_handle, GxFeatureID.INT_H_BLANKING)
        self.VBlanking = IntFeature(self.__dev_handle, GxFeatureID.INT_V_BLANKING)
        self.UserPassword = StringFeature(self.__dev_handle, GxFeatureID.STRING_USER_PASSWORD)
        self.VerifyPassword = StringFeature(self.__dev_handle, GxFeatureID.STRING_VERIFY_PASSWORD)
        self.UserData = BufferFeature(self.__dev_handle, GxFeatureID.BUFFER_USER_DATA)
        self.AALightEnvironment = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_AA_LIGHT_ENVIRONMENT)
        self.FrameInformation = BufferFeature(self.__dev_handle, GxFeatureID.BUFFER_FRAME_INFORMATION)
        self.ImageGrayRaiseSwitch = EnumFeature(self.__dev_handle, GxFeatureID.ENUM_IMAGE_GRAY_RAISE_SWITCH)


