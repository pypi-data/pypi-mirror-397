from dataclasses import dataclass, field, fields
from typing import Literal, TypeAlias

from hdxms_datasets.models import StructureMapping
import polars as pl
import solara

from instagibbs.methods import (
    ddG_from_area,
    dG_from_area,
    lasso_regression,
    ridge_regression,
    subtract_peptides,
    weighted_average,
)
from instagibbs.models import HDXState
from instagibbs.quantities import DDG, DG, DRFU, RFU, PlotQty


ReductionType: TypeAlias = Literal["weighted_average", "ridge_regression", "lasso_regression"]


@dataclass
class DataManager:
    hdx_states: dict[str, HDXState]
    # TODO as enum; with LUT for plotqtys
    qty: solara.Reactive[PlotQty] = field(default_factory=lambda: solara.reactive(DG))
    base_state: solara.Reactive[str] = field(init=False)
    diff_state: solara.Reactive[str] = field(init=False)

    exposure: solara.Reactive[str] = field(init=False)  # base/diff exposure? maybe not allow
    residue_reduction: solara.Reactive[ReductionType] = field(
        default_factory=lambda: solara.Reactive("weighted_average")
    )
    alpha: solara.Reactive[float] = field(default_factory=lambda: solara.reactive(0.1))

    _supported_qtys = {qty.name: qty for qty in [DG, DDG, RFU, DRFU]}

    def __post_init__(self):
        all_states = list(self.hdx_states.keys())
        self.base_state = solara.Reactive(all_states[0])
        self.diff_state = solara.Reactive(all_states[1] if len(all_states) > 1 else all_states[0])

        # TODO RFUs check for exposure in both states
        self.exposure = solara.Reactive(
            str(self.hdx_states[self.base_state.value].exposure.tolist()[0])
        )

    @property
    def hdx_base(self) -> HDXState:
        return self.hdx_states[self.base_state.value]

    @property
    def hdx_diff(self) -> HDXState:
        return self.hdx_states[self.diff_state.value]

    def get_peptide_df(self) -> pl.DataFrame:
        qty = self.qty.value
        if qty == DG:
            peptides = dG_from_area(self.hdx_base)
        elif qty == DDG:
            peptides = ddG_from_area(self.hdx_base, self.hdx_diff)
        elif qty == RFU:
            peptides = self.hdx_base.get_rfu_peptides(self.exposure.value)
        elif qty == DRFU:
            rfu_base = self.hdx_base.get_rfu_peptides(self.exposure.value)
            rfu_diff = self.hdx_diff.get_rfu_peptides(self.exposure.value)
            peptides = subtract_peptides(rfu_base, rfu_diff)
        else:
            raise ValueError(f"Unsupported quantity: {qty}")

        return peptides

    def get_residue_df(self) -> pl.DataFrame:
        peptides = self.get_peptide_df()

        if self.residue_reduction.value == "weighted_average":
            residues = weighted_average(peptides)
        elif self.residue_reduction.value == "ridge_regression":
            residues = ridge_regression(peptides, alpha=self.alpha.value)  # for DG/RFU
        elif self.residue_reduction.value == "lasso_regression":
            residues = lasso_regression(peptides, alpha=self.alpha.value)  # for DDG/DRFU
        else:
            raise ValueError(f"Unknown residue reduction method: {self.residue_reduction.value}")

        return residues

    def set_qty(self, qty_name: str):
        if qty_name not in self._supported_qtys:
            raise ValueError(f"Unsupported quantity: {qty_name}")
        new_qty = self._supported_qtys[qty_name]
        if new_qty in [DDG, DRFU] and self.residue_reduction.value == "ridge_regression":
            # lasso regression is not supported for DDG/DRFU
            self.residue_reduction.value = "weighted_average"
        elif new_qty in [DG, RFU] and self.residue_reduction.value == "lasso_regression":
            # ridge regression is not supported for DG/RFU
            self.residue_reduction.value = "weighted_average"

        self.qty.value = new_qty

    @property
    def qty_values(self) -> list[str]:
        """Return the names of the available quantities."""
        return list(self._supported_qtys.keys())

    @property
    def state_values(self) -> list[str]:
        """Return the names of the available states."""
        return list(self.hdx_states.keys())

    @property
    def exposure_values(self) -> list[str]:
        """Return the available exposure values from the base state."""
        # TODO ensure this always matches dataframe column names (or take them from the column names?)
        return [str(e) for e in self.hdx_base.exposure.tolist()]

    @property
    def pdbe_molstar_custom_data(self) -> dict:
        return self.hdx_base.structure.pdbemolstar_custom_data()

    @property
    def structure_mapping(self) -> StructureMapping:
        return self.hdx_base.structure_mapping

    @property
    def is_delta(self) -> bool:
        """Check if the current quantity is a delta quantity (DDG or DRFU)."""
        return self.qty.value in [DDG, DRFU]

    @property
    def label(self) -> str:
        """Return a label for the current quantity."""
        if self.is_delta:
            label = f"{self.qty.value.label}: {self.hdx_base.name} - {self.hdx_diff.name}"
        else:
            label = f"{self.qty.value.label}: {self.hdx_base.name}"

        return label

    def clone(self):
        field_names = [field_info.name for field_info in fields(self)]

        new_dm = DataManager(self.hdx_states)
        for field_name in field_names:
            field_self = getattr(self, field_name)
            if isinstance(field_self, solara.Reactive):
                field_other = getattr(new_dm, field_name)
                field_other.set(field_self.value)
        return new_dm
