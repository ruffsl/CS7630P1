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
from collections import deque

class AntRobot(robot.Robot):    
	def __init__(self, point, config):
		super(AntRobot, self).__init__(point, config)
		self.id = int(rand.random()*1000000)		
		
		self.load = 0
		self.state = 0	# 0 = dig; 2 = transport; 3 = unload
		self.prev_state = 0
		self.surf_orientation = -1	# 0 = left; 1 = right
		self.last_action = np.zeros((2, 1), dtype=float)
		self.last_pos = np.zeros((2, 1), dtype=int)

		self.impatience = 0
		self.pos_hist_len = 20
		self.x_pos_hist = deque([0] * self.pos_hist_len)
		self.y_pos_hist = deque([0] * self.pos_hist_len)
		
		self.IMPATIENCE_THRESH = 40
		self.SURFACE = 0
		
		rand.seed()

		# Instantiate behavior objects
		self.behvr_follow_grav = Behvr_DirectionalBias(0, 1)
		self.behvr_go_to_surf = Behvr_DirectionalBias(0, -1)
		self.behvr_go_left = Behvr_DirectionalBias(-1, 0)
		self.behvr_go_right = Behvr_DirectionalBias(1, 0)
		self.behvr_random_walk = Behvr_RandomWalk()
#		self.behvr_avoid_past = Behvr_AvoidPast()
#		self.behvr_surf_attract = Behvr_SurfAttraction((self.SURFACE-self.config['body_range']))
		self.behvr_unload_dirt = Behvr_UnloadDirt(0.4, self.config['body_range'])
		self.behvr_lay_trail_pheromone = Behvr_LayTrailPheromone(1)
		self.behvr_follow_trail_pheromone = Behvr_FollowTrailPheromone()
		self.behvr_deficit_grab = Behvr_DeficitGrab(self.config['dirt'])
		self.coord_vecsum = Coord_VectorSum()
		
		# Debug/Testing variables
		self.counter = 0

	def update(self, world, robots):
		self.SURFACE = (world.shape[1]*self.config['dirt_ratio'])	

		self.update_impatience()
		
		local_world = self.sense(world)

		# State transition management
		if ( ( self.state == 0 or self.state == 4 ) and self.load >= self.config['max_load'] ):

			# reset impatience level on state switch
			self.impatience = 0

			self.prev_state = self.state
			self.state = 1

		elif ( self.state == 1 and self.rect.center[1] <= (self.SURFACE-2*self.config['body_range']) ):
			self.last_action = np.zeros((2, 1), dtype=float)
			if ( rand.random() < 0.5 ):
				self.surf_orientation = 0
			else:
				self.surf_orientation = 1

			# reset impatience level on state switch
			self.impatience = 0

			self.prev_state = self.state
			self.state = 2				

		elif ( self.state == 2 and ( self.load <= 0 or self.impatience > self.IMPATIENCE_THRESH ) ) :
			self.last_action = np.zeros((2, 1), dtype=float)
			if ( self.surf_orientation == 0 ):
				self.surf_orientation = 1
			else:
				self.surf_orientation = 0

			# reset impatience level on state switch
			self.impatience = 0

			self.prev_state = self.state
			self.state = 3

		elif ( self.state == 3 and self.rect.center[1] > (self.SURFACE+2*self.config['body_range']) ):
			# prob. transition to extension digging
			if ( rand.random() < 0.05 ):
				self.prev_state = self.state
				self.state = 0
			# prob. transition to deficit digging
			elif ( rand.random() < 0.05 ):
				self.behvr_deficit_grab.reset(local_world, self.rect.center[0], self.rect.center[1])
				
				self.prev_state = self.state
				self.state = 4
			# if patience has run out, flip coin to begin extension vs. deficit digging
			elif ( self.impatience > self.IMPATIENCE_THRESH ):
				# reset impatience level on state switch
				self.impatience = 0
			
				if ( rand.random() < 0.5 ):
					self.prev_state = self.state
					self.state = 0
				else:
					self.prev_state = self.state
					self.state = 4
					
		elif ( self.state == 3 and self.rect.center[1] <= (self.SURFACE+2*self.config['body_range']) and self.impatience > self.IMPATIENCE_THRESH ):
			# reset impatience level on state switch
			self.impatience = 0

			self.prev_state = self.state
			self.state = 0
			
		# Gravity-biased tunnel digging (extension grabs)
		if ( self.state == 0 ):

			while (True):
				grav_action = self.behvr_follow_grav.action()
				rwalk_action = self.behvr_random_walk.action(2, -2, 2, -2)
				print 'AntRobot()::update - Gravity Action: ' + str(grav_action) + ' R-Walk Action: ' + str(rwalk_action)
				
				action_list = np.concatenate(([grav_action], [rwalk_action]), 0)
				gain_list = np.array([4, 3])
				arb_res = self.coord_vecsum.coord(action_list.T, gain_list)
				print 'AntRobot()::update - Arbitrated Action: ' + str(arb_res)
				
				self.move(int(arb_res[0]), int(arb_res[1]), world)
				valid_move = self.valid_pos(world, robots)
				if ( not(valid_move) ):
					self.move(int(-1*arb_res[0]), int(-1*arb_res[1]), world)
				else:
					break
			
			self.dig(world)
		
		# Navigate towards surface	
		if ( self.state == 1 ):

			while ( True ):
				surf_action = self.behvr_go_to_surf.action()
				rwalk_action = self.behvr_random_walk.action(2, -2, 1, -1)
				print 'AntRobot()::update - State: ' + str(self.state)  + ' ' + str(self)					
				print 'AntRobot()::update - Surface Action: ' + str(surf_action) + ' R-Walk Action: ' + str(rwalk_action)
				
				# if last state was deficit digging below surface
				if ( self.prev_state == 4 ):
					rev_deficit_grab_action = -1*self.behvr_deficit_grab.action()
					print ' Reverse-Deficit Grab Action: ' + str(rev_deficit_grab_action)					
					
					action_list = np.concatenate(([surf_action], [rwalk_action], [rev_deficit_grab_action]), 0)
					gain_list = np.array([4, 6, 3])
				# if last state was extension digging below surface
				else:
					action_list = np.concatenate(([surf_action], [rwalk_action]), 0)
					gain_list = np.array([6, 3])

				arb_res = self.coord_vecsum.coord(action_list.T, gain_list)
				print 'AntRobot()::update - Arbitrated Action: ' + str(arb_res)
				
				self.move(int(arb_res[0]), int(arb_res[1]), world)
				valid_move = self.valid_pos(world, robots)
				if ( self.collision(world, robots) or not(valid_move) ):
					if ( valid_move and self.impatience > self.IMPATIENCE_THRESH and rand.random() < 0.2):
						self.dig(world)
						break
					else:
						self.move(int(-1*arb_res[0]), int(-1*arb_res[1]), world)
				else:
					break
				
			self.behvr_lay_trail_pheromone.action(world, self.rect.center[0], self.rect.center[1])
				
				
		# Release transported dirt
		if ( self.state == 2 ):
	
			move_fail_cnt = 0
			while ( True ):
				rwalk_action = self.behvr_random_walk.action(0, 0, 2, -2)
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
				valid_move = self.valid_pos(world, robots)
				if ( self.collision(world, robots) or not(valid_move) ):
					move_fail_cnt += 1
					if ( valid_move and move_fail_cnt > 40 ):
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

				# pheromone trail following ABOVE surface
				if ( self.rect.center[1] <= (self.SURFACE-self.config['body_range'] ) ):	
					if ( self.surf_orientation == 0 ):
						surf_bias_action = self.behvr_go_left.action()
					else:
						surf_bias_action = self.behvr_go_right.action()
					print 'AntRobot()::update - State: ' + str(self.state)  + ' ' + str(self)					
					print ' R-Walk Action: ' + str(rwalk_action) + ' Follow Pherom. Action: ' + str(follow_pherom_action) + ' Surf. Bias Action: ' + str(surf_bias_action)
					
					action_list = np.concatenate(([rwalk_action], [follow_pherom_action], [surf_bias_action]), 0)
					gain_list = np.array([6, 8, 3])
					arb_res = self.coord_vecsum.coord(action_list.T, gain_list)
					print 'AntRobot()::update - Arbitrated Action: ' + str(arb_res)

				# pheromone trail following BELOW surface
				else:
					grav_action = self.behvr_follow_grav.action()
					print 'AntRobot()::update - Gravity Action: ' + str(grav_action) + ' R-Walk Action: ' + str(rwalk_action)
					
					action_list = np.concatenate(([rwalk_action], [follow_pherom_action], [grav_action]), 0)
					gain_list = np.array([2, 4, 4])
					arb_res = self.coord_vecsum.coord(action_list.T, gain_list)
					print 'AntRobot()::update - Arbitrated Action: ' + str(arb_res)
				
				self.move(int(arb_res[0]), int(arb_res[1]), world)
				valid_move = self.valid_pos(world, robots)
				if ( self.collision(world, robots) or not(valid_move) ):
					move_fail_cnt += 1
					if ( valid_move and move_fail_cnt > 20 ):
						self.dig(world)
						break
					else:
						self.move(int(-1*arb_res[0]), int(-1*arb_res[1]), world)						
				else:
					break

