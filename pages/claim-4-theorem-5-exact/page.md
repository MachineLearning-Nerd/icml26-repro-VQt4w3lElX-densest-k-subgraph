# Claim 4 — Theorem 5 exact landscape monotonicity

---
<!-- trackio-cell
{"type":"markdown","id":"cell_c4_exact_scope","created_at":"2026-07-22T18:24:00+00:00","title":"Exact claim and source lock"}
-->
### Claim 4 — VERIFIED by an exact certificate

The exact statement audited is Theorem 5 of arXiv:2410.07388:

> If `lambda_2 > lambda_1 > 1` and `x` is a local maximizer of (5) at `lambda_1`, then `x` is also a local maximizer at `lambda_2`.

The paper's accompanying prose says that a larger loading *can* lead to more local maxima. It does **not** say that strict growth occurs for every graph or every parameter pair. The strict-addition result below is therefore an explicit witness, not an overgeneralization.

Source: [ar5iv HTML for arXiv:2410.07388](https://ar5iv.labs.arxiv.org/html/2410.07388), fetched with a browser user agent. Full HTML SHA-256: `94dc307f35bda0046eded2944df2dd7d1a56282462cbc9998fa545b463ac5d66`. Theorem 5 source-block SHA-256: `223903b7037e252de497e6b1bbd51a090dbfff829d19eeac2350aa5f4f23d6ec`; Appendix D source-block SHA-256: `5233cc975af5c763d09f645bb9846767fd088a33ed9bf4f033b8b673082de254`.

---
<!-- trackio-cell
{"type":"markdown","id":"cell_c4_exact_certificate","created_at":"2026-07-22T18:24:00+00:00","title":"Appendix D certificate"}
-->
### Why the implication holds

Lemma 1 supplies the essential gate: because `lambda_1 > 1`, a local maximizer `x` is integral. Every integral point with `sum(x_i)=k` maximizes the squared norm on the capped simplex. Thus, for every nearby feasible `y`,

`g_lambda2(x)-g_lambda2(y) = g_lambda1(x)-g_lambda1(y) + (lambda_2-lambda_1)(||x||^2-||y||^2) >= 0`.

The two summands are nonnegative respectively by local maximality at `lambda_1` and norm maximality of integral `x`. This is the paper's Appendix D argument, expressed without a floating-point optimizer.

---
<!-- trackio-cell
{"type":"code","id":"cell_c4_exact_run","created_at":"2026-07-22T18:24:00+00:00","title":"Primary exact verifier","command":["python3","repro/src/verify_c4_theorem5_exact.py"],"exit_code":0,"duration_s":2.14}
-->
```bash
$ python3 repro/src/verify_c4_theorem5_exact.py
```

```output
claim: C4_exact_Theorem_5_landscape_monotonicity
source: ar5iv:2410.07388 Theorem 5 and Appendix D
attempt_1: exact_identity_cases=16284; capped_simplex_norm_cases=8142; pass=True
attempt_2: exhaustive_graph_lambda_pairs=43060; antecedent_local_maxima=225202; nesting_pass=True
attempt_3: strict_spurious_addition_lambda_3/2_to_5/2=True; witness_edges=0<1
controls: reversed_lambda=True; nonintegral_reference=True; lambda1_gt_1=True
theorem_scope: local-maximizer sets are nested for lambda_2>lambda_1>1
paper_prose_scope: larger lambda can lead to more local maxima; strict addition is witness-based, not universal
verdict: supports
```

The three genuinely different checks are: (1) exact `Fraction` arithmetic for the Appendix D identity and capped-simplex norm bound; (2) exhaustive strict integral local-maxima nesting for every simple graph through five vertices over a noninteger loading grid; and (3) a strict, suboptimal local-maximum witness on a three-vertex path. The witness selects the two nonadjacent leaves: it is not locally maximal at `lambda=3/2`, becomes strictly locally maximal at `lambda=5/2`, and has zero induced edges while the optimum has one.

The controls deliberately test the false reverse nesting, a nonintegral reference that fails norm maximality, and the `lambda_1>1` gate. All three are detected.

---
<!-- trackio-cell
{"type":"code","id":"cell_c4_independent_run","created_at":"2026-07-22T18:24:00+00:00","title":"Independent exact auditor","command":["python3","repro/src/audit_c4_theorem5_independent.py"],"exit_code":0,"duration_s":1.62}
-->
```bash
$ python3 repro/src/audit_c4_theorem5_independent.py
```

```output
claim: C4_independent_Theorem_5_audit
independent_landscape_sweeps=21530; strict_local_points=124604; nesting_pass=True
independent_strict_witness: low_margin=-1/4; high_margin=1/4; suboptimal_edges=0<1
fail_sensitive_reverse_nesting_rejected=True
verdict: supports
```

This auditor imports nothing from the primary verifier, uses a different rational loading grid, and uses a separate four-vertex star witness. The two exact directional margins change from `-1/4` to `+1/4`, while the selected leaf pair remains suboptimal (`0 < 1` edge).

---
<!-- trackio-cell
{"type":"markdown","id":"cell_c4_exact_result","created_at":"2026-07-22T18:24:00+00:00","title":"Result and limits"}
-->
### Result

**SUPPORTED.** The theorem's monotone inclusion is certified algebraically, stress-tested exhaustively on all simple graphs through five vertices, and independently audited. Exact strict witnesses establish the paper's softer statement that increasing the loading *can* add a suboptimal local maximum. This evidence makes no universal strict-growth claim and does not rely on random restarts.
