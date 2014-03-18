# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 17:28:52 2014

@author: whitemrj
"""

import pygame, os
import math
import random
from pygame.locals import *
import RoboSim.Robot.robot

back_image          = 'back2_800_600.bmp'   #must have this file in same dir.
wall_thickness      = 5         #thickness in pixels
wall_color          = 'black'
food_color          = 'green'

color_of_nothing    = 'white'
sim_version         = 'AntSim Alpha 0.1'

r_image          = 'robo1.bmp'  #must have this file in same dir.
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

class sim:
    def __init__(self, main_dir, figsize, fps):
        self.main_dir = main_dir
        self.screen = pygame.display.set_mode(figsize)
        self.fps = fps
        if r_visual_granularity > wall_thickness:
            print 'PARAMETER ERROR: r_visual_granularity exceeds wall_thickness!'
            print 'This can cause wall detection errors!'
        if r_init_x_topleft<wall_thickness or r_init_y_topleft<wall_thickness:
            print 'PARAMETER ERROR: starting position overlaps wall!'
            print 'Check r_init_x|y_topleft and wall_thickness'
        pygame.init()           #also calls display.init()    
        pygame.display.set_caption(sim_version + ' \tmode: teleoperation')
        r_sprite = self.load_image(r_image)
        background  = self.load_image(back_image)
        
        #prepare simulation objects
        self.clock = pygame.time.Clock()
        r = Robot(r_sprite, r_init_x_topleft, r_init_y_topleft,r_init_azi, r_init_fwd_speed,\
                      r_init_spin_speed, r_visual_range, r_visual_angle)
        self.allsprites = pygame.sprite.RenderPlain((r))
        
        #display the environment once, right before event loop
        self.screen.blit(background, (0, 0))
        count = -1
#        for ob in list_obstacles:
#            count = count + 1
#            s = pygame.display.get_surface()
#            s.fill(ob.color, list_rect_obstacles[count])
        r.draw_rays(screen)
        pygame.display.flip()
                    
    def quit(self):
        pygame.quit() #also calls display.quit()
    
    def update(self):
        self.clock.tick(self.fps)      #at most that many fps\
        
        #Event loop################################
        for event in pygame.event.get():
            if event == QUIT:
                going = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    going = False
                if event.key == K_r:        #r is for rotation
                    r.spin(-r_step_theta)   #clockwise
                    r.sense()       #do it here, to avoid fast scrolling when teleoperating 
                if event.key == K_e:        #e is next to r
                    r.spin(r_step_theta)    #counterclockwise
                    r.sense()
                if event.key == K_RIGHT:
                    r.move(r_step_tele,0)
                    r.sense()
                if event.key == K_LEFT:
                    r.move(-r_step_tele,0)
                    r.sense()
                if event.key == K_UP:
                    r.move(0,-r_step_tele)
                    r.sense()
                if event.key == K_DOWN:
                    r.move(0,r_step_tele)
                    r.sense()
               
                if event.key == K_SPACE:
                    r.opmode = 0            #teleop mode
                    pygame.display.set_caption(sim_version + ' \tmode: teleoperation')
                if event.key == K_w:
                    r.opmode = 1            #random walk mode
                    pygame.display.set_caption(sim_version + ' \tmode: random walk+bounce')
                if event.key == K_a:
                    r.opmode = 2            #autonomous navigation mode
                    pygame.display.set_caption(sim_version + ' \tmode: autonomous')
        #End of event loop#######################
        
        
        
        
                        
        #Redrawing    
        allsprites.update()
        screen.blit(background, (0, 0))  #redraws the entire bkgrnd.
        #screen.fill((255,255,255)) # white background
        #screen.blit(red_block, (100,100))
        count = -1
        for ob in list_obstacles:
            count = count + 1
            s = pygame.display.get_surface()
            s.fill(ob.color, list_rect_obstacles[count])
        r.draw_rays(screen)
        allsprites.draw(screen)

        
        #pygame.display.update()
        pygame.display.flip()   #all changes are drawn at once (double buffer)
        #pygame.time.delay(100)
        return going
        

    ''' Changes alpha for surfaces with per-pixel alpha; only for small surfaces!
        Sets alpha for WHITE pixels to new_alpha.
        The alpha value is an integer from 0 to 255, 0 is fully transparent and
        255 is fully opaque. '''
    def change_alpha_for_white(self,surface,new_alpha):
        size = surface.get_size()
        if size[0]>300 or size[1]>300:
            print 'change_alpha_for_white-> size = ', size, ' IMAGE TOO LARGE!'
            return surface
        for y in xrange(size[1]):
	        for x in xrange(size[0]):
	            r,g,b,a = surface.get_at((x,y))
	            if r==255 and g==255 and b==255:
	                    surface.set_at((x,y),(r,g,b,new_alpha))
        return surface
    
    #for collision-checking (right now only in Robot.move()), only the rectangles are needed.
    #so for speed a stripped-down list of rectangles is built:
#    list_rect_obstacles = []
#    for ob in list_obstacles:
#        list_rect_obstacles.append(pygame.Rect(ob.x_topleft,ob.y_topleft,ob.width,ob.height))
    
    
    def load_image(self, name):
        path = os.path.join(self.main_dir, name)
        temp_image = pygame.image.load(path).convert_alpha()  #need this if using ppalpha
        return self.change_alpha_for_white(temp_image, r_transparency)  
