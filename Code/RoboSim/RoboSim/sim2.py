# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 19:08:07 2014

@author: rox
"""

import pygame, os
import random
from pygame.locals import *
import RoboSim.Robot.robot


class sim:
	def __init__(self, robots, config):
		self.config = config
		self.robots = robots
		self.world = self.generateWorld()


		pygame.init()
		pygame.display.set_caption('Robosim!')
		self.b_image  = self.load_image(self.config['b_image'])
		if self.config['b_size']:
			self.screen = pygame.display.set_mode(self.config['b_size'])
		else:
			self.screen = pygame.display.set_mode(self.b_image.get_size())
		self.screen.blit(self.b_image, (0, 0))
		self.clock = pygame.time.Clock()

		self.allrobots = pygame.sprite.RenderPlain(self.robots)

	def generateWorld(self):
		return None

	def render(self):
		self.allrobots.update()
		self.screen.blit(self.b_image, (0, 0))
		self.allrobots.draw(self.screen)
		pygame.display.flip()

	def update(self):
		going = True
		self.clock.tick(self.config['fps'])

		#Event loop################################
		for event in pygame.event.get():
			if event == QUIT:
				going = False
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					going = False
		#End of event loop#########################

		self.render()
		return going

	def quit(self):
		pygame.quit()

	def load_image(self, name):
		path = os.path.join(self.config['path'], name)
		temp_image = pygame.image.load(path)
		return temp_image