from __future__ import annotations
from matplotlib.collections import QuadMesh
import polars as pl
from typing import Callable, Iterable

import matplotlib.cm as cm
import numpy as np
from matplotlib.axes import Axes
from matplotlib.colorbar import Colorbar
from matplotlib.colors import Colormap, Normalize
from matplotlib.patches import Patch, Rectangle
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
from instagibbs.plot.helpers import find_wrap
from instagibbs.quantities import PlotQty
import ultraplot as uplt


def chiclet_quantitative(
    ax: uplt.Axes,
    df: pl.DataFrame,
    x: str = "r_number",
    y_values: Iterable[float] | Callable[[str], float] | None = None,
    cmap: Colormap | None = None,
    norm: Normalize | None = None,
    N: int = 256,
    yscale: str = "log",
    invert_y: bool = False,
    edge_lines: bool | dict = True,
) -> QuadMesh:
    """
    Plot a colormap of quantitative data as discrete chiclets.
    This function creates a colormap visualization where the y-axis represents discrete values
    (typiclly exposure time) and the x-axis represents positions (typically residue numbers).
    Each 'chiclet' or cell in the plot is colored according to the value at that position and y-value.
    Parameters
    ----------
    ax : uplt.Axes
        The axes on which to draw the plot.
    df : pl.DataFrame
        Input DataFrame where one column is the x coordinates, and remaining columns
        are the data values for different y levels.
    x : str, default="r_number"
        Column name in the DataFrame to use as x-coordinates.
    y_values : Iterable[float] | Callable[[str], float] | None, default=None
        Y-coordinates for each row of data. If None, uses the column names converted to float.
        If callable, applies the function to each column name to generate y values.
    cmap : Colormap | None, default=None
        Colormap to use for the plot. If None, uses viridis.
    norm : Normalize | None, default=None
        Normalization to apply to the colormap.
    N : int, default=256
        Number of color levels in the colormap.
    yscale : str, default="log"
        Scale for the y-axis, typically "log" or "linear".
    invert_y : bool, default=False
        Whether to invert the y-axis direction.
    edge_lines : bool | dict, default=True
        Whether to draw horizontal lines at the edges between chiclets.
        If a dict, passes those parameters to the axhline call.
    Returns
    -------
    QuadMesh
        The mesh object created by pcolormesh for further customization.

    """

    data_df = df.drop(x)
    if y_values is None:
        y_values = np.array([float(col) for col in data_df.columns])
    elif callable(y_values):
        y_values = np.array([y_values(col) for col in data_df.columns])
    elif isinstance(y_values, Iterable):
        y_values = np.array(y_values)

    x_vals = df[x]

    data = data_df.to_numpy().T

    diffs = np.diff(y_values)
    y_lower = y_values[0] - diffs[0] / 2
    y_upper = y_values[-1] + diffs[-1] / 2

    ymin = max(y_lower, y_values[0] / 2)
    ymax = min(y_upper, y_values[-1] * 2)

    mesh = ax.pcolormesh(
        x_vals, y_values, data, cmap=cmap or uplt.Colormap("viridis"), norm=norm, N=N
    )

    ax.format(yscale=yscale, ylim=(ymin, ymax), xlabel="Residue number")

    if edge_lines:
        kwargs = dict(color="k", lw=0.5, ls="-")
        if isinstance(edge_lines, dict):
            kwargs |= edge_lines
        edges = uplt.edges(y_values)
        for edge in edges:
            ax.axhline(edge, **kwargs)  # type: ignore

    if invert_y:
        ax.invert_yaxis()

    return mesh


