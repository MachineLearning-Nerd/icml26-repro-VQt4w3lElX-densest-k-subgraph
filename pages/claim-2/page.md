# Claim 2 — Stationary-point dichotomy

---
<!-- trackio-cell
{"type":"markdown","id":"cell_c2_universal_proof","created_at":"2026-07-19T09:14:43+00:00","title":"C2 universal KKT and curvature certificate"}
-->
## Scored statement

For every finite simple graph and non-integer `lambda>1`, each stationary point
is either an integral local maximizer or a non-integral strict saddle.

The KKT partition for `v=(A+lambda I)x` gives `v_i<=mu` on zero coordinates,
`v_i>=mu` on one coordinates, and `v_i=mu` on fractional coordinates.

**Integral case.** A selected gradient is `lambda+integer`; an unselected
gradient is an integer.  Non-integer lambda prevents equality, so KKT weak
ordering becomes a strict selected/unselected gap, the local-maximum certificate
of Theorems 3.6–3.7.

**Non-integral case.** Integer `sum(x)=k` implies distinct fractional `i,j`.
For locally feasible `d=e_i-e_j`, KKT gives `v^T d=0`, and exactly

```text
d^T(A+lambda I)d = 2(lambda-a_ij) > 0.
```

Thus every non-integral stationary point is a strict saddle (Theorem 3.10), and
the two cases exhaust all stationary points.  At `lambda=1` an edge can make
curvature zero; for integer lambda the integral no-tie step can fail.  Both
assumption controls are recorded in the artifact.

**Result: the theorem-level evidence supports the claim.**

Artifact: [proof source and tests](https://huggingface.co/buckets/DineshAI/VQt4w3lElX-artifacts#reproduction-densest-k-subgraph/repro-bundle-v2/repro)
