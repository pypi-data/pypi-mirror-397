# %%

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import ultraplot as uplt
from hdxms_datasets import DataBase
from ipymolstar import PDBeMolstar

from instagibbs.methods import (
    delta_dataframes,
    weighted_average,
)
from instagibbs.plot import (
    pdbemolstar_colors,
    pdbemolstar_tooltips,
    chiclet_quantitative,
    chiclet_categorical,
)
from instagibbs.plot.mpl import mpl_peptides
from instagibbs.quantities import RFU, DRFU
from instagibbs.preprocess import load_hdx_dataset
from hdxms_datasets.utils import slice_exposure
# %%

root = Path(__file__).parent.parent
database_dir = root / "tests" / "test_data"

# %%


def wt_avg_dataframe(df: pl.DataFrame, extend=True) -> pl.DataFrame:
    """Compute weighted average of a peptide value dataframe

    Args:
        df: Dataframe with peptide values
        extend: Whether to extend the dataframe to residue number zero. Defaults to True.

    Returns:
        Dataframe with weighted average values

    """
    dfs = [weighted_average(df, value=col).rename({"value": col}) for col in df.columns[2:]]
    combined = pl.concat(dfs, how="align")
    if extend:
        r_max = int(combined["r_number"].max())  # type: ignore
        extended = pl.DataFrame({"r_number": np.arange(0, r_max + 1)}).join(
            combined, on="r_number", how="left"
        )
        return extended

    return combined


# %%

DATASET = "HDX_D9096080"  # SecBs state data
DATASET = "HDX_5756A4C0"
PLOT_QTY = "frac_fd_control"
PLOT_QTY = "frac_max_uptake"


# %%
db = DataBase(database_dir)
dataset = db.load_dataset(DATASET)  # Should load the dataset from the database
states = load_hdx_dataset(dataset)

# %%
state_base = list(states.values())[0]  # take the first state as base
state_diff = list(states.values())[1]  # take the second state as diff

exposure = state_base.exposure.tolist()[0]

# %%
rfu_peptides = slice_exposure(state_base.data)[0]
# %%
fig, ax = plt.subplots()
annotate = {"fontsize": 10}
patches = mpl_peptides(
    ax,
    rfu_peptides,
    RFU,
    value=PLOT_QTY,
    annotate=annotate,
)
fig.tight_layout()
ax.set_title(f"RFU ({PLOT_QTY})")


# %%
delta_rfu_peptides = delta_dataframes(state_diff.data, state_base.data, value=PLOT_QTY, how="right")

fig, ax = plt.subplots()
annotate = {"fontsize": 10}
patches = mpl_peptides(
    ax,
    slice_exposure(delta_rfu_peptides)[0],
    DRFU,
    value=f"delta_{PLOT_QTY}",
    annotate=annotate,
)
ax.set_title("ΔRFU (mutant - WT)")
fig.tight_layout()

# %%
state_base.rfu[:, 2:].mean()


# %%
df = state_base.data.pivot(on="exposure", index=["start", "end"], values=PLOT_QTY)
rfu_residues = wt_avg_dataframe(df)
fig, ax = uplt.subplots(refwidth="100mm", refheight="40mm", sharex=False, grid=False)

# quantitative chiclet plot of RFU's
# the chiclet edges are linearly interpolated between y values
# TODO accept qty?
mesh = chiclet_quantitative(
    ax,
    rfu_residues,
    y_values=state_base.exposure,
    cmap=RFU.cmap,
    norm=RFU.norm,
    yscale="log",
    invert_y=False,
    edge_lines={"color": "grey"},
)
ax.colorbar(mesh, width="2.5mm", label="RFU")
ax.format(ylabel="Exposure time (s)", yformatter="log")

