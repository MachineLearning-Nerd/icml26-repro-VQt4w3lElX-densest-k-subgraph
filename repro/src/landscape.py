"""Exact optimization-landscape analysis of the DkS penalty relaxation (3)
over the hypersimplex  C_k^n = {x in [0,1]^n : sum x_i = k}.

We enumerate ALL stationary points exactly via the KKT characterization
(Theorem 3.4): for each partition (S0, S1, Sf) of [n] the free coordinates
satisfy a linear system, which we solve in closed form.  This is exact for small
n (we use n <= 9).  From the enumerated points we verify:

  * Tightness (Theorem 2.3): for lambda >= 1 the global maximum of (3) equals
    the combinatorial DkS optimum (+ lambda k/2 shift); for some lambda < 1 it
    strictly exceeds it (lambda >= 1 is necessary, Theorem 2.1).
  * Dichotomy (Theorems 3.6/3.7/3.10): integral stationary points are local
    maximizers; non-integral stationary points are strict saddles (the Hessian
    M = A + lambda I has a positive-curvature ascent direction on the tangent).
"""
from __future__ import annotations
from typing import List, Tuple
import numpy as np
from itertools import combinations
from dks import g, grad_g, edges


def enumerate_stationary(A: np.ndarray, lam: float, k: int):
    """Return a list of stationary points of (3) as binary masks of membership
    in S0/S1/Sf together with the point x and its gradient vector v.

    Each element: dict with keys 'x', 'v', 'S0','S1','Sf','integral'."""
    n = A.shape[0]
    M = A + lam * np.eye(n)
    pts = []
    seen = set()

    def add(x, S0, S1, Sf):
        key = (tuple(np.round(x, 9)))
        if key in seen:
            return
        seen.add(key)
        pts.append({"x": x, "v": M @ x, "S0": S0, "S1": S1, "Sf": Sf,
                    "integral": len(Sf) == 0})

    # --- vertices: binary x with sum x = k ---
    for S in combinations(range(n), k):
        x = np.zeros(n)
        x[list(S)] = 1.0
        S1 = set(S); S0 = set(range(n)) - S1; Sf = set()
        # Corollary 3.5: integral stationary iff max v_S0 <= min v_S1
        v = M @ x
        if S0:
            if max(v[i] for i in S0) <= min(v[i] for i in S1) + 1e-12:
                add(x, S0, S1, Sf)
        else:
            add(x, S0, S1, Sf)

    # --- interior stationary points: enumerate (S1, Sf) with Sf nonempty ---
    for s1 in range(0, k + 1):            # |S1| fixed at 1's
        for S1c in combinations(range(n), s1):
            S1 = set(S1c)
            rest = [i for i in range(n) if i not in S1]
            # Sf must have size >= k - s1 (to reach sum k) and >=1
            for sf in range(max(1, k - s1), len(rest) + 1):
                for Sfc in combinations(rest, sf):
                    Sf = set(Sfc)
                    S0 = set(rest) - Sf
                    # solve M_ff x_Sf - mu 1 = -M_f,S1 1 ; 1^T x_Sf = k - s1
                    fidx = sorted(Sf)
                    Mff = M[np.ix_(fidx, fidx)]
                    Mf1 = M[np.ix_(fidx, sorted(S1))] if S1 else np.zeros((sf, 1))
                    b1 = -Mf1 @ np.ones(len(S1)) if S1 else np.zeros(sf)
                    s_target = k - s1
                    if not (0 < s_target < sf):       # need interior sums
                        continue
                    # assembled block system
                    K = np.zeros((sf + 1, sf + 1))
                    K[:sf, :sf] = Mff
                    K[:sf, sf] = -1.0
                    K[sf, :sf] = 1.0
                    rhs = np.zeros(sf + 1)
                    rhs[:sf] = b1
                    rhs[sf] = s_target
                    try:
                        sol = np.linalg.solve(K, rhs)
                    except np.linalg.LinAlgError:
                        continue
                    x_Sf = sol[:sf]
                    mu = sol[sf]
                    if np.any(x_Sf <= 1e-9) or np.any(x_Sf >= 1 - 1e-9):
                        continue                    # not strictly interior
                    x = np.zeros(n)
                    x[list(S1)] = 1.0
                    for j, idx in enumerate(fidx):
                        x[idx] = x_Sf[j]
                    v = M @ x
                    # Theorem 3.4 inequalities: v_S0 <= mu <= v_S1
                    if S0 and max(v[i] for i in S0) > mu + 1e-9:
                        continue
                    if S1 and min(v[i] for i in S1) < mu - 1e-9:
                        continue
                    add(x, S0, S1, Sf)
    return pts


def relaxation_global_max(A: np.ndarray, lam: float, k: int):
    """Global maximum of (3) = max g over all stationary points (exact)."""
    pts = enumerate_stationary(A, lam, k)
    best = -np.inf; best_x = None
    for p in pts:
        gi = g(p["x"], A, lam)
        if gi > best:
            best, best_x = gi, p["x"]
    return best, best_x, pts


def hessian_curvature(A, lam, x, Sf):
    """Smallest eigenvalue of the Hessian M=A+lambda I restricted to the tangent
    space of the active constraints at x (the free coords Sf for an interior
    point).  Positive => an ascent direction exists => strict saddle."""
    n = A.shape[0]
    M = A + lam * np.eye(n)
    if Sf:  # interior: tangent = span of free coords, project out all-ones
        fidx = np.array(sorted(Sf))
        sub = M[np.ix_(fidx, fidx)]
        # tangent within the sum constraint: directions d with d_Sf summing to 0
        e = np.ones(len(fidx)) / len(fidx)
        P = np.eye(len(fidx)) - np.outer(e, e)
        T = P @ sub @ P
        eig = np.linalg.eigvalsh(T)
        return float(eig.max()), float(eig.min())
    return None, None


def classify(pt, A, lam):
    """Return ('integral_local_max'|'nonintegral_strict_saddle', ascent_eig)."""
    if pt["integral"]:
        # Theorem 3.6 (lambda>1): local max iff integral and max v_S0 < min v_S1
        v = pt["v"]
        if pt["S0"]:
            is_localmax = max(v[i] for i in pt["S0"]) < min(v[i] for i in pt["S1"]) - 1e-9
        else:
            is_localmax = True
        return ("integral_local_max" if is_localmax else "integral_not_localmax"), None
    else:
        ascent, _ = hessian_curvature(A, lam, pt["x"], pt["Sf"])
        return ("nonintegral_strict_saddle" if (ascent is not None and ascent > 1e-9)
                else "nonintegral_flat"), ascent
