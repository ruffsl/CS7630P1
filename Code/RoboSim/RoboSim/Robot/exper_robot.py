# -*- coding: utf-8 -*-

import robot
import numpy as np
import random

class exper_robot(robot.Robot):
#	Base class provides
#	def __init__(self, point, config):
#	def update(self, world, robots):
#	def move(self,dx,dy,world):
#	def load_image(self, name):
# Elevation of surface, 400

	
	def __init__(self, point, config, start):
		robot.Robot.__init__(self, point, config)
		self.state = 0
		self.load = 0
		self.vision = []
		self.touch = [0,0,0,0,0,0,0,0]	#Starting from top, going clockwise, 8 segments
		random.seed()
		self.x_dir = 0
		self.y_dir = 0
		self.dig_length = 0
		self.explore_length = 0
		
		#Sub states for behaviors
		self.start_state = start
		self.unload_state = 0
		self.side = 1
		self.dig_state = 0
		self.wall_follow_state = -1
		self.explore_state = 0
		
		#Constants
		self.DIG_PERSISTANCE = 25
		self.EXPLORE_PERSISTANCE = 10
		self.TOUCH_RANGE = 5
		self.TUNNEL = -4
		self.ROOM = -5
		
### Behaviors and arbitration		
		
	def update(self, world, robots):
		self.vision = self.sense(world)
		self.vision_2_feel(world)
		if self.state == 0:
			self.start(world)
		elif self.state == 1:
			self.dig_tunnel(world)
		elif self.state == 2:
			self.unload_dirt(world)
		elif self.state == 3:
			self.explore(world)
		return None
		
	def start(self, world):
		if self.start_state == 0:
			self.state = 1
		else:
			self.wall_follow_state = -self.start_state
			self.wall_follow(0,world)
			if self.rect.center[1] >= 420:
				self.state = 1
		
	def wall_follow(self,direction, world):
		if direction == 1:
			if self.wall_follow_state == -1:	#Wall follow up left priority
				if self.touch[0] > self.TOUCH_RANGE and self.touch[1] > self.TOUCH_RANGE and self.touch[7] > self.TOUCH_RANGE:
					self.move(0,-1,world)
				elif self.touch[0] > self.TOUCH_RANGE and self.touch[7] > self.TOUCH_RANGE and self.touch[6] > self.TOUCH_RANGE:
					self.move(-1,-1,world)
				elif self.touch[0] > self.TOUCH_RANGE and self.touch[1] > self.TOUCH_RANGE and self.touch[2] > self.TOUCH_RANGE:
					self.move(1,-1,world)
				elif self.touch[7] > self.TOUCH_RANGE and self.touch[6] > self.TOUCH_RANGE and self.touch[5] > self.TOUCH_RANGE:
					self.move(-1,0,world)
				elif self.touch[1] > self.TOUCH_RANGE and self.touch[2] > self.TOUCH_RANGE and self.touch[3] > self.TOUCH_RANGE:
					self.move(1,0,world)
					self.wall_follow_state = 1
			if self.wall_follow_state == 1:	#Wall follow up right priority
				if self.touch[0] > self.TOUCH_RANGE and self.touch[1] > self.TOUCH_RANGE and self.touch[7] > self.TOUCH_RANGE:
					self.move(0,-1,world)
				elif self.touch[0] > self.TOUCH_RANGE and self.touch[7] > self.TOUCH_RANGE and self.touch[6] > self.TOUCH_RANGE:
					self.move(-1,-1,world)
				elif self.touch[0] > self.TOUCH_RANGE and self.touch[1] > self.TOUCH_RANGE and self.touch[2] > self.TOUCH_RANGE:
					self.move(1,-1,world)
				elif self.touch[1] > self.TOUCH_RANGE and self.touch[2] > self.TOUCH_RANGE and self.touch[3] > self.TOUCH_RANGE:
					self.move(1,0,world)
				elif self.touch[7] > self.TOUCH_RANGE and self.touch[6] > self.TOUCH_RANGE and self.touch[5] > self.TOUCH_RANGE:
					self.move(-1,0,world)
					self.wall_follow_state = -1
		else:
			if self.wall_follow_state == -1:	#Wall follow down left priority
				if self.touch[4] > self.TOUCH_RANGE and self.touch[5] > self.TOUCH_RANGE and self.touch[3] > self.TOUCH_RANGE:
					self.move(0,1,world)
				elif self.touch[4] > self.TOUCH_RANGE and self.touch[5] > self.TOUCH_RANGE and self.touch[6] > self.TOUCH_RANGE:
					self.move(-1,1,world)
				elif self.touch[4] > self.TOUCH_RANGE and self.touch[3] > self.TOUCH_RANGE and self.touch[2] > self.TOUCH_RANGE:
					self.move(1,1,world)
				elif self.touch[7] > self.TOUCH_RANGE and self.touch[6] > self.TOUCH_RANGE and self.touch[5] > self.TOUCH_RANGE:
					self.move(-1,0,world)
				elif self.touch[1] > self.TOUCH_RANGE and self.touch[2] > self.TOUCH_RANGE and self.touch[3] > self.TOUCH_RANGE:
					self.move(1,0,world)
					self.wall_follow_state = 1
			if self.wall_follow_state == 1:	#Wall follow down right priority
				if self.touch[4] > self.TOUCH_RANGE and self.touch[5] > self.TOUCH_RANGE and self.touch[3] > self.TOUCH_RANGE:
					self.move(0,1,world)
				elif self.touch[4] > self.TOUCH_RANGE and self.touch[3] > self.TOUCH_RANGE and self.touch[2] > self.TOUCH_RANGE:
					self.move(1,1,world)
				elif self.touch[4] > self.TOUCH_RANGE and self.touch[5] > self.TOUCH_RANGE and self.touch[6] > self.TOUCH_RANGE:
					self.move(-1,1,world)
				elif self.touch[1] > self.TOUCH_RANGE and self.touch[2] > self.TOUCH_RANGE and self.touch[3] > self.TOUCH_RANGE:
					self.move(1,0,world)
				elif self.touch[7] > self.TOUCH_RANGE and self.touch[6] > self.TOUCH_RANGE and self.touch[5] > self.TOUCH_RANGE:
					self.move(-1,0,world)
					self.wall_follow_state = -1
					
	def explore(self, world):			#Similar to wall following but probabilistic
			
		beacons = self.sense_beacon(self.TUNNEL,world)
		if len(beacons[0]) >= 1:		#Found tunnel beacon
			print 'Found tunnel beacon'
			self.state = 1			#Go to dig mode
			
		noise = random.randint(0,999)
				
		if noise >994:
			print 'Switching to dig mode'
			self.state = 1
			return
			
		if self.explore_state == 0:
			if noise < 300:
				self.explore_state = 1
			elif noise >= 300 and noise < 600:
				self.explore_state = 2
			elif noise >= 600 and noise < 800:
				self.explore_state = 3
			elif noise >= 800 and noise < 1000:
				self.explore_state = 4
		else:
			self.explore_length = self.explore_length + 1
			if self.explore_length > self.EXPLORE_PERSISTANCE:
				self.explore_length = 0
				self.explore_state = 0
			
		if self.explore_state == 1:	#Wall follow down left priority
			if self.touch[4] > self.TOUCH_RANGE and self.touch[5] > self.TOUCH_RANGE and self.touch[3] > self.TOUCH_RANGE:
				self.move(0,1,world)
			elif self.touch[4] > self.TOUCH_RANGE and self.touch[5] > self.TOUCH_RANGE and self.touch[6] > self.TOUCH_RANGE:
				self.move(-1,1,world)
			elif self.touch[4] > self.TOUCH_RANGE and self.touch[3] > self.TOUCH_RANGE and self.touch[2] > self.TOUCH_RANGE:
				self.move(1,1,world)
			elif self.touch[7] > self.TOUCH_RANGE and self.touch[6] > self.TOUCH_RANGE and self.touch[5] > self.TOUCH_RANGE:
				self.move(-1,0,world)
			elif self.touch[1] > self.TOUCH_RANGE and self.touch[2] > self.TOUCH_RANGE and self.touch[3] > self.TOUCH_RANGE:
				self.move(1,0,world)
		elif self.explore_state == 2:	#Wall follow down right priority
			if self.touch[4] > self.TOUCH_RANGE and self.touch[5] > self.TOUCH_RANGE and self.touch[3] > self.TOUCH_RANGE:
				self.move(0,1,world)
			elif self.touch[4] > self.TOUCH_RANGE and self.touch[3] > self.TOUCH_RANGE and self.touch[2] > self.TOUCH_RANGE:
				self.move(1,1,world)
			elif self.touch[4] > self.TOUCH_RANGE and self.touch[5] > self.TOUCH_RANGE and self.touch[6] > self.TOUCH_RANGE:
				self.move(-1,1,world)
			elif self.touch[1] > self.TOUCH_RANGE and self.touch[2] > self.TOUCH_RANGE and self.touch[3] > self.TOUCH_RANGE:
				self.move(1,0,world)
			elif self.touch[7] > self.TOUCH_RANGE and self.touch[6] > self.TOUCH_RANGE and self.touch[5] > self.TOUCH_RANGE:
				self.move(-1,0,world)
		elif self.explore_state == 3:	#Wall follow left priority
			if self.touch[7] > self.TOUCH_RANGE and self.touch[6] > self.TOUCH_RANGE and self.touch[5] > self.TOUCH_RANGE:
				self.move(-1,0,world)
			elif self.touch[4] > self.TOUCH_RANGE and self.touch[5] > self.TOUCH_RANGE and self.touch[6] > self.TOUCH_RANGE:
				self.move(-1,1,world)
			elif self.touch[6] > self.TOUCH_RANGE and self.touch[7] > self.TOUCH_RANGE and self.touch[0] > self.TOUCH_RANGE:
				self.move(-1,-1,world)
			elif self.touch[5] > self.TOUCH_RANGE and self.touch[4] > self.TOUCH_RANGE and self.touch[3] > self.TOUCH_RANGE:
				self.move(0,1,world)
		elif self.explore_state == 4:	#Wall follow right priority
			if self.touch[1] > self.TOUCH_RANGE and self.touch[2] > self.TOUCH_RANGE and self.touch[3] > self.TOUCH_RANGE:
				self.move(1,0,world)
			elif self.touch[4] > self.TOUCH_RANGE and self.touch[3] > self.TOUCH_RANGE and self.touch[2] > self.TOUCH_RANGE:
				self.move(1,1,world)
			elif self.touch[0] > self.TOUCH_RANGE and self.touch[1] > self.TOUCH_RANGE and self.touch[2] > self.TOUCH_RANGE:
				self.move(1,-1,world)
			elif self.touch[5] > self.TOUCH_RANGE and self.touch[4] > self.TOUCH_RANGE and self.touch[3] > self.TOUCH_RANGE:
				self.move(0,1,world)
	
	def dig_tunnel(self,world):
		if self.load > self.config['max_load']:
			self.lay_beacon(self.TUNNEL, world)
			self.state = 2
			self.dig_state = 0
		elif self.rect.center[1] < 420:
			self.move(0,1,world)
			digs = self.dig(world)
