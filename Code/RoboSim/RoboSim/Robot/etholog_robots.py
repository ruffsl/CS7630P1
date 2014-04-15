# -*- coding: utf-8 -*-
"""
Created on Wed Mar 19 01:20:48 2014

@author: changah
"""

import pygame
from pygame.locals import *
from skimage import draw
import math
import robot
import numpy as np
import random as rand

class AntRobot(robot.Robot):    
	def __init__(self, point, config):
		super(AntRobot, self).__init__(point, config)
		self.load = 0
		self.state = 0	# 0 = dig; 2 = transport; 3 = unload
		self.surf_orientation = -1	# 0 = left; 1 = right
		self.last_action = np.zeros((2, 1), dtype=float)
		self.last_pos = np.zeros((2, 1), dtype=int)
		self.impatience = 0
		
		rand.seed()

		# Instantiate behavior objects
		self.behvr_follow_grav = Behvr_DirectionalBias(0, 1, 2)
		self.behvr_go_to_surf = Behvr_DirectionalBias(0, -1, 2)
		self.behvr_go_left = Behvr_DirectionalBias(-1, 0, 1)
		self.behvr_go_right = Behvr_DirectionalBias(1, 0, 1)
		self.behvr_random_walk = Behvr_RandomWalk()
		self.behvr_avoid_past = Behvr_AvoidPast()
#		self.behvr_surf_attract = Behvr_SurfAttraction((400-self.config['body_range']))
		self.behvr_unload_dirt = Behvr_UnloadDirt(0.4, self.config['body_range'])
		self.behvr_lay_trail_pheromone = Behvr_LayTrailPheromone(1)
		self.behvr_follow_trail_pheromone = Behvr_FollowTrailPheromone()
		self.coord_vecsum = Coord_VectorSum()
		
		# Debug/Testing variables
		self.counter = 0

	def update(self, world, robots):
		local_world = self.sense(world)
		# local_world = np.array([0, 0])

		if ( self.state == 0 and self.load >= self.config['max_load'] ):
			self.state = 1
		elif ( self.state == 1 and self.rect.center[1] <= (400-self.config['body_range']-4) ):
			self.last_action = np.zeros((2, 1), dtype=float)
			if ( rand.random() < 0.5 ):
				self.surf_orientation = 0
			else:
				self.surf_orientation = 1
			self.state = 2				
		elif ( self.state == 2 and self.load <= 0 ):
			self.last_action = np.zeros((2, 1), dtype=float)
			if ( self.surf_orientation == 0 ):
				self.surf_orientation = 1
			else:
				self.surf_orientation = 0
			self.state = 3
		elif ( self.state == 3 and self.rect.center[1] > 400 ):
			if ( rand.random() < 0.05 or self.impatience > 20 ):
				self.state = 0
			
		# Dig downwards tunnel
		if ( self.state == 0 ):
#		if ( self.state == 0 and self.load < self.config['max_load'] ):
			grav_action = self.behvr_follow_grav.action()
			rwalk_action = self.behvr_random_walk.action(2, -2, 2, -2)
			print 'AntRobot()::update - Gravity Action: ' + str(grav_action) + ' R-Walk Action: ' + str(rwalk_action)
			
			action_list = np.concatenate(([grav_action], [rwalk_action]), 0)
			gain_list = np.array([2, 3])
			arb_res = self.coord_vecsum.coord(action_list.T, gain_list)
			print 'AntRobot()::update - Arbitrated Action: ' + str(arb_res)
			
			self.move(int(arb_res[0]), int(arb_res[1]), world)
			
			self.dig(world)
		
		# Navigate towards surface	
		if ( self.state == 1 ):
#		if ( self.load > self.config['max_load'] and self.rect.center[1] > (400-self.config['body_range']) ):
			while ( True ):
				surf_action = self.behvr_go_to_surf.action()
				rwalk_action = self.behvr_random_walk.action(2, -2, 1, -1)
				print 'AntRobot()::update - Surface Action: ' + str(surf_action) + ' R-Walk Action: ' + str(rwalk_action)
				
				action_list = np.concatenate(([surf_action], [rwalk_action]), 0)
				gain_list = np.array([3, 2])
				arb_res = self.coord_vecsum.coord(action_list.T, gain_list)
				print 'AntRobot()::update - Arbitrated Action: ' + str(arb_res)
				
				self.move(int(arb_res[0]), int(arb_res[1]), world)
				if ( self.collision(world, robots) ):
					self.move(int(-1*arb_res[0]), int(-1*arb_res[1]), world)
				else:
					break
				
			self.behvr_lay_trail_pheromone.action(world, self.rect.center[0], self.rect.center[1])
				
				
		# Release transported dirt
		if ( self.state == 2 ):
