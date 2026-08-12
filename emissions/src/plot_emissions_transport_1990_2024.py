#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stacked historical transport emissions by mode, 1990-2024 (no
projections/scenarios).

Based on plot_emissions_transport.py, updated for the 2026 CRT submission's
extended 1990-2024 series (emissions/src/parse_svn_2026.py). Axis limits and
the output filename are derived from the data rather than hardcoded.

Heavy duty trucks and buses are plotted as a single combined category
(road_transporation.heavy_duty_trucks_and_buses) rather than the separate
road_transporation.heavy_duty_trucks/.buses columns: the CRT workbooks only
ever report this as one row, and the two-way split in the other columns
comes from a different, manually-maintained spreadsheet that stops at 2021
(both are 0.0 for 2022-2024) - see parse_svn_2026.py's module docstring.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# import historical data
df = pd.read_csv("../data/emissions.historical.energy.transport.csv")

years = df["year"].to_numpy()

columns = [
    "road_transporation.cars",
    "road_transporation.light_duty_trucks",
    "road_transporation.heavy_duty_trucks_and_buses",
    "road_transporation.motorcycles",
    "road_transporation.other",
    "railways",
    "domestic_aviation",
    "domestic_navigation",
    "other_transportation",
    "international_aviation",
    "international_navigation",
]
data = df[columns].to_numpy().transpose()

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
ax.set_xlim([year_min - 1, year_max + 2])
ax.set_ylim([min(0, stack_bottom.min()) - y_pad, stack_top.max() + y_pad])
ax.tick_params(axis='both', which='major', labelsize=16)
ax.set_title(f"Emisije prometa, {year_min}–{year_max}", fontsize=20)

cols = ["lightblue", "dodgerblue", "blue", "lightcyan", "deepskyblue", "silver", "plum",
        "darkturquoise", "lightsteelblue", "violet", "aqua"]
labels = ["avtomobili", "lahka tovorna vozila", "težka tovorna vozila in avtobusi", "motocikli",
          "ostala cestna vozila", "železniški promet", "notranji letalski promet",
          "notranji ladijski promet", "ostalo", "mednarodni letalski promet",
          "mednarodni ladijski promet"]
hatches = 9 * [None] + ['//', '//']

for i in np.arange(0, data_shape[0]):
    ax.bar(years, data[i], bottom=data_stack[i], color=cols[i], label=labels[i], align="edge",
           hatch=hatches[i])
ax.plot(years + 0.5, data[:9].sum(axis=0), lw=5, color="black", label="skupaj (brez medn. prometa)")

legend = ax.legend(fontsize=18, ncol=2, bbox_to_anchor=(0.5, -0.1), loc='upper center',
                    title="Zgodovinske vrednosti")
legend.get_title().set_fontsize('18')

fig.tight_layout()
fig.savefig(f"promet_{year_min}_{year_max}.png", dpi=300)
