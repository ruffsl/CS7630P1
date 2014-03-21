# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 20:07:06 2014

@author: rox
"""

import os, pygame
import abc

class Robot(pygame.sprite.Sprite):
	def __init__(self, point, config):
		pygame.sprite.Sprite.__init__(self)
		self.point = point
		self.config = config
		self.collided = False			#Might need to check this attribute before move is called
		self.load = 0

		self.image  = self.load_image(self.config['r_image'])
#		if self.config['r_size']:
#			self.screen = pygame.display.set_mode(self.config['r_size'])
#		else:
#			self.screen = pygame.display.set_mode(r_image.get_size())

		self.rect = self.image.get_rect()
		self.rect.center = point				#Changed topleft to center
		
		self.dig_mask = self.getMask(self.config['dig_range'])
		self.sense_mask = self.getMask(self.config['sense_range'])
		
	def load_image(self, name):
		path = os.path.join(self.config['path'], name)
		temp_image = pygame.image.load(path)
		return temp_image
	
	def getMask(self, rad):
		return None
	
#Behave############################################################	
	
	@abc.abstractmethod	
	def update(self, world, robots):
		return None


	def move(self,dx,dy,world):
		previous_rect = self.rect
		self.rect = self.rect.move(dx,dy)
		if world[self.rect.center] < 0:		#Check the value in the numpy array for collision
			self.rect = previous_rect
			self.collided = True
		else:							
			self.collided = False
			
	def dig(self,dx,dy,world):
		previous_rect = self.rect
		self.rect = self.rect.move(dx,dy)
		if world[self.rect.center] == -1:			#Moveable object
			if self.load < 50:				#If the robot has room
				self.load = self.load + 1
				world[self.rect.center] = 0
				self.collided = False
			else:
				self.rect = previous_rect
				self.collided = True
		elif world[self.rect.center] == -2:		#Immovable object			
			self.rect = previous_rect
			self.collided = True
		else:								#Nothing there
			self.collided = False
			
	def sense(self, world):
		return None
		
	def drop(self, world):
		return None