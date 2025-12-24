# %%
from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl

base_v = np.vectorize(np.base_repr)


def rgb_to_hex(rgb_a: np.ndarray) -> np.ndarray:
    """Converts rgba
    input values are [0, 255]

    alpha is set to zero

    returns as '#000000'

    adapted from from pyhdx

    """

    if isinstance(rgb_a, np.ndarray):
        # todo: allow rgb arrays
        assert rgb_a.shape[-1] == 4
        if rgb_a.data.c_contiguous:
            rgba_array = rgb_a
        else:
            rgba_array = np.array(rgb_a)
    else:
        raise TypeError(f"Invalid type for 'rgb_a': {rgb_a}")

    ints = rgba_array.astype(np.uint8).view(dtype=np.uint32).byteswap()
    padded = np.char.rjust(base_v(ints // 2**8, 16), 6, "0")
    result = np.char.add("#", padded).squeeze()

    return result


def hex_to_rgb(hex_color: str) -> tuple[int, ...]:
    return tuple(int(hex_color.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))


def clean_types(d: Any) -> Any:
    """cleans up nested dict/list/tuple/other `d` for exporting as yaml/json

    Converts library specific types to python native types, including numpy dtypes,
    OrderedDict, numpy arrays

    # https://stackoverflow.com/questions/59605943/python-convert-types-in-deeply-nested-dictionary-or-array

    """
    if isinstance(d, np.floating):
        return float(d)

    if isinstance(d, np.integer):
        return int(d)

    if isinstance(d, np.ndarray):
        return d.tolist()

    if isinstance(d, list):
        return [clean_types(item) for item in d]

    if isinstance(d, tuple):
        return tuple(clean_types(item) for item in d)

    if isinstance(d, OrderedDict):
        return clean_types(dict(d))

    if isinstance(d, dict):
        return {k: clean_types(v) for k, v in d.items()}

    if isinstance(d, Path):
        return str(d)

    else:
        return d


def sort_columns(df: pl.DataFrame, drop_columns: list[str] = []) -> pl.DataFrame:
    """Sorts the columns of a DataFrame based on the order of the provided list."""
    # typing: mean might return nan/null
    cols_sorted = sorted(df.drop(drop_columns).columns, key=lambda x: df[x].drop_nans().mean())  # type: ignore

    return df.select(drop_columns + cols_sorted)


"""
def find_connected_components(A: np.ndarray) -> list[np.ndarray]:
    # Convert to sparse matrix format, for efficient processing
    A_sparse = csr_matrix(A)

    # Create an adjacency matrix that includes both rows and columns of A
    rows, cols = A_sparse.shape
    adj_matrix = vstack(
        [
            hstack([csr_matrix((rows, rows)), A_sparse]),
            hstack([A_sparse.T, csr_matrix((cols, cols))]),
        ]
    )

    # Find the connected components
    n_components, labels = connected_components(csgraph=adj_matrix, directed=False)

    # Initialize a list to hold the submatrices
    submatrices = []

    # Iterate over each component to extract the submatrix
    for i in range(n_components):
        # Find the row and column indices corresponding to the current component within the original matrix
        row_indices = np.where(labels[:rows] == i)[0]
        col_indices = np.where(labels[rows:] == i)[0]

        # Extract the block corresponding to the current component
        block = A[np.ix_(row_indices, col_indices)]

        # Append the block to the list of submatrices
        submatrices.append((row_indices, col_indices, block))

    return submatrices
"""
