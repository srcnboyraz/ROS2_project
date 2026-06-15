#!/usr/bin/env python3
"""Differential drive motor driver node for dual BTS7960 (IBT-2) modules."""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from gpiozero import PWMOutputDevice, DigitalOutputDevice

# Left side (module 1)
LEFT_EN, LEFT_RPWM, LEFT_LPWM = 17, 18, 27
# Right side (module 2)
RIGHT_EN, RIGHT_RPWM, RIGHT_LPWM = 22, 23, 24

MAX_LINEAR = 0.3     # m/s at full throttle (rough estimate, tune later)
MAX_ANGULAR = 0.5    # rad/s at full throttle
CMD_TIMEOUT = 0.5    # seconds; stop if no command received
LEFT_TRIM  = 1.0 
RIGHT_TRIM = 1.0
DEAD_ZONE = 0.15


class MotorSide:
    def __init__(self, en_pin, rpwm_pin, lpwm_pin):
        self.en = DigitalOutputDevice(en_pin)
        self.rpwm = PWMOutputDevice(rpwm_pin, frequency=1000)
        self.lpwm = PWMOutputDevice(lpwm_pin, frequency=1000)
        self.en.on()

    def set_speed(self, value):
        value = max(-1.0, min(1.0, value))
        if abs(value) < DEAD_ZONE:
            value = 0.0
        elif value > 0:
            value = DEAD_ZONE + (1.0 - DEAD_ZONE) * value
        else:
            value = -(DEAD_ZONE + (1.0 - DEAD_ZONE) * abs(value))
        
        if value >= 0:
            self.lpwm.value = 0
            self.rpwm.value = value
        else:
            self.rpwm.value = 0
            self.lpwm.value = -value

    def stop(self):
        self.rpwm.value = 0
        self.lpwm.value = 0


class MotorDriverNode(Node):
    def __init__(self):
        super().__init__('motor_driver_node')
        self.left = MotorSide(LEFT_EN, LEFT_RPWM, LEFT_LPWM)
        self.right = MotorSide(RIGHT_EN, RIGHT_RPWM, RIGHT_LPWM)
        self.sub = self.create_subscription(Twist, 'cmd_vel', self.on_cmd_vel, 10)
        self.last_cmd_time = self.get_clock().now()
        self.timer = self.create_timer(0.1, self.watchdog)
        self.get_logger().info('Motor driver ready, listening on /cmd_vel')

    def on_cmd_vel(self, msg: Twist):
        self.last_cmd_time = self.get_clock().now()
        linear = msg.linear.x / MAX_LINEAR      # normalize to [-1, 1]
        angular = msg.angular.z / MAX_ANGULAR
        left_speed = (linear - angular) * LEFT_TRIM
        right_speed = (linear + angular) * RIGHT_TRIM
        self.left.set_speed(left_speed)
        self.right.set_speed(right_speed)

    def watchdog(self):
        elapsed = (self.get_clock().now() - self.last_cmd_time).nanoseconds / 1e9
        if elapsed > CMD_TIMEOUT:
            self.left.stop()
            self.right.stop()

    def shutdown(self):
        self.left.stop()
        self.right.stop()


def main():
    rclpy.init()
    node = MotorDriverNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.shutdown()
        node.destroy_node()


if __name__ == '__main__':
    main()
