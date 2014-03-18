# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 17:29:08 2014

@author: whitemrj
"""

fps                 = 20        #at most  this many frames per second
back_image          = 'back2_800_600.bmp'   #must have this file in same dir.
display_cols        = 800
display_rows        = 600
wall_thickness      = 5         #thickness in pixels
wall_color          = 'black'
food_color          = 'green'
trace_color         = 'blue'
trace_arc           = 10        #in degrees, shows on both sides of r.azi
trace_decrease      = -17       #negative, subtracts from robot size to make a smaller trace
trace_width         = 1
leave_trace         = 0         #default mode is not to leave traces

color_of_nothing    = 'white'
sim_version         = 'RoboSim v.19'

r_image          = 'robo2.bmp'  #must have this file in same dir.
r_edge           = 51       #edge of square surrounding robot (in pixels)
r_init_azi       = 0        #azimuth, in degrees (up is 0)
r_init_x_topleft = 10       #must be >= wall_thickness
r_init_y_topleft = 20
r_step_tele      = 10       #steps for teleop, equal in x or y (in pixels)
r_step_theta     = 7.5      #step for teleop, in azimuth
r_init_fwd_speed = 5        #pixels per simulation cycle
r_init_spin_speed= 3        #degrees per simulation cycle
r_transparency   = 75       #0 is totally transp., 255 totally opaque
r_visual_range   = 200      #measured from robot center
r_visual_angle   = 30       #in degrees, must divide 90 exactly!
r_visual_granularity = 5    #must be < wall_thickness for walls to be detected correctly!

import pygame
from pygame.locals import *
import math
import random
import abc


class Robot(pygame.sprite.Sprite):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def __init__(self, image, x_topleft, y_topleft, azimuth, fwd_speed, spin_speed,\
                 visual_range, visual_angle):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
      
        self.image          = image  #Sprites must have an image and a rectangle
        self.image_original = self.image    #unchanging copy, for rotations
        self.rect           = image.get_rect()
        self.rect_original  = self.rect     #unchanging copy, for rotations
        self.rect.topleft   = x_topleft, y_topleft  #for now used only for initial position
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
        n = (self.nr_sensors - 1)/2     #the "natural" sensor range is -n to +n
        granu = r_visual_granularity    #must be at least as large as the wall thickness!!
        for i in range(-n,n+1):         #sense with each of the 2n+1 range sensors
            ang = (self.azi - i*self.visual_angle)*math.pi/180
            for distance in range(granu, self.visual_range+granu, granu):
                x = self.rect.center[0]-distance*math.sin(ang)  #endpoint coordinates
                y = self.rect.center[1]-distance*math.cos(ang)
                nr_collisions = 0
                count = -1          #needed to coordinate the two lists, to extract color after loop
                for ob in list_rect_obstacles:  #use the stripped-down list of rectangles for speed
                    count = count + 1
                    if ob.collidepoint(x,y):
                        nr_collisions = 1
                        break       #breaks out of wall loop
                if nr_collisions:   #non-zero collision
                    break           #breaks out of distance loop
            #distance now has the min. between the visual range and the first collision
            self.retina[i+n][0] = distance
            if nr_collisions:       #nr_collisions is 1 if a collision has occurred
                self.retina[i+n][1] = list_obstacles[count].color #color comes form the larger list
            else:
                self.retina[i+n][1] = pygame.Color(color_of_nothing)
        #print 'sense -->retina is:\n', self.retina
        self.printRetina()
        
    @abc.abstractmethod
    def move(self,dx,dy):
        previous_rect = self.rect           #remember in case undo is necessary
        self.rect = self.rect.move(dx,dy)
        if self.rect.collidelist(list_rect_obstacles) != -1:#if collision exists
            print 'mode  -->I collided with wall(s)',\
                  self.rect.collidelistall(list_rect_obstacles)
            self.rect = previous_rect                   #undo the move
            self.collided = True
        else:                   #if there was no collision
            if leave_trace:     #update trace list
                tr = self.rect.inflate(trace_decrease, trace_decrease)
                list_traces.append(Trace(tr, 90+self.azi-trace_arc, 90+self.azi+trace_arc))
    """           
    def spin(self,dtheta):
        center = self.rect.center
        self.azi += dtheta
        if self.azi >= 360:         #keep theta between -360..360
            self.azi = self.azi-360
        if self.azi <= -360:
            self.azi = self.azi+360
        temp_rota_imag = pygame.transform.rotate(self.image_original, self.azi)
        self.image = pygame.transform.smoothscale(temp_rota_imag,(r_edge,r_edge))
        #smoothscale pads w/pixels having alpha=0. Increasing alpha to see a faint rect.
        self.image = change_alpha_for_alpha(self.image, r_transparency)
        self.rect = self.image.get_rect()
        self.rect.center = center
        #when using transform.smoothscale, rotations never generate collisions, b/c
        #the image always stays a square of edge r_edge
        if leave_trace:     #update trace list
            tr = self.rect.inflate(trace_decrease, trace_decrease)
            list_traces.append(Trace(tr, 90+self.azi-trace_arc, 90+self.azi+trace_arc))
    """

    def spin(self,dtheta):
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
        self.image = change_alpha_for_alpha(self.image, r_transparency)
        if leave_trace:     #update trace list
            tr = self.rect.inflate(trace_decrease, trace_decrease)
            list_traces.append(Trace(tr, 90+self.azi-trace_arc, 90+self.azi+trace))
          
    def draw_rays(self, target_surf):
        n = (self.nr_sensors - 1)/2 #the "natural" sensor range -n to +n
        for i in range(-n,n+1):     #draw the 2n+1 rays of the range sensors
            ang = (self.azi - i*self.visual_angle)*math.pi/180
            x = self.rect.center[0]-self.retina[i+n][0]*math.sin(ang)
            y = self.rect.center[1]-self.retina[i+n][0]*math.cos(ang)
            #use aaline for smoother (but slower) lines
            pygame.draw.line(target_surf, (0,0,0), self.rect.center, (x,y))
########end of Robot class########