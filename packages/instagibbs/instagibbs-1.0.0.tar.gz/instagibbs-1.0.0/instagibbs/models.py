from __future__ import annotations

from functools import cached_property

import numpy as np
import polars as pl
from hdxms_datasets.models import Structure, StructureMapping
from hdxrate import k_int_from_sequence
from polars.exceptions import ColumnNotFoundError
from uncertainties import unumpy as unp


def ensure_equal_exposure(data: pl.DataFrame, exposures: list[float] | None = None) -> pl.DataFrame:
    """Ensure that all peptides have the same exposure."""

    unique_exposures = exposures or data["exposure"].unique()
    cols = ["start", "end"]

    grps = data.group_by(cols)
    dfs = [df for name, df in grps if set(df["exposure"]) == set(unique_exposures)]

    if len(dfs) == 0:
        exp_filtered = pl.DataFrame()
    else:
        exp_filtered = pl.concat(dfs).sort(by=cols + ["exposure"])

    return exp_filtered


class HDXState:
    def __init__(
        self,
        peptide_data: pl.DataFrame,
        metadata: dict,
        structure: Structure,
        structure_mapping: StructureMapping = StructureMapping(),
        name: str = "",
    ):
        peptide_cols = ["start", "end"]

        data = peptide_data.drop_nans(["uptake", "fd_uptake"]).sort(peptide_cols + ["exposure"])

        uptake_pivot = data.pivot(
            on="exposure", index=["start", "end"], values="uptake"
        ).drop_nulls()

        # we keep fd_uptake nulls
        fd_uptake_pivot = data.pivot(on="exposure", index=["start", "end"], values="fd_uptake")

        # these are now a table of unique peptides
        self.peptides = uptake_pivot[peptide_cols]

        # take the unique peptides from the full input table and store as data
        self.data = data.join(self.peptides, on=peptide_cols, how="inner")

        self.peptide_sequence = self.peptides.join(
            self.data["start", "end", "sequence"].unique(), on=["start", "end"], how="left"
        )["sequence"]

        # take the d uptake values as numpy array (N_p, N_e)
        self.uptake = uptake_pivot[:, 2:].to_numpy()
        # fd uptake as numpy array (N_p, )
        self.fd_uptake = fd_uptake_pivot.join(self.peptides, on=peptide_cols, how="inner")[
            :, 2
        ].to_numpy()
        # Exposure as numpy array (N_e, )
        self.exposure = data["exposure"].unique(maintain_order=True).to_numpy()

        self.metadata = metadata
        self.structure = structure
        self.structure_mapping = structure_mapping
        self.name = name

    @property
    def temperature(self) -> float:
        return self.metadata["temperature"]

    @property
    def pH(self) -> float:
        return self.metadata["pH"]

    @property
    def d_percentage(self) -> float:
        return self.metadata["d_percentage"]

    @property
    def n_term(self) -> int:
        return self.metadata["n_term"]

    @property
    def c_term(self) -> int:
        return self.metadata["c_term"]

    @property
    def sequence(self) -> str:
        return self.metadata["sequence"]

    @property
    def intervals(self) -> list[tuple[int, int]]:
        """Return the intervals of the peptides as a list of tuples (start, end)"""
        return [(start, end + 1) for start, end in self.peptides.iter_rows()]

    @property
    def r_number(self) -> np.ndarray:
        return np.arange(self.peptides["start"][0], self.peptides["end"][-1] + 1)

    @property
    def max_uptake(self) -> np.ndarray:
        """Number of exchange-competent peptides"""
        # TODO this information is also in the dataframe (should be)
        max_uptake = np.array([sum([c != "P" for c in seq]) for seq in self.peptide_sequence])

        return max_uptake

    def pivot(self, value: str) -> pl.DataFrame:
        """Pivot the data on the given values column."""
        return self.data.pivot(on="exposure", index=["start", "end"], values=value)

    def to_numpy(self, value: str) -> np.ndarray:
        """Convert the specified values column to a numpy array."""
        return self.data.pivot(on="exposure", index=["start", "end"], values=value)[
            :, 2:
        ].to_numpy()

    def to_uarray(self, value: str) -> np.ndarray:
        """Convert the specified values column to a numpy array."""
        values = self.to_numpy(value)
        values_sd = self.to_numpy(value + "_sd")

        arr = unp.uarray(values, values_sd)
        return arr

    def try_uarray(self, value: str) -> np.ndarray:
        """Try to convert the specified values column to a numpy array with uncertainties."""
        try:
            return self.to_uarray(value)
        except (KeyError, ColumnNotFoundError):
            # if the value is not present, return a numpy array of NaNs
            return self.to_numpy(value)

    def get_rfu_peptides(self, exposure: float | str) -> pl.DataFrame:
        """Get the RFU (fraction with respect to FD values) for a specific exposure time.
        returns dataframe with columns: start, end, sequence, value

        """
        return (
            self.data.pivot(on="exposure", index=["start", "end"], values="frac_fd_control")
            .with_columns(self.peptide_sequence)
            .select(["start", "end", "sequence", str(exposure)])
            .rename({str(exposure): "value"})
        )

    @property
    def rfu(self) -> pl.DataFrame:
        return self.data.pivot(on="exposure", index=["start", "end"], values="frac_fd_control")

    @property
    def uptake_corrected(self) -> np.ndarray:
        """uptake normalized to measured max uptake
        this is the standard m / m0 correction
        returned array has object dtype with uncertainties (nominal values with standard deviations)
        if 'uptake' or 'fd_uptake' have uncertainties.
        """

        uptake = self.try_uarray("uptake")
        fd_uptake = self.try_uarray("fd_uptake")
        max_uptake = self.to_numpy("max_uptake")
        uptake_corrected = uptake * (max_uptake / fd_uptake)

        return uptake_corrected

    @cached_property
    def k_int(self) -> np.ndarray:
        """
        Returns an array of k_int values based on the given sequence, temperature, pH, and d_percentage.

        Returns:
            np.ndarray: An array of k_int values.
        """
        return k_int_from_sequence(
            self.sequence, self.temperature, self.pH, d_percentage=self.d_percentage
        )
