import time
# %%
from FJSSP_parser import *
# %%
from docplex.mp.model import Model

# instance file description nbre_jobs nbre_machine moy chaque ligne contient un job [num op, machines eligible for
# op1, machine num,  processing time, machines eligible for op2, machine num,  processing time]

instance = parse_fjssp_instance("data/Fattahi5.fjs")
n = instance.n  # total number of jobs
m = instance.m  # total number of machines
print(instance)

# %%
# for comparaison with all instances
# instances = [parse_fjssp_instance(f"data/Fattahi{i}.fjs") for i in range(1, 6)]
# instance = instances[2]
# %%
# defining variable indexes

# V(i,j,k) binary matrix for whether op(i,j) can be performed on machine k
v_idx = [(i, j, k) for i in range(n) for j in range(instance.jobs[i].nb_op)
         for k in range(1, instance.m + 1)]

# S(i,j,k) starting time of op(i,j) on machine k
s_idx = [(i, j, k) for i in range(n) for j in range(instance.jobs[i].nb_op)
         for k in range(1, instance.m + 1)]

# C(i,j,k) completion time of op(i,j) on machine k
c_idx = [(i, j, k) for i in range(n) for j in range(instance.jobs[i].nb_op)
         for k in range(1, instance.m + 1)]

# C(i) completion time of job i
ci_idx = [i for i in range(n)]

# Z(i,j,h,g,k) binary matrix of whether op(i,j) proceeds op(h,g) on machine k
z_idx = [(i, j, h, g, k) for i in range(n) for j in range(instance.jobs[i].nb_op)
         for h in range(n) for g in range(instance.jobs[h].nb_op)
         for k in range(1, instance.m + 1)]


# Machine for each Oij
def get_time_machine(i, j, machine):
    for t in instance.jobs[i].operations[j].processing_time:
        if t[0] == machine:
            return t[1]
    return None


def get_machines(operation):
    machines = []
    for i in operation.processing_time:
        machines.append(i[0])
    return machines


# Mij ∩ Mhg
def get_intersection(m1, m2):
    intersection = []
    for machine in m1:
        if machine in m2:
            intersection.append(machine)
    return intersection


# %%
# create one model instance, with a name
model = Model(name='FJSSP')

# defining model decision variables
model.v = model.binary_var_dict(v_idx, name="V")
model.s = model.continuous_var_dict(s_idx, lb=0, name="S")
model.c = model.continuous_var_dict(c_idx, lb=0, name="C")
model.z = model.binary_var_dict(z_idx, name="Z")
model.ci = model.continuous_var_dict(ci_idx, lb=0, name="Ci")
model.C_max = model.integer_var(int(), name="C_max")
M = 10 ** 6  # denotes big number (infinity)

# constraints
for i in range(n):
    # constraint 1: C_max <= Ci ∀i
    model.add_constraint(model.C_max >= model.ci[i], ctname="Constraint_1")

# constraint 2: job completion time >= sum of its final op(i,J) completion time on corresponding machine k of (Mij)
for i in range(n):
    # J = instance.jobs[i].nb_op - 1
    for j in range(instance.jobs[i].nb_op):
        model.add_constraint(model.sum(model.c[i, j, k]
                                       for k in get_machines(instance.jobs[i].operations[j])) <= model.ci[i],
                             ctname="Constraint_2")

# constraint 3: S(i,j,k) + C(i,j,k) <= V(i,j,k)*M [Upper bound] , ∀ i,j,k ∈ Mij
for i in range(n):
    for j in range(instance.jobs[i].nb_op):
        for k in get_machines(instance.jobs[i].operations[j]):
            model.add_constraint(model.s[i, j, k] + model.c[i, j, k] <= model.v[i, j, k] * M, ctname=f"Constraint_3")

# constraint 4: C(i,j,k) >= S(i,j,k) + processing time - (1 - V(i,j,k))*M [Lower bound]  , ∀ i,j,k ∈ Mij
for i in range(n):
    for j in range(instance.jobs[i].nb_op):
        for k in get_machines(instance.jobs[i].operations[j]):
            model.add_constraint(
                model.c[i, j, k] >= (model.s[i, j, k] + get_time_machine(i, j, k) - (1 - model.v[i, j, k]) * M),
                ctname="Constraint_4")

# c 5 & 6 :
for h in range(n):
    for i in range(h):
        for j in range(instance.jobs[i].nb_op):
            for g in range(instance.jobs[h].nb_op):
                K = get_intersection(get_machines(instance.jobs[i].operations[j]),
                                     get_machines(instance.jobs[h].operations[g]))
                # print(i, j, " - ", h, g, ": ", K)

                for k in K:
                    # k = ki - 1
                    # constraint 5 & 6 :

                    model.add_constraint(model.s[i, j, k] >= model.c[h, g, k] - model.z[i, j, h, g, k] * M,
                                         ctname="Constraint_5")
                    model.add_constraint(model.s[h, g, k] >= model.c[i, j, k] - (1 - model.z[i, j, h, g, k]) * M,
                                         ctname="Constraint_6")

# constraint 7: Sum of S(i,j,k) >= Sum of C(i,j-1,k) with k ∈ Mij, ∀ i,∀ j = 2,...,J (starting from 2nd op) [
# op are running sequentially in the same machine]
for i in range(n):
    for j in range(1, instance.jobs[i].nb_op):
        for k in get_machines(instance.jobs[i].operations[j]):
            model.add_constraint(model.sum(model.s[i, j, k] for k in get_machines(instance.jobs[i].operations[j])) >=
                                 model.sum(
                                     model.c[i, j - 1, k2] for k2 in get_machines(instance.jobs[i].operations[j - 1]))
                                 , ctname="cstr7_" + str(i) + "_" + str(j))

# constraint 8: Sum of V(i,j,k) = 1 ∀ i,j (an op is operated at only one machine)
for i in range(n):
    for j in range(instance.jobs[i].nb_op):
        model.add_constraint(model.sum(model.v[i, j, k] for k in get_machines(instance.jobs[i].operations[j])) == 1,
                             ctname="Constraint_8")

# model.add_constraint(model.z[0,0,2,0,0] == 1)
# %%
# objective function
model.minimize(model.C_max)

model.print_information()  # instance 0 , in original paper num of constraints eq 134
model.export_as_lp("lp.lp")

st = time.time()
s = model.solve(log_output=True)
et = time.time()
print("time: ", st - et)
# model.print_solution()
# print("z = ", model.z[0,0,2,0,0].solution_value)
model.print_solution()
