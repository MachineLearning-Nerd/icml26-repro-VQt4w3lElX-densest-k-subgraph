#!/usr/bin/env python3
"""Exact certificate for Claim 1 / Theorem 2 of arXiv:2410.07388.

The proof is algebraic, not an inference from a finite benchmark.  A tiny
polynomial engine checks the two exact objective-gain identities (edge and
non-edge), and Fraction arithmetic checks the rounding invariant on a complete
finite control suite.  No network, floating point, or third-party package is
used.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
import json


SOURCE = {
    "url": "https://ar5iv.labs.arxiv.org/html/2410.07388",
    "html_sha256": "94dc307f35bda0046eded2944df2dd7d1a56282462cbc9998fa545b463ac5d66",
    "scope": "Theorem 2, Corollary 1, and Appendix A (equations 27-28)",
    "theorem2_raw_sha256": "0b520a18d09fa90220483b3335e9fe2b3e1be43397da65ceaaa16cec595e59a5",
    "corollary1_raw_sha256": "026112ac91d8271416fe9e97f266936e3dd9495387a88dce39d0062869b97e21",
    "appendix_a_raw_sha256": "933ee6fbcf6e9c16841b45924f212a125580b2217946024ba034a88103fcc974",
}


class Poly:
    """Sparse exact polynomial in (xi, xj, ui, uj, delta, lambda)."""

    N = 6

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
        terms = dict(self.terms)
        for monomial, coefficient in other.terms.items():
            terms[monomial] = terms.get(monomial, Fraction(0)) + coefficient
            if not terms[monomial]:
                del terms[monomial]
        return Poly(terms)

    __radd__ = __add__

    def __neg__(self):
        return Poly({m: -c for m, c in self.terms.items()})

    def __sub__(self, other):
        return self + (-other if isinstance(other, Poly) else -Fraction(other))

    def __rsub__(self, other):
        return Poly.const(other) - self

    def __mul__(self, other):
        other = other if isinstance(other, Poly) else Poly.const(other)
        terms = {}
        for left_m, left_c in self.terms.items():
            for right_m, right_c in other.terms.items():
                monomial = tuple(a + b for a, b in zip(left_m, right_m))
                terms[monomial] = terms.get(monomial, Fraction(0)) + left_c * right_c
        return Poly(terms)

    __rmul__ = __mul__

    def __pow__(self, power):
        assert power == 2
        return self * self

    def __eq__(self, other):
        other = other if isinstance(other, Poly) else Poly.const(other)
        return self.terms == other.terms


XI, XJ, UI, UJ, DELTA, LAM = (Poly.var(i) for i in range(Poly.N))


def symbolic_gain_identity(adjacency: int) -> bool:
    """Prove Appendix-A equation (27) or (28) coefficient by coefficient."""
    assert adjacency in (0, 1)

    def changing_objective(xi, xj):
        # ui and uj exclude the possible i-j edge; all unchanged terms cancel.
        return 2 * xi * UI + 2 * xj * UJ + 2 * adjacency * xi * xj + LAM * (xi**2 + xj**2)

    expanded = changing_objective(XI + DELTA, XJ - DELTA) - changing_objective(XI, XJ)
    score_i = LAM * XI + UI + adjacency * XJ
    score_j = LAM * XJ + UJ + adjacency * XI
    paper_form = 2 * DELTA * (score_i - score_j) + 2 * (LAM - adjacency) * DELTA**2
    return expanded == paper_form


def objective(adjacency, x, lam):
    n = len(x)
    return sum(
        x[i] * (Fraction(adjacency[i][j]) + (lam if i == j else 0)) * x[j]
        for i in range(n)
        for j in range(n)
    )


def round_exact(adjacency, start, lam):
    """Execute exactly the pairwise rounding update in Appendix A."""
    x = list(start)
    n = len(x)
    trace = []
    while any(value.denominator != 1 for value in x):
        fractional = [i for i, value in enumerate(x) if value.denominator != 1]
        assert len(fractional) >= 2  # integer sum rules out exactly one fractional coordinate
        scores = [lam * x[i] + sum(Fraction(adjacency[i][j]) * x[j] for j in range(n)) for i in range(n)]
        i = max(fractional, key=lambda index: (scores[index], -index))
        j = min((index for index in fractional if index != i), key=lambda index: (scores[index], index))
        assert scores[i] >= scores[j]
        delta = min(x[j], 1 - x[i])
        before = objective(adjacency, x, lam)
        old_fractional = len(fractional)
        x[i] += delta
        x[j] -= delta
        after = objective(adjacency, x, lam)
        assert all(0 <= value <= 1 for value in x)
        assert sum(x) == sum(start)
        assert after >= before
        assert sum(value.denominator != 1 for value in x) < old_fractional
        trace.append({"i": i, "j": j, "delta": str(delta), "gain": str(after - before)})
        assert len(trace) <= n
    return tuple(x), trace


def graph_from_mask(n, mask):
    matrix = [[0] * n for _ in range(n)]
    for bit, (i, j) in enumerate(combinations(range(n), 2)):
        matrix[i][j] = matrix[j][i] = (mask >> bit) & 1
    return matrix


def exact_rounding_controls():
    """Exercise all 4-vertex graphs and a rational feasibility lattice."""
    n, denominator = 4, 3
    cases = steps = 0
    for mask in range(1 << (n * (n - 1) // 2)):
        adjacency = graph_from_mask(n, mask)
        for k in range(1, n):
            for numerators in product(range(denominator + 1), repeat=n):
                if sum(numerators) != k * denominator:
                    continue
                x = tuple(Fraction(value, denominator) for value in numerators)
                for lam in (Fraction(1), Fraction(3, 2), Fraction(2)):
                    rounded, trace = round_exact(adjacency, x, lam)
                    assert all(value.denominator == 1 for value in rounded)
                    assert objective(adjacency, rounded, lam) >= objective(adjacency, x, lam)
                    cases += 1
                    steps += len(trace)
    return {"graphs": 64, "denominator": denominator, "cases": cases, "rounding_steps": steps}


def main():
    identities = {"non_edge_equation_27": symbolic_gain_identity(0), "edge_equation_28": symbolic_gain_identity(1)}
    controls = exact_rounding_controls()
    result = {
        "claim": "Claim 1: relaxation and combinatorial global maximum values coincide for lambda >= 1",
        "source": SOURCE,
        "proof": {
            "symbolic_identities": identities,
            "orientation_term_nonnegative": True,
            "curvature_term_nonnegative": "lambda-a_ij >= 0 for lambda>=1 and a_ij in {0,1}",
            "variant": "number of fractional coordinates strictly decreases",
            "termination_bound": "at most n pairwise updates",
            "reverse_inequality": "every binary feasible point is continuously feasible",
            "universal_conclusion": "every relaxed feasible point rounds to a no-worse binary feasible point",
        },
        "exact_controls": controls,
        "verdict": "supports" if all(identities.values()) and controls["cases"] > 0 else "failed",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verdict"] == "supports" else 1


if __name__ == "__main__":
    raise SystemExit(main())
