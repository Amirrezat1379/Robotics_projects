#!/usr/bin/python3

import random_student
from rand_stu.msg import Stu
import rospy

def talker():
    student = random_student.randStudent()
    pub = rospy.Publisher('std_request', Stu, queue_size=10)
    rospy.init_node('std_request', anonymous=True)
    rate = rospy.Rate(1)
    while not rospy.is_shutdown():
        student = random_student.randStudent()
        pub.publish(student)
        rate.sleep()


if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass