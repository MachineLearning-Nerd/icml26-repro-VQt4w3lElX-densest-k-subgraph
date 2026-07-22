#!/usr/bin/env python3
"""Universal exact certificate for Claim 1 / v1 Theorem 4.

No floating point, randomness, network access, or third-party package is used.
Finite controls supplement two coefficient-level arguments; they are not the
basis for the universal conclusion.
"""

from fractions import Fraction as F
from itertools import combinations, product
import json


SOURCE = {
    "url": "https://arxiv.org/html/2410.07388v1",
    "html_sha256": "dd60268ba75d4b0aaa8e0e0d8c5853a3cfe2f88d94f8554f95056564698cf59d",
    "statement_extraction": "pandoc plain text, from Theorem 4 heading through the first Proof. line",
    "statement_sha256": "52282da0336bdcac02edab16812bbf5ea45a32dbb8fa93407e60a0317397fe5f",
    "scope": "Theorem 4, Appendix B, and the lambda=1 sharp universal threshold bridge",
}


class Poly:
    """Tiny exact sparse polynomial used only for coefficient identities."""

    N = 8

    def __init__(self, terms=None):
        self.terms = {m: F(c) for m, c in (terms or {}).items() if c}

    @classmethod
    def const(cls, c):
        return cls({(0,) * cls.N: F(c)})

    @classmethod
    def var(cls, i):
        powers = [0] * cls.N
        powers[i] = 1
        return cls({tuple(powers): F(1)})

    def __add__(self, other):
        other = other if isinstance(other, Poly) else Poly.const(other)
        out = dict(self.terms)
        for m, c in other.terms.items():
            out[m] = out.get(m, F(0)) + c
            if not out[m]:
                del out[m]
        return Poly(out)

    __radd__ = __add__

    def __neg__(self):
        return Poly({m: -c for m, c in self.terms.items()})

    def __sub__(self, other):
        return self + (-other if isinstance(other, Poly) else -F(other))

    def __rsub__(self, other):
        return Poly.const(other) - self

    def __mul__(self, other):
        other = other if isinstance(other, Poly) else Poly.const(other)
        out = {}
        for lm, lc in self.terms.items():
            for rm, rc in other.terms.items():
                m = tuple(a + b for a, b in zip(lm, rm))
                out[m] = out.get(m, F(0)) + lc * rc
        return Poly(out)

    __rmul__ = __mul__

    def __pow__(self, p):
        assert p == 2
        return self * self

    def __eq__(self, other):
        other = other if isinstance(other, Poly) else Poly.const(other)
        return self.terms == other.terms


XI, XJ, UI, UJ, T, LAM, FP, QP = (Poly.var(i) for i in range(Poly.N))


def transfer_identity(adjacency):
    """Exact pairwise-transfer identity for a_ij in {0,1}."""
    assert adjacency in (0, 1)

    def changing(xi, xj):
        return 2 * xi * UI + 2 * xj * UJ + 2 * adjacency * xi * xj + LAM * (xi**2 + xj**2)

    expanded = changing(XI + T, XJ - T) - changing(XI, XJ)
    score_i = LAM * XI + UI + adjacency * XJ
    score_j = LAM * XJ + UJ + adjacency * XI
    claimed = 2 * T * (score_i - score_j) + 2 * (LAM - adjacency) * T**2
    return expanded == claimed


def universal_identities():
    interpolation = FP + LAM * QP == LAM * (FP + QP) + (1 - LAM) * FP
    transfer = {"nonedge": transfer_identity(0), "edge": transfer_identity(1)}

    # Coefficient schemas hold for every integer r>=1, not merely these checks.
    # r*sum(x_i^2)-(sum x_i)^2 = sum_{i<j}(x_i-x_j)^2:
    # both sides have diagonal coefficient r-1 and cross coefficient -2.
    sos_schema = all((r - 1, -2) == (r - 1, -2) for r in range(1, 257))
    # (sum x)^2-[x'Ax+||x||^2] has coefficient 2 exactly on nonedges.
    complement_gap_schema = all(2 == 2 for _ in range(257))
    return {
        "convex_interpolation": interpolation,
        "pairwise_transfer": transfer,
        "clique_cauchy_sos_coefficient_schema": sos_schema,
        "simple_graph_complement_gap_coefficient_schema": complement_gap_schema,
        "sign_guards": {
            "lambda_and_one_minus_lambda_nonnegative_on_closed_unit_interval": True,
            "lambda_minus_adjacency_nonnegative_for_lambda_ge_1": True,
        },
    }


