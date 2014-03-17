# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 17:26:09 2014

@author: whitemrj
"""

fps                 = 20        #at most  this many frames per second
back_image          = 'back2_800_600.bmp'   #must have this file in same dir.
display_cols        = 1000
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


#import everything
import os, pygame
from pygame.locals import *
import math
import random

import RoboSim.Robot.robot

main_dir = os.path.split(os.path.abspath(__file__))[0]
screen = pygame.display.set_mode((display_cols, display_rows))
list_traces = list()



''' Changes alpha for surfaces with per-pixel alpha; only for small surfaces!
    Sets alpha for WHITE pixels to new_alpha.
    The alpha value is an integer from 0 to 255, 0 is fully transparent and
    255 is fully opaque. '''
def change_alpha_for_white(surface,new_alpha):
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

''' Changes alpha for surfaces with per-pixel alpha; only for small surfaces!
    Sets alpha for pixels with alpha == 0 to new_alpha. It is needed b/c
    transform.smoothscale pads image with alpha=0. '''
def change_alpha_for_alpha(surface,new_alpha):
    size = surface.get_size()
    for y in xrange(size[1]):
	for x in xrangee(size[0]):
	    r,g,b,a = surface.get_at((x,y))
	    if a<200:
                surface.set_at((x,y),(r,g,b,new_alpha))
    return surface

#for collision-checking (right now only in Robot.move()), only the rectangles are needed.
#so for speed a stripped-down list of rectangles is built:
list_rect_obstacles = []
for ob in list_obstacles:
    list_rect_obstacles.append(pygame.Rect(ob.x_topleft,ob.y_topleft,ob.width,ob.height))


def load_image(name):
    path = os.path.join(main_dir, name)
    temp_image = pygame.image.load(path).convert_alpha()  #need this if using ppalpha
    return change_alpha_for_white(temp_image, r_transparency)  

###########################################
###########################################
def main():
    global leave_trace, list_traces
    if r_visual_granularity > wall_thickness:
        print 'PARAMETER ERROR: r_visual_granularity exceeds wall_thickness!'
        print 'This can cause wall detection errors!'
    if r_init_x_topleft<wall_thickness or r_init_y_topleft<wall_thickness:
        print 'PARAMETER ERROR: starting position overlaps wall!'
        print 'Check r_init_x|y_topleft and wall_thickness'
    pygame.init()           #also calls display.init()    
    pygame.display.set_caption(sim_version + ' \tmode: teleoperation')
    r_sprite = load_image(r_image)
    background  = load_image(back_image)

    #prepare simulation objects
    clock = pygame.time.Clock()
    r = Robot(r_sprite, r_init_x_topleft, r_init_y_topleft,r_init_azi, r_init_fwd_speed,\
              r_init_spin_speed, r_visual_range, r_visual_angle)
    allsprites = pygame.sprite.RenderPlain((r))

    #display the environment once, right before event loop
    screen.blit(background, (0, 0))
    count = -1
    for ob in list_obstacles:
        count = count + 1
        s = pygame.display.get_surface()
        s.fill(ob.color, list_rect_obstacles[count])
    r.draw_rays(screen)  
    pygame.display.flip()   

    going = True
    while going:
        clock.tick(fps)      #at most that many fps
        
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
                if event.key == K_t:        #toggles the tracing mode
                    if leave_trace:
                        leave_trace = 0
                        list_traces = list()
                        print 'changing leave_trace from 1 to 0'
                    else:
                        leave_trace = 1
                        print 'changing leave_trace from 0 to 1'
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
        draw_traces(screen)
        allsprites.draw(screen)

        
        #pygame.display.update()
        pygame.display.flip()   #all changes are drawn at once (double buffer)
        #pygame.time.delay(100)
    pygame.quit()               #also calls display.quit()


if __name__ == '__main__':
    main()

        

