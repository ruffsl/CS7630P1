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
			'path'		:	None,
			'seed'		: 	42}

#import everything
import os
from RoboSim.Robot import robot2
from RoboSim import sim2


###########################################
###########################################
def main():
	config['path'] = os.path.split(os.path.abspath(__file__))[0]
	myRobot = robot2.Robot((500,500), config)
	robots = (myRobot)
	mainSim = sim2.sim(robots, config)

	going = True
	while going:
		going = mainSim.update()
	mainSim.quit() #also calls display.quit()

if __name__ == '__main__':
    main()