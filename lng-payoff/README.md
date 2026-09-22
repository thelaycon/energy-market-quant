# LNG Cargo Diversion Option — Bonny Island (Nigeria) Case Study

This project values the **destination flexibility** embedded in an FOB LNG
cargo loading at Bonny Island, Nigeria: the buyer's right to route the
cargo to Europe (priced off TTF) or divert it to Asia (priced off JKM),
whichever nets back more once shipping cost is accounted for. That
flexibility is modeled as a **spread option** and priced step by step,
starting simple and adding realism.

All prices used are from public sources (ICE, CME, aggregators), not
Platts-grade or exchange settlement data, and are labeled with their
source throughout. No confidential or proprietary data is used anywhere
in this project.

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
At these reference prices, the cargo is **near the money**: breakeven
JKM ≈ $27.60 (JKM would need to rise ~6% from $26.00 for diversion to
pay). Intrinsic value at these prices is $0.00.

### Limitations / assumptions
1. Prices are reference points from aggregators, not exchange settlement
   data.
2. FX (EUR/USD) is held fixed; not modeled as a risk factor.
3. No timing gap: prices are compared at a single instant, ignoring the
   real nomination-date structure (addressed conceptually in Step 2).
4. Single cargo, single decision — no portfolio or multi-cargo effects.
5. Shipping build-up applies one charter rate to both routes (no distinct
   Pacific rate available); ignores ballast-leg fuel, canal fees, and
   route disruptions.
6. No regas/terminal cost differences by destination.

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

### Margrabe's formula (K = 0)

For the option to exchange asset 2 (TTF) for asset 1 (JKM), with no strike:

    V = e^(-rT) [ F1 · N(d1) − F2 · N(d2) ]

    d1 = [ ln(F1/F2) + 0.5σ²T ] / (σ√T)
    d2 = d1 − σ√T
    σ  = sqrt( σ1² + σ2² − 2ρσ1σ2 )

where F1, F2 are the forward prices, σ1, σ2 are their volatilities, ρ is
their correlation, T is time to expiry, r is the discount rate, and
N(·) is the standard normal CDF. σ is the volatility of the **spread**
(F1 − F2), the single quantity that determines the option's value.

### Kirk's approximation (K > 0)

No exact formula exists once a non-zero strike is introduced, since
F2 + K is not lognormal. Kirk (1995) approximates it by treating F2 + K
as a single asset and rescaling its volatility by its share of the total:

    F2' = F2 + K
    w   = F2 / F2'
    σ_K = sqrt( σ1² + (w·σ2)² − 2ρσ1(w·σ2) )

    d1 = [ ln(F1/F2') + 0.5σ_K²T ] / (σ_K√T)
    d2 = d1 − σ_K√T

    V = e^(-rT) [ F1 · N(d1) − F2' · N(d2) ]

Setting K = 0 recovers F2' = F2, w = 1, and the formula collapses exactly
to Margrabe. Approximation quality is expected to be good here since K is
small relative to F2 (~2.6%).

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
estimates.** Step 4 replaces these with values calibrated to historical
TTF/JKM price data.

### Key results (illustrative)
- Intrinsic value at these prices: $0.00 (out of the money)
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

## Step 3: Real Forward Curves (ICE & CME)

### What this step does
Replaces the reference prices used in Steps 1-2 with real, sourced
forward curves, and re-examines the option's moneyness across the full
observable curve rather than at a single price point.

### Data sources
| Series | Source | Retrieved | Coverage |
|---|---|---|---|
| TTF | ICE Endex WebICE, delayed quotes | 22 Sep 2026 | Oct 2026 – Feb 2028 |
| JKM | CME Group, delayed quotes | 22 Sep 2026 | Nov 2026 – Apr 2028 |

Both are free, exchange-published, timestamped quotes (no subscription
required). TTF is converted to USD/MMBtu using the EUR/USD rate from
Step 1 to make the two series comparable. The curves are merged on 14
overlapping contract months (Nov 2026 – Feb 2028) for analysis.

### Key results
| | Value |
|---|---|
| Spread (JKM − TTF) across all 14 observed months | **Positive** in every month, $0.46–$2.59/MMBtu |
| Widest spread | Nov 2026 (~$2.59/MMBtu) |
| Narrowest spread | May 2027 (~$0.46/MMBtu) |
| Dec26 TTF (USD) | $23.31/MMBtu |
| Dec26 JKM | $25.38/MMBtu |
| Dec26 spread | $2.07/MMBtu |
| **Dec26 intrinsic value** (spread − K) | **+$1.36/MMBtu (~$4.6M/cargo)** |

### What this shows
Using real curve data instead of the Step 1-2 reference prices, JKM
trades above TTF across the entire observed curve, and the diversion
option is **in the money** at the 3-month nomination point, not
near-breakeven as the Step 1-2 reference prices implied. The spread is
not constant across the curve: it narrows sharply into spring 2027
(bottoming around May 2027), which is the point where the diversion
decision is most sensitive to price moves.

### Seasonality
Both curves show the same shape: elevated winter prices (Nov 2026–Feb
2027), a sharp drop heading into spring 2027, and a flatter
summer/shoulder band. This shape is the input Step 4 uses to separate
seasonal pattern from genuine random price movement.

### Limitations
- Quotes are delayed (10-15 min) and, for JKM, reflect prior-day
  settlement rather than live trades at retrieval time.
- Only 14 months have data on both sides; the full curve (through 2033
  for TTF) is not yet used.
- A single EUR/USD rate is applied across the whole curve; no forward
  FX curve is used.
- Curve reflects a single day's snapshot, not a time series — no history
  yet to estimate volatility or correlation from (addressed in Step 4).

---

## Next steps
- **Step 4**: two-factor (Schwartz-Smith) calibration for volatility and correlation, replacing today's placeholders
- **Step 5**: Monte Carlo pricing vs Kirk, quantifying where the approximation breaks down
- **Step 6**: route constraints, boil-off, canal transit
- **Step 7**: sensitivities, packaged repo, model memo