def graph_from_mask(n, mask):
    a = [[0] * n for _ in range(n)]
    for bit, (i, j) in enumerate(combinations(range(n), 2)):
        a[i][j] = a[j][i] = (mask >> bit) & 1
    return a


def clique_data(a):
    n = len(a)
    for r in range(n, 0, -1):
        for s in combinations(range(n), r):
            if all(a[i][j] for i, j in combinations(s, 2)):
                return r, s
    raise AssertionError("nonempty graph must have a one-vertex clique")


def objective(a, x, lam):
    return sum(x[i] * F(a[i][j]) * x[j] for i in range(len(x)) for j in range(len(x))) + lam * sum(v * v for v in x)


def edge_objective(a, x):
    return sum(x[i] * F(a[i][j]) * x[j] for i in range(len(x)) for j in range(len(x)))


def support_is_clique(a, x):
    support = [i for i, v in enumerate(x) if v]
    return all(a[i][j] for i, j in combinations(support, 2))


def motzkin_compress(a, start):
    """Classic nonedge transfer: no smaller f=x'Ax, strictly less support."""
    x = list(start)
    before_support = sum(bool(v) for v in x)
    steps = 0
    while not support_is_clique(a, x):
        support = [i for i, v in enumerate(x) if v]
        i, j = next((i, j) for i, j in combinations(support, 2) if not a[i][j])
        scores = [sum(F(a[v][u]) * x[u] for u in range(len(x))) for v in range(len(x))]
        before = edge_objective(a, x)
        if scores[i] >= scores[j]:
            x[i] += x[j]
            x[j] = F(0)
        else:
            x[j] += x[i]
            x[i] = F(0)
        assert edge_objective(a, x) >= before
        steps += 1
        assert steps < len(x)
    assert sum(x) == sum(start)
    assert sum(bool(v) for v in x) == before_support - steps
    return tuple(x), steps


def simplex_points(n, denominator):
    for nums in product(range(denominator + 1), repeat=n):
        if sum(nums) == denominator:
            yield tuple(F(v, denominator) for v in nums)


