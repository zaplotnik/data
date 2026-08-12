#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stacked historical GHG emissions by source, 1990-2024 (no projections/scenarios).

Based on plot_emissions.py, updated for the 2026 CRT submission's extended
1990-2024 series (emissions/src/parse_svn_2026.py). Axis limits, the
historical/projection splice point and the output filename are all derived
from the data rather than hardcoded, so the next data refresh doesn't
silently drift out of sync with the plot.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# import historical data
df = pd.read_csv("../data/emissions.historical.csv")
data = df.to_numpy()

years = data[:, 0]
data = np.nan_to_num(data)
data = data[:, 2:-1]  # drop year, total_source, and lulucf (reported/targeted separately)
data = data.transpose()

# rearrange data, so intl aviation, navigation and biomass burning come last
data = np.concatenate((data[:7], data[10][np.newaxis, :], data[7:10]), axis=0)

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

# stack tops/bottoms across all years, for data-driven axis limits
stack_top = (data_stack + np.clip(data, 0, None)).max(axis=0)
stack_bottom = (data_stack + np.clip(data, None, 0)).min(axis=0)
y_pad = 0.05 * (stack_top.max() - stack_bottom.min())

fig, ax = plt.subplots(1, figsize=(22, 14))
ax.grid()
ax.set_xlabel("leto", fontsize=18)
ax.set_ylabel(r"emisije [kt ekvivalent CO$_2$]", fontsize=18)
ax.set_xlim([year_min - 1, year_max + 2])
ax.set_ylim([stack_bottom.min() - y_pad, stack_top.max() + y_pad])
ax.tick_params(axis='both', which='major', labelsize=16)
ax.set_title(f"Viri emisij toplogrednih plinov, {year_min}–{year_max}", fontsize=20)

cols = ["blueviolet", "forestgreen", "blue", "grey", "firebrick", "orange",
        "darkkhaki", "slategray", "navy", "aqua", "saddlebrown"]
labels = ["Oskrba z energijo", "Industrija in gradbeništvo", "Promet", "Industrijski procesi",
          "Raba goriv v gospodinjstvih,\nkomercialnih stavbah, kmetijstvu,\ngozdarstvu, ribištvu", "Kmetijstvo",
          "Odpadki", "Ostalo", "Mednarodni letalski promet", "Mednarodni ladijski promet",
          "Biomasa (kurjenje lesa,\npožari)"]
hatches = 8 * [None] + 3 * ['//']

for i in np.arange(0, data_shape[0]):
    ax.bar(years, data[i], bottom=data_stack[i], color=cols[i], label=labels[i], align="edge", hatch=hatches[i])
ax.plot(years + 0.5, data[:8].sum(axis=0), lw=5, color="black",
        label="Skupaj - brez biomase \nin mednarodnega prometa")

legend = ax.legend(fontsize=18, ncol=2, bbox_to_anchor=(0.5, -0.1), loc='upper center',
                    title="Zgodovinske vrednosti")
legend.get_title().set_fontsize('18')

fig.text(0.5, 0.005,
          "Opomba: prikazane emisije ne vključujejo LULUCF (raba zemljišč, sprememba rabe zemljišč in gozdarstvo).",
          ha='center', fontsize=13, style='italic')

fig.tight_layout()
fig.savefig(f"total_{year_min}_{year_max}.png", dpi=300)
