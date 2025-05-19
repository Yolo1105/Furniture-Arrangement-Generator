# rules/symbolic_compiler.py
from z3 import Real, Solver, And

def compile_wall_constraint(furniture, rule):
    x = Real("x")
    y = Real("y")
    min_dist = rule.get("min_wall_distance", 0)
    return And(x >= min_dist, y >= min_dist)

def compile_all_rules(furniture_type, rule_template):
    constraints = []
    for rule_name, rule in rule_template.items():
        if rule["type"] == furniture_type:
            if "min_wall_distance" in rule:
                constraints.append(compile_wall_constraint(furniture_type, rule))
    return constraints