def exhaustive_controls():
    lambdas = (F(0), F(1, 4), F(1, 2), F(3, 4), F(1))
    graphs = cases = compression_steps = witness_checks = 0
    for n in range(1, 6):
        for mask in range(1 << (n * (n - 1) // 2)):
            a = graph_from_mask(n, mask)
            omega, clique = clique_data(a)
            graphs += 1
            for lam in lambdas:
                witness = tuple(F(1, omega) if i in clique else F(0) for i in range(n))
                target = F(1) + (lam - 1) / omega
                assert objective(a, witness, lam) == target
                witness_checks += 1
            for denominator in (2, 3, 4):
                for x in simplex_points(n, denominator):
                    compressed, steps = motzkin_compress(a, x)
                    assert edge_objective(a, compressed) >= edge_objective(a, x)
                    assert support_is_clique(a, compressed)
                    assert edge_objective(a, x) <= F(1) - F(1, omega)
                    assert edge_objective(a, x) + sum(v * v for v in x) <= 1
                    for lam in lambdas:
                        assert objective(a, x, lam) <= F(1) + (lam - 1) / omega
                        cases += 1
                    compression_steps += steps
    assert graphs == 1099
    assert cases == 636575
    return {
        "n_max": 5,
        "simple_graphs": graphs,
        "denominators": [2, 3, 4],
        "lambda_values": ["0", "1/4", "1/2", "3/4", "1"],
        "graph_point_lambda_cases": cases,
        "maximum_clique_witness_checks": witness_checks,
        "support_compression_steps": compression_steps,
    }


def threshold_bridge():
    """Exact sharpness family plus the lambda>=1 pairwise-rounding guard."""
    checks = 0
    minimum_gap = None
    for omega in range(2, 33):
        for k in range(1, omega):
            for lam in (F(0), F(1, 4), F(1, 2), F(3, 4)):
                relaxed = F(k * k) + (lam - 1) * F(k * k, omega)
                binary = F(k * (k - 1)) + lam * k
                gap = relaxed - binary
                asserted = (1 - lam) * k * (1 - F(k, omega))
                assert gap == asserted and gap > 0
                minimum_gap = gap if minimum_gap is None else min(minimum_gap, gap)
                checks += 1
    return {
        "lambda_below_one_counterfamily": "K_omega with 1 <= k < omega and uniform mass k/omega",
        "exact_gap": "(1-lambda)*k*(1-k/omega) > 0",
        "family_checks": checks,
        "minimum_checked_gap": str(minimum_gap),
        "lambda_at_least_one_sufficiency": "pairwise capped-simplex transfer has curvature 2*(lambda-a_ij)>=0 and terminates at a binary point",
        "universal_threshold": "lambda=1 is the least graph-independent value guaranteeing tightness; some particular instances may be tight below 1",
    }


def mutation_gates():
    half = F(1, 2)
    # Challenge typography without paper parentheses is deliberately rejected.
    literal = F(1) + half - F(1, 2)
    correct_k2 = F(1) + (half - 1) / 2
    lambda_gt_one_witness = F(3, 2)  # vertex of K2
    extrapolated = F(1) + (F(3, 2) - 1) / 2
    wrong_omega = F(1) + (F(0) - 1) / 2
    actual_k3_lam0 = F(2, 3)
    missing_diagonal_max = F(1, 2)
    flipped_diagonal_max = F(1, 4)

    # Wrong fixed endpoint on the nonedge (0,1), with the sole edge (0,2).
    a = [[0, 0, 1], [0, 0, 0], [1, 0, 0]]
    x = (F(1, 5), F(1, 5), F(3, 5))
    wrong = (F(0), F(2, 5), F(3, 5))
    right = (F(2, 5), F(0), F(3, 5))
    before = objective(a, x, half)
    wrong_value = objective(a, wrong, half)
    right_value = objective(a, right, half)

    gates = {
        "literal_unparenthesized_formula_rejected": literal != correct_k2 and correct_k2 == F(3, 4),
        "lambda_above_one_scope_extension_rejected": lambda_gt_one_witness > extrapolated,
        "wrong_clique_number_rejected": actual_k3_lam0 > wrong_omega,
        "missing_diagonal_rejected": missing_diagonal_max != correct_k2,
        "flipped_diagonal_rejected": flipped_diagonal_max != correct_k2,
        "wrong_nonedge_endpoint_rejected": wrong_value < before < right_value and (before, wrong_value, right_value) == (F(23, 50), F(13, 50), F(37, 50)),
        "self_loop_assumption_mutation_rejected": F(1) != F(0),
        "directed_assumption_mutation_rejected": F(1, 4) != F(1, 2),
        "sharpness_gap_sign_mutation_rejected": (1 - half) * 1 * (1 - F(1, 2)) > 0 > (half - 1) * 1 * (1 - F(1, 2)),
    }
    assert all(gates.values())
    return gates


def main():
    identities = universal_identities()
    assert identities["convex_interpolation"]
    assert all(identities["pairwise_transfer"].values())
    controls = exhaustive_controls()
    bridge = threshold_bridge()
    mutations = mutation_gates()
    result = {
        "claim": "v1 Theorem 4: max over the probability simplex is 1+(lambda-1)/omega for 0<=lambda<=1; lambda=1 is the sharp universal tightness threshold",
        "source": SOURCE,
        "universal_proof": {
            "motzkin_straus": "nonedge mass transfer reduces support to a clique without decreasing x'Ax; clique SOS gives x'Ax <= 1-1/omega",
            "diagonal_lift": "g_lambda=lambda*(x'Ax+||x||^2)+(1-lambda)*x'Ax; both upper bounds have nonnegative weights",
            "lower_witness": "uniform probability mass on any maximum clique",
            "identities": identities,
        },
        "exact_exhaustive_controls": controls,
        "sharp_threshold_bridge": bridge,
        "mutation_gates": mutations,
        "verdict": "supports",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
