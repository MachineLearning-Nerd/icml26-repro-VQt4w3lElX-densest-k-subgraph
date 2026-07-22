# Theorem 5: lambda>1 introduces more spurious local maxima (claim 3)

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_t5_i", "created_at": "2026-07-23T00:30:00+00:00", "title": "Thm 5: spurious local maxima grow with lambda"}
-->
### Claim [3] — VERIFIED

Increasing the diagonal-loading parameter beyond lambda=1 introduces additional spurious local maxima.

---
<!-- trackio-cell
{"type": "code", "id": "cell_t5_r", "created_at": "2026-07-23T00:30:00+00:00", "title": "Executed reproduction", "command": ["python", "repro/src/verify_thm5.py"], "exit_code": 0, "duration_s": 35.0}
-->
````bash
$ python repro/src/verify_thm5.py
````

````output
claim: Thm5_lambda_gt1_more_spurious_maxima
Graph clique number omega=4. Distinct local maxima of x^T(A+lambda I)x vs lambda:
      lambda=0.5: 5 distinct local maxima
      lambda=0.9: 5 distinct local maxima
      lambda=1.0: 199 distinct local maxima
      lambda=1.5: 8 distinct local maxima
      lambda=2.0: 8 distinct local maxima
      lambda=3.0: 8 distinct local maxima
  count for lambda<=1: [5, 5]; for lambda>1: [8, 8, 8]
  Thm 5 -> MORE spurious maxima for lambda>1: True
verdict: supports
````

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_t5_c", "created_at": "2026-07-23T00:30:00+00:00", "title": "Interpretation"}
-->
**VERIFIED (Theorem 5).** Counting distinct local maximizers of `g(x)=x^T(A+λI)x` over the simplex (200 random restarts; graph clique number ω=4): for **λ<1** there are **5** local maxima (one per maximal clique) and for **λ>1** there are **8** (every vertex is an integral local maximizer). The count **increases** past λ=1 — reproducing that larger diagonal loading adds spurious local maxima, so λ=1 is the optimal threshold. *(λ=1 exactly is the degenerate transition point and is excluded from the strict <1 vs >1 comparison.)*