#			if ( np.all( self.rect.center == self.last_pos ) ):
#				self.impatience += 2
#			elif ( self.impatience > 0 ):
#				self.impatience -= 1
#			print 'self.impatience = ' + str(self.impatience)

			self.last_action = arb_res			
			self.last_pos = self.rect.center

		# Gravity-invariant digging below surface (deficit grabs)
		if ( self.state == 4 ):
			local_world = self.sense(world)
			
			while (True):
				deficit_grab_action = self.behvr_deficit_grab.action()
				rwalk_action = self.behvr_random_walk.action(2, -2, 2, -2)
				print 'AntRobot()::update - State: ' + str(self.state)  + ' ' + str(self)					
				print ' R-Walk Action: ' + str(rwalk_action) + ' Deficit Grab Action: ' + str(deficit_grab_action)					
				
				action_list = np.concatenate(([rwalk_action], [deficit_grab_action]), 0)
				gain_list = np.array([4, 6])
				arb_res = self.coord_vecsum.coord(action_list.T, gain_list)
				print 'AntRobot()::update - Arbitrated Action: ' + str(arb_res)
				
				self.move(int(arb_res[0]), int(arb_res[1]), world)
				valid_move = self.valid_pos(world, robots)
				if ( not(valid_move) or self.rect.center[1] <= (self.SURFACE+2*self.config['body_range']) ):
					self.move(int(-1*arb_res[0]), int(-1*arb_res[1]), world)
				else:
					break
			
			self.dig(world)			
			
			self.last_action = arb_res			

	def update_impatience(self):
		min_delta_pos = 6	
		
		# historical position data to allow recognition of lack of progress
		self.x_pos_hist.popleft()
		self.y_pos_hist.popleft()
		self.x_pos_hist.append(self.rect.center[0])
		self.y_pos_hist.append(self.rect.center[1])		

