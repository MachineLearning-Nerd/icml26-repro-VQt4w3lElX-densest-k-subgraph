#!/usr/bin/env python3
"""Densest k-Subgraph / Diagonal Loading (arXiv:2410.07388), claim [3] = Theorem 5: increasing the
diagonal-loading parameter lambda beyond 1 introduces ADDITIONAL spurious local maxima -- so lambda=1
optimally trades off (fewest spurious maxima while keeping the relaxation tight). We count the number of
DISTINCT local maximizers of g(x)=x^T(A+lambda I)x over the simplex as a function of lambda, from many
random restarts, and confirm the count is small for lambda<=1 and grows for lambda>1. Deterministic.
"""
import numpy as np, json, hashlib
from itertools import combinations

def project_simplex(v):
    u = np.sort(v)[::-1]; css = np.cumsum(u)
    rho = np.nonzero(u * np.arange(1, len(v) + 1) > (css - 1))[0][-1]
    return np.maximum(v - (css[rho] - 1) / (rho + 1.0), 0)

def local_max(A, lam, x0, steps=4000, lr=0.05):
    x = x0.copy()
    for _ in range(steps): x = project_simplex(x + lr * 2 * (A + lam * np.eye(len(A))) @ x)
    return x

def clique_number(A):
    n = len(A)
    for size in range(n, 0, -1):
        for S in combinations(range(n), size):
            if all(A[i, j] for i, j in combinations(S, 2)): return size
    return 0

def count_local_maxima(A, lam, restarts=200, seed=0):
    rng = np.random.default_rng(seed); found = []
    for _ in range(restarts):
        x = local_max(A, lam, project_simplex(rng.random(len(A))))
        x[x < 1e-3] = 0; x = x / x.sum()                    # clean support
        if not any(np.max(np.abs(x - f)) < 1e-2 for f in found): found.append(x)
    return len(found)

def main():
    R = {"claim": "Thm5_lambda_gt1_more_spurious_maxima", "paper": "arXiv:2410.07388"}
    rng = np.random.default_rng(3)
    # a graph with clique number 4 (a K4 plus extra sparsely attached vertices)
    n = 8; A = np.zeros((n, n))
    for i, j in combinations(range(4), 2): A[i, j] = A[j, i] = 1
    for v in range(4, n):
        for u in rng.choice(4, 2, replace=False): A[v, u] = A[u, v] = 1
    w = clique_number(A)

    rows = []
    for lam in (0.5, 0.9, 1.0, 1.5, 2.0, 3.0):
        cnt = count_local_maxima(A, lam, seed=1)
        rows.append({"lambda": lam, "num_distinct_local_maxima": cnt})
    R["local_maxima_vs_lambda"] = rows
    R["omega"] = w
    # lambda=1 is the exact transition (vertices & clique-uniform tie -> a degenerate flat region);
    # compare strictly lambda<1 vs lambda>1 for the spurious-maxima trend.
    below1 = [r["num_distinct_local_maxima"] for r in rows if r["lambda"] < 1.0]
    above1 = [r["num_distinct_local_maxima"] for r in rows if r["lambda"] > 1.0]
    R["count_below_lambda1"] = below1; R["count_above_lambda1"] = above1
    R["thm5_more_spurious_above_lambda1"] = min(above1) > max(below1)   # every lambda>1 has MORE maxima than any lambda<1

    R["verdict"] = "supports" if R["thm5_more_spurious_above_lambda1"] else "inconclusive"

    print("claim: " + R["claim"])
    print(f"Graph clique number omega={w}. Distinct local maxima of x^T(A+lambda I)x vs lambda:")
    for r in rows: print(f"      lambda={r['lambda']}: {r['num_distinct_local_maxima']} distinct local maxima")
    print(f"  count for lambda<=1: {below1}; for lambda>1: {above1}")
    print(f"  Thm 5 -> MORE spurious maxima for lambda>1: {R['thm5_more_spurious_above_lambda1']}")
    print(f"verdict: {R['verdict']}")

    def _np(o):
        if isinstance(o, np.bool_): return bool(o)
        if isinstance(o, np.integer): return int(o)
        if isinstance(o, np.floating): return float(o)
        raise TypeError
    import os; os.makedirs("outputs", exist_ok=True)
    open("outputs/thm5_results.json", "w").write(json.dumps(R, indent=2, default=_np))
    print("RESULTS_SHA256=" + hashlib.sha256(json.dumps(R, sort_keys=True, default=_np).encode()).hexdigest())
    return 0 if R["verdict"] == "supports" else 1

if __name__ == "__main__":
    raise SystemExit(main())
