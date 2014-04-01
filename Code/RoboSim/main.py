# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 17:26:09 2014

@author: whitemrj
"""

config = {'fps': 200,
			'b_image'	: 	'background.png',
			'b_size'	: 	None,
			'r_image'	: 	'robo10.png',
			'logo_image'	: 	'logo.png',
			'path'	:	None,
			'seed'	: 	42,
			'max_load':		100,
			'sense_range':	10,
			'dig_range': 	10,
			'body_range':	5,
			'dirt': 			-1,
			'rock': 			-2,
			'unknown':		-3,
			'empty':			 0}

#import everything
import os
from RoboSim.Robot import exper_robot
from RoboSim.Robot import robot
from RoboSim import sim


###########################################
###########################################
def main():
	# Set path to curret root directory for file
	config['path'] = os.path.split(os.path.abspath(__file__))[0]
	# Init Robots with config
#	myRobot = robot.Robot((500,500), config)
	myRobot = exper_robot.exper_robot((500,390), config)
	robots = [myRobot]
	# Init simulation with robots
	mainSim = sim.sim(robots, config)
	
	# Progress flag
	going = True
	# Loop through simulation
	while going:
		# Update simulation and progress flag
		going = mainSim.update()
	# Quit simulation and close window
	mainSim.quit() #also calls display.quit()

if __name__ == '__main__':
    main()