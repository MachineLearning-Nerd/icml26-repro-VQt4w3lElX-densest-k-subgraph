# Methods & environment


---
<!-- trackio-cell
{"type": "code", "id": "cell_42c1638daeea", "created_at": "2026-07-17T05:15:49+00:00", "title": "Pytest suite (24 tests)", "command": ["python", "-m", "pytest", "repro/tests/test_dks.py", "-q"], "exit_code": 0, "duration_s": 26.625}
-->
````bash
$ python -m pytest repro/tests/test_dks.py -q
````

exit 0 · 26.6s


````python title=test_dks.py
"""Formal pytest suite: DkS penalty relaxation landscape (Lu et al. 2410.07388).
Run: pytest -q repro/tests"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
import pytest
from dks import random_graph, planted_dense_graph, combinatorial_opt, g, edges
from landscape import relaxation_global_max, classify, enumerate_stationary
from frankwolfe import frank_wolfe, random_feasible, lmo


# -- Claim 1 / Theorem 2.3: lambda >= 1 tight; lambda < 1 can fail -----------
@pytest.mark.parametrize("seed", range(5))
def test_c1_tight_lambda_ge_1(seed):
    A = random_graph(7, 0.5, seed=seed)
    for k in (3, 4):
        fmax, _ = combinatorial_opt(A, k)
        for lam in (1.0, 1.5, 2.0, 3.0):
            rmax, _, _ = relaxation_global_max(A, lam, k)
            assert abs(rmax - (fmax + lam * k / 2)) < 1e-6, (seed, k, lam)


def test_c1_lambda_lt_1_can_fail():
    """Theorem 2.1 (necessity): some instance with lambda<1 is NOT tight."""
    found_failure = False
    for seed in range(20):
        A = random_graph(8, 0.5, seed=seed)
        for k in (3, 4, 5):
            fmax, _ = combinatorial_opt(A, k)
            for lam in (0.1, 0.5):
                rmax, _, _ = relaxation_global_max(A, lam, k)
                if rmax > fmax + lam * k / 2 + 1e-6:
                    found_failure = True
    assert found_failure


# -- Claim 2 / Theorems 3.6/3.7/3.10: dichotomy at lambda>1 non-integral ------
@pytest.mark.parametrize("seed", range(5))
def test_c2_dichotomy(seed):
    A = random_graph(7, 0.5, seed=seed)
    lam = 1.5
    for k in (3, 4):
        _, _, pts = relaxation_global_max(A, lam, k)
        assert len(pts) > 0
        for p in pts:
            cls, asc = classify(p, A, lam)
            assert cls in ("integral_local_max", "nonintegral_strict_saddle"), (seed, k, cls)
            if cls == "nonintegral_strict_saddle":
                assert asc > 0                  # explicit positive curvature


def test_c2_saddles_have_ascent():
    """Every non-integral stationary point has a positive-curvature direction."""
    A = planted_dense_graph(7, 3, 1.0, 0.3, seed=2)
    _, _, pts = relaxation_global_max(A, 1.5, 3)
    nonint = [p for p in pts if not p["integral"]]
    assert len(nonint) > 0
    for p in nonint:
        cls, asc = classify(p, A, 1.5)
        assert asc > 0


# -- Claim 3 / Section 4: saddle-escaping FW -> integral local max, finite ----
@pytest.mark.parametrize("seed", range(10))
def test_c3_frankwolfe_converges(seed):
    A = random_graph(7, 0.5, seed=seed)
    lam = 1.5
    rng = np.random.default_rng(seed)
    for k in (3, 4):
        for _ in range(6):
            x0 = random_feasible(A.shape[0], k, rng)
            xf, niter, integral, localmax = frank_wolfe(A, lam, k, x0)
            assert integral and localmax, (seed, k, niter)
            assert niter < 2000


# -- Sanity: combinatorial_opt matches an independent edge count --------------
def test_combinatorial_opt_correct():
    A = planted_dense_graph(6, 3, 1.0, 0.0, seed=0)  # 3-clique + isolates
    v, S = combinatorial_opt(A, 3)
    assert v == 3 and edges(A, S) == 3              # the clique has 3 edges


# -- Sanity: relaxation max >= combinatorial always (binary subset of [0,1]) --
def test_relaxation_bounds_combinatorial():
    A = random_graph(7, 0.6, seed=3)
    fmax, _ = combinatorial_opt(A, 3)
    for lam in (0.5, 1.5):
        rmax, _, _ = relaxation_global_max(A, lam, 3)
        assert rmax >= fmax + lam * 3 / 2 - 1e-9

````


````output
........................                                                 [100%]
24 passed in 26.38s

````


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_974aea2f1703", "created_at": "2026-07-17T05:17:58+00:00", "title": "Method & environment"}
-->
**Paper:** Lu, Sidiropoulos & Konar, "On Densest k-Subgraph Mining and Diagonal Loading: Optimization Landscape and Finite-Step Exact Convergence" (arXiv 2410.07388, ICML 2026, VQt4w3lElX). Clean-room from the PDF (no official code).

**Environment:** Python 3.12, numpy/scipy/networkx; CPU only (~1 min evidence, 28 s tests).

**Implementation (repro/src):**
- `dks.py` — DkS problems (1)/(2)/(3), brute-force combinatorial_opt, graph generators.
- `landscape.py` — **exact enumeration of all KKT stationary points** (Theorem 3.4) over 3^n index partitions; global-max computation; Hessian-curvature classification.
- `frankwolfe.py` — saddle-escaping FW with exact 1-D line search + Hessian-ascent escape.
- `run_claims.py` — orchestrator → outputs/*.csv + summary.json.

**Key technique:** the global maximum of the non-convex relaxation (3) and *all* its stationary points are obtained **exactly** by enumerating the KKT partition (S0,S1,Sf) and solving the resulting linear system per face — so C1/C2 are verified rigorously, not just numerically.

24/24 pytest tests pass: C1 tightness (5 seeds × λ-grid) + λ<1 necessity, C2 dichotomy (5 seeds) + saddle-ascent, C3 FW convergence (10 seeds × 12 starts), combinatorial/bound sanity.
