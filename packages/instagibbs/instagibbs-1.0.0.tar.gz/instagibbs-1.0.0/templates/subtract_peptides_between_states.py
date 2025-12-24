"""
Example script on how to directly subtract peptides and an associated value
(e.g., uptake) between two states in an HDX-MS dataset.

"""

# %%
from pathlib import Path

from hdxms_datasets.database import DataBase
from hdxms_datasets.utils import slice_exposure

import polars as pl
from hdxms_datasets.plot import plot_peptides
from instagibbs.methods import delta_dataframes

# %%
root = Path(__file__).parent.parent
database_dir = root / "tests" / "test_data"

# %%
DATASET = "HDX_0A55672B"

# %%
db = DataBase(database_dir)
dataset = db.load_dataset(DATASET)

p_left: pl.DataFrame = dataset.states[0].peptides[0].load().to_native()
p_right: pl.DataFrame = dataset.states[1].peptides[0].load().to_native()
# %%

delta_uptake = delta_dataframes(p_left, p_right, value="uptake")
delta_uptake.head()

# make slicer object to select exposure
data_slice = slice_exposure(delta_uptake)
data_slice[0]
# %%
# select first exposure and plot
# gray peptides have no matching peptide in right state
plot_peptides(data_slice[0], value="delta_uptake")
