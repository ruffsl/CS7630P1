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
		self.room_size = 0
		self.wall_length = 0
		
		#Sub states for behaviors
		self.start_state = start
		self.unload_state = 0
		self.side = 1
		self.dig_state = 0
		self.wall_follow_state = -1
		self.explore_state = 0
		self.dig_room_state = 0
		self.escape_state = 0
		
		#Constants
		self.DIG_PERSISTANCE = 10
		self.EXPLORE_PERSISTANCE = 10
		self.DIGCOIN = -4
		self.ROOM = -5
		self.BRANCH = -6
		
### Behaviors and arbitration		
		
	def update(self, world, robots):
		self.vision = self.sense(world)
		self.vision_2_feel(world)
		print 'State: ', self.state
		if self.state == 0:
			self.start(world)
		elif self.state == 1:
			self.dig_tunnel(world)
		elif self.state == 2:
			self.unload_dirt(world)
		elif self.state == 3:
			self.explore(world)
		elif self.state == 4:
			self.dig_room(world)
		elif self.state == 5:
			self.escape_room(world)
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
				if self.touch[0] == 0 and self.touch[1] == 0 and self.touch[7] == 0:
					self.move(0,-1,world)
				elif self.touch[0] == 0 and self.touch[7] == 0 and self.touch[6] == 0:
					self.move(-1,-1,world)
				elif self.touch[0] == 0 and self.touch[1] == 0 and self.touch[2] == 0:
					self.move(1,-1,world)
				elif self.touch[7] == 0 and self.touch[6] == 0 and self.touch[5] == 0:
					self.move(-1,0,world)
				elif self.touch[1] == 0 and self.touch[2] == 0 and self.touch[3] == 0:
					self.move(1,0,world)
					self.wall_follow_state = 1
			if self.wall_follow_state == 1:	#Wall follow up right priority
				if self.touch[0] == 0 and self.touch[1] == 0 and self.touch[7] == 0:
					self.move(0,-1,world)
				elif self.touch[0] == 0 and self.touch[7] == 0 and self.touch[6] == 0:
					self.move(-1,-1,world)
				elif self.touch[0] == 0 and self.touch[1] == 0 and self.touch[2] == 0:
					self.move(1,-1,world)
				elif self.touch[1] == 0 and self.touch[2] == 0 and self.touch[3] == 0:
					self.move(1,0,world)
				elif self.touch[7] == 0 and self.touch[6] == 0 and self.touch[5] == 0:
					self.move(-1,0,world)
					self.wall_follow_state = -1
		else:
			if self.wall_follow_state == -1:	#Wall follow down left priority
				if self.touch[4] == 0 and self.touch[5] == 0 and self.touch[3] == 0:
					self.move(0,1,world)
				elif self.touch[4] == 0 and self.touch[5] == 0 and self.touch[6] == 0:
					self.move(-1,1,world)
				elif self.touch[4] == 0 and self.touch[3] == 0 and self.touch[2] == 0:
					self.move(1,1,world)
				elif self.touch[7] == 0 and self.touch[6] == 0 and self.touch[5] == 0:
					self.move(-1,0,world)
				elif self.touch[1] == 0 and self.touch[2] == 0 and self.touch[3] == 0:
					self.move(1,0,world)
					self.wall_follow_state = 1
			if self.wall_follow_state == 1:	#Wall follow down right priority
				if self.touch[4] == 0 and self.touch[5] == 0 and self.touch[3] == 0:
					self.move(0,1,world)
				elif self.touch[4] == 0 and self.touch[3] == 0 and self.touch[2] == 0:
					self.move(1,1,world)
				elif self.touch[4] == 0 and self.touch[5] == 0 and self.touch[6] == 0:
					self.move(-1,1,world)
				elif self.touch[1] == 0 and self.touch[2] == 0 and self.touch[3] == 0:
					self.move(1,0,world)
				elif self.touch[7] == 0 and self.touch[6] == 0 and self.touch[5] == 0:
					self.move(-1,0,world)
					self.wall_follow_state = -1
					
	def explore(self, world):			#Similar to wall following but probabilistic
			
