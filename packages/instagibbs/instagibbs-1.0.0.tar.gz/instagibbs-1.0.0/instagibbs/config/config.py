from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from pathlib import Path

import dacite as dc
import yaml
from dacite.data import Data

from instagibbs.utils import clean_types

CONFIG_HOME_DIR = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")) / "instagibbs"
CONFIG_DEFAULT_DIR = Path(__file__).parent


@dataclass
class Config:
    """Global configuration object"""

    database_dir: Path
    remote_url: str

    # when set, directly load this dataset, from memory, local database, or remote database
    dataset_id: str | None = None

    @classmethod
    def from_dict(cls, data: Data):
        config = dc.Config(type_hooks={Path: lambda v: Path(v).expanduser()})
        return dc.from_dict(cls, data, config)

    @classmethod
    def from_yaml(cls, fpath: Path):
        data = yaml.safe_load(fpath.read_text())
        return cls.from_dict(data)

    def to_yaml(self, fpath: Path) -> None:
        s = yaml.dump(clean_types(asdict(self)), sort_keys=False)
        fpath.write_text(s)

    def update(self, data: Data):
        new_data = {**self.__dict__, **data}

        # we use `from_dict` to cast to the correct types
        new_cfg = Config.from_dict(new_data)
        vars(self).update(vars(new_cfg))

    def copy(self) -> Config:
        return Config.from_dict(asdict(self))


def update_config_from_yaml(config_path: Path) -> Config:
    """Updates the global configuration object with settings from a YAML file."""

    data = yaml.safe_load(config_path.read_text())
    cfg.update(data)
    return cfg


cfg_file_paths = [
    Path().cwd() / "instagibbs.yaml",
    CONFIG_HOME_DIR / "instagibbs.yaml",
    CONFIG_DEFAULT_DIR / "default.yaml",
]

# take the first one which exists
cfg_fpath = next((p for p in cfg_file_paths if p.exists()), None)
assert cfg_fpath
cfg = Config.from_yaml(cfg_fpath)
