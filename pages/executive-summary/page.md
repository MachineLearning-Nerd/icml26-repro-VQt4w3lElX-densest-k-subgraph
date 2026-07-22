# Executive summary

---
<!-- trackio-cell
{"type":"markdown","id":"cell_exec_vqt","created_at":"2026-07-19T09:14:40+00:00","title":"Executive summary","pinned":true,"pinned_at":"2026-07-19T09:14:40+00:00"}
-->
The first theorem revision moved C1 and C2 to `verified`; C3 remained `toy`
because its six-step convergence chain cited the paper's theorems instead of
deriving them and its concrete control used only a regular-graph saddle. This
revision directly closes both gaps.

The audit also corrects the evidence record: the earlier C3 optimizer used a
top-eigenvector perturbation, exact line search, and a 200-escape snap.  Those
choices are not Algorithm 1 and are now explicitly treated only as empirical
corroboration.  The scored evidence uses the paper's adaptive FW step and
`k`-th/`(k+1)`-th coordinate-transfer escape, records the non-integer
`1<lambda<2` analysis scope, and fails closed if a proof prerequisite is absent.

The C3 certificate now derives the two standard-step gain cases, finite gap
trigger time, projection residual inequality, local `gamma=1` finish, explicit
coordinate-transfer escape floor, objective ceiling, finite escape count, and
finite trigger reductions. The only imported dependency—the Luo-Tseng local
polyhedral error bound—is stated precisely.

The executed audit matches Section 5.1: official SNAP Facebook data (4,039
nodes, 88,234 edges), `k=20`, `lambda=1.5`, and uniform initialization. The
printed step reaches an integral local maximum in 35 updates with gap 0 and a
final `gamma=1` jump. The paper's constant-denominator control remains
fractional at all 4,039 coordinates with gap `0.131515` after 50,000 updates.

## Scope & cost

| Item | This reproduction | Full independent re-proof |
| --- | --- | --- |
| Scope | Universal C1/C2; equation-level C3; original paper-scale benchmark | Re-prove imported Luo-Tseng error bound from first principles |
| Hardware | Local CPU | Not compute-bound |
| Time | <1 s proof audit; ~9 s benchmark; 8.47 s tests | Mathematical peer review |
| Cost | No paid compute | Research effort |
| Outcome | All DAGs close; paper-scale audit passes; 35/35 tests pass | Not claimed |

---
<!-- trackio-cell
{"type":"figure","id":"cell_poster_vqt","created_at":"2026-07-19T09:14:41+00:00","title":"Universal proof audit poster","pinned":true,"pinned_at":"2026-07-19T09:14:41+00:00"}
-->
````html
<!-- poster_embed.html -->
<iframe src="poster_embed.html" title="Densest-k-Subgraph universal proof audit poster" width="100%" height="700" loading="lazy"></iframe>
````
