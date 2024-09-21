import pyomo.environ as pyo
import pyomo.opt as po

solver = po.SolverFactory('glpk')

vertices = {'Ar', 'Bo', 'Br', 'Ch', 'Co',
            'Ec', 'FG', 'Gu', 'Pa', 'Pe',
            'Su', 'Ur', 'Ve'}

edges = {('FG', 'Su'), ('FG', 'Br'), ('Su', 'Gu'), ('Su', 'Br'),
         ('Gu', 'Ve'), ('Gu', 'Br'), ('Ve', 'Co'), ('Ve', 'Br'),
         ('Co', 'Ec'), ('Co', 'Pe'), ('Co', 'Br'), ('Ec', 'Pe'),
         ('Pe', 'Ch'), ('Pe', 'Bo'), ('Pe', 'Br'), ('Ch', 'Ar'),
         ('Ch', 'Bo'), ('Ar', 'Ur'), ('Ar', 'Br'), ('Ar', 'Pa'),
         ('Ar', 'Bo'), ('Ur', 'Br'), ('Bo', 'Pa'), ('Bo', 'Br'),
         ('Pa', 'Br')}

ncolors = 4
colors = range(1, ncolors + 1)

model = pyo.ConcreteModel()
model.x = pyo.Var(vertices, colors, within=pyo.Binary)
model.y = pyo.Var(domain=pyo.NonNegativeIntegers)

model.node_coloring = pyo.ConstraintList()
for v in vertices:
    model.node_coloring.add(sum(model.x[v, c] for c in colors) == 1)

model.edge_coloring = pyo.ConstraintList()
for v1, v2 in edges:
    for c in colors:
        model.edge_coloring.add(model.x[v1, c] + model.x[v2, c] <= 1)

model.min_coloring = pyo.ConstraintList()
for v in vertices:
    for c in colors:
        model.min_coloring.add(model.y >= c * model.x[v,c])

model.obj = pyo.Objective(expr=model.y)

result = solver.solve(model)

print(pyo.value(model.obj))
