import smach

class CheckFeedbackState(smach.State):
	def __init__(self):
		smach.State.__init__(self, outcomes=['succeeded', 'preempted', 'aborted'],
							 input_keys=['feedback_check_feedback'])

	def execute(self, userdata):
		if userdata.feedback_check_feedback.item_name_list is None or userdata.feedback_check_feedback.item_count_list is None:
			return 'aborted'
		if self._preempt_requested:
			return "preempted"

		return "succeeded"