# %%
from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

import colorcet as cc
import matplotlib.cm as cm
import numpy as np
import tol_colors as tc
from matplotlib.colors import Colormap, Normalize, to_hex
from instagibbs.utils import rgb_to_hex

if TYPE_CHECKING:
    from altair import Scale

NO_COVERAGE = "#8c8c8c"


def make_cmap(cmap_source, bad_color: str = NO_COVERAGE) -> Colormap:
    """Create a colormap with bad values set."""
    cmap = cmap_source.copy()  # Make a copy to avoid modifying original
    cmap.set_bad(bad_color)
    return cmap


@dataclass(frozen=True)
class PlotQty:
    """
    A dataclass to hold the plotting quantity and its associated colormap and normalization.
    """

    name: str
    unit: str
    cmap: Colormap
    vmin: float = 0.0
    vmax: float = 1.0
    clip: bool = True
    scale_factor: float = 1.0

    @property
    def label(self) -> str:
        """
        Returns the label for the quantity, formatted as 'name (unit)'.
        """
        return f"{self.name} ({self.unit})"

    @property
    def mappable(self) -> cm.ScalarMappable:
        """
        Returns a ScalarMappable object for the colormap and normalization.
        """
        return cm.ScalarMappable(norm=self.norm, cmap=self.cmap)

    @property
    def color_bad(self) -> str:
        """
        Returns the color used for bad values (Null/NaN) in the colormap.
        """
        return to_hex(self.cmap.get_bad())  # type: ignore

    @property
    def norm(self) -> Normalize:
        return Normalize(vmin=self.vmin, vmax=self.vmax, clip=self.clip)

    @property
    def alt_scale(self) -> Scale:
        from altair import Scale

        N = 256
        domain = self.norm.vmin, self.norm.vmax
        hex_colors = rgb_to_hex(self.cmap(np.linspace(0, 1, N, endpoint=True), bytes=True))
        scale = Scale(domain=domain, range=hex_colors, clamp=True)  # type: ignore

        return scale

    def get_colors(self, values, bytes: bool = False):
        return self.cmap(self.norm(self.scale_factor * values), bytes=bytes)


RFU = PlotQty(
    name="RFU",
    unit="a.u.",
    cmap=make_cmap(cc.cm.gouldian),
    scale_factor=1.0,
)

DRFU = PlotQty(
    name="ΔRFU",
    unit="a.u.",
    cmap=make_cmap(cc.cm.diverging_bwr_20_95_c54),
    vmin=-0.5,
    vmax=0.5,
    scale_factor=1.0,
)

DG = PlotQty(
    name="ΔG",
    unit="kJ/mol",
    cmap=make_cmap(tc.tol_cmap("rainbow_PuRd")),  # type: ignore
    vmin=-40,
    vmax=-10,
    scale_factor=1e-3,  # convert J to kJ
)

DDG = PlotQty(
    name="ΔΔG",
    unit="kJ/mol",
    cmap=make_cmap(tc.tol_cmap("PRGn").reversed()),  # type: ignore
    vmin=-10,
    vmax=10,
    scale_factor=1e-3,  # convert J to kJ
)
