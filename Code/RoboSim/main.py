# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 17:26:09 2014

@author: whitemrj
"""
tunnel 	= {'color': [255,140,0,255], 'id': -4}
room 		= {'color': [0,255,255,255], 'id': -5}
pheromone = {'color': [255,140,0,255], 'id': 0}

beacons = {'tunnel': tunnel, 'room': room}

config = {'fps': 500,
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
			'pheromone': 	pheromone}

#import everything
import os
from RoboSim.Robot import exper_robot
from RoboSim.Robot import etholog_robots
from RoboSim.Robot import robot
from RoboSim import sim


###########################################
###########################################
def main():
	# Set path to curret root directory for file
	config['path'] = os.path.split(os.path.abspath(__file__))[0]
	# Init Robots with config
#	myRobot = robot.Robot((500,500), config)
	myRobot = exper_robot.exper_robot((250,195), config, 0)
	myRobot2 = exper_robot.exper_robot((270,195), config, 1)
	robots = [myRobot, myRobot2]
	# Init simulation with robots
	mainSim = sim.sim(robots, config)
	
	# Progress flag
	going = True
	render = True
	flags = {'going': going, 'render': render}
	# Loop through simulation
	while flags['going']:
		# Update simulation and progress flag
		mainSim.update(flags)
	# Quit simulation and close window
	mainSim.quit() #also calls display.quit()

if __name__ == '__main__':
    main()