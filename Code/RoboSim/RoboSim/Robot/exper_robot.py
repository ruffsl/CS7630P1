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
	
	def __init__(self, point, config):
		robot.Robot.__init__(self, point, config)
		self.state = 0
		self.load = 0
		self.vision = []
		random.seed()
		self.x_dir = 0
		self.y_dir = 0
		self.segment_length = 0
		
		#Sub states for behaviors
		self.unload_state = 0
		self.dig_state = 0
		
	def update(self, world, robots):
		self.vision = self.sense(world)
		if self.state == 0:
			self.dig_tunnel(world)
		elif self.state == 1:
			self.unload_dirt(world)
		return None
	
	def dig_tunnel(self,world):		#Trivial dig for now
		if self.load > self.config['max_load']:
			self.state = 1
		elif self.dig_state == 0:		#Pick a new direction via random selection
			self.x_dir = random.randint(-1,1)
			self.y_dir = random.randint(0,1)
			self.dig_state = 1
		elif self.dig_state == 1:		#Dig set direction for some distance
			self.move(self.x_dir,self.y_dir,world)
			digs = self.dig(world)
			print 'Dig dig dig: ', digs
			self.segment_length = self.segment_length + 1
			if self.segment_length > 15:
				self.segment_length = 0
				self.dig_state = 0
				
	def unload_dirt(self,world):
		if self.unload_state == 0:				#Move close to wall
			temp = self.vision[self.rel_pt(-3,0)]
			if temp == 0:
				self.move(-1,0,world)
			elif temp == -1:
				self.unload_state = 1
		if self.unload_state == 1:				#Go to surface
			temp = self.vision[self.rel_pt(-4,0)]
			if temp == -1:
				self.move(0,-1,world)
			elif temp == 0:
				self.unload_state = 2
		if self.unload_state == 2:				#Move on top
			temp = self.vision[self.rel_pt(0,4)]
			if temp == 0:
				self.move(-1,-1,world)
			elif temp == -1:
				self.move(0,1,world)
				self.unload_state = 3
		if self.unload_state == 3:				#Travel down hill to find spot
			temp = self.vision[self.rel_pt(-1,3)]
			if temp == 0:
				self.move(-1,1,world)
			elif temp == -1:
				self.unload_state = 4
		if self.unload_state == 4:				#Travel up hill unloading
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
		
		