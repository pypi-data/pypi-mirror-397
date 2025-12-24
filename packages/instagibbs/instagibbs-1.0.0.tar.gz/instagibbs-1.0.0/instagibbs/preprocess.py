import warnings
from hdxms_datasets.models import DeuterationType, HDXDataSet, State
from hdxms_datasets.process import (
    compute_uptake_metrics,
    left_join,
    merge_peptide_tables,
    merge_peptides,
)
from hdxms_datasets.utils import get_peptides_by_type
from scipy.optimize import root_scalar
from hdxrate import k_int_from_sequence
from typing import Optional
import numpy as np
import polars as pl
import narwhals as nw
from instagibbs.models import HDXState as IGState


def has_fd_control(state: State) -> bool:
    """
    Check if the state has a fully deuterated control.
    """
    return any(
        peptide.deuteration_type == DeuterationType.fully_deuterated for peptide in state.peptides
    )


def rootfunc(t: float, k_int: np.ndarray, fd_measured: float) -> float:
    """
    Function to find the root for the back exchange time.
    """

    back_exchange = (1 - np.exp(-k_int * t)).sum()

    return len(k_int) - back_exchange - fd_measured


# TODO log back exchange conditions in datasets
# for now assume pH 4.5 and 0C
def try_correct_backexchange(
    sequence: str,
    fd_sequence: str,
    fd_uptake: float,
    pH: float = 4.5,
    temperature: float = 273.15,
    bracket=[0.1, 1e5],
) -> Optional[float]:
    # calculate the intrinsic rates for known fd control sequence
    k_int_fd = k_int_from_sequence(
        fd_sequence, pH_read=pH, temperature=temperature, ph_correction=False, exchange_type="HD"
    )

    sol = root_scalar(rootfunc, args=(k_int_fd, fd_uptake), bracket=bracket)
    if sol.converged:
        t_be = sol.root
        # calculate the intrinsic rates for the sequence with unknown back exchange
        k_int = k_int_from_sequence(
            sequence, pH_read=pH, temperature=temperature, ph_correction=False, exchange_type="HD"
        )

        # calculate the corrected FD uptake
        fd_uptake_corrected = len(k_int) - (1 - np.exp(-k_int * t_be)).sum().sum()
        return float(fd_uptake_corrected)
    else:
        return None


def adjust_fd_uptake_values(
    target_peptides: pl.DataFrame, fd_peptides: pl.DataFrame
) -> pl.DataFrame:
    """
    Correct the fully deuterated uptake values of target peptides based on known FD peptides.

    Given a known measurement of fully deuterated peptides, this function adjusts the uptake values
    of target peptides, matching by start and end values, but might differ in sequence due to mutations.

    Uptake values are corrected by first calculating an effective back exchange time for the FD peptides,
    then using this time to adjust the uptake values of the target peptides.

    """
    # group by peptide, take fd values
    agg = [pl.col("fd_uptake").unique().first(), pl.col("fd_uptake_sd").unique().first()]
    fd_values = (
        fd_peptides.group_by(["start", "end", "sequence"], maintain_order=True)
        .agg(agg)
        .drop_nulls("fd_uptake")
    )

    peptide_df = target_peptides[["start", "end", "sequence"]].unique(maintain_order=True)

    join = peptide_df.join(fd_values, on=["start", "end"], how="left", suffix="_fd")

    matched_peptides = join.filter(pl.col("sequence") == pl.col("sequence_fd"))
    mismatched_peptides = join.filter(pl.col("sequence") != pl.col("sequence_fd"))

    other = matched_peptides.drop("sequence_fd").rename(
        {"fd_uptake": "uptake", "fd_uptake_sd": "uptake_sd"}
    )

    if mismatched_peptides.is_empty():
        return other
    else:
        # for the mismatched peptides, we calculate the back exchange intrinsic rates for both sequences and use it to correct the FD uptake
        fd_uptake_values = []
        for row in mismatched_peptides.rows(named=True):
            value = try_correct_backexchange(row["sequence"], row["sequence_fd"], row["fd_uptake"])
            fd_uptake_values.append(value)

        # scale new sd with new uptake values
        uptake_sd = ((pl.col("uptake") / pl.col("fd_uptake")) * pl.col("fd_uptake_sd")).alias(
            "uptake_sd"
        )
        fixed = (
            mismatched_peptides.with_columns(pl.Series("uptake", fd_uptake_values))
            .with_columns(uptake_sd)
            .drop("sequence_fd", "fd_uptake_sd", "fd_uptake")
        )

        concat = pl.concat([other, fixed]).sort(by=["start", "end"])
        return concat


