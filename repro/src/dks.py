"""Densest k-Subgraph (DkS) and the diagonal-loaded penalty relaxation of
Lu et al. (2025) / Lu, Sidiropoulos & Konar (arXiv 2410.07388).

Problem (1)  DkS:   max  (1/2) x^T A x   s.t. x in {0,1}^n, sum x_i = k
Problem (2)  diag:  max  g(x) = (1/2) x^T (A + lambda I) x  s.t. x in {0,1}^n, sum x_i = k
Problem (3)  relax: max  g(x) = (1/2) x^T (A + lambda I) x  s.t. x in [0,1]^n, sum x_i = k

A is the symmetric 0/1 adjacency matrix.  f(x)=(1/2)x^T A x counts induced edges;
g(x)=f(x)+(lambda/2)||x||^2.  For integral x, ||x||^2=k so g=f+lambda k/2 (a shift).
"""
from __future__ import annotations
from typing import List, Tuple
import numpy as np
import networkx as nx


def edges(A: np.ndarray, S) -> int:
    """Number of edges induced by subset S."""
    idx = list(S)
    return int(A[np.ix_(idx, idx)].sum() / 2)


def combinatorial_opt(A: np.ndarray, k: int):
    """Exact DkS optimum by brute force: max edges over all k-subsets.
    Returns (best_value_f, best_subset)."""
    from itertools import combinations
    n = A.shape[0]
    best_v, best_S = -1, None
    for S in combinations(range(n), k):
        v = edges(A, S)
        if v > best_v:
            best_v, best_S = v, S
    return best_v, best_S


def g(x: np.ndarray, A: np.ndarray, lam: float) -> float:
    M = A + lam * np.eye(A.shape[0])
    return 0.5 * float(x @ M @ x)


def grad_g(x: np.ndarray, A: np.ndarray, lam: float) -> np.ndarray:
    return (A + lam * np.eye(A.shape[0])) @ x


# --------------------------- graph generators ------------------------------ #
def random_graph(n: int, p: float, seed: int) -> np.ndarray:
    G = nx.gnp_random_graph(n, p, seed=seed)
    A = nx.to_numpy_array(G, dtype=float)
    np.fill_diagonal(A, 0.0)
    A = ((A + A.T) > 0).astype(float)
    return A


def planted_dense_graph(n: int, k: int, p_in: float, p_out: float, seed: int) -> np.ndarray:
    """A graph with a planted dense k-clique-ish core (clique if p_in=1)."""
    rng = np.random.default_rng(seed)
    A = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            in_core = (i < k) and (j < k)
            p = p_in if in_core else p_out
            if rng.random() < p:
                A[i, j] = A[j, i] = 1.0
    return A
