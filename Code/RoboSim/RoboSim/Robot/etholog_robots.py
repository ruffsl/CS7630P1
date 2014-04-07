# -*- coding: utf-8 -*-
"""
Created on Wed Mar 19 01:20:48 2014

@author: changah
"""

import pygame
from pygame.locals import *
import robot
import numpy as np
import random as rand

class AntRobot(robot.Robot):    
	def __init__(self, point, config):
		super(AntRobot, self).__init__(point, config)
		self.load = 0
		self.mode = 0	# 0 = dig; 2 = unload
		rand.seed()

		# Instantiate behavior objects
		self.behvr_follow_grav = Behvr_FollowGravity(0, 1, 5)
		self.behvr_random_walk = Behvr_RandomWalk(2, 2)
		
		self.coord_vecsum = Coord_VectorSum()

	def update(self, occupancy_grid, agent_list):
		#local_world = self.sense(world)
		local_world = np.array([0, 0])
		grav_action = self.behvr_follow_grav.action(local_world)
		rwalk_action = self.behvr_random_walk.action(local_world)
		print 'AntRobot()::update - Gravity Action: ' + str(grav_action) + ' R-Walk Action: ' + str(rwalk_action)
		
		action_list = np.concatenate(([grav_action], [rwalk_action]), 0)
		gain_list = np.array([1, 2])
		arb_res = self.coord_vecsum.arbitrate(action_list.T, gain_list)
		print 'AntRobot()::update - Arbtrated Action: ' + str(arb_res)

        
	def __str__(self):
		return 'AntRobot: pos(x, y) = (%s, %s)'\
		% (self.rect.center[0], self.rect.center[1])



##################################################
########### Behavior Class Definitions ########### 
##################################################

class Behvr_FollowGravity():
	""" """
	def __init__(self, x_dir, y_dir, intensity):
		self.x_dir = x_dir
		self.y_dir = y_dir
		self.intensity = intensity
		
	def action(self, local_world):
		return np.array([self.x_dir*self.intensity, self.y_dir*self.intensity])

class Behvr_RandomWalk():
	""" """
	def __init__(self, x_lim, y_lim):
		self.x_lim = x_lim
		self.y_lim = y_lim
		
	def action(self, local_world):
		return np.array([self.x_lim*rand.random(), self.y_lim*rand.random()])

class Coord_VectorSum():
	""" """
	def __init__(self):
		pass

	# Input(s): 
	# action_list - Concatenated ndarray (matrix) in format:
	#		[[x0, x1, ... ]
	#		 y0, y1, ... ]]
	# gain_list - ndarray: [g1, g2, ...]
	def arbitrate(self, action_list, gain_list):
		res = np.dot(action_list, gain_list)
		print 'Coord_VectorSum()::arbitrate - Vector Sum = ' + str(res)
		
		# Probabilistically determine next move direction 
		# (using vector components for prob. weighting)
		if ( int(res[0] + res[1])*rand.random() < int(res[0]) ):
			return np.array([1, 0])
		else:
			return np.array([0, 1])
				


        
if __name__ == "__main__":
	config = {'fps': 200,
			'b_image'	: 	'background.png',
			'b_size'	: 	None,
			'r_image'	: 	'robo10.png',
			'logo_image'	: 	'logo.png',
			'path'	:	None,
			'seed'	: 	42,
			'max_load':		1000,
			'sense_range':	5,
			'dig_range': 	5,
			'body_range':	5,
			'dirt': 		-1,
			'rock': 		-2,
			'unknown':		-3,
			'empty':		0}
	config['path'] = 'D:\Users\Amblix\Documents\GitHub\CS7630P1\Code\RoboSim'
	mAntRobot = AntRobot((500,390), config)
	for cnt in range(20):
		print(mAntRobot)
		mAntRobot.update('garbage', 'garbage')
