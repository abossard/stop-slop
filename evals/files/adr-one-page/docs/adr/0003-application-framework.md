# ADR-0003: Orleans as the application framework

- Status: accepted
- Date: 2026-03-02

## Context

- Player state is per-player and hot; we need in-memory state with single-writer semantics.

## Decision

Use Microsoft Orleans. Each pod co-hosts the ASP.NET Core API and the Orleans silo.

## Consequences

- Grain calls from the API stay in-process when the grain lives on the same silo.
- Pods need the silo port (11111) and gateway port (30000) open inside the cluster.

## Links

- https://learn.microsoft.com/dotnet/orleans/
