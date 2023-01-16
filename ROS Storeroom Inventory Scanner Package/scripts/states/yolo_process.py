import smach
import rospy

import os
from pathlib import Path
from cv_bridge import CvBridge
import cv2
from yolov4 import Detector
from sensor_msgs.msg import Image

class YOLODetector:
    def __init__(self):
        self.bridge = CvBridge()
        self.cv_image = None
        self.frame = 0
        self.skip = 20  # Processes 1 in every 20 frames
        self.cam_subs = rospy.Subscriber('/camera/image', Image, self.img_callback)
        meta_path =  os.path.join(os.getcwd().parent.absolute(), 'darknet/cfg/coco.data')
        self.detector = Detector(gpu_id=0, config_path='/opt/darknet/cfg/yolov4.cfg',
                                 weights_path='/opt/darknet/yolov4.weights',
                                 lib_darknet_path='/opt/darknet/libdarknet.so',
                                 meta_path=meta_path)

    def img_callback(self, msg):
        if self.frame % self.skip == 0:  # Update frame
            self.cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
        else: # Clear frame
            self.cv_image = None
        self.frame = (self.frame + 1) % self.skip  # This keeps self.frame between 0 and self.skip-1, avoiding overflows

    def find_items(self):
        detections = []
        if self.cv_image is not None:
            cv_img_copy = self.cv_image.copy()
            img_arr = cv2.resize(cv_img_copy, (self.detector.network_width(), self.detector.network_height()))
            detections = self.detector.perform_detect(image_path_or_buf=img_arr, show_image=True)

        return detections

class ObjectIdentifierState(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['succeeded', 'preempted', 'aborted'],
                             input_keys=['find_item', 'object_identifier_feedback'])

    def execute(self, userdata):
        try:
            yolo_ros: YOLODetector = YOLODetector()
        except:
            rospy.logerr("Yolo detector class failed to initialise")
            return "aborted"

        while userdata.find_item not in userdata.object_identifier_feedback.item_name_list:
            if self._preempt_requested:
                return "preempted"

            detections = []

            try:
                detections = yolo_ros.find_items()
            except:
                rospy.logerr("Failed to get detection list")

            for detection in detections:
                if detection.class_name in userdata.object_identifier_feedback.item_name_list:
                    index: int = userdata.object_identifier_feedback.item_name_list.index(detection.class_name)
                    userdata.object_identifier_feedback.item_count_list[index] += 1
                else:
                    userdata.object_identifier_feedback.item_name_list.append(detection.class_name)
                    userdata.object_identifier_feedback.item_count_list.append(1)

        return "succeeded"