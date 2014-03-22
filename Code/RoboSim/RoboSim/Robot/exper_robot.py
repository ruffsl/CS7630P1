# -*- coding: utf-8 -*-

import robot
import numpy as np

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
		
	def update(self, world, robots):
		self.behavior(world)
		return None
	
	def behavior(self,world):
		if self.state == 0:
			if self.load < self.config['max_load']:
				digs = self.dig(world)
				print 'Dig dig dig: ', digs
				self.move(0,1,world)
			else:
				self.state = 1
				
		if self.state == 1:
			if (self.rect.center[1] > 395):
				self.move(0,-1,world)
				print "Soo full!!"
			else:
				self.state = 2
		
		if self.state == 2:
			if self.load > 0:
				drops = np.array([[-1,-5],
										 [-1,-4],
										 [-1,-3],
										 [-1,-2],
										 [-1,-1],
										 [-1, 0],
										 [-1, 1],
										 [-1, 2],
										 [-1, 3],
										 [-1, 4],
										 [-1, 5]])
				x, y = self.rect.center
				drops[:,0] += x
				drops[:,1] += y
				drops = self.drop(world, drops)
				self.move(-1,0,world)
				print "drop drop drop: ", drops
			else:
				self.state = 0
				
	
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
		
		