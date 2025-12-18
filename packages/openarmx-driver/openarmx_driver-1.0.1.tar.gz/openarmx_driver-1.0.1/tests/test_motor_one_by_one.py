#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   test_motor_one_by_one.py
@Time    :   2025/12/16 15:33:02
@Author  :   Wei Lindong 
@Version :   1.0
@Desc    :   测试所有电机逐个运动
'''

import sys
import os

# 添加 src 目录到 Python 路径
# tests/ 和 src/ 是同级目录，需要先回到父目录再进入 src
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)

# 导入 Arm 类和异常
from openarmx_driver import Arm
import time

if __name__ == "__main__":
    # 运动参数（可调）
    kp = 10.0
    kd = 1.0
    red_max = 0.2

    # 初始化左右臂
    right_arm = Arm(can_channel='can0', side='right')
    left_arm = Arm(can_channel='can1', side='left')

    # 开启左右臂电机
    right_arm.enable_all()
    left_arm.enable_all()

    # 设置为 MIT 模式
    right_arm.set_mode('mit')
    left_arm.set_mode('mit')

    # 逐个运动电机
    for arm in [right_arm, left_arm]:
        for motor_id in arm.motor_ids:
            try:
                arm.move_joint_mit(motor_id, position=-red_max, kp=kp, kd=kd)
                time.sleep(0.5)
                arm.home_joint(motor_id, kp=kp, kd=kd)
                time.sleep(0.5)
            except KeyboardInterrupt:
                print("按下 Ctrl+C,结束----")
                right_arm.disable_all()
                left_arm.disable_all()
                break
    
    
    right_arm.close()
    left_arm.close()
