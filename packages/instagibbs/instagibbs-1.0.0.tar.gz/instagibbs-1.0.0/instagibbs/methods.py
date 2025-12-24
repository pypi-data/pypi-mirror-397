from __future__ import annotations

import warnings
from typing import Literal, Tuple
import polars as pl
import numpy as np
from scipy.constants import R
from scipy.optimize import root_scalar
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from uncertainties import unumpy as unp

from instagibbs.models import HDXState


def subtract_peptides(
    peptides_left: pl.DataFrame,
    peptides_right: pl.DataFrame,
    value_left: str = "value",
    value_right: str = "value",
    value_out: str = "value",
):
    """
    Subtract the 'value' column of peptides_right from peptides_left.

    """

    placeholder_name = "_placeholder_"
    # Perform the subtraction
    # Rename the 'value' column in rfu_diff to avoid ambiguity after join
    peptides_right_renamed = peptides_right.rename({value_right: placeholder_name})

    # Perform a left join from rfu_base to rfu_diff_renamed
    # This keeps all rows from rfu_base and matching rows from rfu_diff_renamed
    # If no match, 'value_diff' will be null
    joined_df = peptides_left.join(
        peptides_right_renamed.select(["start", "end", placeholder_name]),
        on=["start", "end"],
        how="left",
    )

    if "sequence" in joined_df.columns:
        select = ["start", "end", "sequence", value_left]
    else:
        select = ["start", "end", value_left]

    # Subtract the values, nulls will propagate (value - null = null)
    subtracted_df = joined_df.with_columns(
        (pl.col(value_left) - pl.col(placeholder_name)).alias(value_out)
    ).select(select)

    return subtracted_df


def stack_uptake_curves(exposure: np.ndarray, uptake: np.ndarray) -> np.ndarray:
    Np, Ne = uptake.shape

    out = np.empty((Np, Ne, 2))
    out[:, :, 0] = exposure[np.newaxis, :]
    out[:, :, 1] = uptake

    return out


def k_int_geomean(peptides: pl.DataFrame, k_int: np.ndarray, n_term: int = 1) -> np.ndarray:
    """Calculate the geometric mean of k_int values per peptide."""
    k_int_peptides = np.empty(len(peptides), dtype=np.float64)
    for i, (start, end) in enumerate(peptides.iter_rows()):
        pep_k_int = k_int[start - n_term : end - n_term + 1]
        nonzero = pep_k_int[np.nonzero(pep_k_int)]
        k_geomean = np.exp(np.mean(np.log(nonzero)))
        k_int_peptides[i] = k_geomean
    return k_int_peptides


def rootfunc_scalar(
    dG: float, time: np.ndarray, area: float, max_d: int, k: float, T: float
) -> float:
    d_ll = max_d * (1 - np.exp((-k * time) / (np.exp(-dG / (R * T)))))
    area_ll = np.trapezoid(d_ll, np.log(time))
    return area_ll - area


def rootfunc_vector(
    dG: np.ndarray, time: np.ndarray, area: np.ndarray, max_d: np.ndarray, k: np.ndarray, T: float
) -> np.ndarray:
    d_ll = max_d * (1 - np.exp((-np.outer(time, k)) / np.exp(-dG / (R * T))))

    area_ll = np.trapezoid(d_ll, np.log(time), axis=0)
    ans = area_ll - area
    ans[np.isnan(ans)] = 0.0  # Handle NaNs

    return ans  # Shape: (n,)


def dG_from_area(
    hdx_state: HDXState,
    bracket: tuple[float, float] = (10e3, -50e3),
) -> pl.DataFrame:
    # TODO: allow errors on exposure time
    t = np.log(hdx_state.exposure)
    u_area = np.trapezoid(hdx_state.uptake_corrected, t, axis=1)
    k_int = k_int_geomean(hdx_state.peptides, hdx_state.k_int, hdx_state.n_term)
    max_d = hdx_state.to_numpy("max_uptake")[:, 0]
    area = unp.nominal_values(u_area)

    t_lower, t_upper = np.log([hdx_state.exposure[0], hdx_state.exposure[-1]])
    time = np.logspace(t_lower, t_upper, 250, endpoint=True, base=np.e)

    dG_root = np.empty(len(hdx_state.peptides), dtype=np.float64)
    for pep_idx in range(len(hdx_state.peptides)):
        args = (
            time,
            area[pep_idx],
            max_d[pep_idx],
            k_int[pep_idx],
            hdx_state.temperature,
        )

        try:
            # Solve for dG
            ans = root_scalar(rootfunc_scalar, args=args, bracket=bracket)
            dG_root[pep_idx] = ans.root if ans.converged else np.nan
        except ValueError:
            dG_root[pep_idx] = np.nan

    # Calculate finite difference errors
    eps = 1e-6
    args = (time, area, max_d, k_int, hdx_state.temperature)
    df_dg = (rootfunc_vector(dG_root + eps, *args) - rootfunc_vector(dG_root - eps, *args)) / (
        2 * eps
    )
    df_dg = np.where(df_dg == 0, np.nan, df_dg)  # Avoid division by zero
    dG_sd = np.abs(1 / df_dg) * unp.std_devs(u_area)

    return hdx_state.peptides.with_columns(
        hdx_state.peptide_sequence,
        pl.lit(dG_root).alias("value"),
        pl.lit(dG_sd).alias("value_sd"),
    )


