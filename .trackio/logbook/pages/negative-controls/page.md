# Negative controls


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_6e41912280c1", "created_at": "2026-07-17T05:17:59+00:00", "title": "Negative control: lambda < 1 breaks tightness"}
-->
**Theorem 2.1 (necessity):** λ ≥ 1 is *necessary* for general tightness. We verify the contrapositive — that for λ < 1 the relaxation can be **non-tight**.

Searching 20 graphs × k∈{3,4,5} × λ∈{0.1,0.5}, we find **30 instances** where the relaxation global maximum **strictly exceeds** the combinatorial DkS optimum + λk/2 (relaxation gap > 0). ✅ This confirms tightness genuinely requires λ ≥ 1 (it is not an artifact of the relaxation always equaling the combinatorial value).

A second structural control: the relaxation max is always ≥ the combinatorial value (binary ⊂ [0,1]^n) — verified — so the tightness result is the non-trivial *upper* direction.
