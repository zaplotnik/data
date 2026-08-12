#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 18 13:16:35 2021

@author: ziga
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os,glob
import matplotlib.pyplot as plt


# import historical data
df = pd.read_csv("../data/emissions.historical.csv")
data = df.to_numpy()

years = data[:,0]
data = np.nan_to_num(data)
data = data[:,2:-1]
data = data.transpose()

# rearrange data, so intl aviation, navigation and biomass burning come last
data = np.concatenate((data[:7],data[10][np.newaxis,:],data[7:10]),axis=0)

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
row_mask = (data<0)
cumulated_data[row_mask] = cumulated_data_neg[row_mask]
data_stack = cumulated_data


# import projections
data_projections_bau = pd.read_csv("../data/emissions.projections.bau.csv")
data_projections_current = pd.read_csv("../data/emissions.projections.current.csv")
data_projections_add = pd.read_csv("../data/emissions.projections.additional_nuclear.csv")
data_projections_ambadd = pd.read_csv("../data/emissions.projections.ambitious_additional_nuclear.csv")

# import emissions ec, paris15,paris20
data_projections_ec = pd.read_csv("../data/emissions.projections.ec_paris.csv")


fig,ax = plt.subplots(1,figsize=(22,14))
ax.grid()
ax.set_xlabel("leto",fontsize=18)
ax.set_ylabel(r"emisije [kt ekvivalent CO$_2$]",fontsize=18)
ax.set_xlim([1984,2032])
ax.set_ylim([-1000,26000])
ax.tick_params(axis='both', which='major', labelsize=16)
# ax.set_title("Viri emisij toplogrednih plinov",fontsize=18)

cols = ["blueviolet","black","blue","grey","firebrick","orange","darkkhaki","slategray","navy","aqua","saddlebrown"]
labels = ["Oskrba z energijo","Industrija in gradbeništvo","Promet","Industrijski procesi",\
          "Raba goriv v gospodinjstvih,\nkomercialnih stavbah, kmetijstvu,\ngozdarstvu, ribištvu","Kmetijstvo",\
          "Odpadki","Ostalo","Mednarodni letalski promet","Mednarodni ladijski promet","Biomasa (kurjenje lesa,\npožari)"]
hatches = 8*[None] + 3*['//']   
     
for i in np.arange(0, data_shape[0]):
    ax.bar(years, data[i], bottom=data_stack[i], color=cols[i], label=labels[i],align="edge",hatch=hatches[i])
ax.plot(years+0.5,data[:8].sum(axis=0), lw=5, color="black",label="Skupaj - brez biomase \nin mednarodnega prometa")    

legend=ax.legend(fontsize=18,ncol=2,bbox_to_anchor=(0., -0.1),loc='upper left',title="Zgodovinske vrednosti")
legend.get_title().set_fontsize('18')


# Create the second legend and add the artist manually.

ind1 = 1
ind2 = 11

lines = []
lines += ax.plot(data_projections_bau["year"].values[ind1:ind2]+0.5,data_projections_bau["total_source"].values[ind1:ind2],\
         lw=4,label="skupaj - scenarij NEPN\n'business as usual'",color="darkviolet")
lines += ax.plot(data_projections_current["year"].values[ind1:ind2]+0.5,data_projections_current["total_source"].values[ind1:ind2],\
         lw=4,label="skupaj - scenarij NEPN\nobstojeci ukrepi",color="red")
lines += ax.plot(data_projections_add["year"].values[ind1:ind2]+0.5,data_projections_add["total_source"].values[ind1:ind2],\
         lw=4,label="skupaj - scenarij NEPN\ndodatni ukrepi,\nnuklearka",color="darkorange")
lines += ax.plot(data_projections_ambadd["year"].values[ind1:ind2]+0.5,data_projections_ambadd["total_source"].values[ind1:ind2],\
         lw=4,label="skupaj - scenarij NEPN\nambiciozni dodatni ukrepi,\nnuklearka",color="gold")
lines += ax.plot(data_projections_ec["year"].values[ind1:ind2]+0.5,data_projections_ec["ec"].values[ind1:ind2],\
         lw=4,label="skupaj - scenarij skladen \ns cilji Evropske komisije",color="yellowgreen")
lines += ax.plot(data_projections_ec["year"].values[ind1:ind2]+0.5,data_projections_ec["paris20"].values[ind1:ind2],\
         lw=4,label="skupaj - scenarij \nPariski sporazum "+r"$\Delta T=$ 2$^\circ$C"+r"$(SLO: \Delta T=$3.2$^\circ$C)",color="lime")
lines += ax.plot(data_projections_ec["year"].values[ind1:ind2]+0.5,data_projections_ec["paris15"].values[ind1:ind2],\
         lw=4,label="skupaj - scenarij \nPariski sporazum "+r"$\Delta T=$1.5$^\circ$C "+r"$(SLO: \Delta T=$2.4$^\circ$C)",color="darkgreen")

from matplotlib.legend import Legend
leg = Legend(ax, lines, \
             ["skupaj - scenarij NEPN 'business as usual'",\
              "skupaj - scenarij NEPN obstoječi ukrepi",\
              "skupaj - scenarij NEPN dodatni ukrepi,\nnuklearka",\
              "skupaj - scenarij NEPN\nambiciozni dodatni ukrepi, nuklearka",\
              "skupaj - cilji Evropske komisije",\
              "skupaj - Pariški sporazum "+r"$\Delta T=$ 2$^\circ$C "+r"$(SLO: \Delta T=$3.2$^\circ$C)",\
              "skupaj - Pariški sporazum "+r"$\Delta T=$1.5$^\circ$C "+r"$(SLO: \Delta T=$2.4$^\circ$C)"], \
              fontsize=18,bbox_to_anchor=(1, -0.1),loc='upper right',title="Projekcije/zaveze")
legend2 = ax.add_artist(leg)
legend2.get_title().set_fontsize('18')

ax.axvspan(0, 2022, alpha=0.1, color='gray')

#plt.legend(ncol=2,fontsize=18,bbox_to_anchor=(1.02, 1), loc='upper left')
fig.tight_layout()
fig.savefig("total_2023.png",dpi=300)

