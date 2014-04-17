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
			'half_life':	10,
			'done_it':	10000}

#import everything
import os
from RoboSim.Robot import exper_robot
from RoboSim.Robot import etholog_robots
from RoboSim.Robot import robot
from RoboSim import sim
import pandas as pd


###########################################
###########################################
def trial(mode):
	# Set path to curret root directory for file
	config['path'] = os.path.split(os.path.abspath(__file__))[0]
	# Init Robots with config
#	myRobot = robot.Robot((500,500), config)
#	myRobot = exper_robot.exper_robot((250,195), config, 0)
	if mode == 'etholog':
		myRobot1 = etholog_robots.AntRobot((200,195), config)
		myRobot2 = etholog_robots.AntRobot((250,195), config)
		myRobot3 = etholog_robots.AntRobot((300,195), config)
		robots = [myRobot1, myRobot2, myRobot3]
	elif mode == 'exper':
		myRobot = exper_robot.exper_robot((250,195), config, 0)
		myRobot2 = exper_robot.exper_robot((270,195), config, 1)
		myRobot3 = exper_robot.exper_robot((210,195), config, -1)
		myRobot4 = exper_robot.exper_robot((310,195), config, 1)
		myRobot5 = exper_robot.exper_robot((320,195), config, 1)
#		myRobot = exper_robot.exper_robot((450,395), config, 0)
#		myRobot2 = exper_robot.exper_robot((470,395), config, 1)
#		myRobot3 = exper_robot.exper_robot((410,395), config, -1)
#		myRobot4 = exper_robot.exper_robot((510,395), config, 1)
#		myRobot5 = exper_robot.exper_robot((520,395), config, 1)
		robots = [myRobot, myRobot2, myRobot3, myRobot4, myRobot5]
	# Init simulation with robots
	mainSim = sim.sim(robots, config)
	
	# Progress flag
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
	return data
	
def to_file(data, i, mode, tag):
	path = os.path.abspath(__file__ + "/../../../")
	path += '/Data/' + mode + '/'
	file_name =  mode + tag + '_trail_%d.csv' % i
	print path + file_name
	df = pd.DataFrame(data) 
	df.to_csv(path + file_name, index=False)
	
def main():
#	mode = 'etholog'
	mode = 'exper'
	tag = ''
	for i in range(1):
		data = trial(mode)
		to_file(data, i, mode, tag)
	

if __name__ == '__main__':
    main()