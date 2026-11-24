# Examples: from slop to no slop

Each slop text below is an original, word for word. Each text under "No slop" follows [the skill](../skills/stop-slop/SKILL.md): it keeps the facts of its original and adds none.

## Short texts

### Example 1: Building products

Slop:

> "Here's the thing: building products is hard. Not because the technology is complex. Because people are complex. Let that sink in."

No slop:

> Building products is hard because people are complex. The technology is not the reason.

What changed:

- "Here's the thing" and "Let that sink in" hold no point, so they are gone.
- "Not because the technology is complex. Because people are complex." were two fragments without a main verb. They are now parts of full sentences.

### Example 2: Teams and alignment

Slop:

> "It turns out that most teams struggle with alignment. The uncomfortable truth is that nobody wants to admit they're confused. And that's okay."

No slop:

> Most teams struggle with alignment. Nobody wants to admit they're confused.

What changed:

- "It turns out that", "The uncomfortable truth is that" and "And that's okay" hold no point, so they are gone.
- The two statements keep every word.

### Example 3: Competition

Slop:

> "In today's fast-paced landscape, we need to lean into discomfort and navigate uncertainty with clarity. This matters because your competition isn't waiting."

No slop:

> We need to accept discomfort and to decide clearly while the situation is uncertain, because your competition is not waiting.

What changed:

- "In today's fast-paced landscape" holds no point, so it is gone.
- "Lean into discomfort" and "navigate uncertainty with clarity" are figures of speech, and a translator would have to ask what they mean. The rewrite uses plain verbs: accept and decide.

### Example 4: Speed, quality, cost

Slop:

> "Speed. Quality. Cost. You can only pick two. That's it. That's the tradeoff."

No slop:

> You can have only two of the three: speed, quality and cost.

What changed:

- "Speed. Quality. Cost." were three fragments. They are now part of one full sentence.
- "That's it. That's the tradeoff." repeat the point, so they are gone.

### Example 5: The best teams

Slop:

> "What if I told you that the best teams don't optimize for productivity? Here's what I mean: they optimize for learning. Think about it."

No slop:

> The best teams optimize for learning and not for productivity.

What changed:

- The question, "Here's what I mean" and "Think about it" hold no point. The claim is now one statement.

## Technical texts

Each slop text in this part is real output, quoted word for word from a single message in an engineering blueprint or a chat transcript.

### Example 6: What a test asserts

Slop:

> "`Run_TerminatesANonYieldingLoop_WithinTheTimeout` runs `while (true) {}` and asserts bounded elapsed time against `HealthModelScriptRuntime.Timeout`, not merely that an error came back."

No slop:

> `Run_TerminatesANonYieldingLoop_WithinTheTimeout` runs `while (true) {}`. It asserts that the elapsed time stays within a bound that comes from `HealthModelScriptRuntime.Timeout`. It does not only assert that an error came back.

What changed:

- "Asserts bounded elapsed time against" packed a statement into a row of words. It is now a clause with a subject and a verb.
- "Not merely that an error came back" became its own sentence.

### Example 7: Why memory is not asserted

Slop:

> "NOTE: memory is deliberately NOT asserted — `MemoryLimitConstraint` self-disables across thread hops (`Environment.CurrentManagedThreadId != _initialThreadId`), so timeout + statement ceiling are the load-bearing limits."

No slop:

> Memory is not asserted, and that is on purpose. `MemoryLimitConstraint` turns itself off when execution moves to another thread (`Environment.CurrentManagedThreadId != _initialThreadId`). The limits that still apply are the timeout and the ceiling on the number of statements.

What changed:

- "Self-disables across thread hops" used a coined phrase. The rewrite says when this happens: "when execution moves to another thread".
- "Timeout + statement ceiling are the load-bearing limits" used a plus sign and a figure of speech. It is now "the limits that still apply".
- "NOTE:" and the capitals in "NOT" are gone.

### Example 8: How to check a guard

Slop:

