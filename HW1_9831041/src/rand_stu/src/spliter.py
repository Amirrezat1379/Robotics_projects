#!/usr/bin/python3
import rospy
from rand_stu.msg import Stu
 
def callback(data):
    student = data
    if student.departement == "Software":
        pub = rospy.Publisher('soft', Stu, queue_size=10)
    else:
        pub = rospy.Publisher('hard', Stu, queue_size=10)
    rate = rospy.Rate(1)
    pub.publish(student)
    rate.sleep()
     
def listener():
    rospy.init_node('spliter', anonymous=True)
    rospy.Subscriber("std_request", Stu, callback)
    rospy.spin()

if __name__ == '__main__':
    listener()