#			print 'Dig dig dig: ', digs
		elif self.dig_state == 0:		#Pick a new direction via random selection
			self.x_dir = random.randint(-1,1)
			self.y_dir = random.randint(0,1)
			if self.x_dir == 0 and self.y_dir == 0:
				self.dig_state = 0
			else:
				self.dig_state = 1
		elif self.dig_state == 1:		#Dig set direction for some distance
			self.move(self.x_dir,self.y_dir,world)
			digs = self.dig(world)
#			print 'Dig dig dig: ', digs
			self.dig_length = self.dig_length + 1
			if self.dig_length > self.DIG_PERSISTANCE:
				self.dig_length = 0
				self.dig_state = 0
				
	def unload_dirt(self,world):
#		print 'Sense:', self.touch, 'State:', self.unload_state, 'Load:', self.load
		if self.unload_state == 0:
			if self.rect.center[1] < 410:
				self.unload_state = 1
			else:
				self.wall_follow(1, world)			#1 goes up
		elif self.unload_state == 1:				#Center in tunnel
#			print self.touch[6]
			if self.touch[6] == self.TOUCH_RANGE+1:
				self.move(-1,0,world)
			elif self.touch[2] == self.TOUCH_RANGE+1:
				self.move(1,0,world)
			else:
				self.unload_state = 2
		elif self.unload_state == 2:				#Go to surface
