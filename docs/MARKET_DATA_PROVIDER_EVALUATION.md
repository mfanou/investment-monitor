# Market-data provider evaluation — preliminary

Last reviewed: 2026-11-22
Status: shortlist only; no provider selected or subscribed.

## Requirements

The monitor needs dependable quotes and OHLCV candles for US equities, Xetra-listed instruments, ETFs, crypto, and spot silver/FX-style symbols. It must expose the provider's instrument identity, exchange, currency, source timestamp, delay/real-time status, and candle completeness. Intraday intervals are needed for configurable charts; daily history is needed for RSI and longer-term analysis.

## Candidate comparison

| Provider | Relevant published offering | Fit and open issues |
|---|---|---|
| EOD Historical Data (EODHD) | EOD + Intraday All-World listed at $29.99/month; published plan includes global intraday stocks/ETFs/forex/crypto and real-time WebSocket access (50 tickers listed). | Leading candidate for a low-cost unified trial. Provider publishes DTE.XETRA and VWCE.XETRA instrument pages. Must test exact intraday/real-time entitlement for these instruments, candle intervals, timestamps, and actual quote quality. Its own disclaimer warns some CFD/ETF/forex prices can be indicative/aggregated rather than exchange-sourced. |
| Twelve Data | Basic: 8 API credits/minute and 800/day; real-time US equities/ETFs, forex and crypto. Global equity/ETF EOD is on Grow plans. Pro is listed from $99/month and adds real-time EU market data. | Good API alternative and useful benchmark, but the exchange list currently marks Xetra (XETR) as EOD with Grow as the minimum individual tier. That is not sufficient for live Xetra alerts without a different eligible feed/add-on. |
| Finnhub | Public pricing page lists paid personal plans from $49.99/month for certain data packages. | Not shortlisted for the first test: verify exact Xetra and ETF coverage, intraday candle entitlements, and complete asset-class fit before reconsidering. |
| Alpha Vantage | Free service lists 25 requests/day; real-time and 15-minute delayed US stock data are premium-only. | Useful for a limited comparison, but low free request quota and separate premium access make it less attractive for frequent multi-symbol monitoring. |

## Preliminary instrument mapping to verify

| User watchlist entry | Candidate EODHD identifier / note | Verification required |
|---|---|---|
| AEM | AEM.US | Confirm exact listing and quote currency. |
| CAT | CAT.US | Confirm exact listing and quote currency. |
| DTE | DTE.XETRA | Provider has a Deutsche Telekom XETRA instrument page; test API data and timestamps. |
| VWCE | VWCE.XETRA | Provider has a Vanguard FTSE All-World UCITS ETF XETRA instrument page; verify listing/ISIN and quote currency against the user's broker instrument. |
| PPFD | Unresolved | Do not silently change to PFFD. PFFD.US is Global X U.S. Preferred ETF, but the user's PPFD label and previously noted price context do not establish that this is the intended instrument. Obtain the exact name or ISIN. |
| BTC | Candidate BTC-USD.CC | Confirm quote pair and whether this is the intended benchmark. |
| XAG/USD | Unresolved provider-specific symbol | Verify whether the provider offers a spot silver quote, its source, unit, currency, and timestamps; do not substitute a silver CFD or futures contract without explicitly labelling it. |

## Test protocol before provider selection

1. Resolve each instrument using provider search and, where possible, ISIN plus exchange MIC. Store a canonical internal instrument ID separately from provider-specific symbols.
2. Request current quote data and historical candles for daily, 1-hour, and 15-minute intervals where available.
3. Record provider timestamp, retrieval timestamp, exchange, currency, delay flag, bid/ask or last price, and candle timezone/session semantics.
4. Compare simultaneous quotes with a trusted broker/exchange reference during an open session; compare end-of-day close after market close. Record deviations rather than assuming the provider is correct.
5. Test rate limits, outages, missing bars, weekends/holidays, daylight-saving transitions, and stale-data detection.
6. Select a provider only after the exact instruments and required entitlements are demonstrated. If one provider cannot cover all assets economically, consider a primary provider plus a narrowly scoped fallback.

## Sources

- EODHD pricing: https://eodhd.com/pricing/
- EODHD exchanges and ticker lists: https://eodhd.com/financial-apis/exchanges-api-list-of-tickers-and-trading-hours
- EODHD DTE.XETRA instrument page: https://eodhd.com/financial-summary/DTE.XETRA
- EODHD VWCE.XETRA instrument page: https://eodhd.com/financial-summary/VWCE.XETRA
- EODHD PFFD.US instrument page: https://eodhd.com/financial-summary/PFFD.US
- EODHD real-time WebSocket coverage: https://eodhd.com/financial-apis/new-real-time-data-api-websockets
- Twelve Data pricing: https://twelvedata.com/pricing
- Twelve Data exchange coverage: https://twelvedata.com/exchanges
- Finnhub pricing: https://api.finnhub.io/pricing-crypto-api
- Alpha Vantage API limits: https://www.alphavantage.co/support/api-key/

## Current recommendation

Use EODHD as the first provider to validate, not as an approved production source yet. Its published pricing and XETRA instrument pages make it the most promising low-cost candidate for the current watchlist. Do not pay until API-level checks establish the actual quote/candle entitlements and data quality for the exact instruments. Keep the provider adapter independent so switching or adding a second provider does not affect the alert engine.
