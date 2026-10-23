#!/usr/bin/env python3

import select
import sys
import termios
import tty
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node

msg = """
---------------------------------------------
Hold keys to move:
W : Forward
S : Backward
A : Turn Left
D : Turn Right
Release all keys : Stop shortly after release
SPACE : Stop immediately
CTRL-C to exit
---------------------------------------------
"""

LINEAR_SPEED = 0.2
ANGULAR_SPEED = 0.4
LINEAR_ACCELERATION = 0.8
ANGULAR_ACCELERATION = 5.0
KEY_TIMEOUT = 0.6


class WASDTeleop(Node):
    def __init__(self):
        super().__init__('wasd_teleop')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.settings = None

    def get_key(self):
        if not select.select([sys.stdin], [], [], 0.05)[0]:
            return None
        return sys.stdin.read(1)

    def publish_cmd(self, linear_x, angular_z):
        twist = Twist()
        twist.linear.x = linear_x
        twist.angular.z = angular_z
        self.publisher_.publish(twist)

    def start(self):
        self.settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin.fileno())
        print(msg, flush=True)

        try:
            linear_x = 0.0
            angular_z = 0.0
            target_linear_x = 0.0
            target_angular_z = 0.0
            last_key_time = None
            last_update_time = time.monotonic()

            while rclpy.ok():
                key = self.get_key()

                if key is None:
                    pass
                elif key in ('w', 'W'):
                    target_linear_x = LINEAR_SPEED
                    target_angular_z = 0.0
                    last_key_time = time.monotonic()
                elif key in ('s', 'S'):
                    target_linear_x = -LINEAR_SPEED
                    target_angular_z = 0.0
                    last_key_time = time.monotonic()
                elif key in ('a', 'A'):
                    target_linear_x = 0.0
                    target_angular_z = ANGULAR_SPEED
                    last_key_time = time.monotonic()
                elif key in ('d', 'D'):
                    target_linear_x = 0.0
                    target_angular_z = -ANGULAR_SPEED
                    last_key_time = time.monotonic()
                elif key == ' ':
                    linear_x = 0.0
                    angular_z = 0.0
                    target_linear_x = 0.0
                    target_angular_z = 0.0
                    last_key_time = None
                elif key == '\x03':
                    break

                now = time.monotonic()
                if (
                    last_key_time is not None
                    and now - last_key_time > KEY_TIMEOUT
                ):
                    target_linear_x = 0.0
                    target_angular_z = 0.0
                    last_key_time = None

                elapsed = now - last_update_time
                max_linear_change = LINEAR_ACCELERATION * elapsed
                max_angular_change = ANGULAR_ACCELERATION * elapsed
                linear_x += max(
                    -max_linear_change,
                    min(target_linear_x - linear_x, max_linear_change),
                )
                angular_z += max(
                    -max_angular_change,
                    min(target_angular_z - angular_z, max_angular_change),
                )
                last_update_time = now

                self.publish_cmd(linear_x, angular_z)
        finally:
            self.publish_cmd(0.0, 0.0)
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)


def main(args=None):
    rclpy.init(args=args)
    node = WASDTeleop()
    node.start()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
