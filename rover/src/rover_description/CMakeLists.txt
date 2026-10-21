cmake_minimum_required(VERSION 3.8)
project(rover_description)

find_package(ament_cmake REQUIRED)

install(
  PROGRAMS
    wasd_teleop.py
  DESTINATION lib/${PROJECT_NAME}
)

install(
  DIRECTORY urdf launch
  DESTINATION share/${PROJECT_NAME}
)
ament_package()
