# ROS-Room-Inventory-Scanner

## Badges
![GitHub last commit](https://img.shields.io/github/last-commit/Bhavik-Gilbert/ROS-Room-Inventory-Scanner)
![GitHub contributors](https://img.shields.io/github/contributors/Bhavik-Gilbert/ROS-Room-Inventory-Scanner)
![Lines of code](https://img.shields.io/tokei/lines/github/Bhavik-Gilbert/ROS-Room-Inventory-Scanner)
![GitHub repo size](https://img.shields.io/github/repo-size/Bhavik-Gilbert/ROS-Room-Inventory-Scanner)    

![GitHub top language](https://img.shields.io/github/languages/top/Bhavik-Gilbert/ROS-Room-Inventory-Scanner)
![GitHub language count](https://img.shields.io/github/languages/count/Bhavik-Gilbert/ROS-Room-Inventory-Scanner)

## About
Our robot, a TurtleBot3, is working in a store doing the inventory of items overnight. It must go around the building noting the items it sees. The owner is interested in all items, but in one above all: cake. The inventory robot must navigate on a specific pattern while reporting the objects that it sees, until it finds cake.

## Project structure
The package is called `ROS Storeroom Inventory Scanner Package` where all functionality resides.

## Installation instructions
To install the software and use it in your local development environment, you must first set up a working ros workspace. From the ros workspace:

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Add package to your ros workspace directory


##Run instructions
To run the software, the package must be correctly installed into a working ros workspace, alongside all the required libraries have been installed.

Setup:
Specify a room to search in and item to search for in the call_search_server.py file before running to get change objective to find a cake in room c.

Terminal 1:
```
$ roscore
```

Terminal 2:
```
$ roslaunch rosplan_stage_demo empty_stage_single_robot.launch
```

Terminal 3:
```
$ rosrun rviz rviz -d `rospack find rosplan_stage_demo`/config/rosplan_stage_demo.rviz
```

Terminal 4:
```
$ rosrun "ROS Storeroom Inventory Scanner Package" roomservice_node.py
```

Terminal 5:
```
$ rosrun "ROS Storeroom Inventory Scanner Package" main_node.py
```

Terminal 6:
```
$ rosrun "ROS Storeroom Inventory Scanner Package" call_search_server.py
```

## Sources
The packages used by this application are specified in `requirements.txt`
