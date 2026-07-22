#!/usr/bin/env python3
"""On Densest k-Subgraph Mining and Diagonal Loading (arXiv:2410.07388). Reproduces the diagonal-loaded
Motzkin-Straus results for the objective  g(x) = x^T (A + lambda I) x  over the simplex Delta_n:
  [0] Theorem 4: for lambda in [0,1], max_{x in Delta_n} g(x) = 1 + (lambda-1)/omega, omega=clique number.
  [1] Corollary 1: for lambda >= 1 there is an INTEGRAL global maximizer (a single vertex gives value
      lambda, tying/beating the clique value at lambda=1) -> the relaxation is tight.
  [2] Lemma 1: for lambda > 1 there is NO non-integral local maximizer (all local maxima are vertices).
  [4] the (saddle-escaping) Frank-Wolfe algorithm converges (monotone objective increase to a stationary pt).
Small graphs with brute-force clique number. Deterministic seeds.
"""
import numpy as np, json, hashlib
from itertools import combinations

def clique_number(A):
    n = len(A)
    for size in range(n, 0, -1):
        for S in combinations(range(n), size):
            if all(A[i, j] for i, j in combinations(S, 2)): return size
    return 0

def g(x, A, lam): return float(x @ (A + lam * np.eye(len(A))) @ x)

def frank_wolfe(A, lam, x0, iters=2000):
    n = len(A); x = x0.copy(); L = np.linalg.norm(A + lam*np.eye(n), 2) + 1e-9; obj = [g(x, A, lam)]
    for _ in range(iters):
        grad = 2 * (A + lam * np.eye(n)) @ x                # maximize -> move toward argmax gradient vertex
        s = np.zeros(n); s[int(np.argmax(grad))] = 1.0      # LMO over the simplex
        d = s - x; gd = grad @ d
        if gd <= 1e-12: break
        gamma = min(1.0, gd / (2 * L * (d @ d) + 1e-12))
        x = x + gamma * d; obj.append(g(x, A, lam))
    return x, obj

def project_simplex(v):
    u = np.sort(v)[::-1]; css = np.cumsum(u); rho = np.nonzero(u * np.arange(1, len(v)+1) > (css - 1))[0][-1]
    theta = (css[rho] - 1) / (rho + 1.0); return np.maximum(v - theta, 0)

def local_max_from(A, lam, x0, steps=3000, lr=0.05):
    x = x0.copy()
    for _ in range(steps):
        x = project_simplex(x + lr * 2 * (A + lam*np.eye(len(A))) @ x)
    return x

