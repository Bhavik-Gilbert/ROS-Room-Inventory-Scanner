#!/usr/bin/env python3

""" Action Client Not Required For Submission"""

import rospy
import actionlib
from second_coursework.msg import SearchAction, SearchGoal

class SearchClient():
    def __init__(self):
        self.client: actionlib.SimpleActionClient = actionlib.SimpleActionClient("search_server", SearchAction)

    def send_goal(self, room_name: str, item_name):
        self.client.wait_for_server()
        goal: SearchGoal = SearchGoal(room_name, item_name)
        self.client.send_goal(goal)
        self.client.feedback_cb = self.feedback_callback
        self.client.wait_for_result()

        return self.client.get_result()

    def feedback_callback(self, feedback_msg):
        rospy.loginfo(feedback_msg)

if __name__ == "__main__":
    try:
        rospy.init_node("search_client_node")
        client = SearchClient()
        print(client.send_goal("c", "cake"))
    except rospy.ROSInterruptException:
        pass