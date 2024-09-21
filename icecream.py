import pyomo.environ as pyo
import pyomo.opt as po


def IC_model(A, h, d, c, b, u):
    # Создаем конкретную модель
    model = pyo.ConcreteModel(name="(H)")

    # Определяем границы для переменных x
    def x_bounds(m, i):
        return (0, u[i])

    # Переменные x с границами
    model.x = pyo.Var(A, bounds=x_bounds)

    # Правило для целевой функции
    def z_rule(model):
        return sum(h[i] * (model.x[i] - (model.x[i] / d[i]) ** 2) for i in A)

    # Определяем целевую функцию (максимизация)
    model.z = pyo.Objective(rule=z_rule, sense=pyo.maximize)

    # Ограничение на бюджет
    model.budgetconstr = pyo.Constraint(
        expr=sum(c[i] * model.x[i] for i in A) <= b
    )

    return model

