set -e
G="git -c user.name=dev -c user.email=dev@example.com"
mkdir -p docs/service-guides
cat > docs/TOC.yml <<'Y'
- name: Service guides
  items:
    - name: Overview
      href: service-guides/index.yml
    - name: Contoso Cache
      href: service-guides/contoso-cache.md
Y
cat > docs/service-guides/index.yml <<'Y'
title: Service guides
items:
  - name: Contoso Cache
    href: contoso-cache.md
Y
printf '# Contoso Cache service guide\n\nGuidance for running Contoso Cache well.\n' > docs/service-guides/contoso-cache.md
git init -q -b main && $G add -A && $G commit -qm "Docs baseline"
git switch -qc add-queue-service-guide
cat > docs/service-guides/contoso-queue.md <<'M'
---
title: Architecture best practices for Contoso Queue
ms.date: 10/20/2026
---

# Architecture best practices for Contoso Queue

Contoso Queue is a managed message queue. This guide covers the five pillars.

## Reliability

TODO: dead-letter queues, zone redundancy, retry guidance.

## Security

TODO: managed identity, private endpoints, encryption at rest.

## Cost optimization

TODO: tiers, message retention, idle namespaces.

## Operational excellence

TODO: alerts on queue depth, health model, deployment slots.

## Performance efficiency

TODO: partitioning, prefetch, batch sizes.
M
python3 - <<'P'
import re
p='docs/TOC.yml'; s=open(p).read()
s+="    - name: Contoso Queue\n      href: service-guides/contoso-queue.md\n"
open(p,'w').write(s)
p='docs/service-guides/index.yml'; s=open(p).read()
s+="  - name: Contoso Queue\n    href: contoso-queue.md\n"
open(p,'w').write(s)
P
$G add -A && $G commit -qm "Add Contoso Queue service guide skeleton"
