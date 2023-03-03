#!/usr/bin/python3

import math
import rospy
import numpy as np
import tf
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry

class VFHControl:
    def __init__(self, goal_position):
        self.vfh_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.goal_position = goal_position
    
    def get_m_parameter(self, laser_scan):
        ranges = laser_scan.ranges
        m = []
        for i in range(len(ranges)):
            if ranges[i] < float(4):
                m.append(1 - ranges[i]/float(4))
            else:
                m.append(0)
        return m

    # funnction to find Valley
    def find_valley(self, hprime, thresh):
        valley = []
        thisValley = []
        j = 0
        for i in range(len(hprime)):
            if hprime[i] < thresh:
                if j == 0:
                    thisValley.append(i)
                j = 1
            else:
                if len(thisValley) > 0:
                    thisValley.append(i - 1)
                    valley.append(thisValley)
                    thisValley = []
        return valley
    
    # function to get heading
    def current_heading(self, msg: Odometry, mode):
        if mode == "current":
            orientation = msg.pose.pose.orientation
            roll, pitch, yaw = tf.transformations.euler_from_quaternion((
                orientation.x ,orientation.y ,orientation.z ,orientation.w
            )) 
            return float("{:.2f}".format(yaw))
        else:
            position = msg.pose.pose.position
            return float("{:.2f}".format(np.arctan2((self.goal_position[1] - position.y), (self.goal_position[0] - position.x))))
    
    def calculate_goal_angle(self, msg: Odometry):
        robot_heading = self.current_heading(msg, "current")
        goal_heading = self.current_heading(msg, "goal")
        return goal_heading - robot_heading
    
    # function to find best angle to go
    def find_best_angle(self, valley, goal_angle):
        min_diffrence = 99999
        j = 0
        for i in range(len(valley)):
            if min_diffrence < abs(goal_angle - valley[i][0]):
                min_diffrence = abs(valley[i][0] - goal_angle)
                j = i
            if min_diffrence < abs(valley[i][1] - goal_angle):
                min_diffrence = abs(valley[i][1] - goal_angle)
                j = i
        return valley[j][0] + (valley[j][1] - valley[j][0]) / 2



    # function to vfh controll
    def vfh_control(self):
        move = Twist()
        # move.angular.z = 0
        move.linear.x = 0
        self.vfh_pub.publish(move)
        # init laser scan
        laser_scan = rospy.wait_for_message('/scan', LaserScan)
        m = self.get_m_parameter(laser_scan)
        h = np.zeros(len(m) // 5)
        for i in range(len(laser_scan.ranges) // 5):
            for j in range(5):
                h[i] += m[i * 5 + j]
        hprime = np.zeros(len(h))
        for i in range(2, len(h) - 2):
            hprime[i] = (h[i - 2] + 2 * h[i - 1] + 2 * h[i] + 2 * h[i + 1] + h[i + 2]) / 5
        valley = self.find_valley(hprime, 0.1)
        # odometry
        odometry = rospy.wait_for_message('/odom', Odometry)
        goal_angle = self.calculate_goal_angle(odometry)
        goal_angle = int(goal_angle * 180 / np.pi)
        if goal_angle < 0:
            goal_angle += 180
        goal_angle = self.find_best_angle(valley, goal_angle)
        return goal_angle

            
