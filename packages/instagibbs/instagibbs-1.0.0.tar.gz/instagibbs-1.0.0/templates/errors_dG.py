"""
Calculating error propagation from uptake sd to deltaG values
"""

# %%
from pathlib import Path

import numdifftools as nd
import numpy as np
import ultraplot as uplt
from hdxms_datasets import DataBase
from scipy.constants import R
from scipy.optimize import root_scalar
from uncertainties import umath
from uncertainties import unumpy as unp
import polars as pl
from numpy.typing import NDArray

from instagibbs.preprocess import load_hdx_dataset

# %%
root = Path(__file__).parent.parent
database_dir = root / "tests" / "test_data"
vault = DataBase(database_dir=database_dir)

# %%

DATASET = "HDX_0A55672B"
ds = vault.load_dataset(DATASET)

states = load_hdx_dataset(ds)
hdx_state = states[ds.get_state(0).name]

# %%

# get uptake and fd_uptake as uarrays (with uncertainties)
uptake = hdx_state.to_uarray("uptake")
fd_uptake = hdx_state.to_uarray("fd_uptake")
max_uptake = hdx_state.to_numpy("max_uptake")

uptake_corrected = uptake * (max_uptake / fd_uptake)


# %%
# Calculate areas (and errors) using trapezoidal rule on log t axis

t = np.log(hdx_state.exposure)
u_area = np.trapezoid(uptake_corrected, t, axis=1)

rel_errors = unp.std_devs(u_area) / unp.nominal_values(u_area)

# %%

# assume a flat 2 second error on exposure time; error for this datasets increases ~2fold
u_exposure = unp.uarray(hdx_state.exposure, 2.0 * np.ones_like(hdx_state.exposure))
u_t = np.array([umath.log(x) for x in u_exposure])

areas_t = np.trapezoid(uptake_corrected, u_t, axis=1)
rel_errors_t = unp.std_devs(areas_t) / unp.nominal_values(areas_t)

fig, ax = uplt.subplots()
ax.hist(rel_errors, bins="fd")
ax.hist(rel_errors_t, bins="fd", label="with uncertainties", alpha=0.5)
rel_errors_t.mean(), rel_errors.mean()
# %%
# comment out to use areas with t-error
# u_area = areas_t

# %%

# k_int geomean per peptide
k_int = np.empty(len(hdx_state.peptides), dtype=np.float64)
for i, (start, end) in enumerate(hdx_state.peptides.iter_rows()):
    pep_k_int = hdx_state.k_int[start - hdx_state.n_term : end - hdx_state.n_term + 1]
    nonzero = pep_k_int[np.nonzero(pep_k_int)]
    k_geomean = np.exp(np.mean(np.log(nonzero)))
    k_int[i] = k_geomean


# %%


def k_int_geomean(
    peptides: pl.DataFrame, k_int: NDArray[np.float64], n_term: int = 1
) -> NDArray[np.float64]:
    """Calculate the geometric mean of k_int values per peptide."""
    k_int_peptides = np.empty(len(peptides), dtype=np.float64)
    for i, (start, end) in enumerate(peptides.iter_rows()):
        pep_k_int = k_int[start - n_term : end - n_term + 1]
        nonzero = pep_k_int[np.nonzero(pep_k_int)]
        k_geomean = np.exp(np.mean(np.log(nonzero)))
        k_int_peptides[i] = k_geomean
    return k_int_peptides


max_d = max_uptake[:, 0]
area = unp.nominal_values(u_area)

# %%


def rootfunc_scalar(
    dG: float, time: np.ndarray, area: float, max_d: int, k: float, T: float
) -> float:
    d_ll = max_d * (1 - np.exp((-k * time) / (np.exp(-dG / (R * T)))))
    area_ll = np.trapezoid(d_ll, np.log(time))
    return area_ll - area


# %%
nboot = 50

bracket: tuple[float, float] = (20e3, -80e3)
t_lower, t_upper = np.log([hdx_state.exposure[0], hdx_state.exposure[-1]])
time = np.logspace(t_lower, t_upper, 250, endpoint=True, base=np.e)

dG_root = np.empty(len(hdx_state.peptides), dtype=np.float64)
dG_sd = np.empty(len(hdx_state.peptides), dtype=np.float64)
dG_sd_boot = np.empty(len(hdx_state.peptides), dtype=np.float64)
for pep_idx in range(len(hdx_state.peptides)):
    # Define the root function
    kwargs = {
        "time": time,
        "area": area[pep_idx],
        "max_d": max_d[pep_idx],
        "k": k_int[pep_idx],
        "T": hdx_state.temperature,
    }

    try:
        # Solve for dG
        ans = root_scalar(rootfunc_scalar, args=tuple(kwargs.values()), bracket=bracket)
        dG_root[pep_idx] = ans.root if ans.converged else np.nan

        d = nd.Derivative(rootfunc_scalar)(ans.root, **kwargs)
        dG_sd[pep_idx] = np.abs(1 / d) * unp.std_devs(u_area[pep_idx])

    except ValueError:
        dG_root[pep_idx] = np.nan

    # try bootstrapping errors
    if dG_root[pep_idx] is not np.nan:
        root_bootstrap = np.empty(nboot)
        for i in range(nboot):
            area_boot = np.random.normal(u_area[pep_idx].nominal_value, u_area[pep_idx].std_dev)
            boot_args = tuple((kwargs | {"area": area_boot}).values())
            try:
                ans = root_scalar(rootfunc_scalar, args=boot_args, bracket=bracket)
                root_bootstrap[i] = ans.root if ans.converged else np.nan
            except ValueError:
                print(i, pep_idx, "failed")

        dG_sd_boot[pep_idx] = np.nanstd(root_bootstrap)


