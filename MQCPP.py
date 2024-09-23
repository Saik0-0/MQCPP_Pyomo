import math

import pyomo.environ as pe

model = pe.ConcreteModel()

gamma = 0.8
V = {1, 2, 3, 4}
E = {(1, 2), (1, 4), (2, 3)}
UB = 5
UB_k = math.floor(0.5 + 0.5 * math.sqrt(1 + 8 * (len(E) / gamma)))

model.i = pe.RangeSet(1, UB)
model.k = pe.RangeSet(1, UB_k)
model.v = pe.Set(initialize=V)
model.edges = pe.Set(dimen=2, initialize={(u, v) for u in V for v in V if u < v})
model.edges_2 = pe.Set(dimen=2, initialize={(u, v) for (u, v) in E})


model.x = pe.Var(model.i, model.v, within=pe.Binary)
model.y = pe.Var(model.i, within=pe.Binary)
model.w = pe.Var(model.i, model.edges, within=pe.Binary)
model.z = pe.Var(model.i, model.k, within=pe.Binary)
model.o = pe.Var(model.i, model.edges_2, within=pe.Binary)


def four_constraint_func(model, v):
    return sum(model.x[i, v] for i in model.i) == 1


def five_constraint_func(model, v, i):
    return model.x[i, v] <= model.y[i]


# def six_constraint_func(model, u, v, i):
#     return model.x[i, u] + model.x[i, v] <= model.w[i, (u, v)] + 1
#
#
# def seven_constraint_func(model, u, v, i):
#     return model.w[i, (u, v)] <= model.x[i, u]
#
#
# def eight_constraint_func(model, u, v, i):
#     return model.w[i, (u, v)] <= model.x[i, v]
#
#
# def nine_constraint_func(model, i):
#     return (sum
#             (sum(model.w[i, (u, v)] for v in model.v if (u, v) in E and u < v)
#              for u in model.v) >=
#             gamma * sum(
#                 sum(model.w[i, (u, v)] for v in model.v if u< v)
#                 for u in model.v))


def ten_constraint_func(model, i):
    if i < UB:
        return model.y[i] >= model.y[i + 1]
    else:
        return pe.Constraint.Skip


def seventeen_constraint_func(model, i, u, v):
    return model.o[i, (u, v)] <= model.x[i, u]


def eighteen_constraint_func(model, i, u, v):
    return model.o[i, (u, v)] <= model.x[i, v]


def nineteen_constraint_func(model, i):
    return sum(model.x[i, v] for v in V) == sum(k * model.z[i, k] for k in model.k)


def twenty_constraint_func(model, i):
    return sum(model.z[i, k] for k in model.k) == model.y[i]


def twentyone_constraint_func(model, i):
    return sum(model.o[i, (u, v)] for (u, v) in model.edges_2) >= gamma * sum((k * (k - 1) / 2) * model.z[i, k] for k in model.k)


model.fourth_constraint = pe.Constraint(model.v, rule=four_constraint_func)
model.fifth_constraint = pe.Constraint(model.v, model.i, rule=five_constraint_func)
# model.six_constraint = pe.Constraint(model.edges, model.i, rule=six_constraint_func)
# model.seven_constraint = pe.Constraint(model.edges, model.i, rule=seven_constraint_func)
# model.eight_constraint = pe.Constraint(model.edges, model.i, rule=eight_constraint_func)
# model.nine_constraint = pe.Constraint(model.i, rule=nine_constraint_func)
model.ten_constraint = pe.Constraint(model.i, rule=ten_constraint_func)
model.seventeen_constraint = pe.Constraint(model.i, model.edges_2, rule=seventeen_constraint_func)
model.eighteen_constraint = pe.Constraint(model.i, model.edges_2, rule=eighteen_constraint_func)
model.nineteen_constraint = pe.Constraint(model.i, rule=nineteen_constraint_func)
model.twenty_constraint = pe.Constraint(model.i, rule=twenty_constraint_func)
model.twentyone_constraint = pe.Constraint(model.i, rule=twentyone_constraint_func)


model.obj = pe.Objective(expr=sum(model.y[i] for i in model.i))