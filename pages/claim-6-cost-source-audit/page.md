# Claim 6 — source-exact Figure 4 cost audit

## Verdict

**REFUTED AS STATED.** The challenge says Frank-Wolfe achieves denser
subgraphs than LRBO, L-ADMM, and EXPP while incurring lower computational cost
on the real-world graphs. The paper's Figure 4 does not show blanket runtime
dominance over all those named competitors: LRBO is plotted below Frank-Wolfe
in 2,018 of 2,231 matched source-image columns across the six datasets.

This does not reject the paper's narrower statement that Frank-Wolfe has low
cost relative to algorithms achieving similar density. It rejects the scored
claim's unqualified conjunction over all three listed baselines.

## Paper source and audited scope

- Primary source: `https://ar5iv.labs.arxiv.org/html/2410.07388`
- Scope: Section 4.1 dataset sizes, Section 4.6, and the six Figure 4 runtime
  panels for Facebook, web-Stanford, com-Youtube, soc-Pokec, as-Skitter, and
  com-Orkut.
- Retrieved HTML SHA-256:
  `94dc307f35bda0046eded2944df2dd7d1a56282462cbc9998fa545b463ac5d66`
- Figure URL prefix:
  `https://ar5iv.labs.arxiv.org/html/2410.07388/assets/fig/`

The paper reports vertex counts from 4,039 through 3,072,441. Its exact prose
qualifies the runtime comparison as lower cost than algorithms that achieve
similar density; it does not say FW is faster than every named baseline.
Fetching the HTML and six source panels was outbound and used a browser-style
User-Agent.

## Deterministic source-image audit

The verifier downloads all six exact PNG panels and rejects any SHA-256 drift.
It decodes the RGBA PNG filters using only the Python standard library. Within
the data-line crop it identifies Matplotlib's exact FW blue `(31,119,180)` and
LRBO purple `(148,103,189)` core pixels. At a shared x-column, the line with the
larger image-y coordinate is the lower plotted runtime. Legend pixels are
excluded by the crop.

```bash
python repro/src/audit_claim6_figure4_cost.py
```

```output
claim=Figure 4 blanket computational-cost dominance over listed baselines
source=ar5iv Figure 4 exact PNG panels
image_hashes_matching=6/6
dataset=Facebook matched_columns=373 lrbo_lower_runtime_columns=299
dataset=web-Stanford matched_columns=362 lrbo_lower_runtime_columns=330
dataset=com-Youtube matched_columns=432 lrbo_lower_runtime_columns=432
dataset=soc-Pokec matched_columns=354 lrbo_lower_runtime_columns=322
dataset=as-Skitter matched_columns=431 lrbo_lower_runtime_columns=431
dataset=com-Orkut matched_columns=279 lrbo_lower_runtime_columns=204
matched_columns_total=2231
lrbo_lower_runtime_columns_total=2018
lrbo_lower_runtime_fraction=90.45%
datasets_with_any_lrbo_lower_runtime=6/6
datasets_with_lrbo_lower_runtime_majority=6/6
verdict=REFUTED_AS_STATED
reason=Figure 4 does not show FW cheaper than every named competitor; LRBO is plotted lower in 90.45% of matched source-image columns.
```

## Source panel hashes

| Panel | SHA-256 |
| --- | --- |
| `Facebook_time.png` | `b711ecefd1229551aa82a4e75df7cb7bfd56a84822ac5cb25fac7c4baedb1d7e` |
| `web-Stanford_time.png` | `c14b11a567bc577305e53470b225ba453bdfcc66651bb23702be7beda6f7e590` |
| `com-Youtube_time.png` | `d667d1d1a78196843da73fbd352b2c44057ccc5190179cdc4ad907a623dc2d31` |
| `soc-Pokec_time.png` | `e8e02d1b4d5cbe05d90b075f1b84b80048e1ea6361252a5acb4b65dccad150f6` |
| `as-Skitter_time.png` | `510c9517cf11db59fff6a9c447cb84155f4e57c869a596b5d75231f3d63d4ada` |
| `com-Orkut_time.png` | `a8a312d3ac2e6144dc89f3b9f9fb2b697eac1d84ee5f5f2ee6278164364ec018` |

## Reproduction boundary

This is an exact audit of the authors' published real-dataset evidence, not a
new execution of LRBO, L-ADMM, EXPP, and FW on the million-vertex inputs. That
distinction is deliberate: the source figures themselves are sufficient to
falsify the challenge's blanket cost-dominance wording.
