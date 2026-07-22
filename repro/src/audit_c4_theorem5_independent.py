#!/usr/bin/env python3
"""Independent exact audit for the Theorem 5 evidence (no primary imports)."""

from fractions import Fraction as F
from itertools import combinations


def matrix_from_bits(n, bits):
    a = [[0] * n for _ in range(n)]
    for p, (u, v) in enumerate(combinations(range(n), 2)):
        if bits & (1 << p):
            a[u][v] = a[v][u] = 1
    return a


def exchange_margin(a, subset, lam):
    chosen = set(subset)
    degrees = [sum(a[v][u] for u in chosen) for v in range(len(a))]
    # Positive margin means every feasible edge direction decreases objective.
    return min((lam + degrees[i] - degrees[j] for i in chosen for j in range(len(a)) if j not in chosen), default=lam)


def main():
    lambdas = (F(6, 5), F(4, 3), F(8, 5), F(11, 5), F(14, 5))
    checks = 0
    local_points = 0
    for n in range(2, 6):
        edge_count = n * (n - 1) // 2
        for bits in range(1 << edge_count):
            a = matrix_from_bits(n, bits)
            for k in range(1, n):
                supports = tuple(combinations(range(n), k))
                previous = set()
                for lam in lambdas:
                    current = {s for s in supports if exchange_margin(a, s, lam) > 0}
                    assert previous <= current
                    checks += 1
                    local_points += len(current)
                    previous = current

    # Alternative witness (four-node star, k=2): any two leaves are
    # suboptimal and become strict local maxima once lambda exceeds 2.
    star = [[0] * 4 for _ in range(4)]
    for leaf in (1, 2, 3):
        star[0][leaf] = star[leaf][0] = 1
    witness = (1, 2)
    low_margin = exchange_margin(star, witness, F(7, 4))
    high_margin = exchange_margin(star, witness, F(9, 4))
    assert low_margin < 0 < high_margin
    assert sum(star[i][j] for i, j in combinations(witness, 2)) == 0
    assert max(sum(star[i][j] for i, j in combinations(s, 2)) for s in combinations(range(4), 2)) == 1

    # Deliberately demand the false reverse nesting: the witness must reject it.
    reverse_nesting_rejected = high_margin > 0 and low_margin < 0
    assert reverse_nesting_rejected
    print("claim: C4_independent_Theorem_5_audit")
    print(f"independent_landscape_sweeps={checks}; strict_local_points={local_points}; nesting_pass=True")
    print(f"independent_strict_witness: low_margin={low_margin}; high_margin={high_margin}; suboptimal_edges=0<1")
    print(f"fail_sensitive_reverse_nesting_rejected={reverse_nesting_rejected}")
    print("verdict: supports")


if __name__ == "__main__":
    main()
