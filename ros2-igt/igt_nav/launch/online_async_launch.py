import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, EmitEvent, LogInfo,
                            RegisterEventHandler)
from launch.conditions import IfCondition
from launch.events import matches_action
from launch.substitutions import (AndSubstitution, LaunchConfiguration,
                                  NotSubstitution)
from launch_ros.actions import LifecycleNode
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from lifecycle_msgs.msg import Transition
from launch_ros.actions import Node


def generate_launch_description():
    pkg_igt_nav = get_package_share_directory('igt_nav')
    autostart = LaunchConfiguration('autostart')
    use_lifecycle_manager = LaunchConfiguration("use_lifecycle_manager")
    use_sim_time = LaunchConfiguration('use_sim_time')
    slam_params_file = LaunchConfiguration('slam_params_file')
    with_rviz = LaunchConfiguration('with_rviz')
    rviz_config_file = os.path.join(pkg_igt_nav, 'rviz', 'slam_toolbox_mapping.rviz')


    declare_autostart_cmd = DeclareLaunchArgument('autostart', default_value='true',
        description='Automatically startup the slamtoolbox. '
                    'Ignored when use_lifecycle_manager is true.')
    
    declare_use_lifecycle_manager = DeclareLaunchArgument(
        'use_lifecycle_manager', default_value='false',
        description='Enable bond connection during node activation')
    
    declare_use_sim_time_argument = DeclareLaunchArgument('use_sim_time',
        default_value='true',
        description='Use simulation/Gazebo clock')
    
    declare_slam_params_file_cmd = DeclareLaunchArgument('slam_params_file',
        default_value=os.path.join(pkg_igt_nav, 'config', 'mapper_params_online_async.yaml'),
        description='Full path to the ROS2 parameters file to use for the slam_toolbox node')
    
    declare_with_rviz = DeclareLaunchArgument('with_rviz',
				default_value='true',
				description="Launch rviz or not")
    
    start_async_slam_toolbox_node = LifecycleNode(
        parameters=[
          slam_params_file,
          {
            'use_lifecycle_manager': use_lifecycle_manager,
            'use_sim_time': use_sim_time
          }
        ],
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        namespace=''
    )

    configure_event = EmitEvent(
        event=ChangeState(
          lifecycle_node_matcher=matches_action(start_async_slam_toolbox_node),
          transition_id=Transition.TRANSITION_CONFIGURE
        ),
        condition=IfCondition(AndSubstitution(autostart, NotSubstitution(use_lifecycle_manager)))
    )

    activate_event = RegisterEventHandler(
        OnStateTransition(
            target_lifecycle_node=start_async_slam_toolbox_node,
            start_state="configuring",
            goal_state="inactive",
            entities=[
                LogInfo(msg="[LifecycleLaunch] Slamtoolbox node is activating."),
                EmitEvent(event=ChangeState(
                    lifecycle_node_matcher=matches_action(start_async_slam_toolbox_node),
                    transition_id=Transition.TRANSITION_ACTIVATE
                ))
            ]
        ),
        condition=IfCondition(AndSubstitution(autostart, NotSubstitution(use_lifecycle_manager)))
    )

    rviz2 = Node(package='rviz2', executable='rviz2',
					name='rviz2',
					arguments=['-d', rviz_config_file],
					parameters=[{'use_sim_time': use_sim_time}],
					output='screen',
					condition=IfCondition(with_rviz))

    ld = LaunchDescription()

    ld.add_action(declare_autostart_cmd)
    ld.add_action(declare_use_lifecycle_manager)
    ld.add_action(declare_use_sim_time_argument)
    ld.add_action(declare_slam_params_file_cmd)
    ld.add_action(start_async_slam_toolbox_node)
    ld.add_action(configure_event)
    ld.add_action(activate_event)
    ld.add_action(declare_with_rviz)
    ld.add_action(rviz2)

    return ld