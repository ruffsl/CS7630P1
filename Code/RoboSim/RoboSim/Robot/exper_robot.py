# -*- coding: utf-8 -*-

import robot

class exper_robot(robot.Robot):
#	Base class provides
#	def __init__(self, point, config):
#	def update(self, world, robots):
#	def move(self,dx,dy,world):
#	def load_image(self, name):
	
	def __init__(self, point, config):
		robot.Robot.__init__(self, point, config)
		self.state = 0
	
	def behavior(self,world):
		if self.state == 0:
			self.move(0,1,world)
			if self.collided == True:
				self.state = 1
		elif self.state == 1:
			self.dig(0,1,world)
			if self.collided == True:
				self.state = 2
		elif self.state == 2:
			print "The ant is full, stop this madness"
			
#		if self.state == 0:
#			self.state = self.bounce(world)
#		elif self.state == 1:
#			self.state = self.stop(world)
	
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
		
		