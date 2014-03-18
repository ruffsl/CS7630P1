# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 17:26:09 2014

@author: whitemrj
"""

fps				= 20        #at most  this many frames per second
figsize			= (800, 600)

#import everything
import os
#import RoboSim.Robot.robot
from RoboSim import sim


###########################################
###########################################
def main():
	main_dir = os.path.split(os.path.abspath(__file__))[0]
#	myRobot = robot()
#	robots = [myRobot]
	mainSim = sim.sim(main_dir=main_dir, figsize=figsize, fps=fps)
	
	going = True
	while going:
		going = mainSim.update()
	mainSim.quit() #also calls display.quit()
	
if __name__ == '__main__':
    main()

        

