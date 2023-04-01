import math
import random
import os
import docplex.cp.model as cp


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

instance = parse_fjssp_instance("temp_data/Fattahi1.fjs")

print(instance.jobs[0].operations[0].processing_time)

model = cp.CpoModel()

Oij={}
Aijk={}
for i in range(instance.n):
	for j in range(instance.jobs[i].nb_op):
		Oij[(i,j)] = cp.interval_var()
		for k in range(instance.m):
			l = [u[0] for u in instance.jobs[i].operations[j].processing_time]
			
			Aijk[(i,j,k)] = cp.interval_var(optional=True, size=instance.jobs[i].operations[j].processing_time[k-1][1] if k in l else 0)


for k in range(instance.m):
	model.add(cp.no_overlap([Aijk[(i,j,k)] for i in range(instance.n) for j in range(instance.jobs[i].nb_op)]))

for i in range(instance.n): 
	for j in range(instance.jobs[i].nb_op):
		if j >= 1: 
			model.add(cp.end_before_start(Oij[i,j-1], Oij[i,j]))
		
		model.add(cp.alternative(Oij[i,j], [Aijk[i,j,k] for k in range(instance.m)]))


model.minimize(model.max([cp.end_of(Oij[i,j]) for i in range(instance.n) for j in range(instance.jobs[i].nb_op)]))

#sol = model.solve()





