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

		self.image  = self.load_image(self.config['r_image'])

		self.rect = self.image.get_rect()
		self.rect.center = point				#Changed topleft to center
		
	def load_image(self, name):
		path = os.path.join(self.config['path'], name)
		temp_image = pygame.image.load(path)
		return temp_image
	
	def getMask(self, world, rad):
		x, y = self.rect.center
		xx, yy = draw.circle(x, y, rad/2.0, world.shape)	#YOU CALL IT DIAMETER IF YOU'RE GOING TO DIVIDE
		xMin = 0								#IT BY TWO RUFFIN JESUS COME ON
		xMax = world.shape[0]-1
		yMin = 0
		yMax = world.shape[1]-1
		
		xxMin = np.asarray(np.where(xx<xMin))[0]
		xxMax = np.asarray(np.where(xx>xMax))[0]
		yyMin = np.asarray(np.where(yy<yMin))[0]
		yyMax = np.asarray(np.where(yy>yMax))[0]
		
		xyd = np.concatenate((xxMin,xxMax,yyMin,yyMax))
		xx = np.delete(xx,xyd)
		yy = np.delete(yy,xyd)
		mask = np.zeros(world.shape)
		mask[xx, yy] = 1
		
		return mask
		
	def getRange(self, world, rad):
		mask = self.getMask(world, rad)
		worldRange = world*mask
		worldRange += (mask-1)*3
		return worldRange
		
	def rel_pt(self, x_point, y_point):	#Give a point relative to robot, return point in global frame
		point = (self.rect.center[0]+x_point,self.rect.center[1]+y_point)
		return point
	
#Behave############################################################	
	
	@abc.abstractmethod	
	def update(self, world, robots):
		return None

	def move(self,dx,dy,world):
		self.rect = self.rect.move(dx,dy)
		return None
		
	def dig(self,world):
		dig_range = self.getRange(world,self.config['dig_range'])
		digs = np.where(dig_range==-1)
		world[digs] = 0
		self.load += digs[0].size
		return digs[0].size
			
	def sense(self, world):
		sense_range = self.getRange(world,self.config['sense_range'])
		return sense_range
		
	def drop(self, world, drops):
		drop_range = self.getRange(world,self.config['dig_range'])
		possible_drops = np.where(drop_range[tuple(drops.T)]>=0)
		drops = drops[possible_drops]
		world[tuple(drops.T)] = -1
		self.load -= drops.shape[0]
		return drops.shape[0]