import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

# ============================================================
# INPUTS
# ============================================================

MWH_TO_MMBTU = 3.412142

TTF_EUR = 79.5
EURUSD = 1.1539
JKM_REF = 26.0
SHIP_ASIA = 1.27
SHIP_EU = 0.56


# ============================================================
# FUNCTIONS
# ============================================================

def eur_mwh_to_usd_mmbtu(p_eur_mwh, eurusd):
    return p_eur_mwh * eurusd / MWH_TO_MMBTU


def netbacks(jkm, ttf_eur, eurusd, ship_asia, ship_eu):
    nb_eu = eur_mwh_to_usd_mmbtu(ttf_eur, eurusd) - ship_eu
    nb_asia = jkm - ship_asia
    return nb_eu, nb_asia


def flexibility_payoff(jkm, ttf_eur, eurusd, ship_asia, ship_eu):
    nb_eu, nb_asia = netbacks(
        jkm, ttf_eur, eurusd, ship_asia, ship_eu
    )
    return np.maximum(nb_asia - nb_eu, 0)


# ============================================================
# DERIVED VALUES
# ============================================================

ttf_usd = eur_mwh_to_usd_mmbtu(TTF_EUR, EURUSD)

K = SHIP_ASIA - SHIP_EU

breakeven_jkm = ttf_usd + K

be_ttf_eur = (
    (JKM_REF - K)
    * MWH_TO_MMBTU
    / EURUSD
)


# ============================================================
# SANITY CHECKS
# ============================================================

assert flexibility_payoff(
    breakeven_jkm,
    TTF_EUR,
    EURUSD,
    SHIP_ASIA,
    SHIP_EU
) < 1e-9

assert flexibility_payoff(
    breakeven_jkm + 1,
    TTF_EUR,
    EURUSD,
    SHIP_ASIA,
    SHIP_EU
) > 0


print(f"TTF in USD:      ${ttf_usd:.2f}/MMBtu")
print(f"Breakeven JKM:   ${breakeven_jkm:.2f}/MMBtu")
print(f"Strike K:        ${K:.2f}/MMBtu")


# ============================================================
# STYLE
# ============================================================

BG = "#FAFAF8"
TEXT = "#202124"
MUTED = "#6B7280"
GRID = "#D9DDE2"
BLUE = "#1769AA"
TEAL = "#008C95"
RED = "#C0392B"
GREEN = "#16805B"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.labelsize": 10,
    "axes.labelcolor": TEXT,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "text.color": TEXT,
    "axes.edgecolor": "#C7CBD1",
    "axes.linewidth": 0.8,
    "figure.facecolor": BG,
    "axes.facecolor": BG,
})


def clean_axis(ax):
    """Give each axis a clean research-report appearance."""

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.grid(
        True,
        which="major",
        axis="both",
        color=GRID,
        linewidth=0.7,
        alpha=0.55
    )

    ax.grid(
        True,
        which="minor",
        axis="both",
        color=GRID,
        linewidth=0.45,
        alpha=0.25
    )

    ax.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))

    ax.tick_params(
        axis="both",
        which="major",
        length=0,
        pad=7
    )


# ============================================================
# DATA
# ============================================================

jkm = np.linspace(20, 32, 400)

payoff = flexibility_payoff(
    jkm,
    TTF_EUR,
    EURUSD,
    SHIP_ASIA,
    SHIP_EU
)


ttf_grid = np.linspace(60, 100, 400)

payoff2 = flexibility_payoff(
    JKM_REF,
    ttf_grid,
    EURUSD,
    SHIP_ASIA,
    SHIP_EU
)


# ============================================================
# FIGURE
# ============================================================

fig, ax = plt.subplots(
    1,
    2,
    figsize=(13.5, 5.2),
    facecolor=BG
)

# ------------------------------------------------------------
# CHART 1 — PAYOFF VS JKM
# ------------------------------------------------------------

a = ax[0]

a.plot(
    jkm,
    payoff,
    color=BLUE,
    linewidth=2.8,
    solid_capstyle="round",
    label="Asia-diversion value",
    zorder=3
)

# Shade the in-the-money region
mask = jkm >= breakeven_jkm

a.fill_between(
    jkm[mask],
    payoff[mask],
    0,
    color=BLUE,
    alpha=0.10,
    label="Positive option value"
)

# Zero line
a.axhline(
    0,
    color="#8A8F98",
    linewidth=0.9
)

# Breakeven
a.axvline(
    breakeven_jkm,
    color=TEXT,
    linestyle="--",
    linewidth=1.2,
    alpha=0.8
)

a.scatter(
    [breakeven_jkm],
    [0],
    s=55,
    color=TEXT,
    zorder=5
)

# Reference JKM
ref_payoff = flexibility_payoff(
    JKM_REF,
    TTF_EUR,
    EURUSD,
    SHIP_ASIA,
    SHIP_EU
)