# %%
# categorical chiclet plot of RFU's
# each chiclet has the same width on the y axis
fig, ax = uplt.subplots(refwidth="100mm", refheight="40mm", sharex=False, grid=False)
mesh = chiclet_categorical(
    ax,
    rfu_residues,
    x="r_number",
    cmap=RFU.cmap,
    norm=RFU.norm,
    labels=lambda x: f"{float(x):.2f} s",
    invert_y=False,
    edge_lines={"color": "r"},
)
ax.colorbar(mesh, width="2.5mm", label="RFU")

# %%
drfu_peptides_wide = delta_dataframes(
    state_diff.data, state_base.data, value=PLOT_QTY, how="inner"
).pivot(on="exposure", index=["start", "end"], values=f"delta_{PLOT_QTY}")
# %%

drfu_residues_wide = wt_avg_dataframe(drfu_peptides_wide, extend=True)

# %%
fig, ax = uplt.subplots(refwidth="100mm", refheight="40mm", sharex=False, grid=False)
mesh = chiclet_quantitative(
    ax,
    drfu_residues_wide,
    y_values=state_base.exposure,
    cmap=DRFU.cmap,
    norm=DRFU.norm,
    yscale="log",
    invert_y=False,
    edge_lines={"color": "k"},
)
ax.colorbar(mesh, width="2.5mm", label="ΔRFU")
ax.format(ylabel="Exposure time (s)", yformatter="log")

# %%
fig, ax = uplt.subplots(refwidth="100mm", refheight="40mm", sharex=False, grid=False)
mesh = chiclet_categorical(
    ax,
    drfu_residues_wide,
    x="r_number",
    cmap=DRFU.cmap,
    norm=DRFU.norm,
    labels=lambda x: f"{float(x):.2f} s",
    invert_y=False,
    edge_lines={"color": "k"},
)
ax.colorbar(mesh, width="2.5mm", label="ΔRFU")

# %%

drfu_peptides_long = delta_dataframes(state_diff.data, state_base.data, value=PLOT_QTY, how="inner")
drfu_peptides_long

# %%
df_p = slice_exposure(drfu_peptides_long)[0].rename({f"delta_{PLOT_QTY}": "value"})
df_r = weighted_average(df_p)

# %% view delta RFU on a structure
value = str(state_base.exposure[0])
color_data = pdbemolstar_colors(df_r, DRFU)
tooltips = pdbemolstar_tooltips(df_r, DRFU)
view = PDBeMolstar(
    custom_data=dataset.structure.pdbemolstar_custom_data(),
    hide_water=True,
    color_data=color_data,
    tooltips=tooltips,
)

view

# %%


def get_peptide(df, start: int, end: int):
    return df.filter((pl.col("start") == start) & (pl.col("end") == end))


# %%
start, end = state_base.peptides.row(1)
start, end
# %%
peptide_base = get_peptide(state_base.data, start, end)
peptide_diff = get_peptide(state_diff.data, start, end)
peptide_base
# %%


# %%
peptide_base
# %%
d_uptake_corrected = (pl.col("uptake") / pl.col("fd_uptake") * pl.col("max_uptake")).alias(
    "d_uptake_corrected"
)
peptide_base = peptide_base.with_columns(d_uptake_corrected)
peptide_diff = peptide_diff.with_columns(d_uptake_corrected)

# %%
fig, ax = plt.subplots()

x = peptide_base["exposure"]
y = peptide_base["d_uptake_corrected"]
y1 = peptide_diff["d_uptake_corrected"]
ax.fill_between(x, y, y1, color="grey", alpha=0.5)

ax.scatter(peptide_base["exposure"], peptide_base["d_uptake_corrected"], label="WT")
ax.scatter(peptide_diff["exposure"], peptide_diff["d_uptake_corrected"], label="mutant")
max_uptake = peptide_base["max_uptake"].unique().item()
ax.axhline(max_uptake, color="gray", linestyle="--", label="max uptake")
ax.legend()
ax.set_ylim(0, None)

ax.set_xscale("log")
ax.set_xlabel("Exposure time (s)")
ax.set_ylabel("d-uptake (corrected)")
plt.show()

# %%