> "The guard must fail on a mutation, not merely succeed on a clean tree. A guard only ever run against an unchanged tree is a vacuous green. The mutate-and-rerun step is the load-bearing half."

No slop:

> The guard must fail on a mutation. It is not enough that it succeeds on a clean tree. When a guard has only ever run against an unchanged tree, a pass proves nothing. The step that matters is to mutate the tree and to run the guard again.

What changed:

- "A vacuous green" was a coined phrase. It is now "a pass proves nothing".
- "A guard only ever run against an unchanged tree" became a clause with its own verb: "when a guard has only ever run against an unchanged tree".
- "The mutate-and-rerun step is the load-bearing half" became a sentence that says what to do.

### Example 9: A required detail

Slop:

> "This is a required, load-bearing implementation detail for C24/C29/C31, not an optional nicety."

No slop:

> C24, C29 and C31 depend on this detail of the implementation, so it is required.

What changed:

- "Load-bearing" was a figure of speech. The sentence now says what depends on the detail.
- "Not an optional nicety" repeats "required", so it is gone.
- "C24/C29/C31" is written with commas and "and".

### Example 10: Signals that the inspector observed

Slop:

> "Every load-bearing live signal (C1, C3, C4a, C4b, C7, C11) was **independently observed** by this inspector — not taken from replicate — so the external-state dependency driver is mitigated."

No slop:

> As the inspector, I myself observed every live signal that matters: C1, C3, C4a, C4b, C7 and C11. I took none of them from replicate. This mitigates the driver "dependency on external state".

What changed:

- "The external-state dependency driver" stacked three nouns. It is now the driver "dependency on external state".
- "Was independently observed by this inspector" became "I myself observed".
- The two dashes held a second statement. It is now its own sentence.

### Example 11: The state of the SQL

Slop:

> "The key insight: **the SQL hasn't been updated to Level 1 yet** — the `DISTINCT` + `LOWER()` is still a proposal, not deployed."

No slop:

> The SQL has not been updated to Level 1 yet. `DISTINCT` and `LOWER()` are still a proposal and are not deployed.

What changed:

- "The key insight:" holds no point, so it is gone.
- The dash joined two statements. Each one is now a sentence, and the plus sign is now "and".

### Example 12: A reproduced failure

Slop:

> "It exactly reproduced every real corridor pick for all 7 edges and pinpointed `a->p`'s `corr(2, want=206)` call as the exact failure."

No slop:

> It reproduced the real corridor pick of each of the 7 edges exactly. It located the failure at the call `corr(2, want=206)` of `a->p`.

What changed:

- "`a->p`'s `corr(2, want=206)` call" put two names in front of the noun. It is now "the call `corr(2, want=206)` of `a->p`".
- "Every" and "all 7" counted the same edges twice, and "exact" came twice. Each is said once.

### Example 13: The size of a diff

Slop:

> "Clean surgical diff: **1 file, +9/−33 lines.** Only two things changed:"

No slop:

> The diff changes 1 file. It adds 9 lines and removes 33. Only two things changed:

Slop, from a different session:

> "All 4 fixes correct, build clean, syntax clean."

No slop:

> All 4 fixes are correct, the build is clean and the syntax is clean.

What changed:

- Neither text had a verb in its first statement. Both are now full sentences.
- "Clean" and "surgical" rated the diff and added no fact to the numbers, so they are gone.

### Example 14: Three mistakes in criteria

Slop:

> *"Anything that would make these criteria vacuous?"* Three traps, each closed explicitly: measuring the ablation on cached points instead of regenerated ones; measuring long-label containment on the shipped examples; and proving NC-30 against a library the generator wrote in the same process without a fresh decode. Each criterion above names its boundary to block exactly that.

No slop:

> Three mistakes would let these criteria pass without proving anything. The first is to measure the ablation on cached points instead of regenerated ones. The second is to measure the containment of long labels on the shipped examples. The third is to prove NC-30 against a library that the generator wrote in the same process, without a fresh decode. Each criterion above names its boundary, and that boundary rules out its mistake.

What changed:

- "A library the generator wrote" got its "that".
- "Long-label containment" became "the containment of long labels".
- The question to nobody became a statement, and "vacuous" became "pass without proving anything".
- The three items of the list are now three sentences.

## Texts from repositories

Each slop text in this part is quoted word for word from the git history of a public repository. Each source line gives the two commits between which the owner edited the text.

### Example 15: When to run a skill

Source: minime (`abossard/virtucon`), `5b9d75be` -> `725532b5`, `skills/extract/SKILL.md`

Slop:

> Trigger: the coherent task or session boundary has been reached with no active criteria and no blocking issue, or the user explicitly requested extract. It turns raw outcomes into durable knowledge under `raw/`, `wiki/`, and `schema.md`.

No slop:

> Run extract when a task or a session has reached a coherent boundary with no active criteria and no blocking issue, or when the user asks for it explicitly. It turns raw outcomes into durable knowledge under `raw/`, `wiki/`, and `schema.md`.

What changed:

- "The coherent task or session boundary has been reached" put its nouns in a row and its verb in the passive. The task or the session is now the subject.
- "Trigger:" became "Run extract when", and "requested extract" became "asks for it".

### Example 16: A placeholder entity

Source: Azure/azure-monitor-baseline-alerts, `191e5ae4` -> `23d41f17`, `docs/content/patterns/alz/Overview/Health-Models-Adoption.md`

Slop:

> The current pull request gives every child model one healthy dummy entity to confirm the deployment succeeded. The diagram labels that entity as a deployment check because it does not measure domain health. Replace it with the platform and system flows the domain provides.

No slop:

> The current pull request gives every child model one healthy dummy entity to confirm that the deployment succeeded. The diagram labels that entity as a deployment check, because the entity does not measure the health of the domain. Replace it with the platform flows and the system flows that the domain provides.

What changed:

- "The platform and system flows the domain provides" got its "that".
- "Because it does not measure" could point at the diagram or at the entity. The rewrite names the entity.

### Example 17: A health model for each domain

Source: Azure/azure-monitor-baseline-alerts, `ad3b75f4` -> `191e5ae4`, `docs/content/patterns/alz/Overview/Health-Models-Adoption.md`

Slop:

> For each ALZ domains you might create a specific health model that represents the system flows of that domain, with the resources that contribute to it. You can use a mix of manually build entities and modelling and combine it with discovery rules for places where you don't control the life cycle of the contributing resources.

No slop:

> For each ALZ domain you might create a specific health model. The model represents the system flows of that domain, with the resources that contribute to it. You can build and model some entities manually, and you can combine them with discovery rules. Use the rules in places where you do not control the life cycle of the contributing resources.

What changed:

- Each of the two sentences held two statements. They are now four sentences.
- "A mix of manually build entities and modelling" became a clause with verbs: "build and model some entities manually".
- "Each ALZ domains" is corrected to "each ALZ domain".

### Example 18: A checklist

Source: minime (`abossard/virtucon`), `5b9d75be` -> `725532b5`, `skills/replicate/SKILL.md`

Slop:

> - Tick `[x]` on the criterion when its test goes green. **Do this immediately. Do not batch check-offs for later.**
> - Paste raw shortened evidence (command output, test result, key lines) directly under the criterion line. Every `[x]` must have its proof inline — a checkmark without evidence is not a checkmark.
> - If you resolve an unknown during implementation, add it to the Decisions table with its VOI level and source.
> - If you discover a requirement not in the original EARS, note it but do NOT add it to the criteria. That's review's job.
> - Work only on the current correction's active criteria. Archived criteria remain out of scope unless the blueprint marks their baseline proof invalidated.

No slop:

> - Tick `[x]` on the criterion when its test passes. **Do this immediately. Do not collect ticks for later.**
> - Paste raw shortened evidence (command output, test result, key lines) directly under the line of the criterion. Every `[x]` must have its proof inline. A checkmark without evidence is not a checkmark.
> - If you resolve an unknown during implementation, add it to the Decisions table with its VOI level and source.
> - If you discover a requirement that is not in the original EARS, note it but do not add it to the criteria. That is the job of review.
> - Work only on the active criteria of the current correction. Archived criteria remain out of scope unless the blueprint marks their baseline proof as invalidated.

