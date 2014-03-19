# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 19:08:07 2014

@author: rox
"""

import pygame, os
import random
import numpy as np
import Image
from pygame.locals import *
import RoboSim.Robot.robot


class sim:
	def __init__(self, robots, config):
		self.config = config
		self.robots = robots

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

		self.world = self.generateWorld()

	def generateWorld(self):
		world_size = self.screen.get_size()
		world = np.zeros(world_size)
		surface = int((world_size[1]/10.0)*4)
		world[:,surface:-1] = -1
		world[ :, 0] = -2
		world[ :,-1] = -2
		world[ 0, :] = -2
		world[-1, :] = -2
		return world

	def render(self):
		world = self.b_image_raw.copy()

		mask_shape = [self.world.shape[0], self.world.shape[1], 4]
		mask = np.zeros(mask_shape, dtype=np.uint8)
		mask[np.where(self.world.T == -1)] = [36,16,4,200]
		mask = Image.fromarray(mask)
		world.paste(mask, (0, 0, self.world.shape[0], self.world.shape[1]), mask)
		world = np.asarray(world)[...,0:3]

		world = np.swapaxes(world,0,1)
		self.b_image = pygame.surfarray.make_surface(world)
		self.screen.blit(self.b_image, (0, 0))
		self.allrobots.draw(self.screen)

		self.allrobots.update()
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
		self.b_image_raw = Image.open(path)
		return temp_image