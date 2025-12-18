#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   __init__.py
@Time    :   2025/12/16
@Author  :   Wei Lindong
@Version :   1.0
@Desc    :   OpenArmX Driver - Python SDK for OpenArmX robotic arm control
'''

from .arm import Arm
from .robot import Robot
from .exceptions import (
    # 基础异常
    OpenArmXError,

    # CAN 通信异常
    CANError,
    CANInitializationError,
    CANTimeoutError,
    CANTransmissionError,

    # 电机异常
    MotorError,
    MotorNotEnabledError,
    MotorFaultError,
    MotorTimeoutError,
    MotorCalibrationError,

    # 配置异常
    ConfigurationError,
    InvalidMotorIDError,
    InvalidModeError,
    InvalidParameterError,
    ConfigFileError,

    # 限制异常
    LimitExceededError,
    PositionLimitError,
    VelocityLimitError,
    TorqueLimitError,
    KpLimitError,
    KdLimitError,

    # 连接异常
    ConnectionError,
    ConnectionLostError,
)

__version__ = '1.0.1'
__author__ = 'Wei Lindong'

__all__ = [
    # 主接口
    'Arm',
    'Robot',

    # 异常类
    'OpenArmXError',
    'CANError',
    'CANInitializationError',
    'CANTimeoutError',
    'CANTransmissionError',
    'MotorError',
    'MotorNotEnabledError',
    'MotorFaultError',
    'MotorTimeoutError',
    'MotorCalibrationError',
    'ConfigurationError',
    'InvalidMotorIDError',
    'InvalidModeError',
    'InvalidParameterError',
    'ConfigFileError',
    'LimitExceededError',
    'PositionLimitError',
    'VelocityLimitError',
    'TorqueLimitError',
    'KpLimitError',
    'KdLimitError',
    'ConnectionError',
    'ConnectionLostError',
]
