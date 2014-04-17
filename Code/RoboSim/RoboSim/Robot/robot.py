# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 20:07:06 2014

@author: rox
"""

import os, pygame
import numpy as np
from skimage import draw
import abc

class Robot(pygame.sprite.Sprite):
	def __init__(self, point, config):
		pygame.sprite.Sprite.__init__(self)
		self.config = config
		self.collided = False			#Might need to check this attribute before move is called
		self.load = 0
		self.old_load = 0
		
		# Set the robot image from the config
		self.image  = self.load_image(self.config['r_image'])
		# Use a rect opject to keep the pose of the robot
		self.rect = self.image.get_rect()
		# Center the robot about its pose
		self.rect.center = point				#Changed topleft to center
		
	def load_image(self, name):
		'''Load images for the simulation'''
		# Get the path of the image
		path = os.path.join(self.config['path'], name)
		# Load it into a temp var
		temp_image = pygame.image.load(path)
		return temp_image
	
	def getMask(self, world, rad):
		'''Get a mask for the robot's world'''
		# Get the center of the robot pose
		x, y = self.rect.center
		# Draw a circle around that location
		xx, yy = draw.circle(x, y, rad, world.shape)
		# Set the index bounds of the world		
		xMin = 0
		xMax = world.shape[0]-1
		yMin = 0
		yMax = world.shape[1]-1
		# Find the points of the circle that exced the index bounds
		xxMin = np.asarray(np.where(xx<xMin))[0]
		xxMax = np.asarray(np.where(xx>xMax))[0]
		yyMin = np.asarray(np.where(yy<yMin))[0]
		yyMax = np.asarray(np.where(yy>yMax))[0]
		# Clip the shape of the circle to the bounds of the world
		xyd = np.concatenate((xxMin,xxMax,yyMin,yyMax))
		xx = np.delete(xx,xyd)
		yy = np.delete(yy,xyd)
		# Make an empty mask same size as the world
		mask = np.zeros(world.shape)
		# Apply the circle to mask of the world
		mask[xx, yy] = 1
		return mask
		
	def getRange(self, world, rad):
		'''Return the section of the world within range'''
		# Get the mask for the curret world
		mask = self.getMask(world, rad)
		# Apply the mask to the world
		worldRange = world*mask
		# Use the invert of the mask to specify the unknown
		worldRange -= (mask-1)*(self.config['unknown'])
		return worldRange
		
	def rel_pt(self, x_point, y_point):	#Give a point relative to robot, return point in global frame
		'''Return a point relative to the robot'''		
		point = (self.rect.center[0]+x_point,self.rect.center[1]+y_point)
		return point
	
#Behave############################################################	
	
	@abc.abstractmethod	
	def update(self, world, robots):
		'''Update method all robots must implement'''
		self.old_load = self.load
		return None

	@abc.abstractmethod	
	def move(self,dx,dy,world):
		'''Move robot by a given delta'''
		self.rect = self.rect.move(dx,dy)
		return None
		
	def dig(self,world):
		'''Dig the dirt arround the robot'''
		# Get the digging range of the robot
		dig_range = self.getRange(world,self.config['dig_range'])
		# Find all the dirt within range
		digs = np.where(dig_range==self.config['dirt'])
		# Empty out those points
		world[digs] = self.config['empty']
		# Increment the current load counter
		self.load += digs[0].size
		# return the amount of dirt colected
		return digs[0].size
			
	def sense(self, world):
		'''Sense the world arround the robot'''
		# Get the world in sensing range of the robot		
		sense_range = self.getRange(world,self.config['sense_range'])
		return sense_range
		
	def drop(self, world, drops):
		'''Drop dirt at given locations around the robot'''
		# Get the dropping range of the robot
		drop_range = self.getRange(world,self.config['dig_range'])
		# Get the possible dropping locations that are empty		
		possible_drops = np.where(drop_range[tuple(drops.T)]>=self.config['empty'])
		# Cross refrence the robot's drop spots with what is possible
		drops = drops[possible_drops]
		# Deposit the real drops available
		world[tuple(drops.T)] = self.config['dirt']
		# Decrement the load by only by the number of real drops made
		self.load -= drops.shape[0]
		# return the number of real drops made
		return drops.shape[0]
	
	def is_employed(self):
		if self.old_load == self.load:
			return 0
		else:
			return 0