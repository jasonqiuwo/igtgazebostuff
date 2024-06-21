- Create sub directories
```bash
mkdir colcon_ws
cd colcon_ws
mkdir src
cd src
git clone https://github.com/jasonqiuwo/igtgazebostuff.git
cd ..
```


- Run and open Gazebo world 
```bash
cd colcon_ws
cd src
colcon build --symlink-install 
source install/setup.bash
ros2 launch igt_ignition igt_ignition.launch.py with_bridge:=true
```

- Open RViz and create maps using basic SLAM algorithm 
```bash
source install/setup.bash
ros2 launch igt_nav online_sync_launch.py
```

- Save the map after teleop around and  create the map
```bash
ros2 run nav2_map_server map_saver_cli -f name_of_map_file
```

- Open Navigation using Stack (Remember to add the saved map to folders)
```bash
source install/setup.bash
ros2 launch igt_nav navigation2.launch.py
