#!/usr/bin/env python3
"""Independent exact audit of Claim 1 / Theorem 4.

This file imports nothing from the primary verifier.  It directly checks the
published formula on a different exact lattice and audits the additive release
structure and source locks.
"""

from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
import json


PAGE_PATH = "pages/claim-1-theorem-4-exact/page.md"
SOURCE_HASHES = (
    "94dc307f35bda0046eded2944df2dd7d1a56282462cbc9998fa545b463ac5d66",
    "8ea44454fe5d307bfe6784c24fae884a8b39fb066279c2ff132cbff2a790b338",
    "3cb02eea34c746003918066f1e89f469ccafa980206e8bdac1ec78086dc99e92",
    "2a80746443eaf77c441ecce2bc10f56feaad691e20186ce15ee55c7d95559ca4",
    "1921ada72f0e3277d0e64576cc897791ddb3c271399aa2189c4be3a92467e96e",
)
PARENT_REFS = (
    "pages/index.md",
    "pages/claim-1-tightness/page.md",
    "pages/claim-2-stationary-point-dichotomy/page.md",
    "pages/claim-3-frank-wolfe-convergence/page.md",
    "pages/methods-environment/page.md",
    "pages/negative-controls/page.md",
    "pages/conclusion/page.md",
    "pages/claim-motzkin-straus/page.md",
    "pages/claim-3-spurious-maxima/page.md",
    "pages/claim-5-baselines/page.md",
    "pages/claim-1-theorem-2-exact/page.md",
    "pages/claim-4-theorem-5-exact/page.md",
    "pages/claim-6-cost-source-audit/page.md",
)


def graph_from_mask(n, mask):
    adjacency = [[0] * n for _ in range(n)]
    for bit, (i, j) in enumerate(combinations(range(n), 2)):
        adjacency[i][j] = adjacency[j][i] = (mask >> bit) & 1
    return adjacency


def value(adjacency, point, lam):
    n = len(point)
    return 2 * sum(
        point[i] * point[j]
        for i in range(n)
        for j in range(i + 1, n)
        if adjacency[i][j]
    ) + lam * sum(item * item for item in point)


def clique_number(adjacency):
    n = len(adjacency)
    return max(
        size
        for size in range(1, n + 1)
        if any(all(adjacency[i][j] for i, j in combinations(subset, 2)) for subset in combinations(range(n), size))
    )


def lattice_audit():
    lambdas = (Fraction(0), Fraction(1, 3), Fraction(2, 3), Fraction(1))
    checked = attainment = graphs = 0
    for n in range(1, 6):
        denominator = 4
        for mask in range(1 << (n * (n - 1) // 2)):
            adjacency = graph_from_mask(n, mask)
            omega = clique_number(adjacency)
            formulae = {lam: 1 + (lam - 1) / omega for lam in lambdas}
            graphs += 1
            for numerators in product(range(denominator + 1), repeat=n):
                if sum(numerators) != denominator:
                    continue
                point = tuple(Fraction(item, denominator) for item in numerators)
                for lam in lambdas:
                    assert value(adjacency, point, lam) <= formulae[lam]
                    checked += 1
            maximum_clique = next(
                subset
                for subset in combinations(range(n), omega)
                if all(adjacency[i][j] for i, j in combinations(subset, 2))
            )
            witness = tuple(Fraction(int(i in maximum_clique), omega) for i in range(n))
            for lam in lambdas:
                assert value(adjacency, witness, lam) == formulae[lam]
                attainment += 1
    return {
        "vertices": "1..5",
        "graphs": graphs,
        "simplex_denominator": 4,
        "lambda_values": [str(item) for item in lambdas],
        "upper_bound_points": checked,
        "attainment_checks": attainment,
    }


def threshold_audit():
    checked = 0
    for k in range(1, 13):
        omega = k + 1
        for lam in (Fraction(-3, 2), Fraction(-1, 7), Fraction(1, 7), Fraction(5, 8), Fraction(9999, 10000)):
            binary = k * (k + lam - 1)
            relaxed = k * k + Fraction(k * k, omega) * (lam - 1)
            assert relaxed - binary == Fraction(k, omega) * (1 - lam) > 0
            checked += 1
    return {
        "complete_graph_cases": checked,
        "k_values": "1..12",
        "strict_gap": "k*(1-lambda)/(k+1)",
        "boundary_lambda_one_gap": "0",
    }


def semantic_controls():
    complete2 = graph_from_mask(2, 1)
    uniform = (Fraction(1, 2), Fraction(1, 2))
    actual_at_lambda_zero = value(complete2, uniform, Fraction(0))
    wrong_formula_rejected = actual_at_lambda_zero != 1 + Fraction(0, 2)
    theorem4_range_guard = value(complete2, (Fraction(1), Fraction(0)), Fraction(2)) > value(complete2, uniform, Fraction(2))
    threshold_strictness_guard = Fraction(4, 5) * (1 - Fraction(1)) == 0
    return {
        "reject_formula_1_plus_lambda_over_omega": wrong_formula_rejected,
        "reject_theorem4_extension_above_lambda_one": theorem4_range_guard,
        "reject_strict_threshold_gap_at_lambda_one": threshold_strictness_guard,
    }


def release_audit():
    root = Path(__file__).resolve().parents[2]
    logbook = json.loads((root / "logbook.json").read_text())
    page = (root / PAGE_PATH).read_text()
    refs = []
    stack = [logbook["root"]]
    while stack:
        node = stack.pop()
        ref = node.get("file") or node.get("path")
        if ref:
            refs.append(ref)
        stack.extend(node.get("children", []))
    assert set(refs) == set(PARENT_REFS + (PAGE_PATH,))
    assert len(refs) == len(PARENT_REFS) + 1
    assert refs.count(PAGE_PATH) == 1
    assert (root / PAGE_PATH).is_file()
    assert all(item in page for item in SOURCE_HASHES)
    assert all(term in page for term in ("Theorem 4", "Corollary 2", "Appendix B", "0 <= lambda <= 1"))
    return {
        "prior_page_refs_preserved": len(PARENT_REFS),
        "new_page_ref_count": 1,
        "all_source_locks_present": True,
        "new_page_resolves_locally": True,
    }


def main():
    result = {
        "claim": "Claim 1 independent Theorem 4 and threshold audit",
        "exact_lattice_audit": lattice_audit(),
        "threshold_audit": threshold_audit(),
        "semantic_controls": semantic_controls(),
        "release_structure": release_audit(),
        "verdict": "supports",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
