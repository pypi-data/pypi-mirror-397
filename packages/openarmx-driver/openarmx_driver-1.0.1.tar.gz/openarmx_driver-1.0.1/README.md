# OpenArmX Driver

Python SDK for OpenArmX robotic arm control via CAN bus.

## 安装

```bash
pip install openarmx-driver
```

## 快速开始

### 单臂控制

```python
from openarmx_driver import Arm

# 创建右臂实例
arm = Arm('can0', side='right')

# 使能电机
arm.enable_all()

# 设置为 MIT 模式
arm.set_mode('mit')

# 移动关节
arm.move_joint_mit(motor_id=1, position=0.5, kp=10.0, kd=1.0)

# 查看状态
arm.show_motor_status()

# 停止
arm.disable_all()
```

### 双臂控制

```python
from openarmx_driver import Robot

# 创建双臂机器人
robot = Robot(left_canid='can0', right_canid='can1')

# 使能所有电机
robot.enable_all()

# 设置模式
robot.set_mode_all('mit')

# 左右臂对称运动
robot.move_joints_mit(
    left_positions=[0.1, 0.2, 0.3, 0, 0, 0, 0],
    right_positions=[0.1, 0.2, 0.3, 0, 0, 0, 0],
    kp=10.0, kd=1.0
)

# 查看状态
robot.show_all_status()

# 停止
robot.disable_all()
```

## 支持的控制模式

- **MIT 模式**: 位置/速度/扭矩混合控制（带 PD 增益）


## License

This project is licensed under the OpenArmX Research and Education License.
Commercial use requires a separate license.
