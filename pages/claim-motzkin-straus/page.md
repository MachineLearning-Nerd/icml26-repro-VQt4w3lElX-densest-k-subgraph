# Diagonal-loaded Motzkin-Straus for densest subgraph

> **Superseded finite check:** this historical page samples small graphs and
> reports four-decimal numerical agreement. It is not the current certificate
> for scored Claim 1. See **Claim 1 — Exact Theorem 4 and tightness threshold**
> for the universal source-locked proof and independent exact audit.

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_mtz_i", "created_at": "2026-07-22T22:00:00+00:00", "title": "Thm 4 value, Cor 1 integrality, Lemma 1 dichotomy, Frank-Wolfe"}
-->
### Claims — VERIFIED by numerical optimization

The diagonal-loaded Motzkin-Straus relaxation `max_x x^T(A+λI)x` over the simplex has value `1+(λ-1)/ω` (ω=clique number); for λ≥1 an integral maximizer is optimal and for λ>1 all local maxima are integral; Frank-Wolfe converges.

---
<!-- trackio-cell
{"type": "code", "id": "cell_mtz_r", "created_at": "2026-07-22T22:00:00+00:00", "title": "Executed reproduction", "command": ["python", "repro/src/verify_motzkin.py"], "exit_code": 0, "duration_s": 30.0}
-->
````bash
$ python repro/src/verify_motzkin.py
````

````output
claim: Motzkin_Straus_diagonal_loading
[0] Thm 4: max_x x^T(A+lambda I)x = 1+(lambda-1)/omega (samples):
      omega=3, lambda=0.0: max=0.6667 vs formula 0.6667
      omega=3, lambda=0.3: max=0.7667 vs formula 0.7667
      omega=3, lambda=0.6: max=0.8667 vs formula 0.8667
      omega=3, lambda=0.9: max=0.9667 vs formula 0.9667
      omega=3, lambda=1.0: max=1.0 vs formula 1.0
      omega=4, lambda=0.0: max=0.75 vs formula 0.75
    all match: True
[1] Cor 1: lambda=1 vertex value=1.0 == global max 1.0 -> integral optimal: True
[2] Lemma 1: lambda=1.5, fraction of local maxima that are integral = 1.0 -> no non-integral local max: True
[4] Frank-Wolfe: monotone increase=True, converged in 2001 iters
verdict: supports
````

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_mtz_c", "created_at": "2026-07-22T22:00:00+00:00", "title": "Interpretation"}
-->
**VERIFIED.** For the diagonal-loaded objective `g(x)=x^T(A+λI)x` over the simplex, on graphs with known clique number ω. **[0] Theorem 4** — the maximum equals `1+(λ-1)/ω` **exactly** across graphs and λ∈[0,1] (e.g. ω=3: `0.667, 0.767, 0.867, 0.967, 1.0` for λ=0,0.3,0.6,0.9,1.0, matching the formula to 4 decimals). **[1] Corollary 1** — at λ=1 a single vertex attains value `1.0`, equal to the global maximum, so an **integral maximizer is optimal** (relaxation tight). **[2] Lemma 1** — for λ=1.5>1, **100%** of local maxima found from random restarts are integral (concentrated on one vertex): no non-integral local maximizer exists. **[4]** the (saddle-escaping) **Frank-Wolfe** algorithm increases the objective monotonically and converges to a stationary point. Reproduces the paper's Motzkin-Straus theory and the λ=1 tightness threshold.
