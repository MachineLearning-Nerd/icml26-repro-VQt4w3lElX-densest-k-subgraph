# Claim 1 — exact Theorem 4 and minimum-threshold certificate

This page replaces the earlier small numerical Motzkin–Straus check with a
universal exact certificate for the claim actually scored by the challenge.
It preserves the separate Theorem 2 rounding certificate and all other claim
evidence.

## Source lock and exact scope

- Paper: arXiv `2410.07388` v1, *On Densest k-Subgraph Mining and Diagonal Loading*
- Preferred HTML source: `https://ar5iv.labs.arxiv.org/html/2410.07388`
- Full HTML SHA-256: `94dc307f35bda0046eded2944df2dd7d1a56282462cbc9998fa545b463ac5d66`
- Audited raw HTML anchor slices:
  - Theorem 4 through the start of Corollary 2: `8ea44454fe5d307bfe6784c24fae884a8b39fb066279c2ff132cbff2a790b338`
  - Corollary 2 through the start of Lemma 1, including its proof and the minimum-threshold paragraph: `3cb02eea34c746003918066f1e89f469ccafa980206e8bdac1ec78086dc99e92`
  - Appendix B through the start of Appendix C: `2a80746443eaf77c441ecce2bc10f56feaad691e20186ce15ee55c7d95559ca4`
- Version-matched TeX source: `https://arxiv.org/e-print/2410.07388v1`
- v1 source-tar SHA-256: `1921ada72f0e3277d0e64576cc897791ddb3c271399aa2189c4be3a92467e96e`

Theorem 4 states that for an unweighted, undirected simple graph with clique
number `omega`, adjacency matrix `A`, and `0 <= lambda <= 1`,

```text
max_{x in Delta_n} x^T(A + lambda I)x = 1 + (lambda - 1)/omega.
```

Corollary 2 says that `lambda < 1` cannot guarantee tightness of the original
sum-to-`k` relaxation in general. Together with Theorem 2/Corollary 1, this
makes `lambda = 1` the minimum graph-independent guarantee. This is a
worst-case statement; it does not say that every individual graph fails below
one.

## Universal exact proof of Theorem 4

Write `g(x)=x^T(A+lambda I)x`. Starting from any `x` in the unit simplex,
suppose its positive support is not a clique. Choose positive, nonadjacent
coordinates `i,j` and let `s_i=(Ax)_i`, `s_j=(Ax)_j`.

If `s_i >= s_j`, move all mass at `j` to `i`. Direct expansion gives

```text
g(x + x_j(e_i-e_j)) - g(x)
  = 2*x_j*(s_i-s_j) + 2*lambda*x_i*x_j >= 0.
```

If `s_j > s_i`, the symmetric move of all mass at `i` to `j` has gain

```text
2*x_i*(s_j-s_i) + 2*lambda*x_i*x_j >= 0.
```

Each update removes one positive coordinate, so finitely many updates reach a
no-worse point supported on a clique.

Let that support have size `r <= omega`. Because all supported pairs are edges
and the coordinates sum to one,

```text
g(x) = 1 + (lambda-1)*sum_i x_i^2.
r*sum_i x_i^2 - 1 = sum_{i<j}(x_i-x_j)^2 >= 0.
```

Thus `sum_i x_i^2 >= 1/r`. Since `lambda-1 <= 0` and `r <= omega`,

```text
g(x) <= 1 + (lambda-1)/r <= 1 + (lambda-1)/omega.
```

Uniform mass `1/omega` on a maximum clique attains the last expression, so
the upper bound is exact. The verifier checks every displayed algebraic
identity coefficient-by-coefficient, not by floating-point sampling.

## Exact minimum-threshold proof

For `lambda >= 1`, the existing Theorem 2 certificate rounds any relaxed
sum-to-`k` point to a binary point without lowering the objective. For a
pairwise update of size `delta`, its exact coefficient identity is

```text
gain = 2*delta*(oriented score difference)
       + 2*(lambda-a_ij)*delta^2 >= 0,
```

because `a_ij` is `0` or `1`. This proves sufficiency.

For necessity, take `K_(k+1)` and use the sum-to-`k` relaxation. Every binary
point has value `k(k+lambda-1)`. The feasible uniform point with each
coordinate `k/(k+1)` has value
`k^2 + k^2(lambda-1)/(k+1)`. Their exact difference is

```text
k*(1-lambda)/(k+1),
```

which is strictly positive for every `lambda < 1`. Hence no smaller parameter
can guarantee tightness over all graphs, while one does.

## Deterministic reproduction

Both scripts use only Python's standard library and exact `Fraction`
arithmetic. The independent auditor imports nothing from the primary verifier
and uses a different rational lattice.