#		if ( self.load != 0 and self.rect.center[1] <= (400-self.config['body_range']) ):
	
			move_fail_cnt = 0
			while ( True ):
				rwalk_action = self.behvr_random_walk.action(2, -2, 2, -2)
#				avoidp_action = self.behvr_avoid_past.action(self.last_action)
				if ( self.surf_orientation == 0 ):
					surf_bias_action = self.behvr_go_left.action()
				else:
					surf_bias_action = self.behvr_go_right.action()
				print 'AntRobot()::update - State: ' + str(self.state)  + ' ' + str(self)		
				print ' R-Walk Action: ' + str(rwalk_action) + ' Surf. Bias Action: ' + str(surf_bias_action)
				
				action_list = np.concatenate(([rwalk_action], [surf_bias_action]), 0)
				gain_list = np.array([2, 5])
				arb_res = self.coord_vecsum.coord(action_list.T, gain_list)
				print 'AntRobot()::update - Arbitrated Action: ' + str(arb_res)				
								
				self.move(int(arb_res[0]), int(arb_res[1]), world)
				if ( self.collision(world, robots) ):
					move_fail_cnt += 1
					if ( move_fail_cnt > 20 ):
						self.dig(world)
						break
					else:
						self.move(int(-1*arb_res[0]), int(-1*arb_res[1]), world)						
				else:
					break

			self.behvr_lay_trail_pheromone.action(world, self.rect.center[0], self.rect.center[1])		
			
			self.last_action[0] = arb_res[0]			
			unload_dirt, dx, dy = self.behvr_unload_dirt.action(self.last_action)
			print 'Unload Dirt: ' + str(unload_dirt) + ', dx = ' + str(dx) + ', dy = ' + str(dy)
			if ( unload_dirt ):
				self.unload(world, dx, dy)
		
		# Follow/search for pheromones back to digging site
		if ( self.state == 3 ):
			local_world = self.sense(world)
			
			move_fail_cnt = 0
			while ( True ):
				rwalk_action = self.behvr_random_walk.action(1, -1, 2, -2)
				follow_pherom_action = self.behvr_follow_trail_pheromone.action(local_world, \
					self.rect.center[0], self.rect.center[1], self.last_action)

				if ( self.rect.center[1] <= (400-self.config['body_range'] ) ):	
					if ( self.surf_orientation == 0 ):
						surf_bias_action = self.behvr_go_left.action()
					else:
						surf_bias_action = self.behvr_go_right.action()
					print 'AntRobot()::update - State: ' + str(self.state)  + ' ' + str(self)					
					print ' R-Walk Action: ' + str(rwalk_action) + ' Follow Pherom. Action: ' + str(follow_pherom_action) + ' Surf. Bias Action: ' + str(surf_bias_action)
					
					action_list = np.concatenate(([rwalk_action], [follow_pherom_action], [surf_bias_action]), 0)
					gain_list = np.array([8, 2, 10])
					arb_res = self.coord_vecsum.coord(action_list.T, gain_list)
					print 'AntRobot()::update - Arbitrated Action: ' + str(arb_res)				
				else:
					grav_action = self.behvr_follow_grav.action()
					print 'AntRobot()::update - Gravity Action: ' + str(grav_action) + ' R-Walk Action: ' + str(rwalk_action)
					
					action_list = np.concatenate(([rwalk_action], [follow_pherom_action], [grav_action]), 0)
					gain_list = np.array([2, 3, 2])
					arb_res = self.coord_vecsum.coord(action_list.T, gain_list)
					print 'AntRobot()::update - Arbitrated Action: ' + str(arb_res)
				
				self.move(int(arb_res[0]), int(arb_res[1]), world)
				if ( self.collision(world, robots) ):
					move_fail_cnt += 1
					if ( move_fail_cnt > 20 ):
						self.dig(world)
						self.state = 0
						break
					else:
						self.move(int(-1*arb_res[0]), int(-1*arb_res[1]), world)						
				else:
					break

			if ( np.all( self.rect.center == self.last_pos ) ):
				self.impatience += 2
			elif ( self.impatience > 0 ):
				self.impatience -= 1
			print 'self.impatience = ' + str(self.impatience)

			self.last_action = arb_res			
			self.last_pos = self.rect.center

	
	def unload(self, world, dx, dy):
		self.move(dx, dy, world)
		x, y = self.rect.center
		xx, yy = draw.circle(x, y, self.config['dig_range'], world.shape)
		drop_loc = np.concatenate(([xx], [yy]), 0)
		drop_cnt = self.drop(world, drop_loc.T)
		self.move(-1*dx, -1*dy, world)
		print 'Drop Count = ' + str(drop_cnt)	
	
	def collision(self, world, robots):
		mask = self.getMask(world, self.config['body_range'])
		body_locale = world*mask
		return ( np.any( body_locale < 0 ) )
		
								
	def __str__(self):
		return 'AntRobot: pos(x, y) = (%s, %s)'\
		% (self.rect.center[0], self.rect.center[1])



