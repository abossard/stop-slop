# ADR-0020: Azure Front Door as the global entry point

- Status: accepted
- Date: 2026-05-14

## Decision

All public traffic enters through Azure Front Door Premium. It terminates TLS, applies the WAF policy, routes by path and gives one anycast address.

## Links

- https://learn.microsoft.com/azure/frontdoor/
