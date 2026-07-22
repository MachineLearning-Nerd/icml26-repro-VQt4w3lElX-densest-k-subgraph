# Claim 1 — exact Theorem 4 Motzkin–Straus certificate

This additive certificate targets the challenged theorem literally. It leaves
the existing capped-simplex Theorem 2 rounding certificate unchanged and uses
that result only for the `lambda >= 1` sufficiency half of the sharp threshold.

## Version-pinned claim

- Native paper HTML: `https://arxiv.org/html/2410.07388v1`
- Full HTML SHA-256: `dd60268ba75d4b0aaa8e0e0d8c5853a3cfe2f88d94f8554f95056564698cf59d`
- Exact statement extraction: Pandoc plain text, starting at the `Theorem 4
  (An Extension of Motzkin-Straus Theorem)` heading and ending with its first
  `Proof.` line
- Statement SHA-256: `52282da0336bdcac02edab16812bbf5ea45a32dbb8fa93407e60a0317397fe5f`

The v1 theorem assumes an unweighted, undirected, simple graph with clique
number `omega`; for `g(x)=x^T(A+lambda I)x`, `x` on the probability simplex,
and `0 <= lambda <= 1`, it states

```text
max g(x) = 1 + (lambda-1)/omega.
```

The parentheses are essential. The challenge's plain-text `1+lambda-1/omega`
is source-normalized to the displayed paper formula above; a mutation gate
rejects the unparenthesized literal interpretation. The current arXiv v4 is a
major rewrite that no longer numbers this older result as Theorem 4, so this
certificate deliberately uses immutable v1 native HTML rather than the ar5iv
cache, which did not honor version suffixes during the audit.

## Universal primary proof

The primary verifier gives a constructive exact Motzkin–Straus proof. For a
nonedge `i,j`, moving mass between the two coordinates changes
`f(x)=x^T A x` linearly. One endpoint therefore does not decrease `f` and
deletes a support coordinate. Repeating reaches a clique of size `r<=omega`.
On that clique,

```text
r*||x||^2 - 1 = sum_{i<j} (x_i-x_j)^2 >= 0,
f(x) = 1-||x||^2 <= 1-1/omega.
```

Also `f(x)+||x||^2 <= 1`, with the exact gap equal to twice the mass on
nonedges. Since

```text
g_lambda = lambda*(f+||x||^2) + (1-lambda)*f,
```

both coefficients are nonnegative on `[0,1]`, proving the upper bound. Uniform
mass `1/omega` on a maximum clique attains it.

The independent verifier uses a different chain: `g_lambda` is convex along
every nonedge transfer segment because its quadratic coefficient is
`2*lambda>=0`; choosing the better endpoint reaches clique support directly.
There `g=1+(lambda-1)||x||^2`, and the same exact sum-of-squares bound finishes
the proof.

## Why `lambda=1` is the sharp universal tightness threshold

Scaling the simplex witness to mass `k`, for every `lambda<1` and
`1<=k<omega`, uniform mass `k/omega` on a maximum clique is capped-feasible and
beats the best binary `k`-clique by

```text
(1-lambda)*k*(1-k/omega) > 0.
```

Thus values below one cannot guarantee tightness in general. For
`lambda>=1`, the existing exact Theorem 2 certificate proves that every capped
simplex point can be pairwise rounded to a no-worse binary point. Consequently
one is the least graph-independent value that guarantees tightness. This does
not claim every particular instance fails below one.

## Exact controls and fail-sensitive gates

Each standalone script also checks all 1,099 simple graphs through five
vertices, every rational simplex point with denominator 2, 3, or 4, and
`lambda` in `{0,1/4,1/2,3/4,1}`: 636,575 exact graph/point/loading cases.
These are controls around the universal coefficient proof, not a scale-based
inference. Mutations reject the missing parentheses, `lambda>1` extrapolation,
wrong clique number, missing or sign-flipped diagonal, wrong nonedge endpoint,
self-loops, directed adjacency, and a reversed sharpness-gap sign.

## Reproduce

Both programs use only the Python standard library and exact `Fraction`
arithmetic. They contain no timers, randomness, or network calls.

```bash
python repro/src/verify_c1_theorem4_exact.py
python repro/src/audit_c1_theorem4_independent.py
```

### Primary verifier stdout

