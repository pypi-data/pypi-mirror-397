from dataclasses import dataclass
from typing import List, Union, Literal
from ortools.linear_solver import pywraplp
from curvaceous.curve import Curve

Number = Union[int, float]
Domain = Literal["x", "y"]


@dataclass
class Result:
    status: int
    xs: List[float]
    ys: List[float]


@dataclass
class Constraint:
    lb: Number
    ub: Number
    idx: List[int]
    domain: Domain


def maximize(curves: List[Curve], constraints: List[Constraint]) -> Result:
    solver, ws = _create_model(curves, constraints)
    status = solver.Solve()
    return _to_result(status, curves, ws)


def _create_model(curves: List[Curve], constraints: List[Constraint]):
    # Create OR-Tools solver
    solver = pywraplp.Solver.CreateSolver("CBC")
    if not solver:
        raise RuntimeError("CBC solver unavailable")

    ws = []
    bs = []

    # Track contributions for constraints
    costs = {i: [] for i, c in enumerate(constraints) if c.domain == "x"}
    ys_contrib = {i: [] for i, c in enumerate(constraints) if c.domain == "y"}

    objective_terms = []

    for idx, curve in enumerate(curves):
        k = len(curve.xs)

        # Continuous weights
        w = [solver.NumVar(0.0, solver.infinity(), f"w_{idx}_{j}") for j in range(k)]
        ws.append(w)

        # Binary selectors
        b = [solver.IntVar(0, 1, f"b_{idx}_{j}") for j in range(k - 1)]
        bs.append(b)

        # Sum of weights equals 1
        solver.Add(solver.Sum(w[j] for j in range(k)) == 1)

        # Linking constraints
        solver.Add(w[0] <= b[0])
        for j in range(1, k - 1):
            solver.Add(w[j] <= b[j - 1] + b[j])
        solver.Add(w[k - 1] <= b[k - 2])

        # Exactly one segment active
        solver.Add(solver.Sum(b[j] for j in range(k - 1)) == 1)

        # Objective and constraint contributions
        for j in range(k):
            objective_terms.append(w[j] * float(curve.ys[j]))
            for i, c in enumerate(constraints):
                if idx in c.idx:
                    if c.domain == "x":
                        costs[i].append(w[j] * float(curve.xs[j]))
                    elif c.domain == "y":
                        ys_contrib[i].append(w[j] * float(curve.ys[j]))

    # Add global constraints
    for i, c in enumerate(constraints):
        if c.domain == "x":
            expr = solver.Sum(costs[i])
        elif c.domain == "y":
            expr = solver.Sum(ys_contrib[i])
        else:
            continue

        if c.lb is not None:
            solver.Add(expr >= c.lb)
        if c.ub is not None:
            solver.Add(expr <= c.ub)

    # Objective
    solver.Maximize(solver.Sum(objective_terms))

    return solver, ws


def _to_result(status, curves, ws):
    if status == pywraplp.Solver.OPTIMAL:
        return Result(status, *_compute_xs_and_ys(curves, ws))
    return Result(status, None, None)


def _compute_xs_and_ys(curves, ws):
    xs = []
    ys = []
    for i, curve in enumerate(curves):
        k = len(curve)
        xs.append(sum(ws[i][j].solution_value() * float(curve.xs[j]) for j in range(k)))
        ys.append(sum(ws[i][j].solution_value() * float(curve.ys[j]) for j in range(k)))
    return xs, ys