#		print 'Explore behavior state:', self.explore_state
			
		noise = random.randint(0,999)

		beacons = self.sense_beacon(self.ROOM, 0, world)
		if len(beacons[0]) >= 1:		#Found room beacon
			self.dig_room_state = 2		#initialize dig room behavior
			self.state = 4			#Go to dig mode
			return

		beacons = self.sense_beacon(self.DIGCOIN, 1, world)
		if len(beacons[0]) >= 1:		#Found tunnel beacon
			if noise > 998:
				print 'Branching tunnel'
				self.lay_beacon(self.DIGCOIN, world)
				self.state = 1
			elif noise < 996:
				print 'Starting room'
				self.lay_beacon(self.ROOM, world)
				self.dig_room_state = 0
				self.state = 4
			else:
				print 'Continuing tunnel'
				self.state = 1			#Go to dig mode
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
			if self.touch[4] == 0 and self.touch[5] == 0 and self.touch[3] == 0:
				self.move(0,1,world)
				self.x_dir = -1
			elif self.touch[4] == 0 and self.touch[5] == 0 and self.touch[6] == 0:
				self.move(-1,1,world)
				self.x_dir = -1
			elif self.touch[4] == 0 and self.touch[3] == 0 and self.touch[2] == 0:
				self.move(1,1,world)
				self.x_dir = 1
			elif self.touch[7] == 0 and self.touch[6] == 0 and self.touch[5] == 0:
				self.move(-1,0,world)
				self.x_dir = -1
			elif self.touch[1] == 0 and self.touch[2] == 0 and self.touch[3] == 0:
				self.move(1,0,world)
				self.x_dir = 1
		elif self.explore_state == 2:	#Wall follow down right priority
			if self.touch[4] == 0 and self.touch[5] == 0 and self.touch[3] == 0:
				self.move(0,1,world)
				self.x_dir = 1
			elif self.touch[4] == 0 and self.touch[3] == 0 and self.touch[2] == 0:
				self.move(1,1,world)
				self.x_dir = 1
			elif self.touch[4] == 0 and self.touch[5] == 0 and self.touch[6] == 0:
				self.move(-1,1,world)
				self.x_dir = -1
			elif self.touch[1] == 0 and self.touch[2] == 0 and self.touch[3] == 0:
				self.move(1,0,world)
				self.x_dir = 1
			elif self.touch[7] == 0 and self.touch[6] == 0 and self.touch[5] == 0:
				self.move(-1,0,world)
				self.x_dir = -1
		elif self.explore_state == 3:	#Wall follow left priority
			if self.touch[7] == 0 and self.touch[6] == 0 and self.touch[5] == 0:
				self.move(-1,0,world)
				self.x_dir = -1
			elif self.touch[4] == 0 and self.touch[5] == 0 and self.touch[6] == 0:
				self.move(-1,1,world)
				self.x_dir = -1
			elif self.touch[6] == 0 and self.touch[7] == 0 and self.touch[0] == 0:
				self.move(-1,-1,world)
				self.x_dir = -1
			elif self.touch[5] == 0 and self.touch[4] == 0 and self.touch[3] == 0:
				self.move(0,1,world)
				self.x_dir = -1
			elif self.touch[2] == 0 and self.touch[3] == 0 and self.touch[4] == 0:
				self.move(1,1,world)
				self.x_dir = 1
		elif self.explore_state == 4:	#Wall follow right priority
			if self.touch[1] == 0 and self.touch[2] == 0 and self.touch[3] == 0:
				self.move(1,0,world)
				self.x_dir = 1
			elif self.touch[4] == 0 and self.touch[3] == 0 and self.touch[2] == 0:
				self.move(1,1,world)
				self.x_dir = 1
			elif self.touch[0] == 0 and self.touch[1] == 0 and self.touch[2] == 0:
				self.move(1,-1,world)
				self.x_dir = 1
			elif self.touch[5] == 0 and self.touch[4] == 0 and self.touch[3] == 0:
				self.move(0,1,world)
				self.x_dir = 1
			elif self.touch[4] == 0 and self.touch[5] == 0 and self.touch[6] == 0:
				self.move(-1,1,world)
				self.x_dir = -1
	
	def dig_tunnel(self,world):
		if self.load > self.config['max_load']:
			self.lay_beacon(self.DIGCOIN, world)
			self.state = 2
			self.dig_state = 0
			
		elif self.rect.center[1] < 220:
			self.move(0,1,world)
			digs = self.dig(world)
#			print 'Dig dig dig: ', digs
			
		elif self.dig_state == 0:		#Pick a new direction via random selection
			self.x_dir = self.x_dir + random.randint(-1,1)
			if self.x_dir > 1:
				self.x_dir = 1
			elif self.x_dir < -1:
				self.x_dir = -1
			self.y_dir = random.randint(0,1)
			self.y_dir = 1
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
				
	def dig_room(self,world):