What changed:

- "Batch check-offs" was a coined phrase. It is now "collect ticks".
- "A requirement not in the original EARS" became "a requirement that is not in the original EARS".
- "The current correction's active criteria" became "the active criteria of the current correction".
- The third bullet is unchanged, because it has none of the six constructions.

### Example 19: Alert rules without dependencies

Source: Azure/azure-monitor-baseline-alerts, `ad3b75f4` -> `191e5ae4`, `docs/content/patterns/alz/Overview/Health-Models-Adoption.md`

Slop:

> What it does not carry is dependency. Every alert rule is deployed independently of every other one, so nothing in the system knows that an ExpressRoute circuit, a firewall and a gateway are three parts of one connectivity service. Three alerts fire, and a human decides whether that adds up to an outage.

No slop:

> It holds no information about dependencies. Every alert rule is deployed independently of every other one. As a result, nothing in the system records that an ExpressRoute circuit, a firewall and a gateway are three parts of one connectivity service. Three alerts fire, and a person decides whether they add up to an outage.

What changed:

- "Nothing in the system knows" gave a thing a human verb. It is now "records".
- "What it does not carry is dependency" put the statement inside a clause that starts with "what". The subject now comes first.

### Example 20: Three benefits

Source: Azure/azure-monitor-baseline-alerts, `ad3b75f4` -> `191e5ae4`, `docs/content/patterns/alz/Overview/Health-Models-Adoption.md`

Slop:

> - **Fewer alerts, not fewer measurements.** Alerting moves from every rule to the entities you decide matter, so notification volume tracks the number of real problems rather than the size of the estate.
> - **Criticality is expressed once, in the graph.** A dependency says which components a service actually needs, so importance comes from position in the graph instead of a severity set per rule.
> - **Recovery is visible, and measurable.** You see when something clears, and how long it was broken.

No slop:

> - **Fewer alerts, not fewer measurements.** You no longer alert on every rule. You alert on the entities that you decide are important. The number of notifications therefore follows the number of real problems, and not the size of the estate.
> - **Criticality is expressed once, in the graph.** A dependency shows which components a service actually needs. The importance of a component therefore comes from its position in the graph, and not from a severity that is set for each rule.
> - **Recovery is visible, and measurable.** You see when something clears, and how long it was broken.

What changed:

- "A dependency says" gave a thing a human verb. It is now "shows".
- "The entities you decide matter" became "the entities that you decide are important".
- "Notification volume tracks" became "the number of notifications follows".
- "A severity set per rule" became "a severity that is set for each rule".
- The three labels and the third bullet are unchanged.

### Example 21: What `harvest` reads

Source: minime (`abossard/virtucon`), `2e859b26` -> `e4259718`, `assets/ORCHESTRATION.md`

Slop:

> `harvest` also reads the persisted task brief's Decisions table and "Discovered during review" section to learn what categories of criteria the EARS consistently misses — that meta-learning feeds the director's process memory and sharpens future EARS nudges.

No slop:

> `harvest` also reads two parts of the persisted task brief: the Decisions table and the section "Discovered during review". From these it finds the categories of criteria that the EARS consistently misses. This result goes into the director's process memory and makes later EARS nudges more precise.

What changed:

- The slop sentence put a long row of nouns in front of the two things that `harvest` reads. The rewrite names the brief first and then its two parts.
- "What categories of criteria the EARS consistently misses" became "the categories of criteria that the EARS consistently misses".
- "Meta-learning" was a coined label. It is now "this result".
- "Feeds" and "sharpens" were figures of speech. They are now "goes into" and "makes more precise".

## Sentences without a point

Slop:

> "It's important to note that security plays a crucial role."

No slop: leave the sentence out. It states no fact that a reader can use, and "security plays a role" gives a thing a human verb. Write the fact that it announces.