#			print self.touch[6]
			if self.touch[6] <= self.TOUCH_RANGE and self.touch[2] <= self.TOUCH_RANGE:
				self.move(0,-1,world)
			elif self.touch[6] > self.TOUCH_RANGE:
				self.side = -1
				self.move(-1,0,world)
				self.unload_state = 3
			elif self.touch[2] > self.TOUCH_RANGE:
				self.side = 1
				self.move(1,0,world)
				self.unload_state = 3
		elif self.unload_state == 3:				#Move on top
#			print 'Move on top'
			temp = self.touch[4]
			if temp > self.TOUCH_RANGE:
				self.move(self.side,-1,world)
			elif temp <= self.TOUCH_RANGE:
				self.unload_state = 4
		elif self.unload_state == 4:				
			drops = np.array([self.rel_pt(0,4),self.rel_pt(0,-4)])
			drops = self.drop(world,drops)
			self.move(self.side,0,world)
			self.unload_state = 5
		elif self.unload_state == 5:				
			drops = np.array([self.rel_pt(0,4),self.rel_pt(0,-4),self.rel_pt(self.side*-1,3),self.rel_pt(self.side*-1,-3)])
			drops = self.drop(world,drops)
			self.move(self.side,0,world)
			self.unload_state = 6
		elif self.unload_state == 6:				
			drops = np.array([self.rel_pt(0,4),self.rel_pt(0,-4),self.rel_pt(self.side*-1,3),self.rel_pt(self.side*-1,-3),self.rel_pt(self.side*-2,2),self.rel_pt(self.side*-2,-2)])
			drops = self.drop(world,drops)
			self.move(self.side,0,world)
			self.unload_state = 7
		elif self.unload_state == 7:		
			if self.load <= 0:
				self.unload_state = 8
			else:
				drops = np.array([self.rel_pt(0,4),self.rel_pt(0,-4),self.rel_pt(self.side*-1,3),self.rel_pt(self.side*-1,-3),self.rel_pt(self.side*-2,2),self.rel_pt(self.side*-2,-2),self.rel_pt(self.side*-3,-1),self.rel_pt(self.side*-3,0),self.rel_pt(self.side*-3,1)])
				drops = self.drop(world,drops)
				self.move(self.side,0,world)
		elif self.unload_state == 8:
			self.wall_follow(1,world)
			if self.touch[4+2*self.side] > self.TOUCH_RANGE:
				self.unload_state = 9
		elif self.unload_state == 9:
			if self.touch[4+self.side] <= self.TOUCH_RANGE:
				self.move(-self.side,-1,world)
			elif self.touch[4] > self.TOUCH_RANGE:
				self.move(-self.side,0,world)
			else:
				self.unload_state = 10
				self.wall_follow_state = -self.side # set priority
		elif self.unload_state == 10:
			self.wall_follow(0,world)		#anything not 1 goes down
			if self.rect.center[1] > 410:		#back in tunnel
				self.unload_state = 0		#Reset unload
				self.state = 3			#switch to explore mode
			
				
