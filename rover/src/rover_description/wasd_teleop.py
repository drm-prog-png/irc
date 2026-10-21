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
Release all keys : Stop
CTRL-C to exit
---------------------------------------------
"""


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
        twist.linear.y = 0.0
        twist.linear.z = 0.0
        twist.angular.x = 0.0
        twist.angular.y = 0.0
        twist.angular.z = angular_z
        self.publisher_.publish(twist)

    def start(self):
        self.settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin.fileno())
        print(msg, flush=True)

        try:
            while rclpy.ok():
                key = self.get_key()

                linear_x = 0.0
                angular_z = 0.0

                if key is None:
                    pass
                elif key in ('w', 'W'):
                    linear_x = 1.0
                elif key in ('s', 'S'):
                    linear_x = -1.0
                elif key in ('a', 'A'):
                    angular_z = 1.5
                elif key in ('d', 'D'):
                    angular_z = -1.5
                elif key == '\x03':
                    break

                self.publish_cmd(linear_x, angular_z)
                time.sleep(0.02)
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