def ddG_from_area(
    state_base: HDXState,
    state_diff: HDXState,
    intersect_exposure: Literal["interval", "identical"] = "identical",
) -> pl.DataFrame:
    if state_base.temperature != state_diff.temperature:
        warnings.warn("Comparing measurements with different temperatures")

    if len(state_diff.exposure) <= 1 or len(state_base.exposure) <= 1:
        raise ValueError("Must have more than 1 exposure time")

    r, t = intersect(state_base, state_diff, intersect_exposure=intersect_exposure)

    trapz_test = np.trapezoid(t.uptake_corrected, np.log10(t.exposure)[np.newaxis, :], axis=1)
    trapz_ref = np.trapezoid(r.uptake_corrected, np.log10(r.exposure)[np.newaxis, :], axis=1)

    trapz_area = trapz_test - trapz_ref
    ddG_sum = -np.log(10) * R * r.temperature * trapz_area
    length = r.peptides["end"] - r.peptides["start"] + 1
    ddG_mean = ddG_sum / length.to_numpy()

    ddG_df = r.peptides.with_columns(
        pl.lit(unp.nominal_values(ddG_mean)).alias("value"),
        pl.lit(unp.std_devs(ddG_mean)).alias("value_sd"),
    )
    peptides_sequence = state_base.peptides.with_columns(state_base.peptide_sequence)
    ddG_joined = peptides_sequence.join(ddG_df, on=["start", "end"], how="left")

    return ddG_joined


# mark for deprecation
def drfu(
    state_base: HDXState,
    state_diff: HDXState,
) -> pl.DataFrame:
    on = ["start", "end", "exposure"]
    value = "frac_fd_control"
    df_l = state_base.data[on + [value]]
    df_r = state_diff.data[on + [value]]

    joined = df_l.join(df_r, on=on, how="inner", suffix="_right")

    # Subtract the rfu values
    drfu = joined.with_columns(
        (pl.col("frac_fd_control_right") - pl.col("frac_fd_control")).alias("drfu")
    ).drop("frac_fd_control", "frac_fd_control_right")

    # Merge with original dataframe
    output = df_l[on].join(drfu, on=on, how="left")

    return output


# TODO potential target to move to hdxms_datasets ?
def delta_dataframes(
    df_left: pl.DataFrame,
    df_right: pl.DataFrame,
    value: str,
    on: list[str] | None = None,
    how: Literal["inner", "left", "right", "full", "semi", "anti", "cross"] = "right",
    prefix: str = "delta_",
) -> pl.DataFrame:
    """
    Calculate the difference between two DataFrames for a specific value column.
    Keeps all rows from df_left and matches rows from df_right based on the 'on' columns.

    Includes propagation of uncertainties if standard deviation columns are present.

    Args:
        df_left (pl.DataFrame): The left DataFrame.
        df_right (pl.DataFrame): The right DataFrame.
        value (str): The target column to calculate the difference for.
        how (str): The type of join to perform. Defaults to 'right'.
        on (list[str], optional): Columns to join on. Defaults to ["protein", "state", "start", "end", "exposure"],
            if present.
        prefix (str, optional): Prefix for the new columns. Defaults to "delta_".
    """

    on_columns = ["protein", "state", "start", "end", "exposure"]
    common_columns = set(df_left.columns).intersection(set(df_right.columns))
    if value not in common_columns:
        raise ValueError(f"Target column '{value}' must be present in both DataFrames.")

    if on is None:
        on = [col for col in on_columns if col in common_columns]

    select_columns = [value]
    if value + "_sd" in df_left.columns and value + "_sd" in df_right.columns:
        select_columns.append(value + "_sd")

    with_columns = [(pl.col(value) - pl.col(f"{value}_right")).alias(f"{prefix}{value}")]
    if value + "_sd" in select_columns:
        with_columns.append(
            (pl.col(f"{value}_sd") ** 2 + pl.col(f"{value}_sd_right") ** 2)
            .sqrt()
            .alias(f"{prefix}{value}_sd")
        )

    matching_peptides = df_left.join(df_right.select(on + select_columns), on=on, how=how)

    drop_columns = [f"{col}_right" for col in select_columns]
    output = matching_peptides.with_columns(with_columns).drop(drop_columns)

    return output


