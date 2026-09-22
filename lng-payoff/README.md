# LNG Cargo Diversion Option — Bonny Island (Nigeria) Case Study

This project values the **destination flexibility** embedded in an FOB LNG
cargo loading at Bonny Island, Nigeria: the buyer's right to route the
cargo to Europe (priced off TTF) or divert it to Asia (priced off JKM),
whichever nets back more once shipping cost is accounted for. That
flexibility is modeled as a **spread option** and priced step by step,
starting simple and adding realism.

All prices used are **illustrative reference points from public
sources/aggregators**, not Platts-grade or exchange settlement data, and
are clearly labeled as such throughout. No confidential or proprietary
data is used anywhere in this project.

---

## Step 1: Problem Framing & Netback Economics

### What this step does
Frames the core decision and builds the payoff logic before any
option-pricing math is applied.

### Core logic
    netback_europe = TTF (converted to $/MMBtu) − shipping_to_europe
    netback_asia   = JKM − shipping_to_asia
    diversion_value = max(netback_asia − netback_europe, 0)

Rewritten as a spread option payoff:

    payoff = max( JKM − TTF_usd − K, 0 )

where **K = shipping_asia − shipping_europe** is the strike: the extra
shipping cost of routing to Asia instead of Europe. K is a cost
differential, not a market price.

### Inputs used (see code for exact values)
| Input | Value | Source |
|---|---|---|
| TTF | €79.5/MWh | ICE Endex front-month reference, mid-Sep 2026 |
| EUR/USD | 1.1539 | ECB reference rate, 15 Sep 2026 |
| JKM | $26.00/MMBtu | aggregator reference (range seen: $24.8–27.8), mid-Sep 2026 |
| Shipping to Europe | ~$0.56/MMBtu | own build-up: distance, charter day rate (~$25,250/day, Spark), boil-off |
| Shipping to Asia (via Cape) | ~$1.27/MMBtu | own build-up, same method, longer voyage |
| Strike (K) | ~$0.71/MMBtu | shipping_asia − shipping_europe |

### Key result
At current reference prices, the cargo is **near the money**: breakeven
JKM ≈ $27.60 (JKM would need to rise ~6% from $26.00 for diversion to
pay). Intrinsic value today is $0.00.

### Limitations / assumptions
1. Prices are illustrative reference points, not real-time market data.
2. FX (EUR/USD) is held fixed; not modeled as a risk factor.
3. No timing gap: prices are compared at a single instant, ignoring the
   real nomination-date structure (addressed conceptually in Step 2).
4. Single cargo, single decision — no portfolio or multi-cargo effects.
5. Shipping build-up applies one charter rate to both routes (no distinct
   Pacific rate available); ignores ballast-leg fuel, canal fees, and
   route disruptions.
6. No regas/terminal cost differences by destination.
7. Reference prices reflect an unusually disrupted market (Hormuz-related
   supply risk, low EU storage), so calibrated parameters from this
   period may not generalize to calmer markets.

---

## Step 2: Closed-Form Pricing (Margrabe & Kirk)

### What this step does
Prices the destination flexibility as a spread option using two
closed-form formulas: a first estimate, and a benchmark for the Monte
Carlo model built in later steps.

### The option being priced
The buyer must nominate the cargo's destination by a fixed **nomination
date** (modeled as T = 3 months from today). Up to that date, the buyer
holds the right, not the obligation, to choose Asia if it pays enough more
than Europe to cover the extra shipping cost. This makes it a
**European-style spread option**:

    payoff = max( JKM − TTF_usd − shipping_strike, 0 )

- **Spread**: JKM − TTF (in $/MMBtu), the price gap between the two markets.
- **Strike**: the shipping cost differential from Step 1 (K ≈ $0.71/MMBtu).
- **Nomination date**: the contractual deadline for committing the
  destination. Modeled here as a single fixed date; real contracts may use
  a nomination window instead, a possible future refinement.

### Two calculators used
- **Margrabe (1978)**: exact closed-form price when there is no strike
  (K = 0). Used as a simplified reference case.
- **Kirk (1995)**: standard approximation for spread options with a
  non-zero strike. Used for the actual case (K = $0.71). It is an
  approximation because "TTF + strike" is not exactly lognormal; Kirk
  rescales TTF's volatility by its share of the combined price to
  compensate. Approximation quality is expected to be good here since K
  is small relative to TTF (~2.6%).

### Inputs used (see code for exact values)
| Input | Value | Status |
|---|---|---|
| JKM (F1) | $26.00/MMBtu | from Step 1 |
| TTF in USD (F2) | ~$26.88/MMBtu | from Step 1 |
| Strike (K) | ~$0.71/MMBtu | from Step 1 |
| Time to nomination (T) | 0.25 yr | **assumed**, not from a real contract |
| Volatility, JKM & TTF | 60%, 55% | **assumed placeholders** |
| Correlation (ρ) | 0.90 | **assumed placeholder** |
| Interest rate (r) | 4% | flat, illustrative |

**Volatility, correlation, and time-to-nomination are assumptions, not
estimates.** Steps 3/4 replace these with values calibrated to historical
TTF/JKM price data.

### Key results (illustrative)
- Intrinsic value today: $0.00 (out of the money)
- Kirk price: ~$0.73/MMBtu (~$2.5M per cargo), entirely time value
- Margrabe price (no strike): ~$0.97/MMBtu
- Implied probability of finishing in the money: ~30%

### What drives the price
Value depends on the volatility of the **spread** (JKM − TTF), not on
either price's volatility alone. Correlation between the two markets is
the dominant driver: higher correlation → calmer spread → lower option
value, and vice versa. Confirmed via sensitivity sweeps over ρ and
volatility (see notebook).

### Limitations
- Vol, correlation, and shipping strike treated as constant over the
  option's life; no term structure or smile.
- Nomination date modeled as a single point in time, not a window.
- FX (EUR/USD) held fixed; not modeled as a separate risk factor.
- No cap on cargo diversion frequency, volume flexibility, or portfolio
  interaction — this prices a single cargo in isolation.

### Validation
Kirk price cross-checked against a Monte Carlo simulation of the same
lognormal price processes; results agreed to ~3 decimal places
(simulation ≈ $0.7343 vs Kirk = $0.7344, n = 2,000,000 paths). Kirk(K=0)
also confirmed to collapse exactly to Margrabe (assertion test in code).

---

## Next steps
- **Step 3**: real TTF/JKM data, forward curve construction
- **Step 4**: two-factor (Schwartz-Smith) calibration for volatility and correlation, replacing today's placeholders
- **Step 5**: Monte Carlo pricing vs Kirk, quantifying where the approximation breaks down
- **Step 6**: route constraints, boil-off, canal transit
- **Step 7**: sensitivities, packaged repo, model memo
