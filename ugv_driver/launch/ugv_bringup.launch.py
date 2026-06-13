import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.actions import TimerAction



def generate_launch_description():
    # RPLIDAR C1 driver
    lidar = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('sllidar_ros2'),
                         'launch', 'sllidar_c1_launch.py')
        ),
        launch_arguments={'serial_port': '/dev/ttyUSB0'}.items()
    )

    # Static transform: base_link -> laser
    # TODO: replace x and z with measured values (meters)
    # x: lidar offset forward of rotation center, z: height above ground/base
    static_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['--x', '0.0', '--y', '0.0', '--z', '0.15',
                   '--roll', '0', '--pitch', '0', '--yaw', '0',
                   '--frame-id', 'base_link', '--child-frame-id', 'laser']
    )

    # Laser-based odometry (no wheel encoders)
    rf2o = Node(
        package='rf2o_laser_odometry',
        executable='rf2o_laser_odometry_node',
        name='rf2o_laser_odometry',
        parameters=[{
            'laser_scan_topic': '/scan',
            'odom_topic': '/odom',
            'publish_tf': True,
            'base_frame_id': 'base_link',
            'odom_frame_id': 'odom',
            'init_pose_from_topic': '',
            'freq': 10.0,
        }]
    )

    # Motor driver (listens on /cmd_vel)
    motor = Node(
        package='ugv_driver',
        executable='motor_driver_node',
        name='motor_driver_node'
    )

rf2o_delayed = TimerAction(period=3.0, actions=[rf2o])

    
return LaunchDescription([lidar, static_tf, rf2o_delayed, motor])
