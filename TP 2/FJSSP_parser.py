import math
import random
import os

# Class to store the data related to an operation
class Operation:

	def __init__(self, nb_ma):
		self.nb_ma = nb_ma # number of compatible machines
		self.processing_time = [] # list of tuples (machine, time) of size nb_ma 

# Class to store the data related to a job
class Job:

	def __init__(self, nb_op):
		self.nb_op = nb_op # number of operations
		self.operations = [] # liste of Operation of size nb_op

# Class to store the data related to an instance of type Fjssp
class Fjssp_instance:

	def __init__(self, n, m, moy):
		self.n = n
		self.m = m 
		self.moy = moy
		self.jobs = [] # list of Job of size n



def parse_fjssp_instance(filename):
	io = open(filename)
	line = io.readline()
	splitted = line.split()
	n = int(splitted[0])
	m = int(splitted[1])
	moy = 0
	if len(splitted) > 2: 
		moy = float(splitted[2])
	instance = Fjssp_instance(n, m, moy)
	for i in range(n):
		line = io.readline()
		splitted = line.split()
		nb_op = int(splitted[0])
		index = 1
		job = Job(nb_op)
		for j in range(nb_op):
			nb_ma = int(splitted[index])
			operation = Operation(nb_ma)
			for k in range(nb_ma):
				machine = int(splitted[index+1])
				time = int(splitted[index+2])
				operation.processing_time.append((machine, time))
				index += 2
			index+=1
			job.operations.append(operation)
		instance.jobs.append(job)
	return instance

