# Claim 3 — Frank-Wolfe finite exact convergence

---
<!-- trackio-cell
{"type":"markdown","id":"cell_c3_theorem_dag","created_at":"2026-07-19T09:14:44+00:00","title":"C3 paper-faithful convergence certificate"}
-->
## Scored statement and scope

Algorithm 1 reaches an integral local maximizer exactly after finitely many
iterations in the paper's analyzed non-integer `1<lambda<2` regime.

The legacy eigenvector perturbation/exact-line-search/snap experiment is not
Algorithm 1 and is excluded from this proof-level conclusion.  The replacement
implements and tests the printed top-`k` LMO with
`gamma=min{1,G/(L*||d||^2)}` and the `k`-th/`(k+1)`-th coordinate transfer.

## Self-contained convergence argument

For `d=s-x` and gap `G=v^T d`, smoothness plus
`gamma=min{1,G/(L||d||^2)}` gives

```text
gain >= min{G^2/(4kL), G/2} > 0.
```

Summing gains makes every positive trigger reachable in finitely many standard
steps. Projection optimality gives `||R(x)||^2<=G(x)`; the explicitly disclosed
Luo-Tseng polyhedral error bound then gives
`dist_infinity(x,stationary set)<=tau*sqrt(G)` locally.

At an integral local maximum with gradient gap `sigma`, proximity within
`sigma/(4L)` keeps its indicator as the unique top-`k` LMO and proves
`v^T d>=L||d||^2`; hence `gamma=1` reaches it exactly.

For a saddle transfer, exact expansion gives

```text
gain = delta(v_j-v_l)+(lambda-a_jl)delta^2
     >= (lambda-1)delta^2.
```

The closest-integral mass identity yields
`delta>=xi_y/[4(lambda+1)n]` in the accepted neighborhood. Since every
integral gradient difference is `lambda+integer`,
`xi_y>=r=dist(lambda,Z)>0`. Thus every successful escape gains at least

```text
Delta=(lambda-1)r^2/[16(lambda+1)^2 n^2] > 0.
```

Finally `0<=g(x)<=(k^2+lambda*k)/2`, so only finitely many escapes are
possible. Multiplying an early trigger by `beta in (0,1)` reaches its positive
valid value finitely. After the last escape, the gap rate cannot enter another
saddle basin—otherwise another escape occurs—so it enters a local-max basin
and the full-step argument finishes exactly.

## Original Section 5.1 benchmark

The bundled official SNAP graph has 4,039 nodes and 88,234 edges (SHA-256
`125e84db...035d7`). With the paper's `k=20`, `lambda=1.5`, and
`x0=(k/n)1`, Algorithm 1 reaches exact integrality after 35 updates: terminal
gap `0`, 20 ones, zero fractional coordinates, selected/unselected gradient
gap `0.5`, and 190 induced edges. Iteration 34 takes the predicted `gamma=1`
jump. Every gain meets the derived lower bound.

The paper's constant-`2kL` denominator remains fractional at all 4,039
coordinates after 50,000 updates, with integrality `0.9993243` and gap
`0.131515`. This directly reproduces finite exact versus asymptotic behavior at
the paper's scale.

**Result: the proof-level evidence supports the claim within its stated scope.**

Artifacts: [finite-convergence and paper-scale audit](https://huggingface.co/buckets/DineshAI/VQt4w3lElX-artifacts#reproduction-densest-k-subgraph/repro-bundle-v2/docs/FINITE_CONVERGENCE_AUDIT.md) · [machine-readable result](https://huggingface.co/buckets/DineshAI/VQt4w3lElX-artifacts#reproduction-densest-k-subgraph/repro-bundle-v2/repro/outputs/paper_scale_audit.json)
