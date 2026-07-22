# Claim 1 — exact Theorem 2 rounding certificate

This page strengthens the existing finite Claim 1 experiment with the paper's
universal proof mechanism. It does not change Claims 2 or 3.

## Source lock and scope

- Paper: arXiv `2410.07388`, *On Densest k-Subgraph Mining and Diagonal Loading*
- Preferred source: `https://ar5iv.labs.arxiv.org/html/2410.07388`
- Full HTML SHA-256: `94dc307f35bda0046eded2944df2dd7d1a56282462cbc9998fa545b463ac5d66`
- Audited scope: Theorem 2, Corollary 1, and Appendix A equations (27)–(28)
- Raw anchor-slice SHA-256 values:
  - Theorem 2: `0b520a18d09fa90220483b3335e9fe2b3e1be43397da65ceaaa16cec595e59a5`
  - Corollary 1: `026112ac91d8271416fe9e97f266936e3dd9495387a88dce39d0062869b97e21`
  - Appendix A: `933ee6fbcf6e9c16841b45924f212a125580b2217946024ba034a88103fcc974`

Theorem 2 supplies the constructive statement needed by the scored claim: for
every non-integral feasible point and every `lambda >= 1`, there is an integral
feasible point with no smaller diagonal-loaded objective. Corollary 1 turns
that pointwise result into equality of the relaxed and combinatorial optimum
values.

## Exact proof certificate

For `g(x) = x^T(A + lambda I)x`, choose two fractional coordinates `i,j`
oriented so that

```text
lambda*x_i + (A*x)_i >= lambda*x_j + (A*x)_j.
```

Set `delta = min(x_j, 1-x_i)` and `x' = x + delta(e_i-e_j)`. The primary
verifier expands the quadratic coefficient-by-coefficient and checks the exact
identity

```text
g(x') - g(x)
 = 2*delta*((lambda*x_i+s_i) - (lambda*x_j+s_j))
   + 2*(lambda-a_ij)*delta^2.
```

The first term is nonnegative by orientation. The second is nonnegative because
`a_ij` is `0` or `1` and `lambda >= 1`. Feasibility and the coordinate sum are
preserved, while at least one fractional coordinate becomes `0` or `1`.
Therefore the integer-valued count of fractional coordinates strictly
decreases, and after at most `n` updates the point is integral with no smaller
objective. Binary feasible points are already relaxed-feasible, so the two
global maximum values coincide.

## Reproduce

Both scripts use only the Python standard library and exact `Fraction`
arithmetic.

```bash
python repro/src/verify_c1_theorem2_exact.py
python repro/src/audit_c1_theorem2_exact.py
```

The primary verifier checks both Appendix A algebra branches symbolically and
then exercises the exact rounding invariant over all 64 simple four-vertex
graphs. The independent auditor does not import the primary verifier: it
directly compares every exact rational-lattice objective with the best binary
objective for `lambda` in `{1, 3/2, 2}`. Its negative control uses `K4`, `k=2`,
and `lambda=1/2`, where the uniform fractional point strictly beats every
binary point, confirming that the threshold guard is operative.

Expected terminal result from both scripts: `"verdict": "supports"`.