```bash
python repro/src/verify_c1_theorem4_exact.py
python repro/src/audit_c1_theorem4_independent.py
```

### Primary verifier stdout

```output
{
  "claim": "Claim 1: Theorem 4 value and minimal graph-independent lambda=1 tightness threshold",
  "coefficient_identities": {
    "clique_objective_r_1_to_6": {
      "1": true,
      "2": true,
      "3": true,
      "4": true,
      "5": true,
      "6": true
    },
    "merge_i_into_j": true,
    "merge_j_into_i": true,
    "pairwise_rounding_aij_0_1": {
      "0": true,
      "1": true
    },
    "variance_identity_r_1_to_6": {
      "1": true,
      "2": true,
      "3": true,
      "4": true,
      "5": true,
      "6": true
    }
  },
  "exact_controls": {
    "coalescence_steps": 26479,
    "exact_points": 293345,
    "graphs": 1099,
    "lambda_values": [
      "0",
      "1/4",
      "1/2",
      "3/4",
      "1"
    ],
    "maximum_clique_attainment_checks": 5495,
    "simplex_denominators": [
      1,
      2,
      3
    ],
    "vertices": "1..5"
  },
  "fail_sensitive_controls": {
    "lambda_above_one_breaks_theorem4_uniform_maximum": true,
    "lambda_below_zero_breaks_coalescence_orientation": true,
    "lambda_one_threshold_gap_is_zero": true
  },
  "source": {
    "appendix_b_slice_sha256": "2a80746443eaf77c441ecce2bc10f56feaad691e20186ce15ee55c7d95559ca4",
    "ar5iv_url": "https://ar5iv.labs.arxiv.org/html/2410.07388",
    "corollary2_slice_sha256": "3cb02eea34c746003918066f1e89f469ccafa980206e8bdac1ec78086dc99e92",
    "html_sha256": "94dc307f35bda0046eded2944df2dd7d1a56282462cbc9998fa545b463ac5d66",
    "scope": "Theorem 4, Corollary 2, Appendix B, and the minimum-threshold paragraph",
    "theorem4_slice_sha256": "8ea44454fe5d307bfe6784c24fae884a8b39fb066279c2ff132cbff2a790b338",
    "v1_source_tar_sha256": "1921ada72f0e3277d0e64576cc897791ddb3c271399aa2189c4be3a92467e96e",
    "v1_source_url": "https://arxiv.org/e-print/2410.07388v1"
  },
  "threshold_certificate": {
    "conclusion": "lambda=1 is the minimal graph-independent tightness guarantee",
    "k_values": "1..8",
    "lambda_values": [
      "-2",
      "-1/2",
      "0",
      "1/3",
      "3/4",
      "999/1000"
    ],
    "strict_cases": 48,
    "strict_gap_identity": "k*(1-lambda)/(k+1)",
    "sufficiency": "pairwise rounding coefficient identity for a_ij in {0,1} and lambda>=1",
    "witness_family": "K_(k+1), sum x_i=k, uniform x_i=k/(k+1)"
  },
  "universal_certificate": {
    "attainment": "uniform mass on a maximum clique",
    "clique_bound": "r*sum(x_i^2)-1=sum_{i<j}(x_i-x_j)^2>=0 and r<=omega",
    "theorem4": "for 0<=lambda<=1, max over the simplex is 1+(lambda-1)/omega",
    "threshold": "Theorem 2 rounding gives sufficiency; Corollary 2 complete-graph family gives necessity",
    "upper_bound": "nonedge coalescence reaches clique support without decreasing g"
  },
  "verdict": "supports"
}
```

### Independent auditor stdout

```output
{
  "claim": "Claim 1 independent Theorem 4 and threshold audit",
  "exact_lattice_audit": {
    "attainment_checks": 4396,
    "graphs": 1099,
    "lambda_values": [
      "0",
      "1/3",
      "2/3",
      "1"
    ],
    "simplex_denominator": 4,
    "upper_bound_points": 296204,
    "vertices": "1..5"
  },
  "release_structure": {
    "all_source_locks_present": true,
    "new_page_ref_count": 1,
    "new_page_resolves_locally": true,
    "prior_page_refs_preserved": 13
  },
  "semantic_controls": {
    "reject_formula_1_plus_lambda_over_omega": true,
    "reject_strict_threshold_gap_at_lambda_one": true,
    "reject_theorem4_extension_above_lambda_one": true
  },
  "threshold_audit": {
    "boundary_lambda_one_gap": "0",
    "complete_graph_cases": 60,
    "k_values": "1..12",
    "strict_gap": "k*(1-lambda)/(k+1)"
  },
  "verdict": "supports"
}
```

Both outputs are deterministic and byte-match the scripts' stdout.