```json
{
  "claim": "v1 Theorem 4: max over the probability simplex is 1+(lambda-1)/omega for 0<=lambda<=1; lambda=1 is the sharp universal tightness threshold",
  "exact_exhaustive_controls": {
    "denominators": [
      2,
      3,
      4
    ],
    "graph_point_lambda_cases": 636575,
    "lambda_values": [
      "0",
      "1/4",
      "1/2",
      "3/4",
      "1"
    ],
    "maximum_clique_witness_checks": 5495,
    "n_max": 5,
    "simple_graphs": 1099,
    "support_compression_steps": 82471
  },
  "mutation_gates": {
    "directed_assumption_mutation_rejected": true,
    "flipped_diagonal_rejected": true,
    "lambda_above_one_scope_extension_rejected": true,
    "literal_unparenthesized_formula_rejected": true,
    "missing_diagonal_rejected": true,
    "self_loop_assumption_mutation_rejected": true,
    "sharpness_gap_sign_mutation_rejected": true,
    "wrong_clique_number_rejected": true,
    "wrong_nonedge_endpoint_rejected": true
  },
  "sharp_threshold_bridge": {
    "exact_gap": "(1-lambda)*k*(1-k/omega) > 0",
    "family_checks": 1984,
    "lambda_at_least_one_sufficiency": "pairwise capped-simplex transfer has curvature 2*(lambda-a_ij)>=0 and terminates at a binary point",
    "lambda_below_one_counterfamily": "K_omega with 1 <= k < omega and uniform mass k/omega",
    "minimum_checked_gap": "1/8",
    "universal_threshold": "lambda=1 is the least graph-independent value guaranteeing tightness; some particular instances may be tight below 1"
  },
  "source": {
    "html_sha256": "dd60268ba75d4b0aaa8e0e0d8c5853a3cfe2f88d94f8554f95056564698cf59d",
    "scope": "Theorem 4, Appendix B, and the lambda=1 sharp universal threshold bridge",
    "statement_extraction": "pandoc plain text, from Theorem 4 heading through the first Proof. line",
    "statement_sha256": "52282da0336bdcac02edab16812bbf5ea45a32dbb8fa93407e60a0317397fe5f",
    "url": "https://arxiv.org/html/2410.07388v1"
  },
  "universal_proof": {
    "diagonal_lift": "g_lambda=lambda*(x'Ax+||x||^2)+(1-lambda)*x'Ax; both upper bounds have nonnegative weights",
    "identities": {
      "clique_cauchy_sos_coefficient_schema": true,
      "convex_interpolation": true,
      "pairwise_transfer": {
        "edge": true,
        "nonedge": true
      },
      "sign_guards": {
        "lambda_and_one_minus_lambda_nonnegative_on_closed_unit_interval": true,
        "lambda_minus_adjacency_nonnegative_for_lambda_ge_1": true
      },
      "simple_graph_complement_gap_coefficient_schema": true
    },
    "lower_witness": "uniform probability mass on any maximum clique",
    "motzkin_straus": "nonedge mass transfer reduces support to a clique without decreasing x'Ax; clique SOS gives x'Ax <= 1-1/omega"
  },
  "verdict": "supports"
}
```

### Independent verifier stdout

```json
{
  "claim": "independent direct-convexity audit of v1 Theorem 4 and the sharp lambda=1 universal threshold",
  "exact_exhaustive_controls": {
    "denominators": [
      2,
      3,
      4
    ],
    "direct_endpoint_cases": 636575,
    "endpoint_support_deletions": 412355,
    "lambda_values": [
      "0",
      "1/4",
      "1/2",
      "3/4",
      "1"
    ],
    "maximum_clique_witness_checks": 5495,
    "n_max": 5,
    "simple_graphs": 1099
  },
  "mutation_gates": {
    "challenge_parentheses": true,
    "clique_number": true,
    "closed_interval_upper_scope": true,
    "diagonal_present": true,
    "diagonal_sign": true,
    "endpoint_selection": true,
    "sharp_gap_sign": true,
    "simple_no_self_loop": true,
    "undirected": true
  },
  "release_structure": {
    "new_page_ref_count": 1,
    "new_page_resolves": true,
    "protected_page_refs_preserved": 13
  },
  "source": {
    "html_sha256": "dd60268ba75d4b0aaa8e0e0d8c5853a3cfe2f88d94f8554f95056564698cf59d",
    "statement_sha256": "52282da0336bdcac02edab16812bbf5ea45a32dbb8fa93407e60a0317397fe5f",
    "url": "https://arxiv.org/html/2410.07388v1"
  },
  "threshold_bridge": {
    "at_least_one_pair_curvature_checks": 6,
    "below_one_complete_graph_checks": 1984,
    "gap_identity": "(1-lambda)*k*(1-k/omega)",
    "interpretation": "1 is the sharp universal guarantee, not a claim that every fixed instance fails below 1",
    "minimum_checked_strict_gap": "1/8"
  },
  "universal_direct_chain": {
    "clique_closed_form": "g=1+(lambda-1)*sum_i(x_i^2)",
    "clique_sos_bound": "r*sum_i(x_i^2)-1=sum_{i<j}(x_i-x_j)^2 >= 0",
    "nonedge_line_linear_coefficient": "2*((Ax)_i+lambda*x_i-(Ax)_j-lambda*x_j)",
    "nonedge_line_quadratic_coefficient": "2*lambda >= 0",
    "quadratic_endpoint_jensen_gap": "2*lambda*theta*(1-theta)*(U-L)^2 >= 0",
    "variant": "positive support size decreases by one per endpoint step"
  },
  "verdict": "supports"
}
```

Both outputs end with `"verdict": "supports"`. Two consecutive executions of
each verifier must be byte-identical before release.
