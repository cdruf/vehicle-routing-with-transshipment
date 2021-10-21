"""
Model based on Ghiani et al. (2021) - Optimizing a waste collection system with solid waste transfer stations
"""
from collections import namedtuple

import gurobipy as gb
import numpy as np
from gurobipy import GRB

from util import Loc

# %%
Q = 400  # capacity of small vehicles in kg
Q_ = 1400  # capacity of large vehicles in kg
L = 480  # max route duration small vehicles in min
L_ = 480  # max route duration large vehicles in min
speed = 30.0  # average speed of vehicles in km/h

# Collection points (=demand points)
min_lat = 0.0
max_lat = 0.2
min_lon = 0.0
max_lon = 0.2
n_C = 20
CP = namedtuple('CP', ['loc', 'demand'])  # collection point
C = [CP(Loc.get_random(min_lat, max_lat, min_lon, max_lon), np.random.uniform(100, 300))
     for c in range(n_C)]  # set of demand points

# Transshipment stations
n_S = 2  # number of transfer stations
S = [Loc.get_random(min_lat, max_lat, min_lon, max_lon) for _ in range(n_S)]

# Enumerate legs
I = []  # type 1 legs, i.e. route from depot to transfer station
n_I = 10
s_i = {}
t_i = {}
J = []  # type 2 legs, i.e. route from transfer station to transfer station
n_J = 10
s_j = {}
t_j = {}
a_ci = {}  # 1 if collection point c is part of leg i
a_i = {}  # collection points that are part of leg i
a_c = {}  # legs of type 1 that contain collection point c
b_cj = {}  # 1 if collection point c is part of leg j
b_j = {}  # collection points that are part of leg j
b_c = {}  # legs of type 2 that contain collection point c

n_K = n_C  # number of small vehicles
K = list(range(n_K))  # set of homogeneous small vecicles

# %%
model = gb.Model()

# 1, if i in I is selected
x_i = model.addVars()

# 1, if j in J is selected
y_j = model.addVars()

# 1, if i in I is allocated to vehicle k
v_ki = model.addVars()

# 1, if j in J is allocated to vehicle k
w_kj = model.addVars()

# Objective: minimize number of vehicles <=> minimize number of type 1 legs starting at the depot
model.setObjective(v_ki.sum(), GRB.MINIMIZE)

# Constraints: each collection point can only be visited once
model.addConstrs((gb.quicksum([x_i[i] for i in a_c[c]]) +
                  gb.quicksum([y_j[j] for j in b_c[c]]) == 1
                  for c in range(n_C)), "c_cover")

# Constraints: allocate at most one type 1 leg to each small vehicle
model.addConstrs((v_ki.sum(k, '*') <= 1 for k in range(n_K)), "c_leg_t1")

# Constraints: allocate ate most one type 2 leg to each small vehicle (this is a strong assumption!)
model.addConstrs((w_kj.sum(k, '*') <= 1 for k in range(n_K)), "c_leg_t2")

# Constraints: tie variables v_ki with x_i
model.addConstrs((v_ki.sum('*', i) == x_i[i] for i in range(n_I)), "c_tie_v_x")

# Constraints: tie variables w_kj with y_j
model.addConstrs((w_kj.sum('*', j) == y_j[j] for j in range(n_J)), "c_tie_w_y")

# Constraints: a type 2 leg can only be assigned to a vehicle iff a type 1 leg is assigned to it as well
# and the legs must be connected
model.addConstrs((w_kj[k, j] <= gb.quicksum([v_ki[k, i] for i in range(n_I) if s_i[i] == s_j[j]])
                  for k in range(n_K) for j in range(n_J)), "c_tie_legs")

# Constrains: limit route durations
model.addConstrs((gb.quicksum([t_i[i] * v_ki[k, i] for i in range(n_I)]) +
                  gb.quicksum([t_j[j] * w_kj[k, j] for j in range(n_J)]) <= L
                  for k in range(n_K)), "c_route_dur")

# %%

# Optimize
model.update()
model.optimize()

for k in range(n_K):
    for v in v_ki.select(k, '*'):
        if v.x > 0.5:
            i = 1  # TODO
        for w in w_kj.select(k, '*'):
            if w.x > 0.5:
                j = 1  # TODO
        print(f"vehicle {k} route {i}, {j}")