def process_missing_fd_control(target_state: State, fd_peptides: pl.DataFrame) -> pl.DataFrame:
    """
    fd_peptides dataframe should have fd_uptake, fd_uptake_sd columns

    """

    # TODO support multiple partially deuterated peptides (different pH, temperature)
    target_peptides = get_peptides_by_type(
        target_state.peptides, DeuterationType.partially_deuterated
    )
    assert target_peptides is not None
    target_peptides = (
        target_peptides.load().to_polars()["start", "end", "sequence"].unique(maintain_order=True)
    )
    corrected_fd_control = adjust_fd_uptake_values(target_peptides, fd_peptides)

    # process the rest of the state as usual
    pd_peptides = get_peptides_by_type(target_state.peptides, DeuterationType.partially_deuterated)
    assert pd_peptides is not None, "No partially deuterated peptides found in the dataset."
    nd_peptides = get_peptides_by_type(target_state.peptides, DeuterationType.non_deuterated)

    # merge with non-deuterated if available
    # TODO handle missing non-deuterated controls?
    if nd_peptides is None:
        output = pd_peptides.load()
    else:
        output = merge_peptide_tables(
            pd_peptides.load(),
            non_deuterated=nd_peptides.load(),
        )

    output = left_join(
        output, nw.from_native(corrected_fd_control), select_columns=["uptake"], prefix="fd"
    )

    # TODO take the compute step out of the function
    return compute_uptake_metrics(output, exception="ignore").to_polars()


def load_hdx_dataset(dataset: HDXDataSet) -> dict[str, IGState]:
    """
    Load HDX dataset and preprocess it.

    We process the whole dataset in batch to allow for sharing of FD controls between states.

    """
    processed_states: dict[str, pl.DataFrame] = {}
    states_with_fd = [s for s in dataset.states if has_fd_control(s)]
    for state in states_with_fd:
        merged = merge_peptides(state.peptides)
        processed_states[state.name] = compute_uptake_metrics(
            merged, exception="ignore"
        ).to_polars()

    # take the first processed state with FD control to derive FD control for the other states with it
    # or the one with the most peptides?
    # or we merge all FD states?  <- this #TODO
    fd_peptides_ref = next(iter(processed_states.values()))
    remaining_states = [s for s in dataset.states if not has_fd_control(s)]
    for target_state in remaining_states:
        result_df = process_missing_fd_control(target_state, fd_peptides_ref)
        processed_states[target_state.name] = result_df

    assert set(state.name for state in dataset.states) == set(processed_states.keys()), (
        "Not all states were processed."
    )

    out = {}
    for state in dataset.states:
        pd_peptides = get_peptides_by_type(state.peptides, DeuterationType.partially_deuterated)
        assert pd_peptides is not None, "No partially deuterated peptides found in the dataset."

        # check if all peptide mappings are equal, warn if not
        peptide_mappings = [p.structure_mapping for p in state.peptides]
        if not all(peptide_mappings[0] == mapping for mapping in peptide_mappings[1:]):
            warnings.warn("Peptide structure mappings are not all the same for state " + state.name)

        mapping = pd_peptides.structure_mapping

        metadata = {
            "pH": pd_peptides.pH,
            "temperature": pd_peptides.temperature,
            "d_percentage": pd_peptides.d_percentage,
            "n_term": state.protein_state.n_term,
            "c_term": state.protein_state.c_term,
            "sequence": state.protein_state.sequence,
        }

        df = processed_states[state.name]
        ig_state = IGState(
            df, metadata, structure=dataset.structure, structure_mapping=mapping, name=state.name
        )
        out[state.name] = ig_state

    # check if all states have the same structure mapping
    structure_mappings = [state.structure_mapping for state in out.values()]
    if not all(mapping == structure_mappings[0] for mapping in structure_mappings[1:]):
        warnings.warn("Not all states have the same structure mapping.")

    return out