Slop:

> "In an era of unprecedented digital transformation, organizations must navigate..."

No slop: leave the opening out. Write what changed and what the reader should do.

## Whole inputs

Seven inputs and the text that the skill writes for each. Each slop text is an original input, word for word: the request as it was typed and, where the request names one, the file. Each case comes from a correction that the owner made to an agent's writing, and the files are synthetic copies.

### Example 22: A README

Slop, the request:

```text
clean up README.md: keep every fact, cut the filler and the AI-sounding phrasing. edit the file in place.
```

Slop, `README.md`:

```markdown
# 🚀 PulseCheck

## 🌟 Overview

In today's fast-paced digital landscape, monitoring is more important than ever. PulseCheck is a robust, lightweight, and comprehensive uptime monitoring solution that seamlessly empowers teams to stay on top of their services. It's not just a monitoring tool — it's a complete peace-of-mind platform.

## ✨ Key Features

- **Blazing Fast Checks** — PulseCheck runs HTTP checks every 30 seconds by default, ensuring you are always informed.
- **Smart Alerting** — Alerts are sent to Slack or email after 3 consecutive failures, which helps reduce noise and keeps your team focused on what truly matters.
- **Flexible Configuration** — All configuration lives in a single `pulse.yaml` file, making it incredibly easy to get started.

## 🛠️ Getting Started

Getting started with PulseCheck is a breeze! Simply follow these easy steps:

1. First, make sure you have Python 3.12 or newer installed on your machine.
2. Next, install the dependencies by running `make install`.
3. Then, start the development server with `make dev`. The dashboard will be available at http://localhost:8080.
4. Finally, set the `PULSE_SLACK_WEBHOOK` environment variable to enable Slack alerts.

## 💡 Why PulseCheck?

It's important to note that PulseCheck was deliberately designed with simplicity in mind. Rather than overwhelming you with endless options, it focuses on what really matters: knowing when your services are down. Whether you're a solo developer or part of a large team, PulseCheck adapts to your needs.

## 🤝 Contributing

We warmly welcome contributions from the community! Please feel free to open an issue or submit a pull request. Every contribution, no matter how small, makes a difference.

## 📄 License

PulseCheck is proudly released under the MIT License.
```

No slop:

```markdown
# PulseCheck

PulseCheck monitors the uptime of your services. It runs an HTTP check every 30 seconds by default. After 3 failures in a row it sends an alert to Slack or by email, which reduces noise.

All configuration is in one file, `pulse.yaml`.

## Getting started

1. Install Python 3.12 or newer.
2. Run `make install` to install the dependencies.
3. Run `make dev` to start the development server. The dashboard is at http://localhost:8080.
4. Set the `PULSE_SLACK_WEBHOOK` environment variable to turn on Slack alerts.

## Contributing

Contributions are welcome. Open an issue or submit a pull request.

## License

MIT License.
```

What changed:

- The rewrite starts from the points that a new user needs: what the tool does, how to start it, how to contribute, and the license.
- "Uptime monitoring solution" stacked three nouns. A verb now says what the tool does.
- "All configuration lives in a single file" gave a thing a human verb. The configuration now "is in one file".
- The praise ("robust", "seamlessly", "a breeze") held no fact, so no point came from it.

### Example 23: A status for the user

Slop:

```text
Facts: `npm run login` works and opens Edge with a separate profile for sign-in/MFA. Playwright's built-in `browser` fixture lives for a whole worker. Each test needs its own copied persistent profile and browser context. Our adapter tries to make `browser` test-scoped and Playwright rejects that override before launching anything, so the preflight and the minimal/rich E2E tests cannot run yet. I fix the adapter; the user does not need to do anything.

The user asks: and whats the issue still?
```

No slop:

> The tests cannot run yet. Sign-in works: `npm run login` opens Edge with a separate profile for sign-in and MFA.
>
> Playwright keeps its built-in `browser` fixture for as long as a worker runs. Each of our tests needs its own browser context and its own copy of the persistent profile. Our adapter tries to create `browser` once per test. Playwright rejects that change before it launches anything. As a result, the preflight cannot run yet, and neither can the minimal and the rich end-to-end test.
>
> I am fixing the adapter. You do not need to do anything.

