from pathlib import Path
from string import Template
from instagibbs.__version__ import __version__
from hdxms_datasets import HDXDataSet

BASE_DIR = Path(__file__).parent
about_template = Template((BASE_DIR / "about.md").read_text())
subs = {"version": str(__version__)}
about_md = about_template.safe_substitute(subs)


# datasets which are available in memory
IN_MEMORY_DATASETS: dict[str, HDXDataSet] = {}
