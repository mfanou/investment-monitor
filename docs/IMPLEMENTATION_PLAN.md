# Investment Monitor — implementation plan

Last updated: 2026-11-22

## Confirmed product decisions

| Area | Decision |
|---|---|
| Database | Extend the existing SQLite database at data/articles.db |
| Alert engine | Independent Python module |
| Market data | Provider-independent adapter architecture |
| RSI | Mandatory; default period 14 using Wilder smoothing |
| Other indicators | Moving averages and Bollinger Bands optional |
| Charts | Candlesticks; configurable interval and candle count |
| Default chart | 60 daily candles with an RSI panel |
| Notifications and interaction | Telegram commands, buttons, and notifications |
| Initial deployment | Cloud Shell, then migrate to a server |
| ChatGPT alert management | Enabled |
| Alert creation from analysis | Assisted; explicit user approval required before activation |
| Automatic reactions | Configurable reaction level per alert |
| Trading | No autonomous trade execution |

## Target capabilities

### Alert management
- Price threshold and crossing alerts.
- Percentage-move and drawdown-from-high alerts.
- RSI threshold and crossing alerts.
- Optional moving-average and Bollinger Band conditions.
- Combined conditions (AND/OR), cooldowns, re-arming, expiry, pause/resume.
- Alert event and change history.

### ChatGPT control interface
Provide a secured API/MCP-compatible interface, subject to confirming the supported integration route. Initial operations:
- List, inspect, create, update, pause, resume, and delete alerts.
- Retrieve instrument quotes, candles, indicator values, and alert history.
- Create alert proposals in a pending-approval state.
- Activate an assisted alert only after explicit user approval.

ChatGPT must not receive direct database access. The integration must authenticate requests, validate inputs, enforce permissions, and log changes.

### AI reactions
Each alert has a configurable reaction level:
1. Notification only.
2. Contextual technical assessment.
3. Full assessment incorporating relevant technical, news, fundamental, and thesis context.

The alert engine must not wait for an AI response. Persist the event first, deliver the immediate notification, then enqueue any requested analysis. Deduplicate repeated work, retry failures safely, and control model/API costs. External events cannot directly wake this ChatGPT conversation; autonomous analysis requires a separately running model/API worker or equivalent service.

## Implementation roadmap

### M0 — Baseline and safeguards
- Inspect repository, runtime, dependencies, and current database behaviour.
- Document architecture decisions and repository rules.
- Establish tests before modifying shared components.
- Preserve the current RSS monitor, Telegram commands, and SQLite schema.

### M1 — Market-data foundation
- Compare providers against the actual instrument universe: AEM, CAT, DTE, VWCE, PPFD (verify exact instrument/exchange), BTC, and XAG/USD.
- Verify exchange mapping, quote currency, timestamps, delay status, historical OHLCV coverage, supported intervals, API limits, reliability, and costs.
- Implement provider-independent quote and candle interfaces, source metadata, caching, and stale-data safeguards.
- Do not select a provider based on symbol-name matching alone.

### M2 — Alert engine and database migrations
- Add repeatable migrations to the existing SQLite database.
- Implement alert definitions, evaluation, crossing/re-arm state, event history, and notification outbox.
- Add deterministic tests for conditions and state transitions.

### M3 — Telegram management
- Add commands and interactive controls for listing, creating, editing, pausing, resuming, and deleting alerts.
- Preserve existing news notifications and /start and /ping.

### M4 — ChatGPT integration
- Confirm the current supported custom integration/MCP mechanism before implementation.
- Add authenticated, narrowly scoped API operations.
- Support pending proposals and explicit approval before activation.
- Record source analysis, rationale, expiry/review date, creator, and approval.

### M5 — Indicators
- Implement and test RSI(14) with Wilder smoothing.
- Add optional moving averages and Bollinger Bands.
- Define completed-candle versus intraday calculation semantics.

### M6 — Candlestick charts
- Configurable interval and candle count; default 60 daily candles.
- RSI panel mandatory; optional moving-average and Bollinger overlays.
- Handle exchange sessions, timezone boundaries, and incomplete candles explicitly.

### M7 — Automated AI reactions
- Add asynchronous event routing, context assembly, thesis comparison, structured analysis, and Telegram reporting.
- Make reaction level configurable per alert.
- Track event, data snapshot, model result, retries, and costs.

### M8 — Production hardening and migration
- Backups, restore tests, monitoring, secrets management, API security, rate limits, and failure recovery.
- Move from Cloud Shell to the permanent server only after repeatable deployment and recovery tests.

## Initial engineering constraints
- The existing database file is runtime data and is ignored by Git; its live contents must be inspected in the user's Cloud Shell before any migration.
- The repository snapshot alone cannot establish whether Cloud Shell has uncommitted changes or a newer local database.
- Avoid changing shared bot/database code until a baseline test path exists.
