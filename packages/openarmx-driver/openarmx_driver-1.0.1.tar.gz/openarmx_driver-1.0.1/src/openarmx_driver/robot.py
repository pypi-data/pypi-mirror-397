#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   robot.py
@Time    :   2025/12/16 16:39:44
@Author  :   Wei Lindong
@Version :   1.0
@Desc    :   双臂机器人控制接口
'''

from typing import Optional, List, Dict, Tuple
from .arm import Arm
from .exceptions import (
    CANInitializationError,
    InvalidMotorIDError,
    InvalidModeError
)
from ._lib.can_utils import (
    verify_can_interface,
    enable_can_interface
)
from ._lib.log_utils import log_output


class Robot:
    """
    双臂机器人控制类

    管理左右两条机械臂，提供统一的控制接口。

    属性:
        left_arm (Arm): 左臂控制对象
        right_arm (Arm): 右臂控制对象

    示例:
        >>> robot = Robot(left_canid='can0', right_canid='can1')
        >>> robot.enable_all()
        >>> robot.set_mode_all('mit')
        >>> robot.move_all_to_zero_mit(kp=5.0, kd=0.5)
    """

    def __init__(self,
                 left_canid: str = 'can0',
                 right_canid: str = 'can1',
                 motor_ids: Optional[List[int]] = None,
                 auto_enable_can: bool = True,
                 bitrate: int = 1000000,
                 log=None,
                 **kwargs):
        """
        初始化双臂机器人

        参数:
            left_canid (str): 左臂 CAN 通道 (默认: 'can0')
            right_canid (str): 右臂 CAN 通道 (默认: 'can1')
            motor_ids (List[int], optional): 电机ID列表 (默认: [1,2,3,4,5,6,7,8])
            auto_enable_can (bool): 是否自动启用 CAN 接口 (默认: True)
            bitrate (int): CAN 波特率 (默认: 1000000)
            log (callable, optional): 日志函数
            **kwargs: 传递给 Arm 的其他参数

        异常:
            CANInitializationError: CAN 总线初始化失败
        """
        self.left_canid = left_canid
        self.right_canid = right_canid
        self.log = log

        # 检测并启用 CAN 接口
        if auto_enable_can:
            self._check_and_enable_can(left_canid, bitrate)
            self._check_and_enable_can(right_canid, bitrate)

        # 初始化左右臂
        self.left_arm = Arm(
            can_channel=left_canid,
            side='left',
            motor_ids=motor_ids,
            **kwargs
        )
        self.right_arm = Arm(
            can_channel=right_canid,
            side='right',
            motor_ids=motor_ids,
            **kwargs
        )

        # 机械臂列表（便于批量操作）
        self.arms = [self.left_arm, self.right_arm]
        self.arm_names = ['左臂', '右臂']

    def _check_and_enable_can(self, interface: str, bitrate: int = 1000000):
        """
        检测并启用 CAN 接口

        参数:
            interface (str): CAN 接口名称
            bitrate (int): 波特率

        异常:
            CANInitializationError: 启用失败
        """
        # 检查接口是否已经启用
        if verify_can_interface(interface):
            log_output(f"✓ {interface} 已启用", "SUCCESS", self.log)
            return

        # 尝试启用接口
        log_output(f"⚠ {interface} 未启用，正在尝试启用...", "WARNING", self.log)
        success = enable_can_interface(interface, bitrate=bitrate, verbose=False)

        if not success:
            raise CANInitializationError(
                f"无法启用 {interface}。请手动执行:\n"
                f"  sudo ip link set {interface} up type can bitrate {bitrate}"
            )

        log_output(f"✓ {interface} 启用成功", "SUCCESS", self.log)

    def __enter__(self):
        """支持 with 语句"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出时自动关闭"""
        self.shutdown()

    def shutdown(self):
        """关闭所有 CAN 总线连接"""
        for arm in self.arms:
            try:
                arm.bus.shutdown()
            except:
                pass

    # ==================== 使能/失能控制 ====================

    def enable_all(self, motor_ids: Optional[List[int]] = None):
        """
        使能所有机械臂的所有电机

        参数:
            motor_ids (List[int], optional): 指定电机ID列表，默认为所有电机
        """
        for arm in self.arms:
            if motor_ids is None:
                ids = arm.motor_ids
            else:
                ids = motor_ids
            for motor_id in ids:
                arm.enable(motor_id)

    def disable_all(self, motor_ids: Optional[List[int]] = None):
        """
        失能所有机械臂的所有电机

        参数:
            motor_ids (List[int], optional): 指定电机ID列表，默认为所有电机
        """
        for arm in self.arms:
            if motor_ids is None:
                ids = arm.motor_ids
            else:
                ids = motor_ids
            for motor_id in ids:
                arm.disable(motor_id)

    def enable_left(self, motor_ids: Optional[List[int]] = None):
        """使能左臂所有电机"""
        ids = motor_ids if motor_ids else self.left_arm.motor_ids
        for motor_id in ids:
            self.left_arm.enable(motor_id)

    def enable_right(self, motor_ids: Optional[List[int]] = None):
        """使能右臂所有电机"""
        ids = motor_ids if motor_ids else self.right_arm.motor_ids
        for motor_id in ids:
            self.right_arm.enable(motor_id)

    def disable_left(self, motor_ids: Optional[List[int]] = None):
        """失能左臂所有电机"""
        ids = motor_ids if motor_ids else self.left_arm.motor_ids
        for motor_id in ids:
            self.left_arm.disable(motor_id)

    def disable_right(self, motor_ids: Optional[List[int]] = None):
        """失能右臂所有电机"""
        ids = motor_ids if motor_ids else self.right_arm.motor_ids
        for motor_id in ids:
            self.right_arm.disable(motor_id)

    # ==================== 模式设置 ====================

    def set_mode_all(self, mode: str, motor_ids: Optional[List[int]] = None):
        """
        设置所有机械臂的控制模式

        参数:
            mode (str): 控制模式 ('mit', 'csp', 'pp', 'speed', 'current')
            motor_ids (List[int], optional): 指定电机ID列表
        """
        for arm in self.arms:
            ids = motor_ids if motor_ids else arm.motor_ids
            for motor_id in ids:
                arm.set_mode(motor_id, mode)

    def set_mode_left(self, mode: str, motor_ids: Optional[List[int]] = None):
        """设置左臂控制模式"""
        ids = motor_ids if motor_ids else self.left_arm.motor_ids
        for motor_id in ids:
            self.left_arm.set_mode(motor_id, mode)

    def set_mode_right(self, mode: str, motor_ids: Optional[List[int]] = None):
        """设置右臂控制模式"""
        ids = motor_ids if motor_ids else self.right_arm.motor_ids
        for motor_id in ids:
            self.right_arm.set_mode(motor_id, mode)

    # ==================== MIT 模式控制 ====================

    def move_all_to_zero_mit(self, kp: float = 5.0, kd: float = 0.5,
                            motor_ids: Optional[List[int]] = None):
        """
        所有机械臂回到零位 (MIT模式)

        参数:
            kp (float): 位置增益
            kd (float): 速度增益
            motor_ids (List[int], optional): 指定电机ID列表
        """
        for arm in self.arms:
            ids = motor_ids if motor_ids else arm.motor_ids
            for motor_id in ids:
                arm.move_to_zero_mit(motor_id, kp=kp, kd=kd)

    def move_joints_mit(self,
                       left_positions: Optional[List[float]] = None,
                       right_positions: Optional[List[float]] = None,
                       kp: float = 5.0,
                       kd: float = 0.5):
        """
        同时控制左右臂关节位置 (MIT模式)

        参数:
            left_positions (List[float], optional): 左臂各关节位置 [pos1, pos2, ...]
            right_positions (List[float], optional): 右臂各关节位置
            kp (float): 位置增益
            kd (float): 速度增益

        示例:
            >>> # 左右臂对称运动
            >>> robot.move_joints_mit(
            >>>     left_positions=[0.1, 0.2, 0.3, 0.4, 0, 0, 0],
            >>>     right_positions=[0.1, 0.2, 0.3, 0.4, 0, 0, 0],
            >>>     kp=10.0, kd=1.0
            >>> )
        """
        if left_positions:
            for i, pos in enumerate(left_positions):
                motor_id = i + 1
                if motor_id in self.left_arm.motor_ids:
                    self.left_arm.move_joint_mit(motor_id, position=pos, kp=kp, kd=kd)

        if right_positions:
            for i, pos in enumerate(right_positions):
                motor_id = i + 1
                if motor_id in self.right_arm.motor_ids:
                    self.right_arm.move_joint_mit(motor_id, position=pos, kp=kp, kd=kd)

    # ==================== CSP 模式控制 ====================

    def move_joints_csp(self,
                       left_positions: Optional[List[float]] = None,
                       right_positions: Optional[List[float]] = None):
        """
        同时控制左右臂关节位置 (CSP模式)

        参数:
            left_positions (List[float], optional): 左臂各关节位置
            right_positions (List[float], optional): 右臂各关节位置
        """
        if left_positions:
            for i, pos in enumerate(left_positions):
                motor_id = i + 1
                if motor_id in self.left_arm.motor_ids:
                    self.left_arm.move_joint_csp(motor_id, position=pos)

        if right_positions:
            for i, pos in enumerate(right_positions):
                motor_id = i + 1
                if motor_id in self.right_arm.motor_ids:
                    self.right_arm.move_joint_csp(motor_id, position=pos)

    # ==================== 状态查询 ====================

    def get_all_status(self) -> Dict[str, Dict]:
        """
        获取所有机械臂的状态

        返回:
            dict: {
                'left': {motor_id: status_info, ...},
                'right': {motor_id: status_info, ...}
            }
        """
        return {
            'left': self.left_arm.get_all_status(),
            'right': self.right_arm.get_all_status()
        }

    def get_left_status(self, motor_id: Optional[int] = None) -> Dict:
        """获取左臂状态"""
        if motor_id:
            return self.left_arm.get_status(motor_id)
        return self.left_arm.get_all_status()

    def get_right_status(self, motor_id: Optional[int] = None) -> Dict:
        """获取右臂状态"""
        if motor_id:
            return self.right_arm.get_status(motor_id)
        return self.right_arm.get_all_status()

    def show_all_status(self):
        """显示所有机械臂的状态"""
        log_output("="*120, "INFO", self.log)
        log_output("左臂状态 (can0)", "INFO", self.log)
        log_output("="*120, "INFO", self.log)
        self.left_arm.show_motor_status(show_header=True)

        log_output("\n" + "="*120, "INFO", self.log)
        log_output("右臂状态 (can1)", "INFO", self.log)
        log_output("="*120, "INFO", self.log)
        self.right_arm.show_motor_status(show_header=True)
        log_output("="*120, "INFO", self.log)

    def show_left_status(self):
        """显示左臂状态"""
        self.left_arm.show_motor_status()

    def show_right_status(self):
        """显示右臂状态"""
        self.right_arm.show_motor_status()

    # ==================== 零点设置 ====================

    def set_zero_all(self, motor_ids: Optional[List[int]] = None):
        """设置所有机械臂的零点"""
        for arm in self.arms:
            ids = motor_ids if motor_ids else arm.motor_ids
            for motor_id in ids:
                arm.set_zero(motor_id)

    def set_zero_left(self, motor_ids: Optional[List[int]] = None):
        """设置左臂零点"""
        ids = motor_ids if motor_ids else self.left_arm.motor_ids
        for motor_id in ids:
            self.left_arm.set_zero(motor_id)

    def set_zero_right(self, motor_ids: Optional[List[int]] = None):
        """设置右臂零点"""
        ids = motor_ids if motor_ids else self.right_arm.motor_ids
        for motor_id in ids:
            self.right_arm.set_zero(motor_id)