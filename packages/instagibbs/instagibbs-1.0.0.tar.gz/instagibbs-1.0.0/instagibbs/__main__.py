import os
from pathlib import Path
from typing import Optional

import click
from hdxms_datasets import load_dataset
from solara.__main__ import run

from instagibbs.config import (
    CONFIG_DEFAULT_DIR,
    CONFIG_HOME_DIR,
    update_config_from_yaml,
    cfg,
)
from instagibbs.web.constants import IN_MEMORY_DATASETS

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

DEV_MODE = os.environ.get("INSTAGIBBS_DEBUG", "0") == "1"

ROOT = Path(__file__).parent
APP_PATH = ROOT / "web" / "app.py"


@click.group()
def cli():
    """Don't FRET! CLI for analyzing confocal solution smFRET data."""
    pass


def find_config_file(config_path: Path) -> Optional[Path]:
    if config_path.exists():
        return config_path
    elif (pth := CONFIG_HOME_DIR / config_path).exists():
        return pth
    elif (pth := CONFIG_DEFAULT_DIR / config_path).exists():
        return pth


def load_config(config_path: Path) -> None:
    resolved_cfg_path = find_config_file(Path(config_path))
    if not resolved_cfg_path:
        raise click.BadParameter(f"Configuration file '{config_path}' not found")

    update_config_from_yaml(resolved_cfg_path)
    click.echo("Loading config file at: " + str(resolved_cfg_path))


@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.option(
    "--config",
    type=click.Path(file_okay=True, exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Configuration file to use",
)
@click.option(
    "--remote-url",
    help="URL for remote database",
)
@click.option(
    "--database-dir",
    type=click.Path(file_okay=False, exists=True, dir_okay=True, path_type=Path),
    help="Path to local database directory",
)
@click.option(
    "--zip-file",
    type=click.Path(file_okay=True, exists=True, dir_okay=False, path_type=Path),
    help="Path to .zip file containing a dataset to directly load",
)
@click.argument("solara_args", nargs=-1, type=click.UNPROCESSED)
def serve(
    config: Optional[Path] = None,
    remote_url: Optional[str] = None,
    database_dir: Optional[Path] = None,
    zip_file: Optional[Path] = None,
    solara_args=None,
):
    """Run the don't fret web application."""
    if config is not None:
        load_config(Path(config))

    # Update cfg with CLI options (CLI overrides config file)
    if remote_url is not None:
        cfg.remote_url = remote_url
    if database_dir is not None:
        cfg.database_dir = Path(database_dir)

    # if we have a .zip file, load it and add to in-memory datasets
    if zip_file is not None:
        dataset = load_dataset(zip_file)
        IN_MEMORY_DATASETS[dataset.hdx_id] = dataset

        # set the dataset_id to load it directly
        cfg.dataset_id = dataset.hdx_id

    solara_args = solara_args or tuple()
    if DEV_MODE and {"-a", "--auto-restart"}.isdisjoint(solara_args):
        solara_args = (*solara_args, "-a")
    elif "--production" not in solara_args:
        solara_args = (*solara_args, "--production")
    args = [str(APP_PATH), *solara_args]

    run(args)


@cli.command()
@click.option("--user", "user", is_flag=True, help="Create config file in user's home directory")
def config(user: bool):
    """Create a local or global default configuration file."""
    src = ROOT / "config" / "default.yaml"
    if user:
        (CONFIG_HOME_DIR).mkdir(exist_ok=True, parents=True)
        output = CONFIG_HOME_DIR / "instagibbs.yaml"
    else:
        output = Path.cwd() / "instagibbs.yaml"

    if output.exists():
        click.echo(f"Configuration file already exists at '{str(output)}'")
        return

    else:
        output.write_text(src.read_text())

    click.echo(f"Configuration file created at '{str(output)}'")


if __name__ == "__main__":
    cli()