#		self.ave_pos_hist = [ sum(self.x_pos_hist)/20, sum(self.y_pos_hist)/20 ]				
#		max_dx =  np.abs(self.ave_pos_hist[0] - self.rect.center[0])
#		max_dy =  np.abs(self.ave_pos_hist[1] - self.rect.center[1])
		
		max_dx = np.ndarray.max(np.abs(np.array(self.x_pos_hist) - self.rect.center[0]))
		max_dy = np.ndarray.max(np.abs(np.array(self.y_pos_hist) - self.rect.center[1]))
		
		if ( max_dx < min_delta_pos and max_dy < min_delta_pos ):
			self.impatience += 1
		elif ( self.impatience > 0 ):
			self.impatience -= 1
			
		print 'self.impatience = ' + str(self.impatience)
		
	
	def unload(self, world, dx, dy):
		self.move(dx, dy, world)
		
		drop_mask = self.getMask(world, self.config['dig_range'])
		drop_loc = np.asarray(np.where(drop_mask == 1))
#		x, y = self.rect.center
#		xx, yy = draw.circle(x, y, self.config['dig_range'], world.shape)
#		drop_loc = np.concatenate(([xx], [yy]), 0)
		drop_cnt = self.drop(world, drop_loc.T)
		self.move(-1*dx, -1*dy, world)
		print 'Drop Count = ' + str(drop_cnt)	
	
	def valid_pos(self, world, robots):	
		x_bound = world.shape[0]
		y_bound = world.shape[1]
		
		cur_pos = self.rect.center
		within_bounds = 	not( cur_pos[0] > x_bound-1-self.config['body_range'] \
			or cur_pos[0] < self.config['body_range'] \
			or cur_pos[1] > y_bound-1-self.config['body_range'] \
			or cur_pos[1] < self.config['body_range'] )
		print 'valid_pos::within_bounds = ' + str(within_bounds)
		
		robot_collision = False
		for robot in robots:
			if ( self.id != robot.id ):
				dist = np.array(self.rect.center) - np.array(robot.rect.center)
				if ( np.linalg.norm(dist) < 2*self.config['body_range'] ):
					robot_collision = True
					break
		print 'valid_pos::robot_collision = ' + str(robot_collision)

		valid = not(robot_collision) and within_bounds
		print 'valid_pos::valid = ' + str(valid)
			
		return valid
	
	def collision(self, world, robots):			
		mask = self.getMask(world, self.config['body_range'])
		body_locale = world*mask
		return ( np.any( body_locale < 0 ) )
		
								
	def __str__(self):
		return 'AntRobot: id: ' + str(self.id) + ', pos(x, y) = (%s, %s)'\
		% (self.rect.center[0], self.rect.center[1])



##################################################
########### Behavior Class Definitions ########### 
##################################################

