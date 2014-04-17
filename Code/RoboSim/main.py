# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 17:26:09 2014

@author: whitemrj
"""

tunnel 	= {'color': [255,140,0,255], 'id': -4}
room 	= {'color': [0,255,255,255], 'id': -5}
branch 	= {'color': [240,150,240,255], 'id': -6}
pheromone = {'color': [255,140,0,255], 'id': 0}

beacons = {'tunnel': tunnel, 'room': room, 'branch': branch}

config = {'fps': 200,
			'b_image'	: 	'background_500.png',
			'b_size'	: 	None,
			'r_image'	: 	'robo10.png',
			'logo_image'	: 	'logo.png',
			'path'	:	None,
			'seed'	: 	42,
			'max_load':		500,
			'sense_range':	6,
			'dig_range': 		5,
			'body_range':	5,
			'dirt': 			-1,
			'rock': 			-2,
			'unknown':		-3,
			'empty':			 0,
			'beacons':		beacons,
			'pheromone': 	pheromone,
			'dirt_ratio':	4/10.0,
			'done_ratio':	1.5/100.0,
			'half_life':	250,
			'done_it':		2000,
			'trials':		3,
			'n':				1,
#			'mode':			'exper',
			'mode':			'etholog',
			'tag':			None}

#import everything
import os
from RoboSim.Robot import exper_robot
from RoboSim.Robot import etholog_robots
from RoboSim.Robot import robot
from RoboSim import sim
import pandas as pd
import matplotlib.pyplot as plt
import time


###########################################
###########################################
def trial(mode):
	# Set path to curret root directory for file
	config['path'] = os.path.split(os.path.abspath(__file__))[0]
	# Init Robots with config
#	myRobot = robot.Robot((500,500), config)
#	myRobot = exper_robot.exper_robot((250,195), config, 0)
	if mode == 'etholog':
		if config['n'] == 5:
			myRobot1 = etholog_robots.AntRobot((200,195), config)
			myRobot2 = etholog_robots.AntRobot((250,195), config)
			myRobot3 = etholog_robots.AntRobot((300,195), config)
			myRobot4 = 0
			myRobot5 = 0
			robots = [myRobot1, myRobot2, myRobot3, myRobot4, myRobot5]
		if config['n'] == 3:
			myRobot1 = etholog_robots.AntRobot((200,195), config)
			myRobot2 = etholog_robots.AntRobot((250,195), config)
			myRobot3 = etholog_robots.AntRobot((300,195), config)
			robots = [myRobot1, myRobot2, myRobot3]
		if config['n'] == 1:
			myRobot1 = etholog_robots.AntRobot((200,195), config)
			robots = [myRobot1]
			
	elif mode == 'exper':
		if config['n'] == 5:
			myRobot1 = exper_robot.exper_robot((250,195), config, 0)
			myRobot2 = exper_robot.exper_robot((270,195), config, 1)
			myRobot3 = exper_robot.exper_robot((210,195), config, -1)
			myRobot4 = exper_robot.exper_robot((310,195), config, 1)
			myRobot5 = exper_robot.exper_robot((320,195), config, 1)
			robots = [myRobot1, myRobot2, myRobot3, myRobot4, myRobot5]
		if config['n'] == 3:
			myRobot1 = exper_robot.exper_robot((250,195), config, 0)
			myRobot2 = exper_robot.exper_robot((270,195), config, 1)
			myRobot3 = exper_robot.exper_robot((210,195), config, -1)
			robots = [myRobot1, myRobot2, myRobot3]
		if config['n'] == 1:
			myRobot1 = exper_robot.exper_robot((250,195), config, 0)
			robots = [myRobot1]
			
	# Init simulation with robots
	mainSim = sim.sim(robots, config)
	
	# Progress flags
	going = True
	render = False
	logging = True
	flags = {'going': going, 'render': render, 'logging': logging}
	# Loop through simulation
	while flags['going']:
		# Update simulation and progress flag
		mainSim.update(flags)
	# Quit simulation and close window
	data = mainSim.quit() #also calls display.quit()
	# Return the data
	return data
	
def to_file(data, world, i, mode, tag):
	'''Save the logged data to disk'''
	# Get the path of the Data folder
	path = os.path.abspath(__file__ + "/../../../")
	path += '/Data/' + mode + '/'
	# Make a filename
	file_name =  mode + '_' + tag + '_trail_%d' % i
	# Save the logs to a csv file for later
	df = pd.DataFrame(data) 
	df.to_csv(path + file_name + '.csv', index=False)
	# Get a mask of just the dirt
	world = world.T != config['dirt']
	# Save the world to a black and white image
	plt.imsave(path + file_name + '.png', world, cmap=plt.cm.gray)
	# Print that the file is saved
	print "Saved: ", path + file_name
	
def main():
	mode = config['mode']
	# Custome naming tad
	tag = config['tag']
	# If none given
	if not (tag):
		# Then use the current time stamp
		tag = time.strftime("%Y%m%d-%H%M%S")
	# Simulate and log each trial
	for i in range(config['trials']):
		data, world = trial(mode)
		to_file(data, world, i, mode, tag)

if __name__ == '__main__':
    main()