def chiclet_categorical(
    ax: uplt.Axes,
    df: pl.DataFrame,
    x: str = "r_number",
    cmap: Colormap | None = None,
    norm: Normalize | None = None,
    N: int = 256,
    labels: list[str] | str | Callable[[str], str] | None = None,
    invert_y: bool = True,
    edge_lines: bool | dict = True,
) -> QuadMesh:
    """
    Create a categorical heatmap (chiclet plot) using pcolormesh.
    This function creates a heatmap where each row represents a categorical variable (ie protein states, mutants, etc.)
    and each column typically represents a position (like a residue number in a protein).
    Parameters
    ----------
    ax : uplt.Axes
        The axes on which to draw the plot.
    df : pl.DataFrame
        The dataframe containing the data to plot. Should include the column specified by `x`.
    x : str, default="r_number"
        The name of the column in `df` that contains the x-axis values.
    cmap : matplotlib.colors.Colormap or None, default=None
        The colormap to use. If None, defaults to viridis.
    norm : matplotlib.colors.Normalize or None, default=None
        The normalization to use for the colormap.
    N : int, default=256
        Number of color levels in the colormap.
    labels : list[str] or str or Callable[[str], str] or None, default=None
        The y-axis labels for the plot:
        - If None, uses column names from the dataframe
        - If str, formats each column name using the string
        - If callable, applies the function to each column name
        - If list, uses the provided list (must match column count)
    invert_y : bool, default=False
        If True, inverts the y-axis so the first category is at the top.
    edge_lines : bool or dict, default=True
        If True, draws horizontal lines between categories.
        If a dict, passes the dict as keyword arguments to ax.axhline().
    Returns
    -------
    QuadMesh
        The mesh object created by pcolormesh.
    Notes
    -----
    The dataframe columns (except the x column) become the categories (rows) in the plot.
    The x column values become the x-axis values (columns) in the plot.
    """

    data_df = df.drop(x)

    if labels is None:
        labels = data_df.columns
    elif isinstance(labels, str):
        labels = [labels.format(col) for col in data_df.columns]
    elif callable(labels):
        labels = [labels(col) for col in data_df.columns]
    elif isinstance(labels, list):
        if len(labels) != len(data_df.columns):
            raise ValueError(
                f"Length of labels ({len(labels)}) does not match number of columns in dataframe ({len(data_df.columns)})"
            )

    x_vals = df[x]
    y_vals = np.arange(len(labels)) + 1
    data = data_df.to_numpy().T
    mesh = ax.pcolormesh(
        x_vals, y_vals, data, cmap=cmap or uplt.Colormap("viridis"), norm=norm, N=N
    )

    ylocs = uplt.Locator("fixed", locs=y_vals)
    yfmt = uplt.Formatter(labels)
    ax.format(
        yscale="linear",
        xlabel="Residue number",
        ylocator=ylocs,
        yformatter=yfmt,
    )

    if edge_lines:
        kwargs = dict(color="k", lw=0.5, ls="-")
        if isinstance(edge_lines, dict):
            kwargs |= edge_lines
        edges = uplt.edges(y_vals)
        for edge in edges:
            ax.axhline(edge, **kwargs)  # type: ignore

    if invert_y:
        ax.invert_yaxis()

    return mesh


def mpl_peptides(
    ax: Axes,
    df: pl.DataFrame,
    qty: PlotQty,
    start: str = "start",
    end: str = "end",
    value: str = "value",
    colorbar: bool | dict = True,
    annotate: bool | dict = True,
    wrap: int | None = None,
) -> list[Patch]:
    N = len(df)

    colors = qty.get_colors(df[value])

    if wrap is None:
        wrap = find_wrap(df["start", "end"], margin=4, step=1, wrap_limit=200)

    y = np.arange(N) % wrap
    y = wrap - y
    kw = {"linewidth": 0.5, "linestyle": "-", "edgecolor": "k"}
    patches = []
    for idx, (y_pos, _start, _end, color) in enumerate(zip(y, df[start], df[end], colors)):
        width = _end - _start + 1
        rect = Rectangle((_start - 0.5, y_pos - 1), width, 1, facecolor=color, **kw)
        patch = ax.add_patch(rect)
        patches.append(patch)

        if annotate:
            # Annotate the rectangle with the index number
            center_x = _start + width / 2
            center_y = y_pos - 0.5
            annotate_defaults = dict(color="k", fontsize=10, ha="center", va="center")
            if isinstance(annotate, dict):
                annotate_defaults.update(annotate)
            text = str(idx)
            ax.annotate(text, (center_x, center_y), **annotate_defaults)

    # v_start, v_stop = zip(*intervals)
    vlower, vupper = df[start].min(), df[end].max() + 1
    width = vupper - vlower
    pad = 0.05
    xlim = (vlower - pad * width, vupper + 1 + pad * width)
    # pad x lim with range
    ax.set_xlim(*xlim)
    ax.set_ylim(0, wrap)
    ax.set_yticks([])
    ax.set_xlabel("Residue Number")

    if colorbar:
        cbar_kw = dict(width="4mm")
        if isinstance(colorbar, dict):
            cbar_kw.update(colorbar)

        if isinstance(ax, (uplt.Axes, uplt.SubplotGrid)):
            cbar = ax.colorbar(qty.mappable, label=qty.label, **cbar_kw)
        else:
            divider = make_axes_locatable(ax)
            size = uplt.utils.units(cbar_kw["width"])
            pad = cbar_kw.get("pad", 0.05)
            cax = divider.append_axes("right", size=size, pad=uplt.utils.units(pad))
            cmap = cm.get_cmap(qty.cmap, N)
            norm = Normalize(vmin=qty.norm.vmin, vmax=qty.norm.vmax)
            cbar = Colorbar(cax, cmap=cmap, norm=norm)
            cbar.set_label(qty.label)
            cax.grid(False)

    return patches


def scatter(
    ax: Axes,
    df: pl.DataFrame,
    qty: PlotQty,
    r_number: str = "r_number",
    value: str = "value",
    value_sd: str | None = None,
) -> Axes:
    ax.scatter(
        df[r_number],
        df[value] * qty.scale_factor,
        c=df[value] * qty.scale_factor,
        cmap=qty.cmap,
        norm=qty.norm,
    )
    ax.set_ylabel(qty.label)
    ax.set_xlabel("Residue number")

    value_sd = f"{value}_sd" if value_sd is None else value_sd
    if value_sd in df.columns:
        ax.errorbar(
            df[r_number],
            df[value] * qty.scale_factor,
            yerr=df[value_sd] * qty.scale_factor,
            fmt="o",
            ecolor="grey",
            color="none",
            zorder=-10,
        )

    return ax
