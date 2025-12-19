# Why aiocoalesce?

**aiocoalesce** isn't just another library; it’s a strict, correctness-first implementation of the Request Coalescing pattern (often called "SingleFlight") for Python.

It solves the **"Thundering Herd"** problem: preventing thousands of identical concurrent requests from hammering your backend.

But why use this over existing libraries? **Robustness in the face of Cancellation.**

## The "Killer Feature": Cancellation Immunity

In high-concurrency systems, clients disconnect all the time (timeouts, tab closures, refreshed pages). Most coalescing libraries have a critical flaw: **they tie the execution execution to the first requester.**

### The Flaw in Others
Consider this scenario with a naive library:
1. **User A** joins. A DB query starts.
2. **User B** joins and waits for the same query.
3. 🔴 **User A disconnects.**

In many libraries, User A's cancellation **propagates** to the shared task. The DB query dies. **User B crashes or hangs**, even though they did nothing wrong. One impatient user can break the experience for everyone else.

### The aiocoalesce Guarantee
We use `asyncio.shield()` and a detached execution model to ensure:
1. **User A disconnects.**
2. The shared task **continues running** because User B is still waiting.
3. **User B gets the result.**

We protect your users from each other.

---

## Comparison Table

| Feature | `aiocoalesce` | Existing `singleflight` Ports | `lru_cache` | `asyncio.Lock` |
| :--- | :--- | :--- | :--- | :--- |
| **Thundering Herd** | 🟢 **Solved** | 🟢 **Solved** | 🔴 No (Race conditions) | 🟠 Partial (Sequential) |
| **Cancellation Safety** | 🟢 **Robust** (Shielded) | 🔴 **Fragile** (Cascading fails) | N/A | 🟢 Safe |
| **Concurrency** | 🟢 **Parallel Read** | 🟢 **Parallel Read** | N/A | 🔴 **Sequential** |
| **Type Safety** | 🟢 **100% Typed** | 🟠 Mixed | N/A | N/A |

## Who is this for?

- **FastAPI / Django / Starlette Developers** who need to protect expensive endpoints.
- **Data Engineers** serving heavy compute/ML models who want to prevent redundant processing.
- **Systems Engineers** who care about strict `asyncio` correctness.

## Honest Limitations

- **Process-Local Only**: We coalesce requests within a single process. If you have 100 replicas, you will get at most 100 requests (instead of 100,000). Scaling horizontally is safe.
- **Transient Only**: We are not a cache. The moment the task finishes, the result is forgotten. New requests trigger new work. This ensures **freshness**.
