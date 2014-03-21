# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 17:26:09 2014

@author: whitemrj
"""

config = {'fps': 20,
			'b_image'	: 	'background.png',
			'b_size'	: 	None,
			'r_image'	: 	'robo10.png',
			'r_size'	: 	None,
			'path'	:	None,
			'seed'	: 	42,
			'max_load':		10,
			'sense_range':	10,
			'dig_range': 	10,
			'body_range':	5}

#import everything
import os
from RoboSim.Robot import exper_robot
from RoboSim.Robot import robot
from RoboSim import sim


###########################################
###########################################
def main():
	config['path'] = os.path.split(os.path.abspath(__file__))[0]
#	myRobot = robot.Robot((500,500), config)
	myRobot = exper_robot.exper_robot((240,350), config)
	robots = [myRobot]
	mainSim = sim.sim(robots, config)

	going = True
	while going:
		going = mainSim.update()
		myRobot.behavior(mainSim.world)
	mainSim.quit() #also calls display.quit()

if __name__ == '__main__':
    main()