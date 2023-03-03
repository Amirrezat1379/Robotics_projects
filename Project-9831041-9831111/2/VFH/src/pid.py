#!/usr/bin/python3

import math
import rospy
import numpy as np
import tf
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
import vfh

class PIDController:
    def __init__(self):
        self.cmd_vel = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        # init node
        rospy.init_node('pid', anonymous=False)
        # shutdown node
        def shutdown():
            rospy.loginfo("Stopping the robot...")
            self.cmd_vel.publish(Twist())
            rospy.sleep(1)
        rospy.on_shutdown(shutdown)
        self.goal_position = [-8, -8]
        modes = {}
        mode = "path_to_goal"
        modes["path_to_goal"] = [0, 1.5, 15, 0.3, 0.5]
        self.k_i = modes[mode][0]
        self.k_p = modes[mode][1]
        self.k_d = modes[mode][2]
        self.v = modes[mode][3]
        self.D = modes[mode][4]

        self.dt = 0.005
        rate = 1/self.dt
        
        self.r = rospy.Rate(rate)

    def distance_to_goal(self, odometry):
        position = odometry.pose.pose.position
        return math.sqrt((self.goal_position[0] - position.x)**2 + (self.goal_position[1] - position.y)**2)

    # heading of the robot 
    def get_heading(self):
        # waiting for the most recent message from topic /odom
        msg = rospy.wait_for_message("/odom" , Odometry)
        orientation = msg.pose.pose.orientation
        # convert quaternion to odom
        roll, pitch, yaw = tf.transformations.euler_from_quaternion((orientation.x ,orientation.y ,orientation.z ,orientation.w)) 
        return yaw
    
    def start(self):
        sum_i_theta = 0
        previous_error = 0
        move = Twist()
        move.angular.z = 0
        move.linear.x = self.v
        myVfh = vfh.VFHControl(self.goal_position)
        goal_angle = myVfh.vfh_control()
        last_goal = goal_angle
        rospy.loginfo(f"dif = {goal_angle}")
        while not rospy.is_shutdown():
            self.cmd_vel.publish(move)
            laser_scan = rospy.wait_for_message("/scan", LaserScan)
            odometry = rospy.wait_for_message("/odom", Odometry)
            if self.distance_to_goal(odometry) < 0.2:
                rospy.signal_shutdown("goal is reached")
            stop = Twist()
            self.cmd_vel.publish(stop)
            goal_angle = myVfh.vfh_control()
            rospy.loginfo(f"dif = {goal_angle}")
            remaining = goal_angle
            prev_angle = self.get_heading()  
            remaining -= prev_angle          
            twist = Twist()
            twist.angular.z = 1
            self.cmd_vel.publish(twist)
            # rotation loop
            while remaining >= 0:
                current_angle = self.get_heading()
                delta = abs(prev_angle - current_angle)
                remaining -= delta
                prev_angle = current_angle
            self.cmd_vel.publish(stop)
            go = Twist()
            go.linear.x = 0.05
            self.cmd_vel.publish(go)
            front_distance = min(laser_scan.ranges[:35])
            err = min([front_distance, min(laser_scan.ranges[35:180])]) - self.D   # return distance from side wall
            if err == float('inf'):
                err = 10
            sum_i_theta += err * self.dt
            P = self.k_p * err
            I = self.k_i * sum_i_theta
            D = self.k_d * (err - previous_error)
            move.angular.z = 0
            previous_error = err
            if front_distance < self.D:
                move.linear.x = 0
            else:
                move.linear.x = self.v                        
            self.r.sleep()

if __name__ == '__main__':
    try:
        pidc = PIDController()
        pidc.start()
    except rospy.ROSInterruptException:
        rospy.loginfo("Navigation terminated.")
