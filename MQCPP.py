import pyomo.environ as pe

model = pe.ConcreteModel()

UB = 5
UB_k = 
V = {1, 2, 3, 4}
E = {(1, 2), (1, 4), (2, 3)}
gamma = 1

model.i = pe.RangeSet(1, UB)
# model.u = pe.Set(initialize=V)
model.v = pe.Set(initialize=V)
model.edges = pe.Set(dimen=2, initialize={(u, v) for u in V for v in V if u < v})


model.x = pe.Var(model.i, model.v, within=pe.Binary)
model.y = pe.Var(model.i, within=pe.Binary)
model.w = pe.Var(model.i, model.edges, within=pe.Binary)


def four_constraint_func(model, v):
    return sum(model.x[i, v] for i in model.i) == 1


def five_constraint_func(model, v, i):
    return model.x[i, v] <= model.y[i]


def six_constraint_func(model, u, v, i):
    return model.x[i, u] + model.x[i, v] <= model.w[i, (u, v)] + 1


def seven_constraint_func(model, u, v, i):
    return model.w[i, (u, v)] <= model.x[i, u]


def eight_constraint_func(model, u, v, i):
    return model.w[i, (u, v)] <= model.x[i, v]


def nine_constraint_func(model, i):
    return (sum
            (sum(model.w[i, (u, v)] for v in model.v if (u, v) in E and u < v)
             for u in model.v) >=
            gamma * sum(
                sum(model.w[i, (u, v)] for v in model.v if u< v)
                for u in model.v))


def ten_constraint_func(model, i):
    if i < UB:
        return model.y[i] >= model.y[i + 1]
    else:
        return pe.Constraint.Skip


model.fourth_constraint = pe.Constraint(model.v, rule=four_constraint_func)
model.fifth_constraint = pe.Constraint(model.v, model.i, rule=five_constraint_func)
model.six_constraint = pe.Constraint(model.edges, model.i, rule=six_constraint_func)
model.seven_constraint = pe.Constraint(model.edges, model.i, rule=seven_constraint_func)
model.eight_constraint = pe.Constraint(model.edges, model.i, rule=eight_constraint_func)
model.nine_constraint = pe.Constraint(model.i, rule=nine_constraint_func)
model.ten_constraint = pe.Constraint(model.i, rule=ten_constraint_func)

model.obj = pe.Objective(expr=sum(model.y[i] for i in model.i))