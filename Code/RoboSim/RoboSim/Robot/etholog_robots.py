# -*- coding: utf-8 -*-
"""
Created on Wed Mar 19 01:20:48 2014

@author: changah
"""

import pygame
from pygame.locals import *
import math
import random
#from RoboSim.RoboSim.Robot.robot_arch import RobotArch
import robot_arch

class AntRobot(robot_arch.RobotArch):
    """Test subclass of RobotArch abstract base class"""
    
    def __init__(self, image, pos_x, pos_y, azimuth, fwd_speed, spin_speed,\
                 visual_range, visual_angle, load):
        super(AntRobot, self).__init__(image, pos_x, pos_y, azimuth, fwd_speed, spin_speed,\
                 visual_range, visual_angle, load)
        
        # Local (Robot) Constants
        self.transparency   = 75
        self.max_load = 10
        self.max_range = 10
        self.max_speed = 10


    def update(self, occupancy_grid, agent_list):
        """All sprites have an update() method. This function is
        typically called once per frame. IMPORTANT: All actions in
        here execute AFTER the ones called directly in the event loop.
        """
        dx = random.randint(-10, 10)
        dy = random.randint(-10, 10)
        dtheta = random.randint(-45, 45)

        self.sense(occupancy_grid, agent_list)
        self.move(dx, dy)
        self.rotate(dtheta)        
        

    #this function's job is to place in self.retina the range sensed by each sensor
    def sense(self, occupancy_grid, agent_list):
        """Sensor processing of robot's surrounding environment"""
        pass

      
    def move(self,dx,dy):
        """Translate robot by (dx, dy)"""
#        previous_rect = self.rect           #remember in case undo is necessary
#        self.rect = self.rect.move(dx,dy)
#        if self.rect.collidelist(list_rect_obstacles) != -1:#if collision exists
#            print 'mode  -->I collided with wall(s)',\
#                  self.rect.collidelistall(list_rect_obstacles)
#            self.rect = previous_rect                   #undo the move
#            self.collided = True
        self.rect.move_ip(dx, dy)


    def rotate(self,dtheta):
        """Rotate robot by dtheta (degrees)"""
#        center = self.rect.center
#        self.azi += dtheta
#        if self.azi >= 360:         #keep theta between -360..360
#            self.azi = self.azi-360
#        if self.azi <= -360:
#            self.azi = self.azi+360
#        original_rect = self.image_original.get_rect()
#        rotated_image = pygame.transform.rotate(self.image_original, self.azi)
#        rotated_rect  = original_rect.copy()
#        rotated_rect.center = rotated_image.get_rect().center
#        self.image = rotated_image.subsurface(rotated_rect).copy()
#        self.image = change_alpha_for_alpha(self.image, r_transparency)
        self.azi += dtheta
        
    def __str__(self):
        return 'AntRobot: pos(x, y) = (%s, %s), orientation(theta) = %s'\
        % (self.rect.center[0], self.rect.center[1], self.azi)
        
        
if __name__ == "__main__":
    garbage_img = pygame.image.load('../../robo1.bmp')
    mAntRobot = AntRobot(garbage_img, 1, 1, 90, 2, 3, 10, 10, 15)
    for cnt in range(5):
        print(mAntRobot)
        mAntRobot.update('garbage', 'garbage')
