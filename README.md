# Rover simulation (ROS 2 Jazzy)

This package uses Gazebo Sim through `ros_gz_sim` and `ros_gz_bridge`; it does
not use Gazebo Classic or `gazebo_ros`.

Install the Jazzy simulation packages if they are not already installed:

```bash
sudo apt install ros-jazzy-ros-gz ros-jazzy-robot-state-publisher
```

Build and launch from the `rover` workspace:

```bash
source /opt/ros/jazzy/setup.bash
cd rover
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
ros2 launch rover_description spawn_rover.launch.py
```

The launch file starts Gazebo Sim with a local ground-plane world, spawns the
rover from `robot_description`, and bridges `/cmd_vel`, `/odom`, `/tf`, `/imu`,
and `/clock` between ROS and Gazebo. For example, run
`ros2 run rover_description wasd_teleop.py` in another sourced terminal to
drive the rover with the keyboard: W/S move forward/backward, A/D turn left/right,
and Space stops immediately. Releasing a movement key stops after the terminal's
key-repeat timeout.
