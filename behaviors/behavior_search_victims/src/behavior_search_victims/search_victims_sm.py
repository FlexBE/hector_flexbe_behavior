#!/usr/bin/env python
###########################################################
#               WARNING: Generated code!                  #
#              **************************                 #
# Manual changes may get lost if file is generated again. #
# Only code inside the [MANUAL] tags will be kept.        #
###########################################################

import roslib; roslib.load_manifest('behavior_search_victims')
from flexbe_core import Behavior, Autonomy, OperatableStateMachine, ConcurrencyContainer, PriorityContainer, Logger
from flexbe_manipulation_states.get_joints_from_srdf_state import GetJointsFromSrdfState
from behavior_explorationdriveto.explorationdriveto_sm import ExplorationDriveToSM
from hector_flexbe_states.confirm_victim import ConfirmVictim
from hector_flexbe_states.discard_victim import DiscardVictim
from hector_flexbe_states.Decide_If_Victim import DecideIfVictim
from behavior_exploration.exploration_sm import ExplorationSM
from hector_flexbe_states.detect_object import DetectObject
from hector_flexbe_states.move_arm_dyn_state import MoveArmDynState
from flexbe_manipulation_states.moveit_to_joints_state import MoveitToJointsState
# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]
from geometry_msgs.msg import PoseStamped
# [/MANUAL_IMPORT]


'''
Created on Thu May 19 2016
@author: Elisa und Gabriel
'''
class SearchVictimsSM(Behavior):
	'''
	Explore and search victims
	'''


	def __init__(self):
		super(SearchVictimsSM, self).__init__()
		self.name = 'Search Victims'

		# parameters of this behavior

		# references to used behaviors
		self.add_behavior(ExplorationDriveToSM, 'ExplorationDriveTo')
		self.add_behavior(ExplorationSM, 'ExplorationWithDetection/Exploration')

		# Additional initialization code can be added inside the following tags
		# [MANUAL_INIT]
		
		# [/MANUAL_INIT]

		# Behavior comments:



	def create(self):
		srdf = "hector_tracker_robot_moveit_config/config/taurob_tracker.srdf"
		arm_gripper_joints = ["arm_joint_%d"%i for i in range(5)]
		# x:685 y:553, x:911 y:41
		_state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])
		_state_machine.userdata.pose = PoseStamped()
		_state_machine.userdata.group_name = 'arm_group'
		_state_machine.userdata.type = 'hotspot'

		# Additional creation code can be added inside the following tags
		# [MANUAL_CREATE]
		
		# [/MANUAL_CREATE]

		# x:30 y:365, x:130 y:365, x:230 y:365, x:330 y:365, x:430 y:365
		_sm_explorationwithdetection_0 = ConcurrencyContainer(outcomes=['finished', 'failed'], output_keys=['pose', 'victim'], conditions=[
										('finished', [('Exploration', 'finished')]),
										('failed', [('Exploration', 'failed')]),
										('finished', [('Detect_Object', 'found')])
										])

		with _sm_explorationwithdetection_0:
			# x:40 y:44
			OperatableStateMachine.add('Exploration',
										self.use_behavior(ExplorationSM, 'ExplorationWithDetection/Exploration'),
										transitions={'finished': 'finished', 'failed': 'failed'},
										autonomy={'finished': Autonomy.Inherit, 'failed': Autonomy.Inherit})

			# x:346 y:59
			OperatableStateMachine.add('Detect_Object',
										DetectObject(),
										transitions={'found': 'finished'},
										autonomy={'found': Autonomy.Off},
										remapping={'pose': 'pose', 'victim': 'victim'})



		with _state_machine:
			# x:30 y:40
			OperatableStateMachine.add('Get_Compact_Drive_Config',
										GetJointsFromSrdfState(config_name="compact_drive_pose", srdf_file=srdf, move_group="", robot_name=""),
										transitions={'retrieved': 'Set_Initial_Arm', 'file_error': 'failed'},
										autonomy={'retrieved': Autonomy.Off, 'file_error': Autonomy.Off},
										remapping={'joint_values': 'compact_drive_config'})

			# x:881 y:197
			OperatableStateMachine.add('ExplorationDriveTo',
										self.use_behavior(ExplorationDriveToSM, 'ExplorationDriveTo'),
										transitions={'finished': 'MoveArmVictim', 'failed': 'Decide_If_Victim'},
										autonomy={'finished': Autonomy.Inherit, 'failed': Autonomy.Inherit},
										remapping={'pose': 'pose', 'victim': 'victim'})

			# x:420 y:255
			OperatableStateMachine.add('Confirm_Victim',
										ConfirmVictim(),
										transitions={'confirmed': 'Set_Initial_Arm'},
										autonomy={'confirmed': Autonomy.Off},
										remapping={'victim': 'victim'})

			# x:412 y:338
			OperatableStateMachine.add('Discard_Victim',
										DiscardVictim(),
										transitions={'discarded': 'Set_Initial_Arm'},
										autonomy={'discarded': Autonomy.Off},
										remapping={'victim': 'victim'})

			# x:605 y:238
			OperatableStateMachine.add('Decide_If_Victim',
										DecideIfVictim(),
										transitions={'confirm': 'Confirm_Victim', 'discard': 'Discard_Victim', 'retry': 'ExplorationDriveTo'},
										autonomy={'confirm': Autonomy.Full, 'discard': Autonomy.Full, 'retry': Autonomy.Full})

			# x:524 y:122
			OperatableStateMachine.add('ExplorationWithDetection',
										_sm_explorationwithdetection_0,
										transitions={'finished': 'ExplorationDriveTo', 'failed': 'failed'},
										autonomy={'finished': Autonomy.Inherit, 'failed': Autonomy.Inherit},
										remapping={'pose': 'pose', 'victim': 'victim'})

			# x:792 y:334
			OperatableStateMachine.add('MoveArmVictim',
										MoveArmDynState(),
										transitions={'reached': 'Decide_If_Victim', 'sampling_failed': 'finished', 'planning_failed': 'finished', 'control_failed': 'finished'},
										autonomy={'reached': Autonomy.Off, 'sampling_failed': Autonomy.Off, 'planning_failed': Autonomy.Off, 'control_failed': Autonomy.Off},
										remapping={'object_pose': 'pose', 'object_type': 'type', 'object_id': 'victim'})

			# x:229 y:137
			OperatableStateMachine.add('Set_Initial_Arm',
										MoveitToJointsState(move_group="arm_with_gripper_group", joint_names=arm_gripper_joints, action_topic='/move_group'),
										transitions={'reached': 'ExplorationWithDetection', 'planning_failed': 'failed', 'control_failed': 'failed'},
										autonomy={'reached': Autonomy.Off, 'planning_failed': Autonomy.Off, 'control_failed': Autonomy.Off},
										remapping={'joint_config': 'compact_drive_config'})


		return _state_machine


	# Private functions can be added inside the following tags
	# [MANUAL_FUNC]
	
	# [/MANUAL_FUNC]
