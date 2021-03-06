#!/usr/bin/env python

import rospy
from flexbe_core import EventState, Logger

from flexbe_core.proxy import ProxyActionClient

from hector_move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from monstertruck_msgs.srv import SetAlternativeTolerance
from actionlib_msgs.msg import GoalID
from rospy import Time
from dynamic_reconfigure.client import Client

'''
Created on 15.06.2015

@author: Philipp Schillinger
'''

class MoveToFixedWaypoint(EventState):
	'''
	Lets the robot move to a given waypoint.

	-- allow_backwards 	Boolean 	Allow the robot to drive backwards when approaching the given waypoint.

	># waypoint		PoseStamped		Specifies the waypoint to which the robot should move.
	># speed					Speed of the robot

	<= reached 					Robot is now located at the specified waypoint.
	<= failed 					Failed to send a motion request to the action server.
	'''

	def __init__(self, allow_backwards = False):
		'''
		Constructor
		'''
		super(MoveToFixedWaypoint, self).__init__(outcomes=['reached', 'failed'],
											input_keys=['waypoint','speed'])
		
		self._action_topic = '/move_base'
		self._move_client = ProxyActionClient({self._action_topic: MoveBaseAction})
		#self.set_tolerance = rospy.ServiceProxy('/controller/set_alternative_tolerances', SetAlternativeTolerance)
		
		self._dynrec = Client("/vehicle_controller", timeout = 10)
		self._defaultspeed = 0.1

		self._allow_backwards = allow_backwards

		self._failed = False
		self._reached = False
		
		
	def execute(self, userdata):
		'''
		Execute this state
		'''
		
		if self._failed:
			return 'failed'
		if self._reached:
			return 'reached'

		if self._move_client.has_result(self._action_topic):
			result = self._move_client.get_result(self._action_topic)
			self._dynrec.update_configuration({'speed':self._defaultspeed})	
			if result.result == 1:
				self._reached = True
				return 'reached'
			else:
				self._failed = True
				Logger.logwarn('Failed to reach waypoint!')
				return 'failed'


			
	def on_enter(self, userdata):

		
		speedValue = self._dynrec.get_configuration(timeout = 0.5)
		if speedValue is not None:
			self._defaultspeed = speedValue['speed']	
			
		self._dynrec.update_configuration({'speed':userdata.speed})		

		self._startTime = Time.now()

		self._failed = False
		self._reached = False
		
		#goal_id = GoalID()
		#goal_id.id = 'abcd'
		#goal_id.stamp = Time.now()

		action_goal = MoveBaseGoal()
		action_goal.target_pose = userdata.waypoint
		action_goal.speed = userdata.speed
		action_goal.reverse_allowed = self._allow_backwards

		if action_goal.target_pose.header.frame_id == "":
			action_goal.target_pose.header.frame_id = "world"

		try:
			self._move_client.send_goal(self._action_topic, action_goal)
			#resp = self.set_tolerance(goal_id, 0.2, 1.55)
		except Exception as e:
			Logger.logwarn('Failed to send motion request to waypoint (%(x).3f, %(y).3f):\n%(err)s' % {
				'err': str(e),
				'x': userdata.waypoint.pose.position.x,
				'y': userdata.waypoint.pose.position.y
			})
			self._failed = True
		
		Logger.loginfo('Driving to next waypoint')
			

	def on_stop(self):
		try:
			if self._move_client.is_available(self._action_topic) \
			and not self._move_client.has_result(self._action_topic):
				self._move_client.cancel(self._action_topic)
		except:
			# client already closed
			pass

	def on_exit(self, userdata):
		try:
			if self._move_client.is_available(self._action_topic) \
			and not self._move_client.has_result(self._action_topic):
				self._move_client.cancel(self._action_topic)
		except:
			# client already closed
			pass

	def on_pause(self):
		self._move_client.cancel(self._action_topic)

	def on_resume(self, userdata):
		self.on_enter(userdata)
