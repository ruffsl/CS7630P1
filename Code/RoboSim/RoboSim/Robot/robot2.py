# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 20:07:06 2014

@author: rox
"""

import os, pygame

class Robot(pygame.sprite.Sprite):
	def __init__(self, point, config):
		pygame.sprite.Sprite.__init__(self)
		self.point = point
		self.config = config


		self.image  = self.load_image(self.config['r_image'])
#		if self.config['r_size']:
#			self.screen = pygame.display.set_mode(self.config['r_size'])
#		else:
#			self.screen = pygame.display.set_mode(r_image.get_size())

		self.rect = self.image.get_rect()
		self.rect.topleft = point

	def update(self, world, robots):
		return None


	def move(self,dx,dy,world):
		previous_rect = self.rect
		self.rect = self.rect.move(dx,dy)
		if self.rect.collidelist(world) != -1:
			self.rect = previous_rect
			self.collided = True


	def load_image(self, name):
		path = os.path.join(self.config['path'], name)
		temp_image = pygame.image.load(path)
		return temp_image