#		self.dig_room_state = state
#		self.x_dir = side
		if self.load > self.config['max_load']:
			self.state = 5		#escape
		elif self.dig_room_state == 0:		#choose size
			self.room_size = random.randint(20,55)
			self.dig_room_state = 1
		elif self.dig_room_state == 1:		#first wall
			if self.room_size > self.wall_length:
				self.move(0,1,world)
				self.dig(world)
				self.wall_length = self.wall_length + 1
			else:
				self.dig_room_state = 4
				self.wall_length = 0
		elif self.dig_room_state == 2:		#Align to beacon		
			beacons = self.sense_beacon(self.ROOM, 0, world)

			if beacons[0][0] > self.rect.center[0]:
				x_val =1
			elif beacons[0][0] < self.rect.center[0]:
				x_val = -1
			else:
				x_val = 0
				
			if beacons[1][0] > self.rect.center[1]:
				y_val =1
			elif beacons[1][0] < self.rect.center[1]:
				y_val = -1
			else:
				y_val = 0
				
			if x_val == 0 and y_val == 0:
				self.wall_length = 0
				self.dig_room_state = 3
			else:
				self.move(x_val, y_val, world)
		
		elif self.dig_room_state == 3:		#measure size
			if self.touch[4] == 0:
				self.wall_length = self.wall_length + 1
				self.move(0,1,world)
			else:
				if self.touch[2] == 0:
					self.x_dir = 1
				else:
					self.x_dir = -1
				self.room_size = self.wall_length
				self.wall_length = 0
				self.dig_room_state = 4
				
		elif self.dig_room_state == 4:		#bottom border
			if self.room_size > self.wall_length:
				self.move(self.x_dir,0,world)
				self.dig(world)
				self.wall_length = self.wall_length + 1
			else:
				self.dig_room_state = 5
				self.wall_length = 0
				
		elif self.dig_room_state == 5:		#side border
			if self.room_size > self.wall_length:
				self.move(0,-1,world)
				self.dig(world)
				self.wall_length = self.wall_length + 1
			else:
				self.dig_room_state = 6
				self.wall_length = 0
				
		elif self.dig_room_state == 6:		#top border
			if self.room_size > self.wall_length:
				self.move(-self.x_dir,0,world)
				self.dig(world)
				self.wall_length = self.wall_length + 1
			else:
				self.dig_room_state = 7
				self.wall_length = 0
				
		elif self.dig_room_state == 7:		#move to center dirt
			self.move(self.x_dir, 1, world)
			self.dig(world)
			self.wall_length = self.wall_length+1
			if self.touch[4] == 1:
				self.dig_room_state = 8
				
		elif self.dig_room_state == 8:		#clear out dirt
			if self.wall_length >= self.room_size:
				self.state = 5		#finished, leave
			elif self.touch[7] == 1 or self.touch[0] == 1 or self.touch[1] == 1:
				self.move(0,-1,world)
				self.dig(world)
				self.wall_length = self.wall_length-1
			elif self.touch[2] == 1:
				self.move(1,0,world)
				self.dig(world)
			elif self.touch[6] == 1:
				self.move(-1,0,world)
				self.dig(world)
			elif self.touch[4] == 1:
				self.move(0,1,world)
				self.dig(world)
				self.wall_length = self.wall_length+1
			else:
				self.move(-1,0,world)
				self.dig(world)
			
	def escape_room(self,world):
		beacons = self.sense_beacon(self.ROOM, 0, world)
		if len(beacons[0]) >= 1:		#Found exit
			self.state = 2			#unload
			return
#		print 'x_dir: ', self.x_dir, 'escape_state: ', self.escape_state
		if self.escape_state == 0:
			if self.touch[1] == 0 and self.touch[2] == 0 and self.touch[3] == 0:
				self.move(1,0,world)
			else:
				if self.x_dir == 1:
					self.escape_state = 1
				else:
					self.escape_state = 3
		elif self.escape_state == 1:
			if self.touch[3] == 0 and self.touch[4] == 0 and self.touch[5] == 0:
				self.move(0,1,world)
			else:
				if self.x_dir == 1:
					self.escape_state = 2
				else:
					self.escape_state = 0
		elif self.escape_state == 2:
			if self.touch[5] == 0 and self.touch[6] == 0 and self.touch[7] == 0:
				self.move(-1,0,world)
			else:
				if self.x_dir == 1:
					self.escape_state = 3
				else:
					self.escape_state = 1
		elif self.escape_state == 3:
			if self.touch[7] == 0 and self.touch[0] == 0 and self.touch[1] == 0:
				self.move(0,-1,world)
			else:
				if self.x_dir == 1:
					self.escape_state = 0
				else:
					self.escape_state = 2
				
	def unload_dirt(self,world):
		print 'Sense:', self.touch, 'State:', self.unload_state
		if self.unload_state == 0:
			if self.rect.center[1] < 210:
				self.unload_state = 1
			else:
				self.wall_follow(1, world)			#1 goes up
		elif self.unload_state == 1:				#Center in tunnel
