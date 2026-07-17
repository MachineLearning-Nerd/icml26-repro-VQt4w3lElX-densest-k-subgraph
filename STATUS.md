# STATUS — DkS Penalty Relaxation Landscape (`VQt4w3lElX`)

**Session:** NewPaper. **Last updated:** 2026-07-17. **State:** locally complete; GitHub push pending; HF queued.

## Source
- arXiv 2410.07388 (Lu, Sidiropoulos, Konar). Clean-room from PDF.
- All 3 claims CPU-feasible via exact KKT enumeration on small graphs.

## Evidence (locally complete)
- **C1 verified (exact):** relaxation tight for λ≥1 — 180/180 cases, gap 0.0;
  30 λ<1 failures confirm necessity (Thm 2.1).
- **C2 verified (exact):** dichotomy at λ=1.5 — 8,605 stationary points all
  classify as integral-local-max (853) or non-integral-strict-saddle (7,752);
  min ascent curvature 0.625.
- **C3 verified:** saddle-escaping FW reaches integral local-max in 144/144 runs.
- **24/24 pytest tests pass** (28 s).
- Trackio complete/tagged/pinned/command-captured.

## Next
- Push GitHub `MachineLearning-Nerd/icml26-repro-VQt4w3lElX-densest-k-subgraph`.
- Publish `DineshAI/VQt4w3lElX` after HF quota reset; verify tags/bucket; `under_verdict`.
