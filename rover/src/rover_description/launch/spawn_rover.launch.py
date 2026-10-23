import os
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    SetEnvironmentVariable,
    UnsetEnvironmentVariable,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('rover_description')
    ros_gz_sim_share = get_package_share_directory('ros_gz_sim')
    urdf_path = os.path.join(pkg_share, 'urdf', 'rover.urdf')
    world_path = os.path.join(pkg_share, 'worlds', 'empty.sdf')

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': Path(urdf_path).read_text(encoding='utf-8'),
            'use_sim_time': True,
        }],
        output='screen',
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_share, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_path}'}.items(),
    )

    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/camera@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
        ],
        remappings=[
            ('/camera', '/camera/image_raw'),
            ('/camera_info', '/camera/camera_info'),
        ],
        output='screen',
    )

    spawn_rover = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'differential_drive_rover',
            '-z', '0.03',
        ],
        output='screen',
    )

    snap_gui_environment = [
        UnsetEnvironmentVariable(name)
        for name in os.environ
        if name.startswith(('SNAP', 'GTK', 'GDK', 'QT_'))
    ]

    return LaunchDescription([
        *snap_gui_environment,
        SetEnvironmentVariable('GZ_PARTITION', 'rover_sim'),
        gazebo,
        robot_state_publisher,
        ros_gz_bridge,
        spawn_rover,
    ])
