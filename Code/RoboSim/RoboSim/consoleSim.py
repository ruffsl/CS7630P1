# -*- coding: utf-8 -*-

class Map:
	def __init__(self,size,num_agents):	#Takes size in row/column format
		self.grid = [[0 for i in range(size[1])] for j in range(size[0])]
		self.agent_list = [[0,0] for i in range(num_agents)]
	
	def printGrid(self):
		for i in self.grid:	#For each row i
			for j in i:		#For each column j of row i
				if j>=0:
					print " - ",	#Print that node
				else:
					print "[ ]",
			print ""
		print "\n"
		
	def createDirt(self, top_left, bottom_right):
		for i in range(top_left[0],bottom_right[0]):
			for j in range(top_left[1],bottom_right[1]):
				self.grid[i][j] = -1
		

#Just for testing
temp_size = [10,15]
temp_map = Map(temp_size, 2)
temp_map.printGrid()
temp_map.createDirt([3,0],[10,15])
temp_map.printGrid()