##################################################
########### Behavior Class Definitions ########### 
##################################################


class Behvr_FollowTrailPheromone():
	""" Usage: Behvr_FollowTrailPheromone() """
	def __init__(self):
		pass
	
	def action(self, local_world, x_pos, y_pos, last_action):
		abs_pherom_loc = np.asarray(np.where(local_world > 0))
		pherom_val = local_world[abs_pherom_loc[0].tolist(), abs_pherom_loc[1].tolist()]
		print 'abs_pherom_loc = ' + str(abs_pherom_loc)
		print 'abs_pherom_val = ' + str(pherom_val)
		print 'last_action = ' + str(last_action)
		vector = np.array([0, 0])

		if ( last_action[0] > 0 ):
			valid_x_region = np.asarray(np.where(abs_pherom_loc[0] > (x_pos-2)))
		elif ( last_action[0] < 0 ):
			valid_x_region = np.asarray(np.where(abs_pherom_loc[0] < (x_pos+2)))
		else:
			valid_x_region = np.array(range(abs_pherom_loc[0].size))
		print 'valid_x_region = ' + str(valid_x_region)
			
		if ( last_action[1] > 0 ):
			valid_y_region = np.asarray(np.where(abs_pherom_loc[1] > (y_pos-2)))
		elif ( last_action[1] < 0 ):
			valid_y_region = np.asarray(np.where(abs_pherom_loc[1] < (y_pos+2)))
		else:
			valid_y_region = np.array(range(abs_pherom_loc[1].size))
		print 'valid_y_region = ' + str(valid_y_region)

		valid_indices = np.intersect1d(valid_x_region, valid_y_region)
		filtered_pherom_loc = abs_pherom_loc[:, valid_indices]
				
		rel_pherom_loc = filtered_pherom_loc.T-np.array([x_pos, y_pos])
		rel_pherom_loc = rel_pherom_loc.T
		pherom_val = local_world[filtered_pherom_loc[0].tolist(), filtered_pherom_loc[1].tolist()]
		
		print 'rel_pherom_loc = ' + str(rel_pherom_loc)
		print 'pherom_val = ' + str(pherom_val)
		
		vector = np.dot(rel_pherom_loc, pherom_val)
		return vector
		

class Behvr_LayTrailPheromone():
	""" Usage: Behvr_LayTrailPheromone(1) """
	def __init__(self, intensity_inc):
		self.intensity_inc = intensity_inc
	
	def action(self, world, x_pos, y_pos):
		world[x_pos, y_pos] += self.intensity_inc
		

