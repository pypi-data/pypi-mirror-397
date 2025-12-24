# %%
from __future__ import annotations

from hdxms_datasets.utils import slice_exposure
import matplotlib.pyplot as plt
from hdxms_datasets import DataBase
from pathlib import Path

from instagibbs.methods import drfu
from instagibbs.preprocess import load_hdx_dataset
from instagibbs.plot import mpl_peptides
from instagibbs.quantities import RFU, DRFU

# %%
root = Path(__file__).parent.parent
database_dir = root / "tests" / "test_data"

# %%

DATASET = "HDX_0A55672B"  # SecBs state data

db = DataBase(database_dir)
dataset = db.load_dataset(DATASET)  # Should load the dataset from the database
states = load_hdx_dataset(dataset)
# %%

state_base = list(states.values())[0]  # take the first state as base
state_diff = list(states.values())[1]  # take the second state as diff

data = slice_exposure(state_base.data)[0]
data

fig, ax = plt.subplots()
patches = mpl_peptides(ax, data, qty=RFU, value="frac_fd_control")

# %%
fig, ax = plt.subplots()
drfu_data = drfu(state_base, state_diff)
patches = mpl_peptides(ax, slice_exposure(drfu_data)[0], qty=DRFU, value="drfu")
