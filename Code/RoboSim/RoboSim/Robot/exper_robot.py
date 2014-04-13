# -*- coding: utf-8 -*-

import robot
import numpy as np
import random

class exper_robot(robot.Robot):
#	Base class provides
#	def __init__(self, point, config):
#	def update(self, world, robots):
#	def move(self,dx,dy,world):
#	def load_image(self, name):
# Elevation of surface, 400

	
	def __init__(self, point, config):
		robot.Robot.__init__(self, point, config)
		self.state = 0
		self.load = 0
		self.vision = []
		self.touch = [0,0,0,0,0,0,0,0]	#Starting from top, going clockwise, 8 segments
		random.seed()
		self.x_dir = 0
		self.y_dir = 0
		self.segment_length = 0
		
		#Sub states for behaviors
		self.unload_state = 0
		self.dig_state = 0
		
		#Constants
		self.RANDOM_LENGTH = 15
		self.TOUCH_RANGE = 4
		
	def update(self, world, robots):
		self.vision = self.sense(world)
		self.vision_2_feel(world)
		if self.state == 0:
			self.dig_tunnel(world)
		elif self.state == 1:
			self.unload_dirt(world)
		return None
		
	def vision_2_feel(self, world):
		#Top -> 0
		if self.vision[self.rel_pt(0,-1)] == -1 or self.vision[self.rel_pt(0,-1)] == -2:
			self.touch[0] = 1
		elif self.vision[self.rel_pt(0,-2)] == -1 or self.vision[self.rel_pt(0,-2)] == -2:
			self.touch[0] = 2
		elif self.vision[self.rel_pt(0,-3)] == -1 or self.vision[self.rel_pt(0,-3)] == -2:
			self.touch[0] = 3
		elif self.vision[self.rel_pt(0,-4)] == -1 or self.vision[self.rel_pt(0,-4)] == -2:
			self.touch[0] = 4
		else:
			self.touch[0] = 5
		#Top right -> 1
		if self.vision[self.rel_pt(1,-1)] == -1 or self.vision[self.rel_pt(1,-1)] == -2:
			self.touch[1] = 2
		elif self.vision[self.rel_pt(1,-2)] == -1 or self.vision[self.rel_pt(1,-2)] == -2:
			self.touch[1] = 3
		elif self.vision[self.rel_pt(2,-1)] == -1 or self.vision[self.rel_pt(2,-1)] == -2:
			self.touch[1] = 3
		elif self.vision[self.rel_pt(1,-3)] == -1 or self.vision[self.rel_pt(1,-3)] == -2:
			self.touch[1] = 4
		elif self.vision[self.rel_pt(2,-2)] == -1 or self.vision[self.rel_pt(2,-2)] == -2:
			self.touch[1] = 4
		elif self.vision[self.rel_pt(3,-1)] == -1 or self.vision[self.rel_pt(3,-1)] == -2:
			self.touch[1] = 4
		else:
			self.touch[1] = 5
		#right -> 2
		if self.vision[self.rel_pt(1,0)] == -1 or self.vision[self.rel_pt(1,0)] == -2:
			self.touch[2] = 1
		elif self.vision[self.rel_pt(2,0)] == -1 or self.vision[self.rel_pt(2,0)] == -2:
			self.touch[2] = 2
		elif self.vision[self.rel_pt(3,0)] == -1 or self.vision[self.rel_pt(3,0)] == -2:
			self.touch[2] = 3
		elif self.vision[self.rel_pt(4,0)] == -1 or self.vision[self.rel_pt(4,0)] == -2:
			self.touch[2] = 4
		else:
			self.touch[2] = 5
		#bot right -> 3
		if self.vision[self.rel_pt(1,1)] == -1 or self.vision[self.rel_pt(1,1)] == -2:
			self.touch[3] = 2
		elif self.vision[self.rel_pt(1,2)] == -1 or self.vision[self.rel_pt(1,2)] == -2:
			self.touch[3] = 3
		elif self.vision[self.rel_pt(2,1)] == -1 or self.vision[self.rel_pt(2,1)] == -2:
			self.touch[3] = 3
		elif self.vision[self.rel_pt(1,3)] == -1 or self.vision[self.rel_pt(1,3)] == -2:
			self.touch[3] = 4
		elif self.vision[self.rel_pt(2,2)] == -1 or self.vision[self.rel_pt(2,2)] == -2:
			self.touch[3] = 4
		elif self.vision[self.rel_pt(3,1)] == -1 or self.vision[self.rel_pt(3,1)] == -2:
			self.touch[3] = 4
		else:
			self.touch[3] = 5
		#bot -> 4
		if self.vision[self.rel_pt(0,1)] == -1 or self.vision[self.rel_pt(0,1)] == -2:
			self.touch[4] = 1
		elif self.vision[self.rel_pt(0,2)] == -1 or self.vision[self.rel_pt(0,2)] == -2:
			self.touch[4] = 2
		elif self.vision[self.rel_pt(0,3)] == -1 or self.vision[self.rel_pt(0,3)] == -2:
			self.touch[4] = 3
		elif self.vision[self.rel_pt(0,4)] == -1 or self.vision[self.rel_pt(0,4)] == -2:
			self.touch[4] = 4
		else:
			self.touch[4] = 5
		#bot left -> 5
		if self.vision[self.rel_pt(-1,1)] == -1 or self.vision[self.rel_pt(-1,1)] == -2:
			self.touch[5] = 2
		elif self.vision[self.rel_pt(-1,2)] == -1 or self.vision[self.rel_pt(-1,2)] == -2:
			self.touch[5] = 3
		elif self.vision[self.rel_pt(-2,1)] == -1 or self.vision[self.rel_pt(-2,1)] == -2:
			self.touch[5] = 3
		elif self.vision[self.rel_pt(-1,3)] == -1 or self.vision[self.rel_pt(-1,3)] == -2:
			self.touch[5] = 4
		elif self.vision[self.rel_pt(-2,2)] == -1 or self.vision[self.rel_pt(-2,2)] == -2:
			self.touch[5] = 4
		elif self.vision[self.rel_pt(-3,1)] == -1 or self.vision[self.rel_pt(-3,1)] == -2:
			self.touch[5] = 4
		else:
			self.touch[5] = 5
		#left -> 6
		if self.vision[self.rel_pt(-1,0)] == -1 or self.vision[self.rel_pt(-1,0)] == -2:
			self.touch[6] = 1
		elif self.vision[self.rel_pt(-2,0)] == -1 or self.vision[self.rel_pt(-2,0)] == -2:
			self.touch[6] = 2
		elif self.vision[self.rel_pt(-3,0)] == -1 or self.vision[self.rel_pt(-3,0)] == -2:
			self.touch[6] = 3
		elif self.vision[self.rel_pt(-4,0)] == -1 or self.vision[self.rel_pt(-4,0)] == -2:
			self.touch[6] = 4
		else:
			self.touch[6] = 5
		#top left -> 7
		if self.vision[self.rel_pt(-1,-1)] == -1 or self.vision[self.rel_pt(-1,-1)] == -2:
			self.touch[7] = 2
		elif self.vision[self.rel_pt(-1,-2)] == -1 or self.vision[self.rel_pt(-1,-2)] == -2:
			self.touch[7] = 3
		elif self.vision[self.rel_pt(-2,-1)] == -1 or self.vision[self.rel_pt(-2,-1)] == -2:
			self.touch[7] = 3
		elif self.vision[self.rel_pt(-1,-3)] == -1 or self.vision[self.rel_pt(-1,-3)] == -2:
			self.touch[7] = 4
		elif self.vision[self.rel_pt(-2,-2)] == -1 or self.vision[self.rel_pt(-2,-2)] == -2:
			self.touch[7] = 4
		elif self.vision[self.rel_pt(-3,-1)] == -1 or self.vision[self.rel_pt(-3,-1)] == -2:
			self.touch[7] = 4
		else:
			self.touch[7] = 5
	
	def dig_tunnel(self,world):		#Trivial dig for now
		if self.load > self.config['max_load']:
			self.state = 1
		elif self.rect.center[1] < 410:
			self.move(0,1,world)
			digs = self.dig(world)
			print 'Dig dig dig: ', digs
		elif self.dig_state == 0:		#Pick a new direction via random selection
			self.x_dir = random.randint(-1,1)
			self.y_dir = random.randint(0,1)
			if self.x_dir == 0 and self.y_dir == 0:
				self.dig_state = 0
			else:
				self.dig_state = 1
		elif self.dig_state == 1:		#Dig set direction for some distance
			self.move(self.x_dir,self.y_dir,world)
			digs = self.dig(world)
			print 'Dig dig dig: ', digs
			self.segment_length = self.segment_length + 1
			if self.segment_length > self.RANDOM_LENGTH:
				self.segment_length = 0
				self.dig_state = 0
				
	def unload_dirt(self,world):
		print 'Unloading ', self.touch, self.unload_state
		if self.unload_state == 0:	#Wall follow left priority
			if self.rect.center[1] < 405:
				self.unload_state = 2
			elif self.touch[0] > self.TOUCH_RANGE and self.touch[1] > self.TOUCH_RANGE and self.touch[7] > self.TOUCH_RANGE:
				self.move(0,-1,world)
			elif self.touch[0] > self.TOUCH_RANGE and self.touch[7] > self.TOUCH_RANGE and self.touch[6] > self.TOUCH_RANGE:
				self.move(-1,-1,world)
			elif self.touch[0] > self.TOUCH_RANGE and self.touch[1] > self.TOUCH_RANGE and self.touch[2] > self.TOUCH_RANGE:
				self.move(1,-1,world)
			elif self.touch[7] > self.TOUCH_RANGE and self.touch[6] > self.TOUCH_RANGE and self.touch[5] > self.TOUCH_RANGE:
				self.move(-1,0,world)
			elif self.touch[1] > self.TOUCH_RANGE and self.touch[2] > self.TOUCH_RANGE and self.touch[3] > self.TOUCH_RANGE:
				self.move(1,0,world)
				self.unload_state = 1
		if self.unload_state == 1:	#Wall follow right priority
			if self.rect.center[1] < 405:
				self.unload_state = 2
			elif self.touch[0] > self.TOUCH_RANGE and self.touch[1] > self.TOUCH_RANGE and self.touch[7] > self.TOUCH_RANGE:
				self.move(0,-1,world)
			elif self.touch[0] > self.TOUCH_RANGE and self.touch[7] > self.TOUCH_RANGE and self.touch[6] > self.TOUCH_RANGE:
				self.move(-1,-1,world)
			elif self.touch[0] > self.TOUCH_RANGE and self.touch[1] > self.TOUCH_RANGE and self.touch[2] > self.TOUCH_RANGE:
				self.move(1,-1,world)
			elif self.touch[1] > self.TOUCH_RANGE and self.touch[2] > self.TOUCH_RANGE and self.touch[3] > self.TOUCH_RANGE:
				self.move(1,0,world)
			elif self.touch[7] > self.TOUCH_RANGE and self.touch[6] > self.TOUCH_RANGE and self.touch[5] > self.TOUCH_RANGE:
				self.move(-1,0,world)
				self.unload_state = 0
		if self.unload_state == 2:				#Go to surface
			print self.touch[6]
			if self.touch[6] < 5:
				self.move(0,-1,world)
			else:
				self.unload_state = 3
			print 'Move to surface'
		if self.unload_state == 3:				#Move on top
			temp = self.vision[self.rel_pt(0,4)]
			if temp == 0:
				self.move(-1,-1,world)
			elif temp == -1:
				self.move(0,1,world)
				self.unload_state = 3
		if self.unload_state == 4:				#Travel down hill to find spot
			temp = self.vision[self.rel_pt(-1,3)]
			if temp == 0:
				self.move(-1,1,world)
			elif temp == -1:
				self.unload_state = 4
		if self.unload_state == 5:				#Travel up hill unloading
			temp = self.vision[self.rel_pt(1,2)]
			drops = np.array([self.rel_pt(0,2)])
			drops = self.drop(world,drops)
			print self.load
			if self.load == 0:
				print 'Out'
			elif temp == 0:
				self.move(0,-1,world)
				self.unload_state = 3
			else:
				self.move(1,-1,world)

				
				
				
			
			
	
	def bounce(self,world):
#		self.move(1,0,world)
		if self.collided != True:
			self.move(1,0,world)
			return 0
		else:
			self.move(-1,0,world)
			return 0
			
	def stop(self,world):
		return 1
		
		