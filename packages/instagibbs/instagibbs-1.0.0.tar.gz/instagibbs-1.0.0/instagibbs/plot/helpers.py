import polars as pl
import numpy as np


# moved to hdxms-datasets
def find_wrap(
    peptides: pl.DataFrame,
    margin: int = 4,
    step: int = 5,
    wrap_limit: int = 200,
) -> int:
    """
    Find the minimum wrap value for a given list of intervals.

    Args:
        peptides: Dataframe with columns 'start' and 'end' representing intervals.
        margin: The margin applied to the wrap value. Defaults to 4.
        step: The increment step for the wrap value. Defaults to 5.
        wrap_limit: The maximum allowed wrap value. Defaults to 200.

    Returns:
        int: The minimum wrap value that does not overlap with any intervals.
    """
    wrap = step

    while True:
        peptides_y = peptides.with_columns(
            (pl.int_range(pl.len(), dtype=pl.UInt32).alias("y") % wrap)
        )

        no_overlaps = True
        for name, df in peptides_y.group_by("y", maintain_order=True):
            overlaps = (np.array(df["end"]) + 1 + margin)[:-1] >= np.array(df["start"])[1:]
            if np.any(overlaps):
                no_overlaps = False
                break
                # return wrap

        wrap += step
        if wrap > wrap_limit:
            return wrap_limit  # Return the maximum wrap limit if no valid wrap found
        elif no_overlaps:
            return wrap
