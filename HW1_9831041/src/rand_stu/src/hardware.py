#!/usr/bin/python3
import rospy
from rand_stu.msg import Stu
 
def callback(data):
    rospy.loginfo(data)
     
def listener():
    rospy.init_node('hardware', anonymous=True)
    rospy.Subscriber("hard", Stu, callback)
    rospy.spin()

if __name__ == '__main__':
    listener()