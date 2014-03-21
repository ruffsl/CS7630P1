# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 23:10:15 2014

@author: changah

Description:
Parameter(s): 
	img_file - full .png image file path & name 
			(eg. 'tools/map_example_1.png')
Output:
	world - matrix (consisting of values 0, -1 or -2) to 
	        replace sim class' self.world attribute

Description:
Given .png image file containing only black (immovable obstacles) 
& white (empty spaces) pixels, generates the corresponding world matrix 
that can be used to replace sim class' self.world attribute

Allows tunnels/cavities to be manually drawn into .png file and then imported 
into a format directly usable by the 'sim' class. This is an aid to allow
quick and controlled testing of robot behaviors

Note: 'tools/background_template.png' contains a 1000x1000 pixel image that
can be used as a starting point from which to create insert underground 
tunnels/cavities
"""

import numpy as np
import scipy as sp

def world_generator(img_file):
	img_map = sp.misc.imread(img_file, 1)
	img_map = img_map.astype(np.uint8)
	img_map = np.swapaxes(img_map, 0, 1)

	world_size = img_map.shape[0], img_map.shape[1]
	world = np.zeros(world_size)

	# assign y >= 400 as movable obstacles (-1 = movable obst)
	surface = int((world_size[1]/10.0)*4)
	world[:,surface:-1] = -1
	
	# carry over img tunnels/cavities (0 = empty space)
	world[np.where(img_map == 255)] = 0

	# world boundaries (-2 = immovable obstacles)
	world[ :, 0] = -2
	world[ :,-1] = -2
	world[ 0, :] = -2
	world[-1, :] = -2	
	
	return world
	
	
#if __name__ == "__main__":
#	cur_world = world_generator('map_example_1.png')
#
#	print 'size: ', cur_world.shape
#
#	print '(1, 1): ', cur_world[20, 407]
#	print '(1, -2): ', cur_world[1, -2]
#	print '(-2, 1): ', cur_world[-2, 1]
#	print '(-2, -2): ', cur_world[-2, -2]
