# Local-builder scale V1

This unpublished, provider-free experiment generates valid synthetic
research-program states and compares V9 all-core context with bounded local
route/author packet models.

- `results-provider-free.json` is deterministic output from
  `experiments/local_builder_scale_probe.py` using the nominal 128,000-token
  evaluation budget.
- No judge or builder provider is invoked.
- The `v10-actual` strategy uses the actual V10 constructors with the fixture's
  oracle-correct route IDs. It measures correct-route packet size, not routing
  quality or the maximum legal route.
- Estimated tokens use compact UTF-8 bytes divided by four. They are not
  provider-reported usage.
- The full design, limitations, and measured summary are in
  `docs/LOCAL_BUILDER_SCALE_EVALUATION.md`.

Regenerate from the repository root with:

```bash
python3 -m experiments.local_builder_scale_probe \
  --input-budget-tokens 128000 \
  --output protocol/experiments/local-builder-scale-v1/results-provider-free.json
```
