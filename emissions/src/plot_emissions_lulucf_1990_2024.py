#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stacked historical LULUCF emissions/removals by land-use category, 1990-2024
(no projections/scenarios).

Based on plot_emissions_lulucf.py, updated for the 2026 CRT submission's
extended 1990-2024 series (emissions/src/parse_svn_2026.py). Axis limits and
the output filename are derived from the data rather than hardcoded.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# import historical data
df = pd.read_csv("../data/emissions.historical.lulucf.csv")
data = df.values

years = data[:, 0]
data = data[:, 2:-1]  # drop year, total, and the always-zero "other" column
data = data.transpose()

data_shape = np.shape(data)


def get_cumulated_array(data, **kwargs):
    cum = data.clip(**kwargs)
    cum = np.cumsum(cum, axis=0)
    d = np.zeros(np.shape(data))
    d[1:] = cum[:-1]
    return d


cumulated_data = get_cumulated_array(data, min=0)
cumulated_data_neg = get_cumulated_array(data, max=0)

# Re-merge negative and positive data.
row_mask = (data < 0)
cumulated_data[row_mask] = cumulated_data_neg[row_mask]
data_stack = cumulated_data

year_min, year_max = int(years.min()), int(years.max())

stack_top = (data_stack + np.clip(data, 0, None)).max(axis=0)
stack_bottom = (data_stack + np.clip(data, None, 0)).min(axis=0)
y_pad = 0.05 * (stack_top.max() - stack_bottom.min())

fig, ax = plt.subplots(1, figsize=(22, 14))
ax.grid()
ax.set_xlabel("leto", fontsize=18)
ax.set_ylabel(r"emisije [kt ekvivalent CO$_2$]", fontsize=18)
ax.set_xlim([year_min - 1, year_max + 1])
ax.set_ylim([stack_bottom.min() - y_pad, stack_top.max() + y_pad])
ax.tick_params(axis='both', which='major', labelsize=16)
ax.set_title(f"LULUCF - raba zemljišč, sprememba rabe zemljišč in gozdarstvo, {year_min}–{year_max}",
             fontsize=20)

cols = ["darkgreen", "y", "lawngreen", "#03fcfc", "grey", "lightgreen", "saddlebrown"]
labels = ["gozdna zemljišča", "njivske površine", "travinje", "mokrišča", "naselja", "druga zemljišča",
          "lesni proizvodi"]

for i in np.arange(0, data_shape[0]):
    ax.bar(years, data[i], bottom=data_stack[i], color=cols[i], label=labels[i], align="edge")
ax.plot(years, data.sum(axis=0), lw=5, color="black", label="skupaj")

legend = ax.legend(fontsize=18, ncol=2, bbox_to_anchor=(0.5, -0.1), loc='upper center',
                    title="Zgodovinske vrednosti")
legend.get_title().set_fontsize('18')

# forest_land flips from a net sink to a net source in 2014 - a real event
# (Feb 2014 ice storm forest damage), not a data artifact - annotate it so
# it doesn't read as a parsing bug.
forest_land_2014 = df.loc[df["year"] == 2014, "forest_land"].values[0]
ax.annotate("žledolom, februar 2014",
            xy=(2014.5, forest_land_2014), xycoords='data',
            xytext=(2014.5, 0.92), textcoords=("data", "axes fraction"),
            fontsize=14, ha='center',
            arrowprops=dict(arrowstyle='->', lw=1.5))

fig.tight_layout()
fig.savefig(f"lulucf_{year_min}_{year_max}.png", dpi=300)