What changed:

- The answer to the question comes first.
- "The fixture lives for a whole worker" gave a thing a human verb. Playwright now keeps the fixture.
- "Test-scoped" was a label. The answer says what it means: once per test.
- "Copied persistent profile" became "its own copy of the persistent profile", and "minimal/rich E2E tests" became "the minimal and the rich end-to-end test".

### Example 24: An explanation in simple words

Slop:

```text
Context: a layered graph layout for health model entities now sorts the node ids once at the start so the same model always produces the same picture. You said: 'so DFS start order, Kahn queue seeding, and rank bucket order are fixed.' can you ELI5 that? make it very short ELI5, trying to avoid specialized terms
```

No slop:

> Three things in the layout depend on the order of the nodes: where it starts, which nodes it handles first, and how it arranges the nodes in each row. The nodes are now sorted before anything else happens, so all three come out the same every time.

What changed:

- "DFS start order", "Kahn queue seeding" and "rank bucket order" were three noun stacks, each a label for a step. Each one now says what the layout does, without the name of an algorithm.
- "Are fixed" can mean repaired or constant. The answer says "come out the same every time".

### Example 25: A summary of an incident

Slop, the request:

```text
summarize the checkout latency investigation from notes/investigation.md for the team channel. write it to SUMMARY.md
```

Slop, `notes/investigation.md`:

```markdown
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
```

No slop:

> Checkout was slow on Tuesday from about 08:40 to 10:58. The 95th percentile of the checkout latency was 2.1 seconds, and it is normally 380 milliseconds.
>
> The cause was inventory-service. An email for a marketing push went out at 08:30, and traffic rose to 2.4 times its normal level. At 08:37 the autoscaler of inventory-service reached its maximum of 12 replicas, and the service became slow. Checkout keeps a database transaction open while it calls inventory-service. The open transactions used up the pool of database connections. Every request to checkout-api then had to wait.
>
> At 10:41 the inventory team raised the maximum to 30 replicas. At 10:58 the checkout latency was back to 410 milliseconds.
>
> Follow-ups:
>
> - Lee moves the call to inventory-service out of the database transaction in this sprint.
> - Sam keeps the maximum at 30 replicas and adds an alert at 80% of that maximum.
> - Sam asks the growth team to tell us before they send a mass email.
> - The pool of checkout-api stays at 50 connections.
>
> We ruled out the deploy of cart-service, the database, Redis and the payment provider.

What changed:

- The summary starts from the points that the team needs: what happened, the cause, the fix and the follow-ups. The four checks that found nothing became one sentence.
- The arrows ("inventory slow -> checkout holds DB tx during remote call -> pool exhausted") became sentences with a subject and a verb, so the reader sees what caused what.
- "Marketing push email" stacked three nouns. It is now "an email for a marketing push".
- "p95", "HPA" and "DB tx" are written out.

### Example 26: A comment on an issue

Slop:

```text
Investigation result: in Windows High Contrast, the browser forces system colors (forced-colors: active) on borders, backgrounds and text, even over !important. Our .hc-* overrides only set background-color; health-state borders use hardcoded hex colors, so all states look the same. Possible fixes: forced-color-adjust: none on graph nodes, or @media (forced-colors: active) mapping states to system colors (LinkText, Highlight, CanvasText, GrayText). References: MDN forced-colors, MDN forced-color-adjust, W3C css-color-adjust-1.

write a comment with that information for the issue about the high contrast graph to COMMENT.md. make it suggestions and hypothesis, super brief, just as ideas to try out. references are the most important thing
```

No slop:

