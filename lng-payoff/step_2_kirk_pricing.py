import numpy as np
from scipy.stats import norm

MWH_TO_MMBTU = 3.412142

# Inputs
jkm = 26.0
ttf_usd = 79.5 * 1.1539 / MWH_TO_MMBTU
strike = 1.27 - 0.56
years = 0.25 # 3 Months
vol_jkm = 0.60 # Assumed
vol_ttf = 0.55 # Assumed
corr = 0.90
rate = 0.04
CARGO = 3.4e6 #MMBTu


def kirk_price(jkm, ttf, strike, vol_jkm, vol_ttf, corr, years, rate):
  """ Price of the spread optiion """

  # Treat "TTF + K" as a combined price 
  europe_side = ttf + strike

  # Because of the combined price, the vol of TTF is scaled down a bit
  share = ttf / europe_side
  vol_ttf_adj = share * vol_ttf

  # How volatile is the gap between the two prices?
  # We use a positive correlation to cancel part of it
  gap_vol = np.sqrt(vol_jkm**2 + vol_ttf_adj**2 - 2 * corr * vol_jkm * vol_ttf_adj) 

  # How many gap-swings away from the breakeven are we?
  time_scale = gap_vol * np.sqrt(years)
  d1 = (np.log(jkm / europe_side) + 0.5 * time_scale**2) / time_scale
  d2 = d1 - time_scale

  # Turn the scores into probabilities between 0 and 1
  price = np.exp(-rate * years) * (jkm * norm.cdf(d1) - europe_side * norm.cdf(d2))

  return price, gap_vol, norm.cdf(d2)


# Run the calculation

price, gap_vol, chance = kirk_price(jkm, ttf_usd, strike, vol_jkm, vol_ttf, corr, years, rate)

margrabe, _, _ = kirk_price(jkm, ttf_usd, 0.0, vol_jkm, vol_ttf, corr, years, rate)

print(f"Intrinsic value today:        ${max(jkm - ttf_usd - strike, 0):.2f}/MMBtu")
print(f"Jumpiness of the gap:         {gap_vol:.0%}")
print(f"Chance of finishing in money: {chance:.0%}")
print(f"Kirk price (strike $0.71):    ${price:.3f}/MMBtu")
print(f"Margrabe price (strike $0):   ${margrabe:.3f}/MMBtu")
print(f"Value per cargo:              ${price * CARGO / 1e6:.2f}M")
