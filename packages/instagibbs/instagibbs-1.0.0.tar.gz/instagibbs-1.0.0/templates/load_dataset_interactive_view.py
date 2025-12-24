"""
Load a set of HDX states and show as ViewCard
For running in (VSCode) interactive window

"""

from pathlib import Path

from hdxms_datasets import DataBase

from instagibbs.models import HDXState
from instagibbs.preprocess import load_hdx_dataset
from instagibbs.web.app import ViewCard, DataManager

# %%

root = Path(__file__).parent.parent
database_dir = root / "tests" / "test_data"
vault = DataBase(database_dir=database_dir)


DATASET = "HDX_0A55672B"
ds = vault.load_dataset(DATASET)

# %%
states = load_hdx_dataset(ds)
dm = DataManager(hdx_states=states)
ViewCard(dm)
# %%