#			print self.touch[6]
			if self.touch[6] == 0:
				self.move(-1,0,world)
			elif self.touch[2] == 0:
				self.move(1,0,world)
			else:
				self.unload_state = 2
		elif self.unload_state == 2:				#Go to surface
#			print self.touch[6]
			if self.touch[6] == 1 and self.touch[2] == 1:
				self.move(0,-1,world)
			elif self.touch[6] == 0:
				self.side = -1
				self.move(-1,0,world)
				self.unload_state = 3
			elif self.touch[2] == 0:
				self.side = 1
				self.move(1,0,world)
				self.unload_state = 3
		elif self.unload_state == 3:				#Move on top
			print 'bottom = ', self.touch[4]
			if self.touch[4] == 0:
				self.move(self.side,-1,world)
			elif self.touch[4] == 1:
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
			if self.touch[4+2*self.side] == 0:
				self.unload_state = 9
		elif self.unload_state == 9:
			if self.touch[4+self.side] == 1:
				self.move(-self.side,-1,world)
			elif self.touch[4] == 0:
				self.move(-self.side,0,world)
			else:
				self.unload_state = 10
				self.wall_follow_state = -self.side # set priority
		elif self.unload_state == 10:
			self.wall_follow(0,world)		#anything not 1 goes down
			if self.rect.center[1] > 210:		#back in tunnel
				self.unload_state = 0		#Reset unload
				self.state = 3			#switch to explore mode
			
### Functions for exper_robot unique actions				
				
	def lay_beacon(self, value, world):
		world[self.rect.center[0],self.rect.center[1]] = value
		
	def sense_beacon(self, value, remove, world):
		sense_range = self.getRange(world,5)
		beacons = np.where(sense_range==value)
		if remove:
			world[beacons] = self.config['empty']
		#print 'beacons: ', beacons[0], beacons[0].shape
		return beacons			
			
	def vision_2_feel(self, world):
		#Top -> 0
		if self.vision[self.rel_pt(0,-5)] == -1 or self.vision[self.rel_pt(1,-5)] == -1 or self.vision[self.rel_pt(2,-5)] == -1 or self.vision[self.rel_pt(-1,-5)] == -1 or self.vision[self.rel_pt(-2,-5)] == -1:
			self.touch[0] = 1
		elif self.vision[self.rel_pt(3,-4)] == -1 or self.vision[self.rel_pt(4,-3)] == -1 or self.vision[self.rel_pt(-3,-4)] == -1 or self.vision[self.rel_pt(-4,-3)] == -1:
			self.touch[0] = 1
		elif self.vision[self.rel_pt(0,-5)] == -2 or self.vision[self.rel_pt(1,-5)] == -2 or self.vision[self.rel_pt(2,-5)] == -2 or self.vision[self.rel_pt(-1,-5)] == -2 or self.vision[self.rel_pt(-2,-5)] == -2:
			self.touch[0] = 2
		elif self.vision[self.rel_pt(3,-4)] == -2 or self.vision[self.rel_pt(4,-3)] == -2 or self.vision[self.rel_pt(-3,-4)] == -2 or self.vision[self.rel_pt(-4,-3)] == -2:
			self.touch[0] = 2
		else:
			self.touch[0] = 0
			
		#Top right -> 1
#		if  self.vision[self.rel_pt(3,-4)] == -1 or self.vision[self.rel_pt(4,-3)] == -1:
#			self.touch[1] = 1
#		elif self.vision[self.rel_pt(3,-4)] == -2 or self.vision[self.rel_pt(4,-3)] == -2:
#			self.touch[1] = 2
#		else:
#			self.touch[1] = 0
			
		#right -> 2
		if self.vision[self.rel_pt(5,0)] == -1 or self.vision[self.rel_pt(5,1)] == -1 or self.vision[self.rel_pt(5,2)] == -1 or self.vision[self.rel_pt(5,-1)] == -1 or self.vision[self.rel_pt(5,-2)] == -1:
			self.touch[2] = 1
		elif self.vision[self.rel_pt(4,-3)] == -1 or self.vision[self.rel_pt(3,-4)] == -1 or self.vision[self.rel_pt(4,3)] == -1 or self.vision[self.rel_pt(3,4)] == -1:
			self.touch[2] = 1
		elif self.vision[self.rel_pt(5,0)] == -2 or self.vision[self.rel_pt(5,1)] == -2 or self.vision[self.rel_pt(5,2)] == -2 or self.vision[self.rel_pt(5,-1)] == -2 or self.vision[self.rel_pt(5,-2)] == -2:
			self.touch[2] = 2
		elif self.vision[self.rel_pt(4,-3)] == -2 or self.vision[self.rel_pt(3,-4)] == -2 or self.vision[self.rel_pt(4,3)] == -2 or self.vision[self.rel_pt(3,4)] == -2:
			self.touch[2] = 2
		else:
			self.touch[2] = 0

		#bot right -> 3
