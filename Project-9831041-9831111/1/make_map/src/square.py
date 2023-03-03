#!/usr/bin/python3

import math
# from turtle import position
import rospy
import numpy as np
import tf
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
import matplotlib.pyplot as plt

class PIDController():
    def __init__(self):
        rospy.loginfo("Start making")
        self.cmd_vel = rospy.Publisher('/cmd_vel', Twist, queue_size=5)
        rospy.init_node('square', anonymous=False)
        def shutdown():
            rospy.loginfo("Stopping the robot...")
            rospy.sleep(1)
        rospy.on_shutdown(shutdown)
        self.mode = rospy.get_param("/square/mode")
        mode = self.mode
        modes = {}
        modes["maze"] = [0, 3, 22, 0.1, 0.5]
        self.k_i = modes[mode][0]
        self.k_p = modes[mode][1]
        self.k_d = modes[mode][2]
        self.v = modes[mode][3]
        self.D = modes[mode][4]
        self.goalx = 3
        self.goaly = -1
        self.dt = 0.005
        rate = 1/self.dt
        self.r = rospy.Rate(rate)
        self.errs = []
        rospy.loginfo("Finished")

    def follow_wall(self):
        sum_i_theta = 0
        previous_error = 0
        move = Twist()
        move.angular.z = 0
        move.linear.x = self.v
        while not rospy.is_shutdown():
            self.cmd_vel.publish(move)

            laser_scan = rospy.wait_for_message("/scan", LaserScan)
            front_distance = min(laser_scan.ranges[:35])
            err = min([front_distance, min(laser_scan.ranges[35:180])]) - self.D   # return distance from side wall
            if err == float('inf'):
                err = 10
            sum_i_theta += err * self.dt
            P = self.k_p * err
            I = self.k_i * sum_i_theta
            D = self.k_d * (err - previous_error)
            move.angular.z = P + I + D 
            previous_error = err       
            if front_distance < self.D:
                move.linear.x = 0
            else:
                move.linear.x = self.v                        
            self.r.sleep()
            
if __name__ == '__main__':
    try:
        pi = math.pi
        pidc = PIDController()
        pidc.follow_wall()
    except rospy.ROSInterruptException:
        rospy.loginfo("Navigation terminated.")