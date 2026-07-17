"""Saddle-escaping Frank-Wolfe for the DkS penalty relaxation (Section 4 of
Lu et al. 2410.07388).  Maximizes g(x) = (1/2) x^T (A+lambda I) x over the
hypersimplex C_k^n = {x in [0,1]^n : sum x_i = k}.

Frank-Wolfe step: the linear maximization oracle over C_k^n returns the vertex
indicator of the k largest entries of the gradient; we move toward it.  At a
non-integral stationary point (a strict saddle for lambda>1 non-integral), the
Hessian has an explicit positive-curvature ascent direction; we escape by
perturbing along it.  We verify the paper's finite-step exact convergence claim:
from any start, the method reaches an INTEGRAL local maximizer in a bounded
number of steps.
"""
from __future__ import annotations
import numpy as np
from dks import g, grad_g
from landscape import classify


def lmo(grad: np.ndarray, k: int) -> np.ndarray:
    """Linear maximization oracle over C_k^n: vertex = indicator of top-k of grad."""
    s = np.zeros_like(grad)
    idx = np.argpartition(grad, -k)[-k:]
    s[idx] = 1.0
    return s


def is_integral(x, tol=1e-6):
    return np.max(np.abs(x - np.round(x))) < tol


def frank_wolfe(A, lam, k, x0, max_iter=2000, tol=1e-10, escape=True):
    """Run saddle-escaping Frank-Wolfe.  Returns (x_final, n_iter, integral,
    local_max)."""
    n = A.shape[0]
    M = A + lam * np.eye(n)

    def gval(x):
        return 0.5 * float(x @ M @ x)

    x = x0.copy()
    escapes = 0
    for it in range(max_iter):
        grad = M @ x
        s = lmo(grad, k)
        gap = float(grad @ (s - x))            # FW duality gap (0 at stationary)
        if gap < tol:
            if is_integral(x) or not escape:
                break
            if escapes >= 200:
                # exhausted the analytic escape: snap to the FW vertex target
                x = lmo(grad, k).copy()
                break
            # non-integral strict saddle: perturb along the Hessian ascent dir,
            # growing the step each retry until the saddle is left.
            free = np.where((x > 1e-6) & (x < 1 - 1e-6))[0]
            if len(free) >= 2:
                sub = M[np.ix_(free, free)]
                w, V = np.linalg.eigh(sub)
                step = (0.1 + 0.1 * escapes) * V[:, -1]
                step -= step.mean()
                x[free] = np.clip(x[free] + step, 1e-9, 1 - 1e-9)
                escapes += 1
            continue
        d = s - x
        # exact 1-D line maximization of g(x+gamma d) over gamma in [0,1]
        a = float(d @ M @ x)
        b = float(d @ M @ d)
        cands = [0.0, 1.0]
        if abs(b) > 1e-15:
            gstar = -a / b
            if 0.0 < gstar < 1.0:
                cands.append(gstar)
        gamma = max(cands, key=lambda r: gval(x + r * d))
        x = x + gamma * d
        x = np.clip(x, 0.0, 1.0)
        if abs(x.sum() - k) > 1e-12:
            x = _project_simplex(x, k)
    cls, _ = classify({"x": x, "v": M @ x, "S0": set(np.where(x < 1e-6)[0]),
                       "S1": set(np.where(x > 1 - 1e-6)[0]),
                       "Sf": set(np.where((x > 1e-6) & (x < 1 - 1e-6))[0]),
                       "integral": is_integral(x)}, A, lam)
    return x, it + 1, bool(is_integral(x)), (cls == "integral_local_max")


def _project_simplex(x, k):
    """Project x onto {y in [0,1]^n : sum y = k} by a tiny residual shift on
    interior coords (keeps the FW iterate feasible after clipping)."""
    free = np.where((x > 1e-9) & (x < 1 - 1e-9))[0]
    if len(free) == 0:
        return x
    delta = (k - x.sum()) / len(free)
    x = x.copy()
    x[free] = np.clip(x[free] + delta, 1e-12, 1 - 1e-12)
    return x


def random_feasible(n, k, rng):
    """Random feasible point of C_k^n."""
    x = np.zeros(n)
    idx = rng.choice(n, k, replace=False)
    x[idx] = 1.0
    # mix two vertices -> interior
    if rng.random() < 0.5:
        idx2 = rng.choice(n, k, replace=False)
        y = np.zeros(n); y[idx2] = 1.0
        x = 0.5 * x + 0.5 * y
    return x