> In Windows High Contrast, all health states look the same in the graph. My guess at the cause: the browser replaces the colors of borders, backgrounds and text with system colors (`forced-colors: active`), even where a rule says `!important`. Our `.hc-*` overrides set only `background-color`, and the borders that show the health state use hex colors that are written into the CSS.
>
> Two ideas to try:
>
> - Set `forced-color-adjust: none` on the graph nodes.
> - In `@media (forced-colors: active)`, map the states to system colors (`LinkText`, `Highlight`, `CanvasText`, `GrayText`).
>
> References:
>
> - MDN, forced-colors: https://developer.mozilla.org/en-US/docs/Web/CSS/@media/forced-colors
> - MDN, forced-color-adjust: https://developer.mozilla.org/en-US/docs/Web/CSS/forced-color-adjust
> - W3C, CSS Color Adjustment Module Level 1: https://www.w3.org/TR/css-color-adjust-1/

What changed:

- "Health-state borders" and "hardcoded hex colors" became clauses: "the borders that show the health state" and "hex colors that are written into the CSS".
- The two fixes had no verb. Each one now says what to do.
- "My guess at the cause" marks the finding as a hypothesis, which the request asks for.
- Each reference has its own line and its link, because the request calls the references the most important part.

### Example 27: A design decision

Slop:

```text
Write ADR-0040 in docs/adr/ using docs/adr/0000-adr-template.md: Orleans ingress goes Azure Front Door -> internal load balancer -> pods, with no NGINX ingress controller. Each pod co-hosts ASP.NET Core (Kestrel, port 8080) and the Orleans silo (ADR-0003), so the in-process client routes grain calls with the silo's cluster view. Front Door (ADR-0020) already provides WAF, TLS, path routing and global anycast.
```

No slop, `docs/adr/0040-orleans-ingress.md`:

```markdown
# ADR-0040: Orleans traffic enters through Azure Front Door, with no NGINX ingress controller

- Status: proposed
- Date: 2026-11-24

## Context

Each pod hosts both ASP.NET Core (Kestrel, port 8080) and the Orleans silo (ADR-0003). The Orleans client therefore runs in the same process as the silo, and it uses the silo's view of the cluster to route each call to its grain.

Azure Front Door (ADR-0020) already provides the WAF, TLS, routing by path and a global anycast address.

## Decision

Traffic for Orleans enters through Azure Front Door, passes an internal load balancer and reaches the pods. We do not run an NGINX ingress controller.

## Consequences

- The load balancer can send a request to any pod, because the client in that pod routes the call to its grain.
- We have no ingress controller to deploy and to update.

## Links

- [ADR-0003: Orleans as the application framework](0003-application-framework.md)
- [ADR-0020: Azure Front Door as the global entry point](0020-global-entry-point.md)
```

What changed:

- The arrows became a sentence that says where the traffic goes.
- "The in-process client routes grain calls with the silo's cluster view" packed three ideas. The record says where the client runs, what it uses, and what it routes.
- "Path routing" and "global anycast" became "routing by path" and "a global anycast address".
- "NGINX ingress controller" stays, because it is the name that people use for the product.
- The request states no consequences. The two in the record follow from its facts.

### Example 28: A note in a README

Slop:

```text
[review] MEDIUM: provider.bicep healthEndpoints output has a downstream consumer nobody knows about

tools/dashboard/deploy.ps1 parses healthEndpoints from the provider deployment. infra/provider/README.md does not mention this consumer; a refactor of the output will break the dashboard pipeline.

Suggested: add a one-line note in the README that healthEndpoints is parsed by tools/dashboard/deploy.ps1.

please add a note to infra/provider/README.md
```

No slop, the "Outputs" section of `infra/provider/README.md`:

```markdown
## Outputs

- `providerId`: resource ID of the registration.
- `healthEndpoints`: array of `{ region, url }` objects. `tools/dashboard/deploy.ps1` parses this output. If you change the output, change that script as well, or the dashboard pipeline breaks.
```

What changed:

- "provider.bicep healthEndpoints output" stacked three names. The note stands next to the output, so it says "this output".
- "A downstream consumer nobody knows about" was a label for one script. The note names the script.
- "A refactor of the output will break the dashboard pipeline" became a condition with a person who acts.
