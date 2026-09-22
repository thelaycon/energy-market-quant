import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load 
ttf = pd.read_csv("ttf_forward_curve_2026-09-22.csv", parse_dates=["contract_month"])
jkm = pd.read_csv("jkm_forward_curve_2026-09-22.csv", parse_dates=["contract_month"])

print(ttf.head())
print(jkm.head())
print(f"TTF: {len(ttf)}")
print(f"JKM: {len(jkm)}")

# Convert TTF to USD/MMBtu 
MWH_TO_MMBTU = 3.412142
EURUSD = 1.1539

ttf["price_usd_mmbtu"] = ttf["price_eur_mwh"] * EURUSD / MWH_TO_MMBTU

# Rename before merge (avoids duplicate-column bug) 
ttf_renamed = ttf[["contract_month", "price_usd_mmbtu"]].rename(
    columns={"price_usd_mmbtu": "ttf_usd"}
)
jkm_renamed = jkm[["contract_month", "price_usd_mmbtu"]].rename(
    columns={"price_usd_mmbtu": "jkm"}
)

# Merge on shared contract months 
curve = pd.merge(ttf_renamed, jkm_renamed, on="contract_month", how="inner")
curve = curve.sort_values("contract_month").reset_index(drop=True)

curve["spread"] = curve["jkm"] - curve["ttf_usd"]
print(curve)

# Tightest-spread month (closest to breakeven) 
tightest = curve.loc[curve["spread"].idxmin()]
print(f"Tightest spread: {tightest['contract_month'].strftime('%Y-%m')}, "
      f"${tightest['spread']:.2f}/MMBtu")

# Plot
fig, ax = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

ax[0].plot(curve["contract_month"], curve["ttf_usd"], marker="o", label="TTF (USD/MMBtu)")
ax[0].plot(curve["contract_month"], curve["jkm"], marker="o", label="JKM (USD/MMBtu)")
ax[0].set_ylabel("$/MMBtu")
ax[0].set_title("TTF vs JKM forward curves (22 Sep 2026, ICE + CME, delayed)")
ax[0].legend()
ax[0].grid(alpha=0.3)

ax[1].bar(curve["contract_month"], curve["spread"], width=20,
          color=np.where(curve["spread"] >= 0, "tab:green", "tab:red"))
ax[1].axhline(0, color="black", lw=0.8)
ax[1].set_ylabel("Spread: JKM - TTF_usd ($/MMBtu)")
ax[1].set_xlabel("Contract month")
ax[1].grid(alpha=0.3)

# Annotate the tightest-spread point on the bar chart
ax[1].annotate(
    f"Tightest: {tightest['contract_month'].strftime('%b %y')}\n${tightest['spread']:.2f}",
    xy=(tightest["contract_month"], tightest["spread"]),
    xytext=(tightest["contract_month"], tightest["spread"] + 1.0),
    ha="center",
    arrowprops=dict(arrowstyle="->", color="black"),
)

plt.tight_layout()
plt.show()

# Dec26 decision point (3 months out)
K = 0.71  # shipping strike from Step 1

row = curve[curve["contract_month"] == "2026-12-01"].iloc[0]
intrinsic = row["jkm"] - row["ttf_usd"] - K

print(f"Dec26 TTF (USD): ${row['ttf_usd']:.2f}/MMBtu")
print(f"Dec26 JKM:       ${row['jkm']:.2f}/MMBtu")
print(f"Spread:          ${row['spread']:.2f}/MMBtu")
print(f"Strike K:        ${K:.2f}/MMBtu")
print(f"Intrinsic value at Dec26: ${intrinsic:.2f}/MMBtu")