def coverage_blocks(intervals: list[tuple[int, int]]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert a list of intervals into a matrix representation and calculate block sizes.
    Each block is defined as the regions between consecutive edges of the intervals, ie
    sections of residues which are covered by an unique set of peptides.

    Args:
        intervals: A list of (start, end) tuples representing intervals
    Returns:
        A tuple containing:
        - X: A matrix where rows correspond to blocks (regions between consecutive edges)
             and columns correspond to intervals. The value X[i, j] is the size of block i
             if it's covered by interval j, otherwise 0. The shape of X is (n_blocks, n_intervals).
        - block_sizes: An array of sizes for each block
    Example:
        >>> coverage_blocks([(1, 5), (3, 7)])
        (array([[2, 0],  # Block [1, 3] is only covered by first interval
                [2, 2],  # Block [3, 5] is covered by both intervals
                [0, 2]]), # Block [5, 7] is only covered by second interval
         array([2, 2, 2])) # Sizes of the blocks [1, 3], [3, 5], [5, 7]
    """
    edges = np.array(sorted({a for tup in intervals for a in tup}))
    block_sizes = np.diff(edges)

    X = np.zeros((len(edges) - 1, len(intervals)), dtype=int)
    for i, tup in enumerate(intervals):
        e_start, e_stop = np.searchsorted(edges, tup)
        blocks = np.diff(edges[e_start : e_stop + 1])

        X[e_start:e_stop, i] = blocks

    return X, block_sizes


def weighted_average(
    df: pl.DataFrame,
    value: str = "value",
) -> pl.DataFrame:
    """
    Calculate weighted average of values over residues based on peptide intervals.
    Any NaN values in the `values` column will be dropped before calculation.

    Args:
        df (pl.DataFrame): DataFrame containing peptide intervals and values.
        start (str): Column name for the start of the peptide interval.
        end (str): Column name for the end of the peptide interval (inclusive interval).
        values (str): Column name for the values to average.
    """

    expected_columns = {"start", "end", value}
    if not expected_columns.issubset(df.columns):
        raise ValueError(f"DataFrame must contain columns: {expected_columns}")

    df = df.drop_nans([value]).drop_nulls([value])

    peptide_intervals = [(_start, _end + 1) for _start, _end in zip(df["start"], df["end"])]
    r_number = np.arange(df["start"].min(), df["end"].max() + 1)  # type: ignore
    X, block_sizes = coverage_blocks(peptide_intervals)

    with np.errstate(invalid="ignore"):
        Z_norm = X / np.sum(X, axis=1, keepdims=True)
    value_blocks = Z_norm.dot(df[value])
    values_residue = np.repeat(value_blocks, block_sizes)

    return pl.DataFrame({"r_number": r_number, "value": values_residue})


def _linear_regression_base(
    df: pl.DataFrame,
    model,
    value: str = "value",
    value_sd: str | None = None,
    n_bootstrap: int = 50,
) -> pl.DataFrame:
    """Base function for linear regression methods (Ridge, Lasso, etc.)"""
    expected_columns = {"start", "end", value}
    if not expected_columns.issubset(df.columns):
        raise ValueError(f"DataFrame must contain columns: {expected_columns}")

    df = df.drop_nans([value]).drop_nulls([value])

    peptide_intervals = [(_start, _end + 1) for _start, _end in zip(df["start"], df["end"])]
    r_number = np.arange(df["start"].min(), df["end"].max() + 1)  # type: ignore

    X, block_sizes = coverage_blocks(peptide_intervals)
    X_norm = X / np.sum(X, axis=0)

    y = df[value].to_numpy()
    model.fit(X_norm.T, y)
    values_residue = np.repeat(model.coef_ + model.intercept_, block_sizes)
    no_coverage = np.repeat(X.sum(axis=1) == 0, block_sizes)
    values_residue[no_coverage] = np.nan
    data_dict = {"r_number": r_number, "value": values_residue}

    value_sd = f"{value}_sd" if value_sd is None else value_sd
    if value_sd in df.columns and n_bootstrap != 0:
        y_std = df[value_sd].to_numpy()
        out = []
        for _ in range(n_bootstrap):
            y_boot = np.random.normal(y, y_std)
            model.fit(X_norm.T, y_boot)
            out.append(model.coef_ + model.intercept_)

        errors = np.std(np.array(out), axis=0)
        sd_values_residue = np.repeat(errors, block_sizes)
        sd_values_residue[no_coverage] = np.nan
        data_dict["value_sd"] = sd_values_residue

    return pl.DataFrame(data_dict)


def ridge_regression(
    df: pl.DataFrame,
    value: str = "value",
    value_sd: str | None = None,
    alpha: float = 1.0,
    n_bootstrap: int = 50,
) -> pl.DataFrame:
    if alpha == 0:
        model = LinearRegression()
    else:
        model = Ridge(alpha=alpha)

    return _linear_regression_base(df, model, value, value_sd, n_bootstrap)


# works well for ddG since the data is already centered
# see: https://medium.com/@mukulranjan/how-does-lasso-regression-l1-encourage-zero-coefficients-but-not-the-l2-20e4893cba5d
def lasso_regression(
    df: pl.DataFrame,
    value: str = "value",
    value_sd: str | None = None,
    alpha: float = 1.0,
    n_bootstrap: int = 50,
) -> pl.DataFrame:
    if alpha == 0:
        model = LinearRegression()
    else:
        model = Lasso(alpha=alpha, fit_intercept=False)

    return _linear_regression_base(df, model, value, value_sd, n_bootstrap)


def intersect(
    s_left: HDXState,
    s_right: HDXState,
    intersect_exposure: Literal["interval", "identical"] = "identical",
) -> tuple[HDXState, HDXState]:
    """Intersect HDX states by their peptides and exposures.

    Args:
        s_left (HDXState): The first HDX state.
        s_right (HDXState): The second HDX state.
        intersect_exposure (Literal["interval", "identical"]): How to intersect exposures.
            - "identical": Only keep exposures that are identical in both states.
            - "interval": Selects the largest exposure interval in the set of matching exposures,
                  ie allows for missing exposure data at intermediate time points.
    Returns:
        tuple[HDXState, HDXState]: A tuple containing two HDXState objects with intersected data.
    """

    if intersect_exposure == "identical":
        on = ["start", "end", "exposure"]
        d_match_left = s_left.data.join(s_right.data[on], on=on, how="inner")
        d_match_right = s_right.data.join(s_left.data[on], on=on, how="inner")
    elif intersect_exposure == "interval":
        matching_exposure = set(s_left.exposure) & set(s_right.exposure)
        vmin, vmax = min(matching_exposure), max(matching_exposure)

        d_left = s_left.data.filter(pl.col("exposure").is_between(vmin, vmax))
        d_right = s_right.data.filter(pl.col("exposure").is_between(vmin, vmax))

        on = ["start", "end"]
        d_match_left = d_left.join(d_right[on], on=on, how="inner")
        d_match_right = d_right.join(d_left[on], on=on, how="inner")

    s_match_left = HDXState(d_match_left, s_left.metadata, structure=s_left.structure)
    s_match_right = HDXState(d_match_right, s_right.metadata, structure=s_right.structure)

    return s_match_left, s_match_right


# def intersect_peptides(p_left: Protein, p_right: Protein) -> tuple[Protein, Protein]:
#     matching_peptides = set(p_left.peptides) & set(p_right.peptides)

#     bools_left = np.array([peptide in matching_peptides for peptide in p_left.peptides])
#     bools_right = np.array([peptide in matching_peptides for peptide in p_right.peptides])

#     return p_left.index(bools_left, axis=0), p_right.index(bools_right, axis=0)


# def intersect_exposures(
#     p_left: Protein, p_right: Protein, intersect: Literal["interval", "identical"] = "identical"
# ) -> tuple[Protein, Protein]:
#     matching_exposure = np.intersect1d(p_left.exposure, p_right.exposure)

#     if intersect == "identical":
#         bools_left = np.isin(p_left.exposure, matching_exposure)
#         bools_right = np.isin(p_right.exposure, matching_exposure)
#     elif intersect == "interval":
#         vmin, vmax = np.min(matching_exposure), np.max(matching_exposure)
#         bools_left = (p_left.exposure >= vmin) & (p_left.exposure <= vmax)
#         bools_right = (p_right.exposure >= vmin) & (p_right.exposure <= vmax)
#     else:
#         raise ValueError("`intersect` must be 'identical' or 'interval'")

#     return p_left.index(bools_left, axis=1), p_right.index(bools_right, axis=1)


def D_t(dG, time, temperature, k_int):
    """Calculate D-uptake as a function of time"""
    D_t = 1 - np.exp(
        np.divide(
            -k_int * time,
            1 + np.exp(dG / (R * temperature)),
        )
    )

    return D_t


def func_root_dg(
    dG: float, time: float, d_uptake: float, temperature: float, k_int: np.ndarray
) -> float:
    """function find root for dG given d_uptake and time"""
    dt = D_t(dG, time, temperature, k_int)

    return np.sum(dt) - d_uptake


def func_root_time(
    time: float, dG: float, d_uptake: float, temperature: float, k_int: np.ndarray
) -> float:
    """function find root for time given dG and d_uptake"""
    dt = D_t(dG, time, temperature, k_int)

    return np.sum(dt) - d_uptake
