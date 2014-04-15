# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 19:08:07 2014

@author: rox
"""

import pygame, os
import numpy as np
import Image
from pygame.locals import *
import RoboSim.Robot.robot


class sim:
	def __init__(self, robots, config):
		self.config = config
		self.robots = robots
		# Init pygame setup
		pygame.init()
		# set the window caption
		pygame.display.set_caption('Robosim!')
		# set the window icon
		pygame.display.set_icon(pygame.image.load(os.path.join(self.config['path'],'logo.png')))
		
		# Load in the background image		
		self.b_image  = self.load_image(self.config['b_image'])
		# If the window size is specifed
		if self.config['b_size']:
			# Then use the resolution from the config
			self.screen = pygame.display.set_mode(self.config['b_size'])
		else:
			# Otherwise use the resolution from the background image
			self.screen = pygame.display.set_mode(self.b_image.get_size())
		# Blend the background into the pygame screen
		self.screen.blit(self.b_image, (0, 0))
		# Init the clock used for refreshing sim
		self.clock = pygame.time.Clock()
		# Setup a render plane for all robots
		self.allrobots = pygame.sprite.RenderPlain(self.robots)
		# Generate the world and levels of dirt
		self.world = self.generateWorld()

	def generateWorld(self):
		'''Generate the starting world used in the simulation'''
		# Get the size of the world from the screen
		world_size = self.screen.get_size()
		# Init a empty matrix to store world
		world = np.zeros(world_size)
		# Specify the elevation of the surface
		surface = int((world_size[1]*self.config['dirt_ratio']))
		# Generate the dirt below the surface
		world[:,surface:-1] = self.config['dirt']
		# Set the bounds of the world with rock
		world[ :, 0] = self.config['rock']
		world[ :,-1] = self.config['rock']
		world[ 0, :] = self.config['rock']
		world[-1, :] = self.config['rock']
		return world

	def render(self, flags):
		'''Render the current state of the simulation'''
		
		if(flags['render']):
			# Make a copy of the current world
			world = self.b_image_raw.copy()
			# Get the dimentions of the world
			mask_shape = [self.world.shape[0], self.world.shape[1], 4]
			# Create a mask the same size as the world
			mask = np.zeros(mask_shape, dtype=np.uint8)
			# Make a dark shade of opaque dirt color
			dirt_color = [4,4,4,246]
			# Apply the color to the mask where dirt exsists in the world
			mask[np.where(self.world == -1)] = dirt_color
			for key, value in self.config['beacons'].items():
				mask[np.where(self.world == value['id'])] = value['color']
			pheromones = np.where(self.world > 0)
			if(pheromones[0].size):
				pheromone_colors = np.asarray([self.config['pheromone']['color']] * pheromones[0].size)
				print self.world[pheromones]
				pheromone_colors[:,3] = np.clip(self.world[pheromones]*int((255-60)/255),0,255) + np.clip(self.world[pheromones], 0, 1)*60
				mask[pheromones] = pheromone_colors
			# Ajust the mask as to match the upright image background
			mask = Image.fromarray(mask).transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_90)
			# Paste background with that of the mask to get the current world view		
			world.paste(mask, (0, 0, self.world.shape[0], self.world.shape[1]), mask)
			# Strip off the alpha channel, just use RGB channels		
			world = np.asarray(world)[...,0:3]
			# Transpose the image so its upright, not sideways
			world = np.swapaxes(world,0,1)
			# Make a serface from it
			self.b_image = pygame.surfarray.make_surface(world)
			# Then blend that surface with the screen
			self.screen.blit(self.b_image, (0, 0))
		
		# Render the robot movments
		self.allrobots.draw(self.screen)
		# Push the new frame to the display
		pygame.display.flip()

	def update(self, flags):
		'''Update the current state of the simulation'''
		# Set the flag by defult
#		going = True
		# Tic the clock acording to the fps speed
		self.clock.tick(self.config['fps'])
		
		#Event loop################################
		for event in pygame.event.get():
			if event == QUIT:
				flags['going'] = False
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					flags['going'] = False
				if event.key == K_SPACE:
					flags['render'] = not flags['render'] 
					print "render: ", flags['render']
		#End of event loop#########################

		# Now update all the robots
		self.allrobots.update(self.world, self.robots)
		# Then render all of the changes
		self.render(flags)
		# Return the state of the simulation
#		return going

	def quit(self):
		'''Quite the simulation'''
		pygame.quit()

	def load_image(self, name):
		'''Load images for the simulation'''
		# Get the path of the image
		path = os.path.join(self.config['path'], name)
		# Load it into a temp var
		temp_image = pygame.image.load(path)
		# Also keep the image around for the simulation rendering
		self.b_image_raw = Image.open(path)
		return temp_image