import polars as pl

from instagibbs.plot.helpers import find_wrap
import altair as alt
from instagibbs.quantities import PlotQty
from uncertainties import ufloat


def alt_rectangles(peptides: pl.DataFrame, wrap: int | None = None) -> pl.DataFrame:
    wrap = find_wrap(peptides, step=1) if wrap is None else wrap
    columns = [
        (pl.col("start") - 0.5).alias("x"),
        (pl.col("end") + 0.5).alias("x2"),
        (wrap - (pl.col("idx") % wrap)).alias("y"),
    ]

    rectangles = (
        peptides["start", "end"]
        .with_row_index("idx")
        .with_columns(columns)
        .with_columns((pl.col("y") - 1).alias("y2"))
    )

    return rectangles


def alt_peptides(
    peptides: pl.DataFrame,
    qty: PlotQty,
    value: str = "value",
    value_sd: str | None = None,
    width: str | int = "container",
    height: str | int = 350,
    wrap: int | None = None,
    fill_nan: bool = True,
) -> alt.Chart:
    if fill_nan:
        # nan values can cause problems in serialization
        peptides = peptides.fill_nan(None)

    value_sd = value_sd or f"{value}_sd"

    if value_sd in peptides.columns:
        tooltip_value = []
        for v, v_sd in zip(peptides[value], peptides[value_sd]):
            if v is not None and v_sd is not None:
                z = ufloat(v, v_sd).std_score(0)
                tooltip_value.append(
                    f"{v * qty.scale_factor:.2f} \u00b1 {v_sd * qty.scale_factor:.2f} ({z:.1f}\u03c3)"  # type: ignore
                )
            else:
                tooltip_value.append("NaN")
    else:
        tooltip_value = [
            f"{value * qty.scale_factor:.2f}" if value is not None else ""
            for value in peptides[value]
        ]

    rectangles = alt_rectangles(peptides, wrap=wrap)
    peptide_source = peptides.join(rectangles, on=["start", "end"], how="left").with_columns(
        pl.col(value) * qty.scale_factor, pl.Series(tooltip_value).alias("tooltip_value")
    )

    invalid = {"color": {"value": qty.color_bad}}
    peptide_chart = (
        alt.Chart(peptide_source)
        .mark_rect(
            stroke="black",
        )
        .encode(
            x=alt.X("x:Q", title="Residue Number"),
            y=alt.Y("y:Q", title="", axis=alt.Axis(ticks=False, domain=False, labels=False)),
            x2=alt.X2("x2:Q"),
            y2=alt.Y2("y2:Q"),
            tooltip=[
                alt.Tooltip("idx:Q", title="Index"),
                alt.Tooltip("start:Q", title="Start"),
                alt.Tooltip("end:Q", title="End"),
                alt.Tooltip("sequence:N", title="Sequence"),
                alt.Tooltip("tooltip_value:N", title=qty.label),
            ],
            color=alt.Color(f"{value}:Q", scale=qty.alt_scale, title=qty.label),
        )
        .configure_scale(invalid=invalid)
    )

    return peptide_chart.properties(height=height, width=width)


def alt_residues(
    residues: pl.DataFrame,
    qty: PlotQty,
    value: str = "value",
    value_sd: str | None = None,
    r_number: str = "r_number",
    width: str | int = "container",
    height: str | int = 350,
    pad: float | None = None,
    fill_nan: bool = True,
) -> alt.LayerChart | alt.Chart:
    if fill_nan:
        # nan values can cause problems in serialization
        residues = residues.fill_nan(None)

    zoom = alt.selection_interval(bind="scales")

    value_sd = f"{value}_sd" if value_sd is None else value_sd
    residue_source = residues.with_columns(pl.col(value) * qty.scale_factor)
    if pad is None:
        scale = alt.Undefined
    else:
        rv_min = residue_source[value].min()
        rv_max = residue_source[value].max()

        pad = (rv_max - rv_min) * 0.1  # type: ignore
        domain = rv_min - pad, rv_max + pad  # type: ignore

        scale = alt.Scale(domain=domain)  # type: ignore

    if value_sd in residues.columns:
        residue_source = residue_source.with_columns(pl.col(value_sd) * qty.scale_factor)
        residue_source = residue_source.with_columns(
            (pl.col(value) - pl.col(value_sd)).alias("y"),
            (pl.col(value) + pl.col(value_sd)).alias("y2"),
        )
        error_chart = (
            alt.Chart(residue_source)
            .mark_errorbar(ticks=True)
            .encode(
                alt.X(f"{r_number}:Q", title="Residue Number"),
                alt.Y("y:Q", title=qty.label, scale=scale),
                alt.Y2("y2:Q"),
                # color=alt.value(NO_COVERAGE),
            )
        )
    else:
        error_chart = None

    invalid = {"color": {"value": qty.color_bad}}
    residue_chart = (
        alt.Chart(residue_source)
        .mark_circle(size=100)
        .encode(
            x=alt.X(
                f"{r_number}:Q",
                title="Residue Number",
            ),
            y=alt.Y(f"{value}:Q", title=qty.label, scale=scale),
            tooltip=[
                alt.Tooltip(f"{r_number}:Q", title="Residue Number"),
                alt.Tooltip(f"{value}:Q", title=qty.label, format=".2f"),  # TODO: std tooltip
            ],
            color=alt.Color(f"{value}:Q", scale=qty.alt_scale, title=qty.label),
        )
        .add_params(zoom)
    )

    if error_chart is not None:
        chart = error_chart + residue_chart
    else:
        chart = residue_chart

    return chart.properties(height=height, width=width).configure_scale(invalid=invalid)
