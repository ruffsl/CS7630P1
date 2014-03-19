# -*- coding: utf-8 -*-

class Map:
	def __init__(self,size):	#Takes size in row/column format
		self.grid = [[0 for i in range(size[1])] for j in range(size[0])]
	
	def printGrid(self):
		for i in self.grid:	#For each row i
			for j in i:		#For each column j of row i
				print j,	#Print that node
			print ""
		print "\n"
		

		
#Just for testing
temp_size = [10,15]
temp_map = Map(temp_size)
temporary_map.printGrid()