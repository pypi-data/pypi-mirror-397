# %%
from dataclasses import replace
from pathlib import Path

import matplotlib.pyplot as plt
import ultraplot as uplt
from hdxms_datasets.database import DataBase
from ipymolstar import PDBeMolstar

from instagibbs.methods import (
    ddG_from_area,
    dG_from_area,
    lasso_regression,
    ridge_regression,
    weighted_average,
)
from instagibbs.plot.alt import alt_peptides, alt_residues
from instagibbs.plot.mpl import mpl_peptides, scatter
from instagibbs.plot.structure import pdbemolstar_colors, pdbemolstar_tooltips
from instagibbs.preprocess import load_hdx_dataset
from instagibbs.quantities import DDG, DG

# %%
root = Path(__file__).parent.parent
database_dir = root / "tests" / "test_data"

# %%
DATASET = "HDX_0A55672B"  # SecBs state data
# DATASET = "HDX_BABA5B4C"  # Peterle 1MB

db = DataBase(database_dir)
dataset = db.load_dataset(DATASET)  # Should load the dataset from the database
# %%
states = load_hdx_dataset(dataset)

state_base = list(states.values())[0]  # take the first state as base
state_diff = list(states.values())[1]  # take the second state as diff

# %%
dG_peptides = dG_from_area(state_base)
ddG_peptides = ddG_from_area(state_base, state_diff)

# %%
dG_residues_wt_avg = weighted_average(dG_peptides)
dG_residues_ridge = ridge_regression(dG_peptides, alpha=0.1)

ddG_residues_wt_avg = weighted_average(ddG_peptides)
ddG_residues_lasso = lasso_regression(ddG_peptides, alpha=1.0)

# %%
alt_peptides(dG_peptides, DG).interactive()

# %%
alt_peptides(ddG_peptides, DDG).interactive()

# %%
alt_residues(
    ddG_residues_lasso,
    DDG,
    height=200,
    # value_sd='test',
)


# %%
fig, ax = uplt.subplots(refaspect=1.61, width="120mm")
cbar = {"width": "4mm", "pad": "1mm"}
rectangles = mpl_peptides(ax, dG_peptides, DG, colorbar=cbar)

# %%
fig, ax = plt.subplots()
annotate = {"fontsize": 10}
patches = mpl_peptides(
    ax,
    ddG_peptides,
    DDG,
    annotate=annotate,
)
fig.tight_layout()

# %%

fig, axes = uplt.subplots(nrows=2, sharex=True, axwidth="80mm", refaspect=1.6)
scatter(axes[0], dG_residues_wt_avg, DG)
scatter(axes[1], dG_residues_ridge, DG)

# %%

fig, axes = uplt.subplots(nrows=2, sharex=True, axwidth="80mm", refaspect=1.6)
scatter(axes[0], dG_residues_ridge, DG)
scatter(axes[1], ddG_residues_wt_avg, DDG)

# %%
# for the moment we assume all peptides in all states map to the structure in the same way
#

DDG_rescale = replace(DDG, vmin=-2, vmax=2)

# %%
mapping = state_base.structure_mapping
color_data = pdbemolstar_colors(ddG_residues_wt_avg, qty=DDG_rescale, mapping=mapping)
tooltips = pdbemolstar_tooltips(ddG_residues_wt_avg, qty=DDG_rescale, mapping=mapping)
color_data

# %%

view = PDBeMolstar(
    custom_data=dataset.structure.pdbemolstar_custom_data(),
    hide_water=True,
    color_data=color_data,
    tooltips=tooltips,
)
view

# %%
