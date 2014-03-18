# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 17:29:08 2014

@author: whitemrj
"""

import pygame
from pygame.locals import *
import math
import random


class Robot(pygame.sprite.Sprite):
    def __init__(self, image, x_topleft, y_topleft, azimuth, fwd_speed, spin_speed,\
                 visual_range, visual_angle):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        #Sprites must have an image and a rectangle
        self.image          = image
        self.image_original = self.image    #unchanging copy, for rotations
        self.rect           = image.get_rect()
        self.rect_original  = self.rect     #unchanging copy, for rotations
        self.rect.topleft   = x_topleft, y_topleft  #for now used only for initial position
        self.fwd_speed      = fwd_speed
        self.spin_speed     = spin_speed
        self.azi            = azimuth       #in degrees
        self.collided       = False
        self.opmode         = 0             #0=tele, 1=(random)walk 2=auto
        self.spin_angle_left= 0             #relative angle left to spin
        #these are the parameters of the range-sensing system
        self.visual_range   = visual_range
        self.visual_angle   = visual_angle
        self.nr_sensors     = 2*90/self.visual_angle+1
        self.retina         = list([self.visual_range, pygame.Color(color_of_nothing)]\
                                   for i in range(self.nr_sensors))

    def printRetina(self):
        """Prints the content of the retina list"""
        for s in self.retina:
            if (s[0] == self.visual_range): #this really means >=, since sense() func. caps distances
                                            #to visual_range
                print '>'+str(self.visual_range)
            else:       #obstacle detected
                print s
        print '\n'

    def update(self):
        """All sprites have an update() method. This function is
        typically called once per frame. IMPORTANT: All actions in
        here execute AFTER the ones called directly in the event loop.
        """
        if   (self.opmode == 0): self.mode_0_tele()     #teleop mode    
        elif (self.opmode == 1): self.mode_1_walk()     #RW (random walk)
        elif (self.opmode == 2): self.mode_2_auto()     #autonomous
        else:
            print 'ERROR! Undefined operation mode!'
            
    def mode_0_tele(self):
        #self.sense()       #no sensing here, it's done only at keypress
        if self.collided:
                print 'update-->self.opmode==0 THAT HURT!'
                self.collided = False
        #else:                  #teleop mode and not collided
                #do nothing, wait for teleop. commands from kbd.

    def mode_1_walk(self):
        self.sense()
        if self.collided:       #collision in prev. cycle --> start SPIN
                print 'update-->self.opmode==1 THAT HURT!'
                self.collided = False
                walk_dazi = random.randint(-180, 180)
                if math.fabs(walk_dazi) <= self.spin_speed:    #can spin in 1 cycle
                    self.spin(walk_dazi)
                else:
                    if walk_dazi > 0:   #calculate the angle's sign
                        sign = 1
                    else:
                        sign = -1
                    self.spin(sign*self.spin_speed)
                    self.spin_angle_left = walk_dazi-sign*self.spin_speed                
        else:                   #not collided --> finish SPIN, or MOVE fwd
            if math.fabs(self.spin_angle_left) > 0:     #must finish SPIN
                if math.fabs(self.spin_angle_left) <= self.spin_speed:    #can spin in 1 cycle
                    self.spin(self.spin_angle_left)
                    self.spin_angle_left = 0
                else:
                    if self.spin_angle_left > 0:   #calculate the angle's sign
                        sign = 1
                    else:
                        sign = -1
                    self.spin(sign*self.spin_speed)
                    self.spin_angle_left -= sign*self.spin_speed 
            else:                            #MOVE fwd
                #calculate displacements based on azimuth and speed
                temp_unghi = self.azi*math.pi/180
                walk_dx = -self.fwd_speed*math.sin(temp_unghi)
                walk_dy = -self.fwd_speed*math.cos(temp_unghi)
                self.move(walk_dx, walk_dy)
    ########end mode_1_walk(self)########

    def mode_2_auto(self):
        """The Autonomous mode (press key A) is currently an exact copy of the Random Walk mode
        (press key W). This mode is provided simply as a starting point for further changes in the code."""
        self.sense()
        if self.collided:       #collision in prev. cycle --> start SPIN
                print 'update-->self.opmode==2 THAT HURT!'
                self.collided = False
                walk_dazi = random.randint(-180, 180)
                if math.fabs(walk_dazi) <= self.spin_speed:    #can spin in 1 cycle
                    self.spin(walk_dazi)
                else:
                    if walk_dazi > 0:   #calculate the angle's sign
                        sign = 1
                    else:
                        sign = -1
                    self.spin(sign*self.spin_speed)
                    self.spin_angle_left = walk_dazi-sign*self.spin_speed                
        else:                   #not collided --> finish SPIN, or MOVE fwd
            if math.fabs(self.spin_angle_left) > 0:     #must finish SPIN
                if math.fabs(self.spin_angle_left) <= self.spin_speed:    #can spin in 1 cycle
                    self.spin(self.spin_angle_left)
                    self.spin_angle_left = 0
                else:
                    if self.spin_angle_left > 0:   #calculate the angle's sign
                        sign = 1
                    else:
                        sign = -1
                    self.spin(sign*self.spin_speed)
                    self.spin_angle_left -= sign*self.spin_speed 
            else:               #MOVE fwd
                #calculate displacements based on azimuth and speed
                temp_unghi = self.azi*math.pi/180
                walk_dx = -self.fwd_speed*math.sin(temp_unghi)
                walk_dy = -self.fwd_speed*math.cos(temp_unghi)
                self.move(walk_dx, walk_dy)
    ########end mode_2_auto(self)########
        
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
    
    #this function's job is to place in self.retina the range sensed by each sensor
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
          
    def draw_rays(self, target_surf):
        n = (self.nr_sensors - 1)/2 #the "natural" sensor range -n to +n
        for i in range(-n,n+1):     #draw the 2n+1 rays of the range sensors
            ang = (self.azi - i*self.visual_angle)*math.pi/180
            x = self.rect.center[0]-self.retina[i+n][0]*math.sin(ang)
            y = self.rect.center[1]-self.retina[i+n][0]*math.cos(ang)
            #use aaline for smoother (but slower) lines
            pygame.draw.line(target_surf, (0,0,0), self.rect.center, (x,y))
########end of Robot class########