### Functions for exper_robot unique actions				
				
	def lay_beacon(self, value, world):
		world[self.rect.center[0],self.rect.center[1]] = value
		
	def sense_beacon(self, value, world):
		sense_range = self.getRange(world,3)
		beacons = np.where(sense_range==value)
		world[beacons] = self.config['empty']
		#print 'beacons: ', beacons[0], beacons[0].shape
		return beacons			
			
	def vision_2_feel(self, world):
		#Top -> 0
		if self.vision[self.rel_pt(0,-1)] == -1 or self.vision[self.rel_pt(0,-1)] == -2:
			self.touch[0] = 1
		elif self.vision[self.rel_pt(0,-2)] == -1 or self.vision[self.rel_pt(0,-2)] == -2:
			self.touch[0] = 2
		elif self.vision[self.rel_pt(0,-3)] == -1 or self.vision[self.rel_pt(0,-3)] == -2:
			self.touch[0] = 3
		elif self.vision[self.rel_pt(0,-4)] == -1 or self.vision[self.rel_pt(0,-4)] == -2:
			self.touch[0] = 4
		elif self.vision[self.rel_pt(0,-5)] == -1 or self.vision[self.rel_pt(0,-5)] == -2:
			self.touch[0] = 5
		else:
			self.touch[0] = 6
		#Top right -> 1
		if self.vision[self.rel_pt(1,-1)] == -1 or self.vision[self.rel_pt(1,-1)] == -2:
			self.touch[1] = 2
		elif self.vision[self.rel_pt(1,-2)] == -1 or self.vision[self.rel_pt(1,-2)] == -2:
			self.touch[1] = 3
		elif self.vision[self.rel_pt(2,-1)] == -1 or self.vision[self.rel_pt(2,-1)] == -2:
			self.touch[1] = 3
		elif self.vision[self.rel_pt(1,-3)] == -1 or self.vision[self.rel_pt(1,-3)] == -2:
			self.touch[1] = 4
		elif self.vision[self.rel_pt(2,-2)] == -1 or self.vision[self.rel_pt(2,-2)] == -2:
			self.touch[1] = 4
		elif self.vision[self.rel_pt(3,-1)] == -1 or self.vision[self.rel_pt(3,-1)] == -2:
			self.touch[1] = 4
		elif self.vision[self.rel_pt(3,-2)] == -1 or self.vision[self.rel_pt(3,-2)] == -2:
			self.touch[1] = 5
		elif self.vision[self.rel_pt(2,-3)] == -1 or self.vision[self.rel_pt(2,-3)] == -2:
			self.touch[1] = 5
		#Skipping 1/4 blocks
		else:
			self.touch[1] = 6
		#right -> 2
		if self.vision[self.rel_pt(1,0)] == -1 or self.vision[self.rel_pt(1,0)] == -2:
			self.touch[2] = 1
		elif self.vision[self.rel_pt(2,0)] == -1 or self.vision[self.rel_pt(2,0)] == -2:
			self.touch[2] = 2
		elif self.vision[self.rel_pt(3,0)] == -1 or self.vision[self.rel_pt(3,0)] == -2:
			self.touch[2] = 3
		elif self.vision[self.rel_pt(4,0)] == -1 or self.vision[self.rel_pt(4,0)] == -2:
			self.touch[2] = 4
		elif self.vision[self.rel_pt(5,0)] == -1 or self.vision[self.rel_pt(5,0)] == -2:
			self.touch[2] = 5
		else:
			self.touch[2] = 6
		#bot right -> 3
		if self.vision[self.rel_pt(1,1)] == -1 or self.vision[self.rel_pt(1,1)] == -2:
			self.touch[3] = 2
		elif self.vision[self.rel_pt(1,2)] == -1 or self.vision[self.rel_pt(1,2)] == -2:
			self.touch[3] = 3
		elif self.vision[self.rel_pt(2,1)] == -1 or self.vision[self.rel_pt(2,1)] == -2:
			self.touch[3] = 3
		elif self.vision[self.rel_pt(1,3)] == -1 or self.vision[self.rel_pt(1,3)] == -2:
			self.touch[3] = 4
		elif self.vision[self.rel_pt(2,2)] == -1 or self.vision[self.rel_pt(2,2)] == -2:
			self.touch[3] = 4
		elif self.vision[self.rel_pt(3,1)] == -1 or self.vision[self.rel_pt(3,1)] == -2:
			self.touch[3] = 4
		elif self.vision[self.rel_pt(2,3)] == -1 or self.vision[self.rel_pt(2,3)] == -2:
			self.touch[3] = 5
		elif self.vision[self.rel_pt(3,2)] == -1 or self.vision[self.rel_pt(3,2)] == -2:
			self.touch[3] = 5
		elif self.vision[self.rel_pt(1,4)] == -1 or self.vision[self.rel_pt(1,4)] == -2:
			self.touch[3] = 5
		else:
			self.touch[3] = 6
		#bot -> 4
		if self.vision[self.rel_pt(0,1)] == -1 or self.vision[self.rel_pt(0,1)] == -2:
			self.touch[4] = 1
		elif self.vision[self.rel_pt(0,2)] == -1 or self.vision[self.rel_pt(0,2)] == -2:
			self.touch[4] = 2
		elif self.vision[self.rel_pt(0,3)] == -1 or self.vision[self.rel_pt(0,3)] == -2:
			self.touch[4] = 3
		elif self.vision[self.rel_pt(0,4)] == -1 or self.vision[self.rel_pt(0,4)] == -2:
			self.touch[4] = 4
		elif self.vision[self.rel_pt(0,5)] == -1 or self.vision[self.rel_pt(0,5)] == -2:
			self.touch[4] = 5
		else:
			self.touch[4] = 6
		#bot left -> 5
		if self.vision[self.rel_pt(-1,1)] == -1 or self.vision[self.rel_pt(-1,1)] == -2:
			self.touch[5] = 2
		elif self.vision[self.rel_pt(-1,2)] == -1 or self.vision[self.rel_pt(-1,2)] == -2:
			self.touch[5] = 3
		elif self.vision[self.rel_pt(-2,1)] == -1 or self.vision[self.rel_pt(-2,1)] == -2:
			self.touch[5] = 3
		elif self.vision[self.rel_pt(-1,3)] == -1 or self.vision[self.rel_pt(-1,3)] == -2:
			self.touch[5] = 4
		elif self.vision[self.rel_pt(-2,2)] == -1 or self.vision[self.rel_pt(-2,2)] == -2:
			self.touch[5] = 4
		elif self.vision[self.rel_pt(-3,1)] == -1 or self.vision[self.rel_pt(-3,1)] == -2:
			self.touch[5] = 4
		elif self.vision[self.rel_pt(-2,3)] == -1 or self.vision[self.rel_pt(-2,3)] == -2:
			self.touch[5] = 5
		elif self.vision[self.rel_pt(-3,2)] == -1 or self.vision[self.rel_pt(-3,2)] == -2:
			self.touch[5] = 5
		elif self.vision[self.rel_pt(-1,4)] == -1 or self.vision[self.rel_pt(-1,4)] == -2:
			self.touch[5] = 5
		else:
			self.touch[5] = 6
		#left -> 6
		if self.vision[self.rel_pt(-1,0)] == -1 or self.vision[self.rel_pt(-1,0)] == -2:
			self.touch[6] = 1
		elif self.vision[self.rel_pt(-2,0)] == -1 or self.vision[self.rel_pt(-2,0)] == -2:
			self.touch[6] = 2
		elif self.vision[self.rel_pt(-3,0)] == -1 or self.vision[self.rel_pt(-3,0)] == -2:
			self.touch[6] = 3
		elif self.vision[self.rel_pt(-4,0)] == -1 or self.vision[self.rel_pt(-4,0)] == -2:
			self.touch[6] = 4
		elif self.vision[self.rel_pt(-5,0)] == -1 or self.vision[self.rel_pt(-5,0)] == -2:
			self.touch[6] = 5
		else:
			self.touch[6] = 6
		#top left -> 7
		if self.vision[self.rel_pt(-1,-1)] == -1 or self.vision[self.rel_pt(-1,-1)] == -2:
			self.touch[7] = 2
		elif self.vision[self.rel_pt(-1,-2)] == -1 or self.vision[self.rel_pt(-1,-2)] == -2:
			self.touch[7] = 3
		elif self.vision[self.rel_pt(-2,-1)] == -1 or self.vision[self.rel_pt(-2,-1)] == -2:
			self.touch[7] = 3
		elif self.vision[self.rel_pt(-1,-3)] == -1 or self.vision[self.rel_pt(-1,-3)] == -2:
			self.touch[7] = 4
		elif self.vision[self.rel_pt(-2,-2)] == -1 or self.vision[self.rel_pt(-2,-2)] == -2:
			self.touch[7] = 4
		elif self.vision[self.rel_pt(-3,-1)] == -1 or self.vision[self.rel_pt(-3,-1)] == -2:
			self.touch[7] = 4
		elif self.vision[self.rel_pt(-2,-3)] == -1 or self.vision[self.rel_pt(-2,-3)] == -2:
			self.touch[7] = 5
		elif self.vision[self.rel_pt(-3,-2)] == -1 or self.vision[self.rel_pt(-3,-2)] == -2:
			self.touch[7] = 5
		else:
			self.touch[7] = 6

	def stop(self,world):
		return 1
		
		