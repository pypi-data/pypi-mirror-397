# %%
from __future__ import annotations

from pathlib import Path

import numpy as np
import polars as pl
import pytest
from hdxms_datasets import DataBase, HDXDataSet

from instagibbs.methods import (
    ddG_from_area,
    dG_from_area,
    drfu,
    ridge_regression,
    weighted_average,
)
from instagibbs.models import HDXState
from instagibbs.preprocess import load_hdx_dataset

test_dir = Path(__file__).parent
database_dir = test_dir / "test_data"
vault = DataBase(database_dir=database_dir)

DATASET = "HDX_0A55672B"
STATE_WT = "Tetramer"


@pytest.fixture()
def dataset() -> HDXDataSet:
    ds = vault.load_dataset(DATASET)
    return ds


@pytest.fixture()
def states(dataset: HDXDataSet) -> dict[str, HDXState]:
    return load_hdx_dataset(dataset)


@pytest.fixture()
def reference_result() -> np.lib.npyio.NpzFile:
    return np.load(test_dir / "test_reference" / "secb_results.npz")


def test_load_state(dataset: HDXDataSet):
    states = load_hdx_dataset(dataset)
    hdx_state = states[STATE_WT]

    assert isinstance(hdx_state, HDXState)

    peptide = hdx_state.peptides[0]
    assert isinstance(peptide, pl.DataFrame)

    peptide_sequence = hdx_state.peptide_sequence
    assert len(peptide_sequence) == 63
    assert peptide_sequence[0] == "MTFQIQRIY"


def test_dG_from_area(states: dict[str, HDXState], reference_result: np.lib.npyio.NpzFile):
    hdx_state = states[STATE_WT]
    dG_peptides = dG_from_area(hdx_state)

    assert isinstance(dG_peptides, pl.DataFrame)
    assert len(dG_peptides) == 63

    # Compare with reference result
    ref_dG_peptides = reference_result["dG_peptides"]
    np.testing.assert_allclose(
        -dG_peptides["value"].to_numpy(), ref_dG_peptides, rtol=1e-5, equal_nan=True
    )

    dG_residue = weighted_average(dG_peptides)
    assert isinstance(dG_residue, pl.DataFrame)
    assert len(dG_residue) == 147

    # Compare with reference result
    ref_dG_residue = reference_result["dG_residue"]
    np.testing.assert_allclose(
        -dG_residue["value"].to_numpy(), ref_dG_residue, rtol=1e-5, equal_nan=True
    )

    dG_residue_ridge = ridge_regression(dG_peptides, alpha=0.1)
    assert isinstance(dG_residue_ridge, pl.DataFrame)
    assert len(dG_residue_ridge) == 147

    # Compare with reference result
    ref_dG_residue_ridge = reference_result["dG_residue_ridge"]
    test_dG_residue_ridge = dG_residue_ridge["value"].to_numpy()

    # sets NaNs from test to reference
    ref_dG_residue_ridge[np.isnan(test_dG_residue_ridge)] = np.nan

    np.testing.assert_allclose(
        -test_dG_residue_ridge, ref_dG_residue_ridge, rtol=1e-5, equal_nan=True
    )


def test_rfu(states: dict[str, HDXState], reference_result: np.lib.npyio.NpzFile):
    hdx_state = states[STATE_WT]
    rfu_df = hdx_state.rfu

    assert isinstance(rfu_df, pl.DataFrame)
    rfu_peptides = rfu_df[:, 2:].to_numpy()
    assert rfu_peptides.shape == (63, 5)

    # Compare with reference result
    ref_rfu_peptides = reference_result["rfu_peptides"]
    np.testing.assert_allclose(rfu_peptides, ref_rfu_peptides, rtol=1e-5)


def test_ddG_drfu(states: dict[str, HDXState], reference_result: np.lib.npyio.NpzFile):
    names = list(states.keys())
    base_state_name = names[0]
    diff_state_name = names[1]
    state_base = states[base_state_name]
    state_diff = states[diff_state_name]

    ddg_peptides = ddG_from_area(state_base, state_diff)
    assert isinstance(ddg_peptides, pl.DataFrame)

    assert len(ddg_peptides) == 63

    # Compare with reference result
    ref_ddG_peptides = reference_result["ddg_peptides"]
    np.testing.assert_allclose(
        ddg_peptides["value"].to_numpy(), ref_ddG_peptides, rtol=1e-5, equal_nan=True
    )

    drfu_df = drfu(state_base, state_diff)
    assert isinstance(drfu_df, pl.DataFrame)

    drfu_peptides = drfu_df.pivot(on="exposure", index=["start", "end"], values="drfu")
    drfu_peptides = drfu_peptides[:, 2:].to_numpy()

    assert drfu_peptides.shape == (63, 5)

    # Compare with reference result
    ref_drfu_peptides = reference_result["drfu_peptides"]
    np.testing.assert_allclose(drfu_peptides, ref_drfu_peptides, rtol=1e-5, equal_nan=True)
