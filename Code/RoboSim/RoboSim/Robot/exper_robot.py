# -*- coding: utf-8 -*-

import robot

class exper_robot(robot.Robot):
#	Base class provides
#	def __init__(self, point, config):
#	def update(self, world, robots):
#	def move(self,dx,dy,world):
#	def load_image(self, name):
	
	def test_behavior(self,world):
#		self.move(1,0,world)
		if self.collided != True:
			self.move(1,0,world)
		else:
			self.move(-1,0,world)
		