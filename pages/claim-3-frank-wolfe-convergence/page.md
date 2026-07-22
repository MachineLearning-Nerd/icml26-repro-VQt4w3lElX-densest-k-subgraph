# Claim 3 — Frank-Wolfe convergence


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_1208de277749", "created_at": "2026-07-17T05:17:34+00:00", "title": "C3 verdict: saddle-escaping FW reaches integral local-max, finite steps"}
-->
**Claim 3 (Section 4):** the saddle-escaping Frank-Wolfe algorithm achieves **finite-step exact convergence** to an integral local maximizer (explaining why FW yields integral solutions without rounding).

- **144/144** random-init runs reach an **integral local maximizer** (median few steps; FW + Hessian-ascent saddle escape + FW-vertex target).
- By the dichotomy (C2), any integral stationary point reached at λ=1.5 is automatically a local maximizer.

The LMO over the hypersimplex returns the indicator of the k largest gradient entries; exact 1-D line search is used. The escape perturbs along the top eigenvector of the reduced Hessian when the FW gap vanishes at a non-integral point.