#		if  self.vision[self.rel_pt(3,4)] == -1 or self.vision[self.rel_pt(4,3)] == -1:
#			self.touch[3] = 1
#		elif self.vision[self.rel_pt(3,4)] == -2 or self.vision[self.rel_pt(4,3)] == -2:
#			self.touch[3] = 2
#		else:
#			self.touch[3] = 0	
		
		#bot -> 4
		if self.vision[self.rel_pt(0,5)] == -1 or self.vision[self.rel_pt(1,5)] == -1 or self.vision[self.rel_pt(2,5)] == -1 or self.vision[self.rel_pt(-1,5)] == -1 or self.vision[self.rel_pt(-2,5)] == -1:
			self.touch[4] = 1
		elif self.vision[self.rel_pt(3,4)] == -1 or self.vision[self.rel_pt(4,3)] == -1 or self.vision[self.rel_pt(-3,4)] == -1 or self.vision[self.rel_pt(-4,3)] == -1:
			self.touch[4] = 1
		elif self.vision[self.rel_pt(0,5)] == -2 or self.vision[self.rel_pt(1,5)] == -2 or self.vision[self.rel_pt(2,5)] == -2 or self.vision[self.rel_pt(-1,5)] == -2 or self.vision[self.rel_pt(-2,5)] == -2:
			self.touch[4] = 2
		elif self.vision[self.rel_pt(3,4)] == -2 or self.vision[self.rel_pt(4,-3)] == -2 or self.vision[self.rel_pt(-3,4)] == -2 or self.vision[self.rel_pt(-4,3)] == -2:
			self.touch[4] = 2
		else:
			self.touch[4] = 0
			
		#bot left -> 5
#		if  self.vision[self.rel_pt(-3,4)] == -1 or self.vision[self.rel_pt(-4,3)] == -1:
#			self.touch[5] = 1
#		elif self.vision[self.rel_pt(-3,4)] == -2 or self.vision[self.rel_pt(-4,3)] == -2:
#			self.touch[5] = 2
#		else:
#			self.touch[5] = 0
			
		#left -> 6
		if self.vision[self.rel_pt(-5,0)] == -1 or self.vision[self.rel_pt(-5,1)] == -1 or self.vision[self.rel_pt(-5,2)] == -1 or self.vision[self.rel_pt(-5,-1)] == -1 or self.vision[self.rel_pt(-5,-2)] == -1:
			self.touch[6] = 1
		elif self.vision[self.rel_pt(-4,-3)] == -1 or self.vision[self.rel_pt(-3,-4)] == -1 or self.vision[self.rel_pt(-4,3)] == -1 or self.vision[self.rel_pt(-3,4)] == -1:
			self.touch[6] = 1
		elif self.vision[self.rel_pt(-5,0)] == -2 or self.vision[self.rel_pt(-5,1)] == -2 or self.vision[self.rel_pt(-5,2)] == -2 or self.vision[self.rel_pt(-5,-1)] == -2 or self.vision[self.rel_pt(-5,-2)] == -2:
			self.touch[6] = 2
		elif self.vision[self.rel_pt(-4,-3)] == -2 or self.vision[self.rel_pt(-3,-4)] == -2 or self.vision[self.rel_pt(-4,3)] == -2 or self.vision[self.rel_pt(-3,4)] == -2:
			self.touch[6] = 2
		else:
			self.touch[6] = 0
			
		#top left -> 7
#		if  self.vision[self.rel_pt(-3,-4)] == -1 or self.vision[self.rel_pt(-4,-3)] == -1:
#			self.touch[7] = 1
#		elif self.vision[self.rel_pt(-3,-4)] == -2 or self.vision[self.rel_pt(-4,-3)] == -2:
#			self.touch[7] = 2
#		else:
#			self.touch[7] = 0

	def stop(self,world):
		return 1
		
		