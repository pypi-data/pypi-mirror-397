from __future__ import annotations
import polars as pl
from collections import defaultdict

import numpy as np
import numpy.typing as npt
from instagibbs.utils import rgb_to_hex
from instagibbs.quantities import PlotQty
from hdxms_datasets.models import StructureMapping
import itertools


def augment_chain(
    data: list[dict],
    mapping: StructureMapping,
) -> list[dict]:
    """Augment a list of data with chain information"""

    chain_name = "auth_asym_id" if mapping.auth_chain_labels else "struct_asym_id"
    if mapping.chain:
        aug_data = []
        for elem, chain in itertools.product(data, mapping.chain):
            aug_data.append(elem | {chain_name: chain})
    else:
        aug_data = data

    return aug_data


def pdbemolstar_colors(
    df: pl.DataFrame,
    qty: PlotQty,
    mapping: StructureMapping = StructureMapping(),
) -> dict:
    """
    Generate a list of colors for residues in a DataFrame based on a colormap and normalization.

    Parameters:
        df: DataFrame containing residue numbers and values.
        qty: PlotQty instance containing colormap and normalization information.
        mapping:


    Returns:
        List of colors corresponding to the residue numbers.
    """

    # TODO make in sync with hdxms-datasets; currently duplicated code

    color_bytes = qty.get_colors(df["value"], bytes=True)
    color_hex = rgb_to_hex(color_bytes)  # type: ignore

    non_selected_color = qty.color_bad
    residue_name = "auth_residue_number" if mapping.auth_residue_numbers else "residue_number"

    data = [{residue_name: mapping.map(r), "color": c} for r, c in zip(df["r_number"], color_hex)]
    color_data = {
        "data": augment_chain(data, mapping),
        "nonSelectedColor": non_selected_color,
    }

    return color_data


def pdbemolstar_tooltips(
    df: pl.DataFrame,
    qty: PlotQty,
    mapping: StructureMapping = StructureMapping(),
    formatter: str = "{:.2f}",
) -> dict:
    """
    Create tooltip data for PDBe-MolStar visualization.
    This function generates a dictionary containing tooltip data for each residue,
    formatting values according to specified parameters.

    Parameters
    ----------
    df : pl.DataFrame
        DataFrame containing residue numbers and values.
    unit : str, default="kJ/mol"
        Unit to display after the value.
    qty : PlotQty
        PlotQty object
    formatter : str, default="{:.2f}"
        String format pattern for the value.


    Returns
    -------
    dict
        Dictionary with a "data" key containing a list of dictionaries with
        residue numbers and tooltip strings.

    """

    df = df.drop_nulls().drop_nans()

    residue_name = "auth_residue_number" if mapping.auth_residue_numbers else "residue_number"
    data = [
        {
            residue_name: mapping.map(int(resi)),
            "tooltip": qty.name + ": " + f"{formatter.format(val * qty.scale_factor)} {qty.unit}",
        }
        for resi, val in zip(df["r_number"], df["value"])
    ]

    tooltips = {
        "data": augment_chain(data, mapping),
    }

    return tooltips


def pymol_color_script(
    residues: list[int] | npt.NDArray[np.integer] | pl.Series,
    colors: list[str],
    no_coverage: str,
    residue_range: tuple[int, int],
) -> str:
    color_mapping = defaultdict(list)
    for r, c in zip(residues, colors):
        color_mapping[c.replace("#", "0x")].append(r)

    # any residue within the expected range that are not specified are
    # colored as no coverage
    missing_residues = set(range(*residue_range)) - set(residues)
    color_mapping[no_coverage.replace("#", "0x")] = list(missing_residues)

    s = ""
    for color, r_grp in color_mapping.items():
        s += f"color {color}, resi {'+'.join(map(str, r_grp))}\n"

    return s
