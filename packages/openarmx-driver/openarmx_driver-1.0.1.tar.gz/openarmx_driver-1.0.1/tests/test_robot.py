#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   test_robot.py
@Time    :   2025/12/16
@Author  :   Wei Lindong
@Version :   1.0
@Desc    :   Robot 类测试示例（自动检测并启用 CAN）
'''

import sys
import os
import time

# 添加 src 目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)

from openarmx_driver import Robot


if __name__ == "__main__":
    print("="*60)
    print("Robot 类测试 - 自动 CAN 检测和启用")
    print("="*60)

    # Robot 会自动检测并启用 CAN 接口
    # 如果 can0 或 can1 未启用，会自动尝试启用
    with Robot(left_canid='can0', right_canid='can1') as robot:

        # 使能所有电机
        robot.enable_all()

        # 设置为 MIT 模式
        robot.set_mode_all('mit')

        # 显示所有电机状态
        robot.show_all_status()

        # 左右臂对称运动
        robot.move_joints_mit(
            left_positions=[0.1, 0.2, 0.3, 0, 0, 0, 0],
            right_positions=[0.1, 0.2, 0.3, 0, 0, 0, 0],
            kp=10.0,
            kd=1.0
        )
        time.sleep(2)

        # 回到零位
        robot.move_all_to_zero_mit(kp=5.0, kd=0.5)
        time.sleep(1)

        # 停止所有电机
        robot.disable_all()
