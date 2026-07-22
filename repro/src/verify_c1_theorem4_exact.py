#!/usr/bin/env python3
"""Exact certificate for Claim 1 / Theorem 4 of arXiv:2410.07388 v1.

The universal result is certified algebraically.  Exhaustive Fraction-based
controls exercise the constructive support-coalescence proof on every simple
graph through five vertices.  No network, floating point, randomness, or
third-party package is used.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations
import json


SOURCE = {
    "ar5iv_url": "https://ar5iv.labs.arxiv.org/html/2410.07388",
    "html_sha256": "94dc307f35bda0046eded2944df2dd7d1a56282462cbc9998fa545b463ac5d66",
    "scope": "Theorem 4, Corollary 2, Appendix B, and the minimum-threshold paragraph",
    "theorem4_slice_sha256": "8ea44454fe5d307bfe6784c24fae884a8b39fb066279c2ff132cbff2a790b338",
    "corollary2_slice_sha256": "3cb02eea34c746003918066f1e89f469ccafa980206e8bdac1ec78086dc99e92",
    "appendix_b_slice_sha256": "2a80746443eaf77c441ecce2bc10f56feaad691e20186ce15ee55c7d95559ca4",
    "v1_source_url": "https://arxiv.org/e-print/2410.07388v1",
    "v1_source_tar_sha256": "1921ada72f0e3277d0e64576cc897791ddb3c271399aa2189c4be3a92467e96e",
}


class Poly:
    """Sparse exact polynomial used for coefficient-level identity checks."""

    N = 9

    def __init__(self, terms=None):
        self.terms = {m: Fraction(c) for m, c in (terms or {}).items() if c}

    @classmethod
    def const(cls, value):
        return cls({(0,) * cls.N: Fraction(value)})

    @classmethod
    def var(cls, index):
        exponent = [0] * cls.N
        exponent[index] = 1
        return cls({tuple(exponent): Fraction(1)})

    def __add__(self, other):
        other = other if isinstance(other, Poly) else Poly.const(other)
        result = dict(self.terms)
        for monomial, coefficient in other.terms.items():
            result[monomial] = result.get(monomial, Fraction(0)) + coefficient
            if not result[monomial]:
                del result[monomial]
        return Poly(result)

    __radd__ = __add__

    def __neg__(self):
        return Poly({m: -c for m, c in self.terms.items()})

    def __sub__(self, other):
        return self + (-other if isinstance(other, Poly) else -Fraction(other))

    def __rsub__(self, other):
        return Poly.const(other) - self

    def __mul__(self, other):
        other = other if isinstance(other, Poly) else Poly.const(other)
        result = {}
        for left_m, left_c in self.terms.items():
            for right_m, right_c in other.terms.items():
                monomial = tuple(a + b for a, b in zip(left_m, right_m))
                result[monomial] = result.get(monomial, Fraction(0)) + left_c * right_c
        return Poly(result)

    __rmul__ = __mul__

    def __pow__(self, power):
        assert power == 2
        return self * self

    def __eq__(self, other):
        other = other if isinstance(other, Poly) else Poly.const(other)
        return self.terms == other.terms


VARS = [Poly.var(i) for i in range(Poly.N)]
XI, XJ, SI, SJ, DELTA, LAM = VARS[:6]


def symbolic_identities():
    """Check all universal equalities coefficient by coefficient."""
    changing = 2 * XI * SI + 2 * XJ * SJ + LAM * (XI**2 + XJ**2)
    merge_j_into_i = 2 * (XI + XJ) * SI + LAM * (XI + XJ) ** 2
    merge_i_into_j = 2 * (XI + XJ) * SJ + LAM * (XI + XJ) ** 2
    merge_i_expected = 2 * XJ * (SI - SJ) + 2 * LAM * XI * XJ
    merge_j_expected = 2 * XI * (SJ - SI) + 2 * LAM * XI * XJ

    pairwise = {}
    for adjacency in (0, 1):
        local = (
            2 * XI * SI
            + 2 * XJ * SJ
            + 2 * adjacency * XI * XJ
            + LAM * (XI**2 + XJ**2)
        )
        shifted = (
            2 * (XI + DELTA) * SI
            + 2 * (XJ - DELTA) * SJ
            + 2 * adjacency * (XI + DELTA) * (XJ - DELTA)
            + LAM * ((XI + DELTA) ** 2 + (XJ - DELTA) ** 2)
        )
        expected = (
            2 * DELTA * ((LAM * XI + SI + adjacency * XJ) - (LAM * XJ + SJ + adjacency * XI))
            + 2 * (LAM - adjacency) * DELTA**2
        )
        pairwise[str(adjacency)] = shifted - local == expected

    clique_objective = {}
    variance = {}
    xvars = VARS[:6]
    for r in range(1, 7):
        xs = xvars[:r]
        adjacency_part = sum(xs[i] * xs[j] for i in range(r) for j in range(r) if i != j)
        square_sum = sum(x * x for x in xs)
        total = sum(xs)
        clique_objective[str(r)] = adjacency_part + LAM * square_sum == total**2 + (LAM - 1) * square_sum
        variance[str(r)] = r * square_sum - total**2 == sum(
            (xs[i] - xs[j]) ** 2 for i in range(r) for j in range(i + 1, r)
        )

    return {
        "merge_j_into_i": merge_j_into_i - changing == merge_i_expected,
        "merge_i_into_j": merge_i_into_j - changing == merge_j_expected,
        "pairwise_rounding_aij_0_1": pairwise,
        "clique_objective_r_1_to_6": clique_objective,
        "variance_identity_r_1_to_6": variance,
    }


def graph_from_mask(n, mask):
    matrix = [[0] * n for _ in range(n)]
    for bit, (i, j) in enumerate(combinations(range(n), 2)):
        matrix[i][j] = matrix[j][i] = (mask >> bit) & 1
    return matrix


def objective(adjacency, x, lam):
    n = len(x)
    return 2 * sum(
        x[i] * x[j]
        for i in range(n)
        for j in range(i + 1, n)
        if adjacency[i][j]
    ) + lam * sum(value * value for value in x)


def compositions(total, parts):
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in compositions(total - first, parts - 1):
            yield (first,) + rest


def clique_number(adjacency):
    n = len(adjacency)
    best = 1
    for size in range(2, n + 1):
        for subset in combinations(range(n), size):
            if all(adjacency[i][j] for i, j in combinations(subset, 2)):
                best = size
    return best


def support_is_clique(adjacency, x):
    support = [i for i, value in enumerate(x) if value]
    return all(adjacency[i][j] for i, j in combinations(support, 2))


def coalesce_to_clique(adjacency, start, lam):
    """Construct the no-worse clique-supported point used in the proof."""
    assert lam >= 0
    x = list(start)
    steps = 0
    while not support_is_clique(adjacency, x):
        support = [i for i, value in enumerate(x) if value]
        i, j = next((i, j) for i, j in combinations(support, 2) if not adjacency[i][j])
        scores = [sum(Fraction(adjacency[v][u]) * x[u] for u in range(len(x))) for v in range(len(x))]
        before = objective(adjacency, x, lam)
        if scores[i] >= scores[j]:
            expected_gain = 2 * x[j] * (scores[i] - scores[j]) + 2 * lam * x[i] * x[j]
            x[i] += x[j]
            x[j] = Fraction(0)
        else:
            expected_gain = 2 * x[i] * (scores[j] - scores[i]) + 2 * lam * x[i] * x[j]
            x[j] += x[i]
            x[i] = Fraction(0)
        after = objective(adjacency, x, lam)
        assert after - before == expected_gain
        assert after >= before
        assert sum(x) == 1 and all(value >= 0 for value in x)
        steps += 1
        assert steps < len(x)
    return tuple(x), steps


def exact_graph_controls():
    lambdas = (Fraction(0), Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1))
    graphs = points = coalescence_steps = attainment_checks = 0
    for n in range(1, 6):
        for mask in range(1 << (n * (n - 1) // 2)):
            adjacency = graph_from_mask(n, mask)
            omega = clique_number(adjacency)
            graphs += 1
            maximum_clique = next(
                subset
                for subset in combinations(range(n), omega)
                if all(adjacency[i][j] for i, j in combinations(subset, 2))
            )
            for lam in lambdas:
                witness = tuple(Fraction(int(i in maximum_clique), omega) for i in range(n))
                formula = 1 + (lam - 1) / omega
                assert objective(adjacency, witness, lam) == formula
                attainment_checks += 1
            for denominator in (1, 2, 3):
                for numerators in compositions(denominator, n):
                    x = tuple(Fraction(value, denominator) for value in numerators)
                    # The chosen nonedge orientation depends only on A*x, so
                    # one exact coalescence trace certifies the full lambda grid.
                    clique_x, steps = coalesce_to_clique(adjacency, x, Fraction(0))
                    for lam in lambdas:
                        value = objective(adjacency, x, lam)
                        clique_value = objective(adjacency, clique_x, lam)
                        formula = 1 + (lam - 1) / omega
                        assert value <= clique_value <= formula
                        assert support_is_clique(adjacency, clique_x)
                        points += 1
                    coalescence_steps += steps
    return {
        "vertices": "1..5",
        "graphs": graphs,
        "lambda_values": [str(value) for value in lambdas],
        "simplex_denominators": [1, 2, 3],
        "exact_points": points,
        "coalescence_steps": coalescence_steps,
        "maximum_clique_attainment_checks": attainment_checks,
    }


def threshold_certificate():
    lambdas = (Fraction(-2), Fraction(-1, 2), Fraction(0), Fraction(1, 3), Fraction(3, 4), Fraction(999, 1000))
    cases = 0
    for k in range(1, 9):
        omega = k + 1
        for lam in lambdas:
            binary_value = k * (k + lam - 1)
            uniform_relaxed_value = k * k + Fraction(k * k, omega) * (lam - 1)
            gap = uniform_relaxed_value - binary_value
            assert gap == Fraction(k, omega) * (1 - lam) > 0
            cases += 1
    return {
        "witness_family": "K_(k+1), sum x_i=k, uniform x_i=k/(k+1)",
        "k_values": "1..8",
        "lambda_values": [str(value) for value in lambdas],
        "strict_gap_identity": "k*(1-lambda)/(k+1)",
        "strict_cases": cases,
        "sufficiency": "pairwise rounding coefficient identity for a_ij in {0,1} and lambda>=1",
        "conclusion": "lambda=1 is the minimal graph-independent tightness guarantee",
    }


def fail_sensitive_controls():
    empty2 = graph_from_mask(2, 0)
    half = (Fraction(1, 2), Fraction(1, 2))
    negative_lambda_merge_decreases = objective(empty2, (Fraction(1), Fraction(0)), Fraction(-1)) < objective(empty2, half, Fraction(-1))

    complete2 = graph_from_mask(2, 1)
    uniform_value = objective(complete2, half, Fraction(2))
    endpoint_value = objective(complete2, (Fraction(1), Fraction(0)), Fraction(2))
    lambda_above_one_breaks_uniform_maximum = endpoint_value > uniform_value

    k, lam = 3, Fraction(1)
    threshold_gap_at_boundary = Fraction(k, k + 1) * (1 - lam)
    return {
        "lambda_below_zero_breaks_coalescence_orientation": negative_lambda_merge_decreases,
        "lambda_above_one_breaks_theorem4_uniform_maximum": lambda_above_one_breaks_uniform_maximum,
        "lambda_one_threshold_gap_is_zero": threshold_gap_at_boundary == 0,
    }


def all_true(value):
    if isinstance(value, dict):
        return all(all_true(item) for item in value.values())
    return value is True


def main():
    identities = symbolic_identities()
    exact = exact_graph_controls()
    threshold = threshold_certificate()
    controls = fail_sensitive_controls()
    verdict = "supports" if all_true(identities) and all_true(controls) and exact["exact_points"] and threshold["strict_cases"] else "failed"
    result = {
        "claim": "Claim 1: Theorem 4 value and minimal graph-independent lambda=1 tightness threshold",
        "source": SOURCE,
        "universal_certificate": {
            "theorem4": "for 0<=lambda<=1, max over the simplex is 1+(lambda-1)/omega",
            "upper_bound": "nonedge coalescence reaches clique support without decreasing g",
            "clique_bound": "r*sum(x_i^2)-1=sum_{i<j}(x_i-x_j)^2>=0 and r<=omega",
            "attainment": "uniform mass on a maximum clique",
            "threshold": "Theorem 2 rounding gives sufficiency; Corollary 2 complete-graph family gives necessity",
        },
        "coefficient_identities": identities,
        "exact_controls": exact,
        "threshold_certificate": threshold,
        "fail_sensitive_controls": controls,
        "verdict": verdict,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if verdict == "supports" else 1


if __name__ == "__main__":
    raise SystemExit(main())