def main():
    R = {"claim": "Motzkin_Straus_diagonal_loading", "paper": "arXiv:2410.07388"}
    rng = np.random.default_rng(0)
    # test graphs with known clique numbers
    def clique_plus(omega, extra):                          # K_omega + `extra` sparsely-connected vertices
        n = omega + extra; A = np.zeros((n, n))
        for i, j in combinations(range(omega), 2): A[i, j] = A[j, i] = 1
        for v in range(omega, n):                           # attach each extra to <=omega-2 clique nodes (no bigger clique)
            for u in rng.choice(omega, min(omega - 2, omega), replace=False): A[v, u] = A[u, v] = 1
        return A
    graphs = [clique_plus(3, 2), clique_plus(4, 3), clique_plus(5, 4)]

    # ---------- [0] Theorem 4 value formula (lambda in [0,1]) ----------
    rows = []
    ok0 = True
    for gi, A in enumerate(graphs):
        w = clique_number(A)
        for lam in (0.0, 0.3, 0.6, 0.9, 1.0):
            best = -1
            for _ in range(40):                             # multi-start global max over simplex
                x, _o = frank_wolfe(A, lam, project_simplex(rng.random(len(A))))
                best = max(best, g(x, A, lam))
            theo = 1 + (lam - 1) / w
            rows.append({"graph": gi, "omega": w, "lambda": lam, "max": round(best, 4), "1+(lam-1)/omega": round(theo, 4)})
            if abs(best - theo) > 0.02: ok0 = False
    R["thm4_value_examples"] = rows[:6]
    R["thm4_max_equals_formula"] = ok0

    # ---------- [1] Cor 1: lambda>=1 integral (vertex) maximizer is optimal ----------
    A = graphs[1]; w = clique_number(A); n = len(A)
    lam = 1.0
    vertex_val = max(g(np.eye(n)[i], A, lam) for i in range(n))    # best single vertex = lambda
    best_cont = max(g(frank_wolfe(A, lam, project_simplex(rng.random(n)))[0], A, lam) for _ in range(40))
    R["cor1_lambda1_vertex_value"] = round(vertex_val, 4); R["cor1_lambda1_global_max"] = round(best_cont, 4)
    R["cor1_integral_maximizer_optimal"] = abs(vertex_val - best_cont) < 0.02

    # ---------- [2] Lemma 1: lambda>1 -> every local maximizer is INTEGRAL (a vertex) ----------
    lam = 1.5; integral_count = 0; trials = 60
    for _ in range(trials):
        xl = local_max_from(A, lam, project_simplex(rng.random(n)))
        if np.max(xl) > 0.999: integral_count += 1                # concentrated on one vertex => integral
    R["lemma1_frac_local_maxima_integral"] = round(integral_count / trials, 3)
    R["lemma1_no_nonintegral_local_max"] = integral_count == trials

    # ---------- [4] Frank-Wolfe convergence (monotone increase, stabilises) ----------
    x, obj = frank_wolfe(graphs[2], 0.5, project_simplex(rng.random(len(graphs[2]))))
    R["fw_monotone_increase"] = bool(all(obj[i+1] >= obj[i] - 1e-9 for i in range(len(obj)-1)))
    R["fw_converged"] = bool(abs(obj[-1] - obj[-2]) < 1e-7 or len(obj) < 2000)
    R["fw_iterations"] = len(obj)

    R["verdict"] = "supports" if (R["thm4_max_equals_formula"] and R["cor1_integral_maximizer_optimal"]
                                  and R["lemma1_no_nonintegral_local_max"] and R["fw_monotone_increase"]) else "inconclusive"

    print("claim: " + R["claim"])
    print(f"[0] Thm 4: max_x x^T(A+lambda I)x = 1+(lambda-1)/omega (samples):")
    for r in rows[:6]: print(f"      omega={r['omega']}, lambda={r['lambda']}: max={r['max']} vs formula {r['1+(lam-1)/omega']}")
    print(f"    all match: {R['thm4_max_equals_formula']}")
    print(f"[1] Cor 1: lambda=1 vertex value={R['cor1_lambda1_vertex_value']} == global max {R['cor1_lambda1_global_max']} -> integral optimal: {R['cor1_integral_maximizer_optimal']}")
    print(f"[2] Lemma 1: lambda=1.5, fraction of local maxima that are integral = {R['lemma1_frac_local_maxima_integral']} -> no non-integral local max: {R['lemma1_no_nonintegral_local_max']}")
    print(f"[4] Frank-Wolfe: monotone increase={R['fw_monotone_increase']}, converged in {R['fw_iterations']} iters")
    print(f"verdict: {R['verdict']}")

    def _np(o):
        if isinstance(o, np.bool_): return bool(o)
        if isinstance(o, np.integer): return int(o)
        if isinstance(o, np.floating): return float(o)
        raise TypeError
    import os; os.makedirs("outputs", exist_ok=True)
    open("outputs/motzkin_results.json", "w").write(json.dumps(R, indent=2, default=_np))
    print("RESULTS_SHA256=" + hashlib.sha256(json.dumps(R, sort_keys=True, default=_np).encode()).hexdigest())
    return 0 if R["verdict"] == "supports" else 1

if __name__ == "__main__":
    raise SystemExit(main())
