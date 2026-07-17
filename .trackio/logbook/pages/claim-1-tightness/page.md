# Claim 1 — Tightness


---
<!-- trackio-cell
{"type": "code", "id": "cell_cbc9d394a871", "created_at": "2026-07-17T05:17:11+00:00", "title": "Full evidence (C1 tightness + C2 dichotomy + C3 FW)", "command": ["python", "repro/src/run_claims.py"], "exit_code": 0, "duration_s": 70.609}
-->
````bash
$ python repro/src/run_claims.py
````

exit 0 · 70.6s


````python title=run_claims.py
"""Evidence orchestrator: Densest k-Subgraph penalty relaxation — landscape &
finite-step convergence (Lu et al., arXiv 2410.07388, VQt4w3lElX).

Verifies the three scored claims EXACTLY (via KKT stationary-point enumeration)
on a battery of small graphs and writes outputs/.  Deterministic; re-run-safe.
"""
import os, sys, csv, json
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from dks import random_graph, planted_dense_graph, combinatorial_opt, g
from landscape import relaxation_global_max, classify
from frankwolfe import frank_wolfe, random_feasible

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "outputs")
os.makedirs(OUT, exist_ok=True)


def graph_battery():
    out = []
    for seed in range(6):
        for p in (0.3, 0.6):
            out.append((f"Gnp(n=8,p={p},s={seed})", random_graph(8, p, seed)))
    for seed in range(3):
        out.append((f"planted(n=8,k=4,s={seed})", planted_dense_graph(8, 4, 1.0, 0.2, seed)))
    return out


