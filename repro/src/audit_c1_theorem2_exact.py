#!/usr/bin/env python3
"""Independent exact audit of Claim 1 for arXiv:2410.07388.

This auditor does not import the primary verifier.  It directly compares the
best binary objective with every point on several exact rational lattices for
all 64 simple graphs on four vertices.  It also requires the expected additive
logbook node and a strict lambda<1 counterexample.
"""

from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
import json


SOURCE_SHA256 = "94dc307f35bda0046eded2944df2dd7d1a56282462cbc9998fa545b463ac5d66"
PAGE_PATH = "pages/claim-1-theorem-2-exact/page.md"
PARENT_REFS = [
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
]


def graph_from_mask(n, mask):
    matrix = [[0] * n for _ in range(n)]
    for bit, (i, j) in enumerate(combinations(range(n), 2)):
        matrix[i][j] = matrix[j][i] = (mask >> bit) & 1
    return matrix


def objective(adjacency, x, lam):
    return sum(
        x[i] * (Fraction(adjacency[i][j]) + (lam if i == j else 0)) * x[j]
        for i in range(len(x))
        for j in range(len(x))
    )


def binary_points(n, k):
    for selected in combinations(range(n), k):
        chosen = set(selected)
        yield tuple(Fraction(int(i in chosen)) for i in range(n))


def lattice_points(n, k, denominator):
    for numerators in product(range(denominator + 1), repeat=n):
        if sum(numerators) == k * denominator:
            yield tuple(Fraction(value, denominator) for value in numerators)


def exhaustive_value_audit():
    n = 4
    checked = 0
    for mask in range(1 << (n * (n - 1) // 2)):
        adjacency = graph_from_mask(n, mask)
        for k in range(1, n):
            for lam in (Fraction(1), Fraction(3, 2), Fraction(2)):
                binary_max = max(objective(adjacency, x, lam) for x in binary_points(n, k))
                for denominator in (2, 3, 4):
                    for x in lattice_points(n, k, denominator):
                        assert objective(adjacency, x, lam) <= binary_max
                        checked += 1
    return {"graphs": 64, "lambda_values": ["1", "3/2", "2"], "denominators": [2, 3, 4], "points_checked": checked}


def negative_control():
    n, k = 4, 2
    complete = graph_from_mask(n, (1 << (n * (n - 1) // 2)) - 1)
    lam = Fraction(1, 2)
    fractional = (Fraction(1, 2),) * n
    relaxed_value = objective(complete, fractional, lam)
    binary_value = max(objective(complete, x, lam) for x in binary_points(n, k))
    assert relaxed_value > binary_value
    return {"graph": "K4", "k": k, "lambda": str(lam), "fractional_value": str(relaxed_value), "binary_max": str(binary_value), "strict_gap": str(relaxed_value - binary_value)}


def release_structure_audit():
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
    # Stack traversal reverses child order.  This exact set is the live parent
    # tree; parent files are supplied by snapshot overlay at publication time.
    assert set(refs) == set(PARENT_REFS + [PAGE_PATH])
    assert len(refs) == len(PARENT_REFS) + 1
    assert (root / PAGE_PATH).is_file()
    assert refs.count(PAGE_PATH) == 1
    assert SOURCE_SHA256 in page
    assert "Theorem 2" in page and "Corollary 1" in page and "Appendix A" in page
    return {
        "reachable_refs_after_overlay": len(refs),
        "parent_refs_preserved": len(PARENT_REFS),
        "new_page_ref_count": 1,
        "new_page_resolves_locally": True,
    }


def main():
    exact = exhaustive_value_audit()
    control = negative_control()
    structure = release_structure_audit()
    result = {
        "claim": "Claim 1 independent exact value audit",
        "source_html_sha256": SOURCE_SHA256,
        "exact_lattice_audit": exact,
        "negative_control": control,
        "release_structure": structure,
        "verdict": "supports",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
