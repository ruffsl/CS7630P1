# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 17:29:08 2014

@author: changah, whitemrj
"""

import pygame
from pygame.locals import *
import math
import abc


class Robot(pygame.sprite.Sprite):
    """Abstract base 'Robot' class from which to subclass more specific
    Robot architecture classes
    
    Subclasses MUST implement abstract methods:
    update( ... )
    sense( ... )
    move( ... )
    rotate( ... )
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, image, pos_x, pos_y, azimuth, fwd_speed, spin_speed,\
                 visual_range, visual_angle):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
      
        self.image          = image  #Sprites must have an image and a rectangle
        self.image_original = self.image    #unchanging copy, for rotations
        self.r_transparency = 75
        self.rect           = image.get_rect()
        self.rect_original  = self.rect     #unchanging copy, for rotations
        self.rect.center    = pos_x, pos_y  #for now used only for initial position
        self.fwd_speed      = fwd_speed
        self.spin_speed     = spin_speed
        self.azi            = azimuth       #in degrees
        self.collided       = False
        self.spin_angle_left= 0             #relative angle left to spin
        #these are the parameters of the range-sensing system
        self.visual_range   = visual_range
        self.visual_angle   = visual_angle

    @abc.abstractmethod
    def update(self):
        """All sprites have an update() method. This function is
        typically called once per frame. IMPORTANT: All actions in
        here execute AFTER the ones called directly in the event loop.
        """
        pass

    #this function's job is to place in self.retina the range sensed by each sensor
    @abc.abstractmethod
    def sense(self):
        """Generate/extract local sensor data (eg. objects present within 
        sensor range) from current state of sim environment
        """
        pass
        
    @abc.abstractmethod
    def move(self,dx,dy):
        '''Translate robot in (x, y)'''
        previous_rect = self.rect           #remember in case undo is necessary
        self.rect = self.rect.move(dx,dy)

    @abc.abstractmethod
    def rotate(self,dtheta):
        center = self.rect.center
        self.azi += dtheta
        if self.azi >= 360:         #keep theta between -360..360
            self.azi = self.azi-360
        if self.azi <= -360:
            self.azi = self.azi+360
        original_rect = self.image_original.get_rect()
        rotated_image = pygame.transform.rotate(self.image_original, self.azi)
        rotated_rect  = original_rect.copy()
        rotated_rect.center = rotated_image.get_rect().center
        self.image = rotated_image.subsurface(rotated_rect).copy()
        self.image = change_alpha_for_alpha(self.image, self.r_transparency)

########end of Robot class########