def claim1_tightness():
    """C1 / Theorem 2.3: for lambda >= 1, relaxation global max == combinatorial
    DkS (+ lambda k/2 shift).  Also exhibit lambda < 1 failures (necessity)."""
    rows = []; worst_tight = 0.0; n_fail = 0
    for name, A in graph_battery():
        n = A.shape[0]
        for k in (3, 4, 5):
            fmax, _ = combinatorial_opt(A, k)
            for lam in (1.0, 1.5, 2.0, 3.0):           # lambda >= 1: must be tight
                rmax, _, _ = relaxation_global_max(A, lam, k)
                gap = rmax - (fmax + lam * k / 2)
                worst_tight = max(worst_tight, abs(gap))
                rows.append({"graph": name, "k": k, "lambda": lam, "tight": bool(abs(gap) < 1e-6),
                             "relax_max": rmax, "combinatorial_shifted": fmax + lam * k / 2, "gap": gap})
            for lam in (0.1, 0.5):                     # lambda < 1: may fail
                rmax, _, _ = relaxation_global_max(A, lam, k)
                gap = rmax - (fmax + lam * k / 2)
                if gap > 1e-6:
                    n_fail += 1
                rows.append({"graph": name, "k": k, "lambda": lam, "tight": bool(gap < 1e-6),
                             "relax_max": rmax, "combinatorial_shifted": fmax + lam * k / 2, "gap": gap})
    with open(os.path.join(OUT, "c1_tightness.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    tight_rows = [r for r in rows if r["lambda"] >= 1]
    return {"claim": "C1 tightness (lambda>=1)",
            "tight_cases_lambda_ge_1": sum(r["tight"] for r in tight_rows),
            "total_cases_lambda_ge_1": len(tight_rows),
            "worst_gap_lambda_ge_1": worst_tight,
            "all_tight": all(r["tight"] for r in tight_rows),
            "lambda_lt_1_failures_found": n_fail}


def claim2_dichotomy():
    """C2 / Theorems 3.7 & 3.10: for lambda > 1 non-integral, every stationary
    point is either an integral local maximizer or a non-integral strict saddle."""
    rows = []; min_ascent = np.inf; all_clean = True
    for name, A in graph_battery():
        for k in (3, 4, 5):
            lam = 1.5                              # lambda > 1, non-integral
            _, _, pts = relaxation_global_max(A, lam, k)
            for p in pts:
                cls, asc = classify(p, A, lam)
                rows.append({"graph": name, "k": k, "lambda": lam,
                             "integral": p["integral"], "class": cls,
                             "ascent_curvature": asc if asc is not None else ""})
                if cls == "nonintegral_strict_saddle" and asc is not None:
                    min_ascent = min(min_ascent, asc)
                if cls not in ("integral_local_max", "nonintegral_strict_saddle"):
                    all_clean = False
    with open(os.path.join(OUT, "c2_dichotomy.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    return {"claim": "C2 dichotomy (lambda=1.5 non-integral)",
            "stationary_points": len(rows),
            "integral_local_max": sum(1 for r in rows if r["class"] == "integral_local_max"),
            "nonintegral_strict_saddle": sum(1 for r in rows if r["class"] == "nonintegral_strict_saddle"),
            "min_ascent_curvature_at_saddles": float(min_ascent),
            "all_classified_cleanly": all_clean,
            "clean_dichotomy": all_clean}


def claim3_frankwolfe():
    """C3 / Section 4: saddle-escaping FW converges to an integral local
    maximizer in a finite (bounded) number of steps, from random starts."""
    rows = []; rng = np.random.default_rng(0)
    max_steps = 0; n_integral = 0; n_localmax = 0; total = 0
    for name, A in graph_battery()[:9]:
        n = A.shape[0]
        for k in (3, 4):
            lam = 1.5
            for trial in range(8):
                x0 = random_feasible(n, k, rng)
                xf, niter, integral, localmax = frank_wolfe(A, lam, k, x0)
                max_steps = max(max_steps, niter)
                total += 1
                n_integral += int(integral)
                n_localmax += int(localmax)
                rows.append({"graph": name, "k": k, "trial": trial, "steps": niter,
                             "integral": integral, "local_max": localmax,
                             "final_g": g(xf, A, lam)})
    with open(os.path.join(OUT, "c3_frankwolfe.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    return {"claim": "C3 saddle-escaping Frank-Wolfe",
            "runs": total, "reached_integral": n_integral,
            "reached_local_max": n_localmax,
            "max_steps_observed": max_steps,
            "always_integral_local_max": (n_integral == total and n_localmax == total)}


def main():
    print("=== Claim 1: tightness ==="); r1 = claim1_tightness(); print(json.dumps(r1, indent=2))
    print("=== Claim 2: dichotomy ==="); r2 = claim2_dichotomy(); print(json.dumps(r2, indent=2))
    print("=== Claim 3: Frank-Wolfe ==="); r3 = claim3_frankwolfe(); print(json.dumps(r3, indent=2))
    overall = {
        "paper": "Densest k-Subgraph: penalty relaxation landscape (Lu et al. 2410.07388, VQt4w3lElX)",
        "claims": {"C1_tightness": r1, "C2_dichotomy": r2, "C3_frankwolfe": r3},
        "verdict": {"C1_verified": r1["all_tight"], "C2_verified": r2["clean_dichotomy"],
                    "C3_verified": r3["always_integral_local_max"]},
    }
    json.dump(overall, open(os.path.join(OUT, "summary.json"), "w"), indent=2)
    print("\nWrote", ", ".join(sorted(os.listdir(OUT))))


if __name__ == "__main__":
    main()

````


````output
=== Claim 1: tightness ===
{
  "claim": "C1 tightness (lambda>=1)",
  "tight_cases_lambda_ge_1": 180,
  "total_cases_lambda_ge_1": 180,
  "worst_gap_lambda_ge_1": 0.0,
  "all_tight": true,
  "lambda_lt_1_failures_found": 30
}
=== Claim 2: dichotomy ===
{
  "claim": "C2 dichotomy (lambda=1.5 non-integral)",
  "stationary_points": 8605,
  "integral_local_max": 853,
  "nonintegral_strict_saddle": 7752,
  "min_ascent_curvature_at_saddles": 0.625,
  "all_classified_cleanly": true,
  "clean_dichotomy": true
}
=== Claim 3: Frank-Wolfe ===
{
  "claim": "C3 saddle-escaping Frank-Wolfe",
  "runs": 144,
  "reached_integral": 144,
  "reached_local_max": 144,
  "max_steps_observed": 202,
  "always_integral_local_max": true
}

Wrote c1_tightness.csv, c2_dichotomy.csv, c3_frankwolfe.csv, summary.json

````


---
<!-- trackio-cell
{"type": "artifact", "id": "cell_f324692941f6", "created_at": "2026-07-17T05:17:11+00:00", "title": "Artifact: c2_dichotomy.csv", "path": "outputs/c2_dichotomy.csv", "size": 617634, "artifact_type": "dataset", "auto": true}
-->
**📦 Artifact** `outputs/c2_dichotomy.csv` · dataset · 0.6 MB

trackio-local-path://outputs/c2_dichotomy.csv


---
<!-- trackio-cell
{"type": "artifact", "id": "cell_6cd7dadd768b", "created_at": "2026-07-17T05:17:11+00:00", "title": "Artifact: c1_tightness.csv", "path": "outputs/c1_tightness.csv", "size": 13471, "artifact_type": "dataset", "auto": true}
-->
**📦 Artifact** `outputs/c1_tightness.csv` · dataset · 13.5 kB

trackio-local-path://outputs/c1_tightness.csv


---
<!-- trackio-cell
{"type": "artifact", "id": "cell_f587935d38a2", "created_at": "2026-07-17T05:17:11+00:00", "title": "Artifact: c3_frankwolfe.csv", "path": "outputs/c3_frankwolfe.csv", "size": 6174, "artifact_type": "dataset", "auto": true}
-->
**📦 Artifact** `outputs/c3_frankwolfe.csv` · dataset · 6.2 kB

trackio-local-path://outputs/c3_frankwolfe.csv


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_d6def673cbb6", "created_at": "2026-07-17T05:17:33+00:00", "title": "C1 verdict: relaxation is tight for lambda >= 1"}
-->
**Claim 1 (Theorem 2.3):** for penalty parameter **λ ≥ 1**, the global maximum of the diagonal-loaded relaxation (3) **equals** the combinatorial DkS optimum (1) plus the λk/2 diagonal shift. Equivalently, the relaxed global optimum is attained at an **integral** point.

We verify by computing the relaxation's **exact global maximum** via exhaustive KKT stationary-point enumeration (Theorem 3.4) and comparing to brute-force DkS.

| λ range | cases | result |
|---|---|---|
| λ ≥ 1 (1.0, 1.5, 2.0, 3.0) | **180/180** | tight (gap = 0.0, machine precision) |
| λ < 1 (0.1, 0.5) | — | **30 failures** found (relaxation strictly exceeds combinatorial) |

The λ<1 failures confirm **Theorem 2.1** (λ ≥ 1 is *necessary* for general tightness). Tightness holds for **all** subgraph sizes k (extending Lu et al.'s λ=1/Barman's λ=2 results).
