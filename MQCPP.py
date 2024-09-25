import math

import pyomo.environ as pe

gamma = 0.8
V = [1, 2, 3, 4, 5, 6, 7]
E = [(1, 2), (1, 4), (2, 3)]
UB = 5
UB_k = math.floor(0.5 + 0.5 * math.sqrt(1 + 8 * (len(E) / gamma)))


def model_standard_formulation(gamma, V, E, UB):
    model = pe.ConcreteModel()

    model.i = pe.RangeSet(1, UB)
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
                    sum(model.w[i, (u, v)] for v in model.v if u < v)
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

    return model


def model_using_size_decomposition(gamma, V, E, UB, UB_k):
    model = pe.ConcreteModel()
    model.i = pe.RangeSet(1, UB)
    model.v = pe.Set(initialize=V)
    model.k = pe.RangeSet(1, UB_k)
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

    def seventeen_constraint_func(model, i, u, v):
        return model.o[i, (u, v)] <= model.x[i, u]

    def eighteen_constraint_func(model, i, u, v):
        return model.o[i, (u, v)] <= model.x[i, v]

    def nineteen_constraint_func(model, i):
        return sum(model.x[i, v] for v in V) == sum(k * model.z[i, k] for k in model.k)

    def twenty_constraint_func(model, i):
        return sum(model.z[i, k] for k in model.k) == model.y[i]

    def twenty_one_constraint_func(model, i):
        return (sum(model.o[i, (u, v)] for (u, v) in model.edges_2) >=
                gamma * sum((k * (k - 1) / 2) * model.z[i, k] for k in model.k))

    model.fourth_constraint = pe.Constraint(model.v, rule=four_constraint_func)
    model.fifth_constraint = pe.Constraint(model.v, model.i, rule=five_constraint_func)
    model.seventeen_constraint = pe.Constraint(model.i, model.edges_2, rule=seventeen_constraint_func)
    model.eighteen_constraint = pe.Constraint(model.i, model.edges_2, rule=eighteen_constraint_func)
    model.nineteen_constraint = pe.Constraint(model.i, rule=nineteen_constraint_func)
    model.twenty_constraint = pe.Constraint(model.i, rule=twenty_constraint_func)
    model.twenty_one_constraint = pe.Constraint(model.i, rule=twenty_one_constraint_func)

    model.obj = pe.Objective(expr=sum(model.y[i] for i in model.i))
    return model


def model_formulation_by_representatives(gamma, V, UB_k):
    model = pe.ConcreteModel()

    model.v = pe.Set(initialize=V)
    model.k = pe.RangeSet(1, UB_k)
    model.edges = pe.Set(dimen=2, initialize={(u, v) for u in V for v in V if u < v})
    model.edges_triples = pe.Set(dimen=3, initialize={(u, v, v_1) for u in V for v in V for v_1 in V if u <= v < v_1})

    model.X = pe.Var(model.edges_3, within=pe.Binary)
    model.W = pe.Var(model.edges_triples, within=pe.Binary)
    model.Z = pe.Var(model.v, model.k, within=pe.Binary)

    def twenty_five_constraint_func(model, v):
        return sum(model.X[u, v] for u in model.v if u <= v) == 1

    def twenty_six_constraint_func(model, u, v):
        return model.X[u, v] <= model.X[u, u]

    def twenty_seven_constraint_func(model, u, v, v_1):
        return model.X[u, v] + model.X[u, v_1] <= model.W[u, v, v_1] + 1

    def twenty_eight_constraint_func(model, u, v, v_1):
        return model.W[u, v, v_1] <= model.X[u, v]

    def twenty_nine_constraint_func(model, u, v, v_1):
        return model.W[u, v, v_1] <= model.X[u, v_1]

    def thirty_constraint_func(model, u):
        if u < len(V):
            return (sum(
                sum(model.W[u, v, v_1] for v_1 in model.v if v < v_1 and (v, v_1) in model.e)
                for v in model.v if u <= v) >= gamma *
                    sum(sum(model.W[u, v, v_1] for v_1 in model.v if v < v_1) for v in model.v if u <= v))
        else:
            return pe.Constraint.Skip

    model.twenty_five_constraint = pe.Constraint(model.v, rule=twenty_five_constraint_func)
    model.twenty_six_constraint = pe.Constraint(model.edges, rule=twenty_six_constraint_func)
    model.twenty_seven_constraint = pe.Constraint(model.edges_triples, rule=twenty_seven_constraint_func)
    model.twenty_eight_constraint = pe.Constraint(model.edges_triples, rule=twenty_eight_constraint_func)
    model.twenty_nine_constraint = pe.Constraint(model.edges_triples, rule=twenty_nine_constraint_func)
    model.thirty_constraint = pe.Constraint(model.v, rule=thirty_constraint_func)

    model.obj = pe.Objective(expr=sum(model.X[u, u] for u in model.v))
    return model


def model_representatives_using_decomposition(gamma, V, UB_k):
    model = pe.ConcreteModel()

    model.v = pe.Set(initialize=V)
    model.k = pe.RangeSet(1, UB_k)
    model.edges = pe.Set(dimen=2, initialize={(u, v) for u in V for v in V if u < v})
    model.edges_triples = pe.Set(dimen=3, initialize={(u, v, v_1) for u in V for v in V for v_1 in V if u <= v < v_1})

    model.X = pe.Var(model.edges_3, within=pe.Binary)
    model.W = pe.Var(model.edges_triples, within=pe.Binary)
    model.Z = pe.Var(model.v, model.k, within=pe.Binary)
    model.O = pe.Var(model.edges_triples_2, within=pe.Binary)

    def twenty_five_constraint_func(model, v):
        return sum(model.X[u, v] for u in model.v if u <= v) == 1

    def twenty_six_constraint_func(model, u, v):
        return model.X[u, v] <= model.X[u, u]

    def thirty_six_constraint_func(model, u, v, v_1):
        return model.O[u, v, v_1] <= model.X[u, v]

    def thirty_seven_constraint_func(model, u, v, v_1):
        return model.O[u, v, v_1] <= model.X[u, v_1]

    def thirty_eight_constraint_func(model, u):
        return sum(model.X[u, v] for v in model.v if v >= u) == sum(k * model.Z[u, k] for k in model.k)

    def thirty_nine_constraint_func(model, u):
        return sum(model.Z[u, k] for k in model.k) == model.X[u, u]

    def forty_constraint_func(model, u):
        return (sum(model.O[u, v, v_1] for (v, v_1) in model.e if u <= v < v_1) >=
                gamma * sum((k * (k - 1) / 2) * model.Z[u, k] for k in model.k))

    model.twenty_five_constraint = pe.Constraint(model.v, rule=twenty_five_constraint_func)
    model.twenty_six_constraint = pe.Constraint(model.edges, rule=twenty_six_constraint_func)
    model.thirty_six_constraint = pe.Constraint(model.edges_triples_2, rule=thirty_six_constraint_func)
    model.thirty_seven_constraint = pe.Constraint(model.edges_triples_2, rule=thirty_seven_constraint_func)
    model.thirty_eight_constraint = pe.Constraint(model.v, rule=thirty_eight_constraint_func)
    model.thirty_nine_constraint = pe.Constraint(model.v, rule=thirty_nine_constraint_func)
    model.forty_constraint = pe.Constraint(model.v, rule=forty_constraint_func)

    model.obj = pe.Objective(expr=sum(model.X[u, u] for u in model.v))
    return model
