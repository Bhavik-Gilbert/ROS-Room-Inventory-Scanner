#!/usr/bin/env python3

import roslib
import rospy
import actionlib
import math
from second_coursework.msg import SearchAction, SearchGoal, SearchFeedback, SearchResult
from second_coursework.srv import GetRoomCoord, GetRoomCoordRequest
from move_base_msgs.msg import MoveBaseAction
import smach
from smach_ros import ServiceState, SimpleActionState

from states import check_pose, yolo_process, check_feedback

roslib.load_manifest('second_coursework')

class SeachServer:
    feedback: SearchFeedback = SearchFeedback()
    result: SearchResult = SearchResult()

    def __init__(self):
        self.server = actionlib.SimpleActionServer("search_server", SearchAction, execute_cb=self.execute, auto_start=False)
        self.server.start()

    def execute(self, request: SearchGoal):
        self.feedback.item_name_list = []
        self.feedback.item_count_list = []

        def cb_child_termination(outcome_map):
            return True

        def cb_out(outcome_map):
            if outcome_map['OBJECT_MACHINE'] == 'succeeded':
                return 'succeeded'
            else:
                return 'aborted'

        # Create concurrence machine
        cc = smach.Concurrence(outcomes=['succeeded', 'aborted', 'preempted'],
                               default_outcome='succeeded',
                               child_termination_cb=cb_child_termination,
                               outcome_cb=cb_out)

        with cc:
            # Create move state machine
            sm_move = smach.StateMachine(outcomes=['succeeded', 'aborted', 'preempted'])
            sm_move.userdata.point_data = None
            sm_move.userdata.move_base_data = None
            with sm_move:
                smach.StateMachine.add('GETPOSE',
                                       ServiceState('/GetRoomCoord', GetRoomCoord,
                                                    request=GetRoomCoordRequest(request.roomname),
                                                    response_slots=['point']),
                                       transitions={'succeeded': 'CHECKPOSE', 'aborted': 'aborted', 'preempted': 'preempted'},
                                       remapping={'point': 'point_data'}
                                       )
                smach.StateMachine.add('CHECKPOSE', check_pose.CheckPoseState(),
                                       transitions={'aborted': 'GETPOSE', 'succeeded': 'MOVETOPOSE', 'preempted': 'preempted'},
                                       remapping={'check_point_data': 'point_data'}
                                       )

                @smach.cb_interface(input_keys=['move_point_data'])
                def cb_move_base_goal(userdata, move_base_goal):
                    move_base_goal.target_pose.header.frame_id = "map"
                    move_base_goal.target_pose.header.stamp = rospy.Time.now()

                    move_base_goal.target_pose.pose.position.x = userdata.move_point_data.x
                    move_base_goal.target_pose.pose.position.y = userdata.move_point_data.y
                    move_base_goal.target_pose.pose.orientation.w = math.cos(-math.pi / 4)

                    return move_base_goal

                smach.StateMachine.add('MOVETOPOSE',
                                       SimpleActionState('/move_base', MoveBaseAction, goal_cb=cb_move_base_goal),
                                       transitions={'succeeded': 'GETPOSE', 'aborted': 'GETPOSE', 'preempted': 'preempted'},
                                       remapping={'move_point_data': 'point_data'}
                                       )

            # Create identifier state machine
            sm_identifier = smach.StateMachine(outcomes=['succeeded', 'aborted', 'preempted'])
            sm_identifier.userdata.action_server_feedback = self.feedback
            sm_identifier.userdata.find_item_name = request.itemname
            with sm_identifier:
                smach.StateMachine.add('OBJECTIDENTIFIER', yolo_process.ObjectIdentifierState(),
                                       transitions={'succeeded': 'succeeded', 'aborted': 'aborted', 'preempted': 'preempted'},
                                       remapping={'find_item': 'find_item_name','object_identifier_feedback': 'action_server_feedback'}
                                       )

            # Create feedback state machine
            sm_feedback = smach.StateMachine(outcomes=['succeeded', 'aborted', 'preempted'])
            sm_feedback.userdata.action_server_feedback = self.feedback
            with sm_feedback:
                smach.StateMachine.add('CHECKFEEDBACK', check_feedback.CheckFeedbackState(),
                                        transitions={'succeeded': 'WRITEFEEDBACK', 'aborted': 'aborted', 'preempted': 'preempted'},
                                        remapping={'feedback_check_feedback': 'action_server_feedback'}
                                        )

                @smach.cb_interface(outcomes=['succeeded'])
                def feedback_cb(cb):
                    rate: rospy.Rate = rospy.Rate(5)
                    for i in range(5):
                        self.server.publish_feedback(self.feedback)
                        rate.sleep()
                    return 'succeeded'

                smach.StateMachine.add('WRITEFEEDBACK', smach.CBState(feedback_cb),
                                       transitions={'succeeded': 'CHECKFEEDBACK'}
                                       )

            # Add concurrence states
            smach.Concurrence.add('MOVEMENT_MACHINE', sm_move)
            smach.Concurrence.add('OBJECT_MACHINE', sm_identifier)
            smach.Concurrence.add('FEEDBACK_MACHINE', sm_feedback)

        outcome = cc.execute()

        self.result.item_name_list = self.feedback.item_name_list
        self.result.item_count_list = self.feedback.item_count_list

        if outcome == "succeeded":
            self.server.set_succeeded(self.result)
            self.result.time = rospy.Time.now()
        elif outcome == "preempted":
            self.server.set_preempted(self.result)
            rospy.logerr("Server closed preemptively")
        else:
            self.server.set_aborted(self.result)
            rospy.logerr("Server aborted")


def main():
    rospy.init_node('main_node')
    server = SeachServer()
    rospy.spin()


if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
