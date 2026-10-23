# Distinct counts in the metrics pipeline

The usage dashboard shows "unique tenants" and "non-empty models" by summing per-minute counts, so a tenant active in 60 minutes counts 60 times.

The metrics backend supports distinct-count columns. A distinct-count column keeps a HyperLogLog sketch per time bucket and merges sketches at query time. Standard error is about 0.8% with the default precision (14). Precision 16 lowers it to about 0.4% and quadruples sketch memory.

Options:

| Option | Accuracy | Cost | Effort |
|---|---|---|---|
| Enable distinctCountColumns on TenantId and ModelId | ~0.8% error | +2 dimensions storage, about 4% more ingestion cost | config change + redeploy |
| Export raw events to the warehouse and count there | exact | warehouse compute per refresh | new pipeline |
| Keep summing, label the tiles "tenant-minutes" | wrong for the question asked | none | label change |

Implementation steps if we enable it:
1. Add `distinctCountColumns: [TenantId, ModelId]` to the metric definition.
2. Redeploy the metrics account config.
3. Switch the dashboard query to `dcount()`.
4. Backfill is not possible; counts start from the deploy date.
5. Compare one week against the warehouse export.

Links:
- https://docs.example.com/metrics/howto/distinct-count
- https://docs.example.com/metrics/faq
