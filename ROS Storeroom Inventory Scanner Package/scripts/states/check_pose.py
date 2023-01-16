import smach
import rospy

class CheckPoseState(smach.State):
	def __init__(self):
		smach.State.__init__(self, outcomes=['succeeded', 'aborted', 'preempted'],
							input_keys = ['check_point_data']
							)

	def execute(self, userdata):
		if self._preempt_requested:
			return "preempted"
		if userdata.check_point_data is None:
			return "aborted"

		return "succeeded"