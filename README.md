# Densest k-Subgraph Penalty Relaxation: Landscape & Finite-Step Convergence — ICML 2026 Reproduction

Reproduction of **Lu, Sidiropoulos & Konar, "On Densest k-Subgraph Mining and
Diagonal Loading: Optimization Landscape and Finite-Step Exact Convergence
Analysis"** (arXiv [2410.07388](https://arxiv.org/abs/2410.07388), ICML 2026,
OpenReview [`VQt4w3lElX`](https://openreview.net/forum?id=VQt4w3lElX)).

The paper analyzes the penalty-based non-convex relaxation of Densest k-Subgraph
(DkS) introduced by Lu et al. (AAAI 2025):

```
max  g(x) = ½ xᵀ(A + λI)x   s.t.  x ∈ [0,1]ⁿ,  Σ xᵢ = k          (relaxation (3))
```
where `A` is the graph adjacency and λ the diagonal-loading penalty. It proves
the relaxation is **tight**, the landscape has a **strict stationary-point
dichotomy**, and a **saddle-escaping Frank-Wolfe** converges in **finite steps**.

## Claims reproduced

| # | Claim | Status |
|---|---|---|
| **C1** | **Tightness (Thm 2.3):** for λ ≥ 1 the relaxation's global max equals the combinatorial DkS optimum. | ✅ Verified (exact) |
| **C2** | **Dichotomy (Thm 3.7/3.10):** for λ > 1 non-integral, every stationary point is either an integral local max or a non-integral strict saddle. | ✅ Verified (exact) |
| **C3** | **Frank-Wolfe (§4):** saddle-escaping FW reaches an integral local maximizer in finite steps. | ✅ Verified |

## Method

The key technique is **exact enumeration of all KKT stationary points**
(Theorem 3.4): for each partition `(S0, S1, Sf)` of `[n]` the free coordinates
solve a linear system, solved in closed form. This gives the relaxation's exact
global maximum and *all* stationary points, so C1/C2 are verified rigorously,
not just numerically.

* `repro/src/dks.py` — problems (1)/(2)/(3), brute-force combinatorial DkS, graphs.
* `repro/src/landscape.py` — exact KKT stationary-point enumeration, global max,
  Hessian-curvature classification.
* `repro/src/frankwolfe.py` — saddle-escaping FW (exact 1-D line search + ascent escape).
* `repro/src/run_claims.py` — orchestrator → `outputs/`.
* `repro/tests/test_dks.py` — 24 pytest tests.

## How to run

```bash
uv venv --python 3.12 .venv && source .venv/bin/activate
uv pip install numpy scipy networkx pytest
python -m pytest repro/tests/test_dks.py -q          # 24 tests
python repro/src/run_claims.py                       # writes outputs/
```

## Headline results (CPU, exact)

**C1 — tightness.** Across 15 graphs × k∈{3,4,5} × λ∈{1,1.5,2,3}: **180/180**
cases tight (gap = 0.0). For λ∈{0.1,0.5}: **30 failures** found (relaxation
strictly exceeds combinatorial), confirming **λ ≥ 1 is necessary** (Thm 2.1).

**C2 — dichotomy (λ=1.5).** **8,605 stationary points** enumerated exactly;
**every one** classifies as integral-local-max (853) or non-integral-strict-saddle
(7,752); **0** other. Min ascent curvature at saddles **0.625 > 0**.

**C3 — Frank-Wolfe.** **144/144** random-init runs reach an integral local
maximizer in a finite number of steps (median few).

## Scope & cost

| | This reproduction | Full replication |
|---|---|---|
| Scope | All 3 claims; exact KKT enumeration, 15 graphs, k∈{3,4,5}, λ-grid | same |
| Hardware | 4 vCPU (CPU only) | any CPU |
| Time | ~1 min evidence, 28 s tests | — |
| Cost | $0 | — |
| Outcome | All three claims verified exactly | — |
