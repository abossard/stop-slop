# Health models service guide

A health model shows the health of a workload as a tree of entities. Each entity gets its state from signals, and parents roll up the states of their children.

## Reliability

Model each zone as its own entity so a zone outage shows as degraded, not unhealthy. Set the root's aggregation to "worst of" only when any child failure takes the workload down.

## Operational excellence

Use the health model in deployment pipelines. A rollout stops when the model turns degraded.

### Worked example

The workload root has three children:

- **Workload runtime**: request success rate and latency from the application.
- **Validation tests**: synthetic transactions that run every five minutes against the public endpoint.
- **Bug reports**: count of open severity 1 and 2 bugs from the tracker.

The root uses "worst of" aggregation. A failing validation test turns the root unhealthy even when the runtime signals are green.

## Cost optimization

Signals that query logs cost more than metric signals. Prefer metrics, and set log signal intervals to 5 minutes or more.
