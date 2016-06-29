#!/usr/bin/env python

import rospy
from flexbe_core import EventState, Logger

from flexbe_core.proxy import ProxyActionClient, ProxyServiceCaller

from hector_move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from monstertruck_msgs.srv import SetAlternativeTolerance
from actionlib_msgs.msg import GoalID
from rospy import Time

from hector_nav_msgs.srv import GetRobotTrajectory, GetRobotTrajectoryRequest

'''
Created on 15.06.2015

@author: Philipp Schillinger
'''

class CreatePath(EventState):
	'''
	Lets the robot move along a given path.
	
	
	<= succeeded					Robot is now located at the specified waypoint.
	<= failed 					Failed to send a motion request to the action server.
	'''

	def __init__(self):
		'''
		Constructor
		'''
		super(CreatePath, self).__init__(outcomes=['succeeded', 'failed'], output_keys=['path'])
		
		self._failed = False
		self._succeeded = False
	
		self._serv = ProxyServiceCaller({'trajectory': GetRobotTrajectory})
		
		
	def execute(self, userdata):
		'''
		Execute this state
		'''
		
		if self._failed:
			return 'failed'
		if self._succeeded:
			return 'succeeded'

		

			
	def on_enter(self, userdata):
		
		path = self._serv.call('trajectory', GetRobotTrajectoryRequest())
		
		userdata.path = path.trajectory
		
		#userdata.path.header.frame_id = 'map'
		Logger.loginfo('Failed to send motion request to waypoint (%(x).3f, %(y).3f)' % {
				'x': path.trajectory.poses[1].pose.position.x,
				'y': path.trajectory.poses[1].pose.position.y
			})
		Logger.loginfo('Frame id (%(x)s)' % {
				'x': path.trajectory.header.frame_id
			})
		self._succeeded = True
	
			

	def on_stop(self):
		pass

	def on_exit(self, userdata):	
		pass

	def on_pause(self):
		pass

	def on_resume(self, userdata):
		pass