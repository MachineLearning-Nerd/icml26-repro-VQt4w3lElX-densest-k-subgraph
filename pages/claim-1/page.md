# Claim 1 — Tightness

---
<!-- trackio-cell
{"type":"markdown","id":"cell_c1_universal_proof","created_at":"2026-07-19T09:14:42+00:00","title":"C1 universal proof certificate"}
-->
## Scored statement

For every finite simple graph, every integer `1 <= k < n`, and every penalty
`lambda >= 1`, the global maximum of

```text
g(x)=1/2 x^T(A+lambda I)x,  x in [0,1]^n,  sum(x)=k
```

equals the combinatorial Densest-`k`-Subgraph optimum plus `lambda*k/2`.

## Universal proof certificate

Let `s=A*x`.  A non-integral feasible `x` has at least two fractional
coordinates because `sum(x)=k` is an integer.  Orient two so
`lambda*x_i+s_i >= lambda*x_j+s_j`.  Set
`delta=min{x_j,1-x_i}`, `d=e_i-e_j`, and `x'=x+delta*d`.  The update remains
feasible, and exact quadratic expansion gives

```text
g(x')-g(x)
 = delta[(lambda*x_i+s_i)-(lambda*x_j+s_j)]
   + (lambda-a_ij)*delta^2 >= 0.
```

The first term is nonnegative by orientation; the second is nonnegative because
`a_ij in {0,1}` and `lambda>=1`.  Either `x'_i=1` or `x'_j=0`, so the number of
fractional coordinates strictly decreases.  It terminates at integral `z` with
`g(z)>=g(x)`.  Since `g(z)=f(z)+lambda*k/2` and every integral point is already
relaxed-feasible, both optima are equal.

The executable DAG checks the exact `lambda=1`, `a_ij in {0,1}` boundary.  The
former 180/180 finite cases are corroboration only.

**Result: the theorem-level evidence supports the claim.**

Artifact: [theorem certificates](https://huggingface.co/buckets/DineshAI/VQt4w3lElX-artifacts#reproduction-densest-k-subgraph/repro-bundle-v2/repro/outputs/theorem_certificates.json)