class Behvr_UnloadDirt():
	""" Usage: Behvr_UnloadDirt(0.4) """
	def __init__(self, drop_prob, body_range):
		self.drop_prob = drop_prob
		self.body_range = body_range
	
	def action(self, last_action):
		# if dice roll -> unload dirt
		unload_dirt = False
		dx, dy = 0, 0
		if ( rand.random() < self.drop_prob ):
			unload_dirt = True
			while ( dx == 0 or dy == 0 ):
				if ( last_action[0] > 0 ):
					sign = 1
				else:
					sign = -1
			
				dx = sign*(2*self.body_range)
			
				if (rand.random() < 0.5):
					dy = 2*self.body_range
				else:
					dy = 0
			
			if ( dx != 0 and dy != 0 ):
				if ( dx > 0 ):
					dx -= 1
				else:
					dx += 1
				dy -= 1
				
		return [unload_dirt, dx, dy]


class Behvr_PointRepulsion():
	""" Usage: Behvr_PointRepulsion(500, 395) """
	def __init__(self, x_center, y_center):
		self.x_center = x_center
		self.y_center = y_center
	
	def action(self, x_pos, y_pos, supress_x=0, supress_y=0):
		vector = np.array([0, 0])
		x_delta = x_pos - self.x_center
		y_delta = y_pos - self.y_center

		if ( x_delta > 0 ):
			x_scale = 1
		else:
			x_scale = -1
		if ( y_delta > 0 ):
			y_scale = 1
		else:
			y_scale = -1
			
		vector[0] = -1*(supress_x-1)*x_scale/(1+x_delta)^2 
		vector[1] = -1*(supress_y-1)*y_scale/(1+y_delta)^2

		return vector	


class Behvr_SurfAttraction():
	""" Usage: Behvr_SurfAttraction(400) """
	def __init__(self, surf_y_pos):
		self.surf_y_pos = surf_y_pos
	
	def action(self, y_pos):
		vector = np.array([0, 0])
		vector[1] = -1*(y_pos - self.surf_y_pos)^2 

		return vector			
	
	
class Behvr_AvoidPast():
	""" Usage: Behvr_AvoidPast() """
	def __init__(self):
		pass
		
	def action(self, last_action):
		x_dir = 0
		y_dir = 0
		
		if (last_action[0] > 0):
			x_dir = 1
		elif (last_action[0] < 0):
			x_dir = -1
			
		if (last_action[1] > 0):
			y_dir = 1
		elif (last_action[1] < 0):
			y_dir = -1
		
#		return np.array([self.x_dir*self.intensity, self.y_dir*self.intensity])
		return np.array([x_dir, y_dir])

class Behvr_DirectionalBias():
	""" Usage: Behvr_DirectionalBias(0, 1, 2) """
	def __init__(self, x_dir, y_dir, intensity):
		self.x_dir = x_dir
		self.y_dir = y_dir
		self.intensity = intensity
		
	def action(self):
		return np.array([self.x_dir*self.intensity, self.y_dir*self.intensity])


class Behvr_RandomWalk():
	""" """
	def __init__(self):
		pass
				
	def action(self, x_lim_p, x_lim_n, y_lim_p, y_lim_n):
		x_rand = (x_lim_p - x_lim_n)*rand.random() + x_lim_n
		y_rand = (y_lim_p - y_lim_n)*rand.random() + y_lim_n
		
		return np.array([x_rand, y_rand])


class Coord_VectorSum():
	""" """
	def __init__(self):
		pass

	# Input(s): 
	# action_list - Concatenated ndarray (matrix) in format:
	#		[[x0, x1, ... ]
	#		 y0, y1, ... ]]
	# gain_list - ndarray: [g1, g2, ...]
	def coord(self, action_list, gain_list):
		res = np.dot(action_list, gain_list)
		print 'Coord_VectorSum()::arbitrate - Vector Sum = ' + str(res)
		
		# Probabilistically determine next move direction 
		# (using vector components for prob. weighting)
		x_sign = -1 if ( int(res[0]) < 0 ) else 1
		y_sign = -1 if ( int(res[1]) < 0 ) else 1 
		x_abs =  math.fabs(int(res[0]))
		y_abs =  math.fabs(int(res[1]))
		if ( (x_abs + y_abs)*rand.random() < x_abs ):
			return np.array([x_sign*1, 0])
		else:
			return np.array([0, y_sign*1])
				


        
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
	for cnt in range(5):
		print(mAntRobot)
		mAntRobot.update('garbage', 'garbage')
