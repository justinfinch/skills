---
okf_version: "0.2"
---

# Concepts

* [Four kinds of client state, four stores — never one store for everything](concepts/client-state-taxonomy.md) - Split client state by what it is rather than by what is convenient — a server cache owned by a query library that fetches, expires and invalidates; ephemeral UI state in a light store or component state; durable pending writes in a purpose-built persistent queue that is deliberately not the query library's mutation cache; and real-time push events patching that query cache directly, which is where an eventually-consistent backend's optimistic read-your-writes echo lives on the client.
* [Scope the offline promise to one write path — store-and-forward capture, not offline mode](concepts/store-and-forward-capture.md) - Name the single workflow that must survive dead connectivity and make only its writes unlosable — a durable local queue that persists before the UI acknowledges, survives process death, and drains in order on reconnect with a client-generated idempotency key, plus a session-scoped read-only cache of just the context that workflow needs — while explicitly declining general offline mode, offline browsing, and conflict resolution, so everything off that path fails visibly instead of pretending.
