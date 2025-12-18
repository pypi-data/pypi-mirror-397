#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   test_motor_all_random.py
@Time    :   2025/12/16
@Author  :   Wei Lindong
@Version :   1.0
@Desc    :   电机随机运动测试
'''

import sys
import os
import time
import random

# 添加 src 目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)

from openarmx_driver import Robot


if __name__ == "__main__":
    # 参数配置
    red_max = 0.3
    time_delay = 0.005
    kp_list = [50, 50, 50, 50, 5, 5, 5, 5]
    kd_list = [5, 5, 5, 5, 0.25, 0.25, 0.25, 0.25]

    # 初始化机器人
    robot = Robot(left_canid='can0', right_canid='can1')

    try:
        # 使能所有电机
        robot.enable_all()
        time.sleep(0.1)

        # 设置运控模式
        robot.set_mode_all('mit')
        time.sleep(0.1)

        # 随机运动循环
        test_id = 0
        while True:
            print(f'test_id:{test_id}')
            test_id += 1

            # 生成随机位置列表
            positions = [
                random.uniform(0.2 * red_max, red_max)
                for _ in range(7)
            ]

            # 左右臂同时移动到随机位置
            for i, pos in enumerate(positions):
                motor_id = i + 1
                kp = kp_list[motor_id - 1] / 2
                kd = kd_list[motor_id - 1] / 2
                robot.left_arm.move_joint_mit(motor_id, position=pos, kp=kp, kd=kd)
                robot.right_arm.move_joint_mit(motor_id, position=pos, kp=kp, kd=kd)
                time.sleep(time_delay)
            time.sleep(1)

            # 回到零位
            robot.move_all_to_zero_mit(kp=5.0, kd=0.5)
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        print(f"错误: {e}")
    finally:
        robot.shutdown()
