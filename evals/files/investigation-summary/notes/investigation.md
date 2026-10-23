# Checkout latency spike, notes

Tue 09:12 p95 checkout latency 2.1s (normal 380ms) since ~08:40. Started at deploy of cart-service 4.18? checked: deploy was 08:55, spike starts 08:40. not the deploy.

09:20 looked at DB. CPU 35%, no slow queries over 200ms in pg_stat_statements top 20. connection pool on checkout-api: 48/50 in use, waiting threads up to 30. hmm.

09:31 maybe Redis? redis latency p99 1.2ms. fine. evictions 0.

09:40 checked payment provider status page: green. our payment-adapter p95 340ms, normal.

09:52 pool exhaustion on checkout-api. who holds connections? thread dump: 41 threads in InventoryClient.reserve() waiting on HTTP to inventory-service, holding a DB transaction open while waiting.

10:05 inventory-service p95 1.8s since 08:38. their HPA hit max replicas (12/12) at 08:37. traffic up 2.4x, marketing push email went out 08:30 (confirmed with growth team).

10:15 so: inventory slow -> checkout holds DB tx during remote call -> pool exhausted -> everything on checkout-api queues.

10:20 tried raising checkout pool to 80 in staging. helps a bit but DB max_connections 200 shared by 4 services, risky.

10:41 inventory team raised HPA max to 30. inventory p95 back to 210ms at 10:52. checkout p95 back to 410ms at 10:58.

11:30 follow-ups discussed with Sam (inventory) and Lee (checkout):
- move InventoryClient.reserve() call out of the DB transaction (Lee, this sprint)
- inventory HPA max stays 30, alert at 80% of max (Sam)
- growth team to give a heads-up before mass emails (Sam asks them)
- pool size stays 50

dead ends: deploy, DB, Redis, payment provider.
