"""
Load a dataset into the web interface.
to run:
`solara run templates/load_dataset_web_interface.py`

"""

# %%
from pathlib import Path
from hdxms_datasets.database import DataBase
import solara
from instagibbs.web.app import DATABASE_DIR, Main

# %%

root = Path(__file__).parent.parent
database_dir = root / "tests" / "test_data"
DATABASE_DIR.set(database_dir)
DATASET = "HDX_0A55672B"

database = DataBase(DATABASE_DIR.value)
print(database.datasets)
# %%


@solara.component  # type: ignore
def Page():
    if DATABASE_DIR.value != database_dir:
        DATABASE_DIR.set(database_dir)

    Main(DATASET)


# %%