class Behvr_DeficitGrab():
	""" Usage: Behvr_DeficitGrab(self.config['dirt']) """
	def __init__(self, dirt_val):
		self.dirt_val = dirt_val
		self.direction = np.array([-1, -1])
	
	def reset(self, local_world, x_pos, y_pos):
		abs_dirt_loc = np.asarray(np.where(local_world == self.dirt_val))
		print 'abs_dirt_loc = ' + str(abs_dirt_loc)
				
		if ( abs_dirt_loc.size == 0 ):
			vector_sum = np.array([rand.random(), rand.random()])
		else:
			rel_dirt_loc = abs_dirt_loc.T-np.array([x_pos, y_pos])
			rel_dirt_loc = rel_dirt_loc.T
			print 'rel_dirt_loc = ' + str(rel_dirt_loc)
			
			vector_sum = np.sum(rel_dirt_loc, 1)
		
		# if vector norm != 0
		if ( np.linalg.norm(vector_sum) > 0 ):		
			vector_sum = vector_sum/np.linalg.norm(vector_sum)		

		self.direction = vector_sum
	
	def action(self):
		return self.direction


class Behvr_FollowTrailPheromone():
	""" Usage: Behvr_FollowTrailPheromone() """
	def __init__(self):
		pass
	
	def action(self, local_world, x_pos, y_pos, last_action):
		abs_pherom_loc = np.asarray(np.where(local_world > 0))
#		print 'abs_pherom_loc = ' + str(abs_pherom_loc)
#		print 'last_action = ' + str(last_action)
		vector_sum = np.array([0, 0])

		if ( last_action[0] > 0 ):
			valid_x_region = np.asarray(np.where(abs_pherom_loc[0] > (x_pos-2)))
		elif ( last_action[0] < 0 ):
			valid_x_region = np.asarray(np.where(abs_pherom_loc[0] < (x_pos+2)))
		else:
			valid_x_region = np.array(range(abs_pherom_loc[0].size))
#		print 'valid_x_region = ' + str(valid_x_region)
			
		if ( last_action[1] > 0 ):
			valid_y_region = np.asarray(np.where(abs_pherom_loc[1] > (y_pos-2)))
		elif ( last_action[1] < 0 ):
			valid_y_region = np.asarray(np.where(abs_pherom_loc[1] < (y_pos+2)))
		else:
			valid_y_region = np.array(range(abs_pherom_loc[1].size))
#		print 'valid_y_region = ' + str(valid_y_region)

		valid_indices = np.intersect1d(valid_x_region, valid_y_region)
#		print 'valid_indices = ' + str(valid_indices)
		if ( valid_indices.size != 0 ):
			filtered_pherom_loc = abs_pherom_loc[:, valid_indices]
					
			rel_pherom_loc = filtered_pherom_loc.T-np.array([x_pos, y_pos])
			rel_pherom_loc = rel_pherom_loc.T
			pherom_val = local_world[filtered_pherom_loc[0].tolist(), filtered_pherom_loc[1].tolist()]
#			print 'rel_pherom_loc = ' + str(rel_pherom_loc)
#			print 'pherom_val = ' + str(pherom_val)
			
			vector_sum = np.dot(rel_pherom_loc, pherom_val)
#			print 'vector_sum (after dot prod) = ' + str(vector_sum)

			# if vector norm != 0
			if ( np.linalg.norm(vector_sum) > 0 ):		
				vector_sum = vector_sum/np.linalg.norm(vector_sum)	
#				print 'vector_sum (after norm) = ' + str(vector_sum)

		return vector_sum
		

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
		if ( last_action[0] != 0 and rand.random() < self.drop_prob ):
			unload_dirt = True

			if ( last_action[0] > 0 ):
				sign = 1
			elif ( last_action[0] < 0 ):
				sign = -1
		
			dx = sign*(2*self.body_range)
			
			if ( rand.random() < 0.99 ):
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
	""" Usage: Behvr_SurfAttraction(self.SURFACE) """
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
	""" Usage: Behvr_DirectionalBias(0, 1) """
	def __init__(self, x_dir, y_dir):
		self.x_dir = x_dir
		self.y_dir = y_dir
		
		self.vector = np.array([self.x_dir, self.y_dir])

		# if vector norm != 0
		if ( np.linalg.norm(self.vector) > 0 ):		
			self.vector = self.vector/np.linalg.norm(self.vector)	
		
	def action(self):
		return self.vector


class Behvr_RandomWalk():
	""" """
	def __init__(self):
		pass
				
	def action(self, x_lim_p, x_lim_n, y_lim_p, y_lim_n):
		x_rand = (x_lim_p - x_lim_n)*rand.random() + x_lim_n
		y_rand = (y_lim_p - y_lim_n)*rand.random() + y_lim_n
		
		vector = np.array([x_rand, y_rand])
		
		# if vector norm != 0
		if ( np.linalg.norm(vector) > 0 ):		
			vector = vector/np.linalg.norm(vector)
		
		return vector


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
#		print 'Coord_VectorSum()::action_list = ' + str(action_list)
#		print 'Coord_VectorSum()::gain_list = ' + str(gain_list)
#		print 'Coord_VectorSum()::res = ' + str(res)
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