a.axvline(
    JKM_REF,
    color=RED,
    linestyle=":",
    linewidth=1.5,
    alpha=0.9
)

a.scatter(
    [JKM_REF],
    [ref_payoff],
    s=55,
    color=RED,
    edgecolor="white",
    linewidth=1,
    zorder=5
)

# Annotation
a.annotate(
    f"Breakeven\n${breakeven_jkm:.2f}",
    xy=(breakeven_jkm, 0),
    xytext=(breakeven_jkm - 2.0, 1.0),
    fontsize=9,
    color=TEXT,
    arrowprops=dict(
        arrowstyle="-",
        color=MUTED,
        lw=0.8
    )
)

a.annotate(
    f"Reference JKM\n${JKM_REF:.1f}",
    xy=(JKM_REF, ref_payoff),
    xytext=(JKM_REF + 0.55, ref_payoff + 0.55),
    fontsize=9,
    color=RED,
    arrowprops=dict(
        arrowstyle="-",
        color=RED,
        lw=0.8
    )
)

a.set_title(
    "Asia Diversion Value vs. JKM",
    loc="left",
    pad=14
)

a.set_xlabel("JKM spot price ($/MMBtu)", labelpad=10)
a.set_ylabel("Option value ($/MMBtu)", labelpad=10)

a.set_xlim(20, 32)
a.set_ylim(bottom=-0.05)

clean_axis(a)


# ------------------------------------------------------------
# CHART 2 — PAYOFF VS TTF
# ------------------------------------------------------------

a = ax[1]

a.plot(
    ttf_grid,
    payoff2,
    color=TEAL,
    linewidth=2.8,
    solid_capstyle="round",
    label="Asia-diversion value",
    zorder=3
)

# Shade positive payoff region
mask2 = ttf_grid <= be_ttf_eur

a.fill_between(
    ttf_grid[mask2],
    payoff2[mask2],
    0,
    color=TEAL,
    alpha=0.10
)

# Zero line
a.axhline(
    0,
    color="#8A8F98",
    linewidth=0.9
)

# Breakeven TTF
a.axvline(
    be_ttf_eur,
    color=TEXT,
    linestyle="--",
    linewidth=1.2,
    alpha=0.8
)

a.scatter(
    [be_ttf_eur],
    [0],
    s=55,
    color=TEXT,
    zorder=5
)

# Reference TTF
ref_payoff_ttf = flexibility_payoff(
    JKM_REF,
    TTF_EUR,
    EURUSD,
    SHIP_ASIA,
    SHIP_EU
)

a.axvline(
    TTF_EUR,
    color=RED,
    linestyle=":",
    linewidth=1.5,
    alpha=0.9
)

a.scatter(
    [TTF_EUR],
    [ref_payoff_ttf],
    s=55,
    color=RED,
    edgecolor="white",
    linewidth=1,
    zorder=5
)

# Annotation
a.annotate(
    f"Breakeven\n€{be_ttf_eur:.1f}/MWh",
    xy=(be_ttf_eur, 0),
    xytext=(be_ttf_eur + 1.5, 1.0),
    fontsize=9,
    color=TEXT,
    arrowprops=dict(
        arrowstyle="-",
        color=MUTED,
        lw=0.8
    )
)

a.annotate(
    f"Reference TTF\n€{TTF_EUR:.1f}",
    xy=(TTF_EUR, ref_payoff_ttf),
    xytext=(TTF_EUR + 1.2, ref_payoff_ttf + 0.55),
    fontsize=9,
    color=RED,
    arrowprops=dict(
        arrowstyle="-",
        color=RED,
        lw=0.8
    )
)

a.set_title(
    "Asia Diversion Value vs. TTF",
    loc="left",
    pad=14
)

a.set_xlabel("TTF price (€/MWh)", labelpad=10)
a.set_ylabel("Option value ($/MMBtu)", labelpad=10)

a.set_xlim(60, 100)
a.set_ylim(bottom=-0.05)

clean_axis(a)


# ============================================================
# FIGURE HEADER
# ============================================================

fig.suptitle(
    "Bonny FOB Cargo — Asia Diversion Option",
    fontsize=17,
    fontweight="bold",
    x=0.055,
    ha="left",
    y=0.99
)

fig.text(
    0.055,
    0.925,
    (
        f"Illustrative payoff analysis  •  "
        f"TTF €{TTF_EUR:.1f}/MWh  •  "
        f"JKM ${JKM_REF:.1f}/MMBtu  •  "
        f"EUR/USD {EURUSD:.4f}"
    ),
    fontsize=9.5,
    color=MUTED
)

fig.text(
    0.055,
    0.015,
    "Source: Based on assumed market data. "
    "Payoff represents incremental value of diverting cargo to Asia vs. Europe.",
    fontsize=8.5,
    color=MUTED
)

plt.subplots_adjust(
    left=0.07,
    right=0.97,
    top=0.82,
    bottom=0.17,
    wspace=0.25
)

plt.show()