dG_root, dG_sd, dG_sd_boot


# %%
# errors by finite differences
def rootfunc_vector(
    dG: np.ndarray, time: np.ndarray, area: np.ndarray, max_d: np.ndarray, k: np.ndarray, T: float
) -> np.ndarray:
    d_ll = max_d * (1 - np.exp((-np.outer(time, k)) / np.exp(-dG / (R * T))))

    area_ll = np.trapezoid(d_ll, np.log(time), axis=0)
    ans = area_ll - area
    ans[np.isnan(ans)] = 0.0  # Handle NaNs

    return ans  # Shape: (n,)


rootfunc_vector(dG_root, time, area, max_d, k_int, hdx_state.temperature)
args = (time, area, max_d, k_int, hdx_state.temperature)

eps = 1e-6
df_dg = (rootfunc_vector(dG_root + eps, *args) - rootfunc_vector(dG_root - eps, *args)) / (2 * eps)
dG_sd_fin_diff = np.abs(1 / df_dg) * unp.std_devs(u_area)
dG_sd_fin_diff
# %%

fig, ax = uplt.subplots()

ax.scatter(dG_sd / dG_root, label="numdifftools")
ax.scatter(dG_sd_boot / dG_root, label="bootstrap")
ax.scatter(dG_sd_fin_diff / dG_root, label="finite differences")
ax.format(ylim=(0, -0.2))

# %%

rel_err1 = np.abs(dG_sd / dG_root)
rel_err2 = np.abs(dG_sd_boot / dG_root)
rel_err3 = np.abs(dG_sd_fin_diff / dG_root)

n = len(rel_err1)
x = np.arange(n)

rng = np.random.default_rng(42)
jitter = 0.15

fig, axes = uplt.subplots(nrows=3, aspect=1.61, axwidth="100mm")
for ax in axes[:2]:
    ax.scatter(x - jitter, rel_err1, label="numdifftools", color="C0", alpha=0.8, s=40, marker="o")
    ax.scatter(x, rel_err2, label="bootstrap", color="C1", alpha=0.8, s=40, marker="s")
    ax.scatter(x + jitter, rel_err3, label="finite diff", color="C2", alpha=0.8, s=40, marker="^")
    ax.legend(loc="r", ncols=1)
    ax.format(
        xlabel="Peptide index",
        ylabel="Relative error",
        title="Relative error comparison of methods",
        grid=True,
    )

axes[0].format(ylim=(0, 0.2))
axes[1].format(ylim=(0, 0.02))

axes[2].scatter(dG_root)
axes[2].format(ylabel="dG (J/mol)", title="DeltaG vlaues")
uplt.show()
# %%
# Plot absolute errors
n = len(rel_err1)
x = np.arange(n)

rng = np.random.default_rng(42)
jitter = 0.15

fig, axes = uplt.subplots(nrows=3, aspect=2, axwidth="100mm")

axes[0].scatter(x - jitter, dG_sd, label="numdifftools", color="C0", alpha=0.8, s=40, marker="o")
axes[0].scatter(x, dG_sd_boot, label="bootstrap", color="C1", alpha=0.8, s=40, marker="s")
axes[0].scatter(
    x + jitter, dG_sd_fin_diff, label="finite diff", color="C2", alpha=0.8, s=40, marker="^"
)
axes[0].legend(loc="r", ncols=1)
axes[0].format(
    xlabel="Peptide index",
    ylabel="Absolute error",
    title="Absolute error comparison of methods",
    grid=True,
)

axes[0].format(ylim=(0, 2000))
axes[2].scatter(dG_root)
axes[2].format(ylabel="dG (J/mol)", title="DeltaG vlaues")
uplt.show()

# %%
fig, axes = uplt.subplots(nrows=4, aspect=2, axwidth="100mm")
axes[0].scatter(np.mean(unp.std_devs(uptake) / unp.nominal_values(uptake), axis=1))
axes[1].scatter(unp.std_devs(uptake) / unp.nominal_values(uptake))
axes[2].scatter(unp.std_devs(fd_uptake) / unp.nominal_values(fd_uptake))
axes[3].scatter(unp.std_devs(u_area) / unp.nominal_values(u_area))
fig.tight_layout()
uplt.show()

# %%
