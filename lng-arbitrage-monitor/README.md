# LNG Arbitrage Monitor

Analysis of the US-to-Europe and Asia-vs-Europe LNG arbitrage using
Henry Hub, TTF, and JKM benchmarks, Jan 2021 – Sep 2026.

## Key findings
- US-to-Europe arb open on 95.3% of days (30d MA, ~$4/MMBtu break-even)
- Spread regimes: 2022 crisis peak ($34 mean), 2023-25 normalization ($8-10), 2026 re-widening ($13.7)
- JKM-TTF near zero in Sep 2026: no directional pull for flexible cargoes

## Methodology
- Front-month futures settlements via Yahoo Finance (NG=F, TTF=F, JKM=F, EURUSD=X)
- TTF converted EUR/MWh → USD/MMBtu (3.412 MMBtu/MWh, daily FX)
- ~1,435 common trading days after inner join
- Proxies used where assessments are proprietary (JKM); limitations documented in deck

## Files
- notebook: full analysis
- slides: summary briefing
