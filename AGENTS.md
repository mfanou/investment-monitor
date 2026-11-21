# Repository guidance

## Project purpose
Personal investment monitoring system with a Telegram interface, an independent alert engine, market-data adapters, and an optional AI analysis worker.

## Preserve existing behaviour
- Keep the RSS news monitor operational.
- Preserve the existing Telegram /start and /ping commands.
- Extend the existing SQLite database at data/articles.db; do not create a second application database.
- Preserve the existing source_state and articles tables and their semantics.
- Never commit credentials, tokens, private account data, or runtime database files.

## Engineering rules
- Make small, testable changes in separate milestones.
- Inspect the current implementation before modifying it.
- Add SQLite schema changes through explicit, repeatable migrations.
- Keep market-data providers behind a provider-independent interface.
- Store timestamps in UTC and retain source timestamp, exchange, currency, and data freshness metadata.
- Never interpret missing or stale market data as zero or as a valid trigger.
- Commit alert events before attempting Telegram delivery; design notification delivery to tolerate retries without duplicate alerts.
- Keep AI analysis asynchronous and separate from time-critical price monitoring.
- ChatGPT-originated alert proposals require explicit user approval before activation.
- Record alert provenance, approval, trigger history, and AI reaction history.
- No autonomous trade execution.

## Quality checks
- Add automated tests for every new calculation, state transition, and migration.
- Test existing news-monitor behaviour when changing shared database or bot code.
- Do not add provider credentials to tracked configuration files.
