#!/usr/bin/env python3

from typing import Any, Dict

import rospy
from second_coursework.srv import GetRoomCoord, GetRoomCoordRequest, GetRoomCoordResponse
from geometry_msgs.msg import Point

rooms: Dict[str, Dict[str, Any]] = {
    "A": {
        "Index": 0,
        "Points": [Point(1.69, 8.87, 0), Point(2.85, 9.19, 0), Point(2.05, 8.31, 0), Point(1.21, 7.52, 0)]
    },
    "B": {
        "Index": 0,
        "Points": [Point(6.02, 8.59, 0), Point(4.89, 9.37, 0), Point(7.42, 7.42, 0), Point(5.99, 6.94, 0)]
    },
    "C": {
        "Index": 0,
        "Points": [Point(11.59, 9.51, 0), Point(9.55, 8.90, 0), Point(9.35, 7.05, 0), Point(10.63, 8.31, 0)]
    },
    "D": {
        "Index": 0,
        "Points": [Point(1.51, 4.34, 0), Point(2.76, 1.27, 0), Point(1.95, 3.29, 0), Point(1.07, 1.05, 0)]
    },
    "E": {
        "Index": 0,
        "Points": [Point(5.85, 3.14, 0), Point(6.28, 1.55, 0), Point(7.37, 1.53, 0), Point(4.63, 5.09, 0)]
    },
    "F": {
        "Index": 0,
        "Points": [Point(11.90, 0.89, 0), Point(9.53, 3.64, 0), Point(9.39, 1.32, 0), Point(12.13, 1.07, 0)]
    }
}


def get_room_coord(req: GetRoomCoordRequest) -> GetRoomCoordResponse:
    global rooms
    room = req.roomname.upper()

    if room in rooms.keys():
        go_to_point: Point = rooms[room]["Points"][rooms[room]["Index"]]
        rooms[room]["Index"] = (rooms[room]["Index"] + 1) % 4
        return GetRoomCoordResponse(go_to_point)

    rospy.logerr("Room provided not in list")
    return None


def main():
    rospy.init_node('roomservice')

    get_room_coord_srv = rospy.Service('GetRoomCoord', GetRoomCoord, get_room_coord)
    rospy.spin()


if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
