# Lessons

- Green tests are scenario evidence, not product evidence. Read assertions and list missing state transitions before using a pass count.
- Model and text classifiers fail on negation, spelling variants, placeholders, and stronger paraphrases. Probe direct counterexamples.
- UI prevention is not idempotency. Duplicate tabs, retries, serverless instances, and direct API calls bypass button disabling and process-local maps.
- Every external side effect needs an ambiguous-success story. A timeout may mean the provider succeeded while the caller never received the response.
- Companion events and reordered webhooks expose overwrite bugs that a single fixture cannot show.
- Async work needs a durable lease, heartbeat, or watchdog. A `running` status without recovery can become a permanent terminal state after process death.
- Validate upstream autocomplete/search records against the downstream form schema before suggesting them to users.
- Bind streamed UI work to stable identities, not array indexes, and ignore stale completions from superseded requests.
- Keep retrieval/search facts in a typed, size-bounded context section. Never concatenate untrusted content with instructions or let enrichment silently become generation truth.
- Reviewer failure must not equal reviewer approval. Parse errors and unavailable secondary models should produce explicit uncertainty.
- Marking durable delivery before a nondurable side effect creates false success. Prefer an outbox or a retryable delivery state.
- Source inspection cannot prove production configuration, provider reachability, or deployed revision. Name that evidence gap instead of guessing.
- Documentation drift is a separate finding only when it can mislead operation, security, or recovery; do not mix it with runtime defects.
- Multi-agent breadth creates duplicates and inconsistent severity. Require stable schemas, a shared truth seed, and a separate adversarial validation pass.
- Public artifacts must be generalized before publishing: remove client names, product domains, credentials, internal paths, private repository URLs, provider account identifiers, and incident-specific data.
