import os
from pathlib import Path
from typing import Callable, Literal
from urllib.parse import parse_qsl
import warnings

import altair as alt
import polars as pl
import solara
import solara.lab
from hdxms_datasets import DataBase
from ipymolstar import PDBeMolstar
from ipymolstar.pdbemolstar import THEMES
from solara.alias import rv

from instagibbs.config import cfg
from instagibbs.plot.alt import alt_peptides, alt_residues
from instagibbs.plot.structure import pdbemolstar_colors, pdbemolstar_tooltips
from instagibbs.preprocess import load_hdx_dataset
from instagibbs.quantities import DDG, DRFU, RFU, PlotQty
from instagibbs.web.methods import (
    default_grid_layout,
    find_free_grid_position,
    new_card,
    td,
    th,
    tr,
)
from instagibbs.web.models import DataManager
from instagibbs.web.constants import BASE_DIR, IN_MEMORY_DATASETS, about_md

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

DEV_MODE = os.environ.get("INSTAGIBBS_DEV", "0") == "1"

if DEV_MODE:
    warnings.warn("Running in DEV mode!")

dprint = print if DEV_MODE else lambda *args, **kwargs: None

# Make ipymolstar use white background by in light theme
THEMES["light"]["bg_color"] = "#FFFFFF"


def is_running_in_huggingface():
    return "SPACE_ID" in os.environ


# Set database directory based on environment
if DEV_MODE:
    database_dir = Path("C:/Users/jhsmi/repos/mine/HDXMS-database/incoming/staging/output")
# TODO remove in favour of config / CLI option
elif is_running_in_huggingface():
    database_dir = Path.cwd().parent / "HDXMS-database" / "datasets"
else:
    database_dir = cfg.database_dir
    database_dir.mkdir(exist_ok=True, parents=True)

DATABASE_DIR = solara.Reactive(database_dir)

# move to constants module
initial_types = ["peptides_chart", "residues_chart", "structure"]
title_mapping = {
    "peptides_chart": "Peptides Chart",
    "residues_chart": "Residues Chart",
    "structure": "Structure View",
    "peptides_table": "Peptides Table",
    "residues_table": "Residues Table",
}

view_values = [{"text": v, "value": k} for k, v in title_mapping.items()]
pin_cards = solara.Reactive(False)

views_type = Literal[
    "peptides_chart", "residues_chart", "structure", "peptides_table", "residues_table"
]


def apply_quantity_scaling(df: pl.DataFrame, qty: PlotQty) -> pl.DataFrame:
    cols = [(pl.col("value") * qty.scale_factor).alias(qty.label)]
    drop_cols = ["value"]
    if "value_sd" in df.columns:
        cols.append((pl.col("value_sd") * qty.scale_factor).alias(f"{qty.label} SD"))
        drop_cols.append("value_sd")
    return df.with_columns(cols).drop(drop_cols)


# %%
@solara.component  # type: ignore
def ViewCard(
    data_manager: DataManager,
    view_type: views_type | solara.Reactive[views_type] = "peptides_chart",
    width="100%",
    height="400px",
    on_delete: Callable[[], None] | None = None,
):
    local_view_type = solara.use_reactive(view_type)
    title = title_mapping.get(local_view_type.value, "View Card")
    dark_effective = solara.lab.use_dark_effective()
    sync_with_global = solara.use_reactive(True)

    # TODO element portal / check reuse
    AltairThemeSetter()

    local_dm = solara.use_memo(lambda: data_manager.clone(), dependencies=[])  # type: ignore
    dm = data_manager if sync_with_global.value else local_dm
    margin = 2
    with rv.Card(
        style_=f"height:{height}; width:{width};",
        class_=f"ma-{margin}",
        elevation=2,
    ):
        # TODO split style into where its needed?
        solara.Style(BASE_DIR / "style.css")
        with rv.CardTitle(
            style_="display: flex; justify-content: space-between; align-items: center;",
            class_="card card--flex",
        ):
            solara.Text(title)
            with solara.Row():
                # how to menu + tooltip?
                # solara.Tooltip("Change view type", children=[dashboard_btn])
                dashboard_btn = solara.IconButton("mdi-view-dashboard", on_click=lambda: None)
                with solara.lab.Menu(activator=dashboard_btn, close_on_content_click=False):
                    with solara.Div(class_="card-menu-content"):
                        solara.Select(
                            "View Type",
                            values=view_values,  # type: ignore
                            value=local_view_type,  # type: ignore
                            dense=False,
                        )
                is_peptide_view = local_view_type.value in ["peptides_table", "peptides_chart"]
                reduction_btn = solara.IconButton(
                    "mdi-alpha-r-circle",
                    on_click=lambda: None,
                    tooltip="Change residue reduction",
                    disabled=is_peptide_view,
                )
                with solara.lab.Menu(activator=reduction_btn, close_on_content_click=False):
                    with solara.Div(class_="card-menu-content"):
                        regression_option = (
                            "lasso_regression" if dm.is_delta else "ridge_regression"
                        )
                        solara.Select(  # type: ignore
                            "Residue Reduction",
                            values=["weighted_average", regression_option],
                            value=dm.residue_reduction.value,
                            on_value=dm.residue_reduction.set,  # type: ignore
                            dense=False,
                        )
                        solara.InputFloat(
                            label="Alpha",
                            value=dm.alpha,
                            disabled=dm.residue_reduction.value == "weighted_average",
                        )

                btn = solara.IconButton("mdi-tune-vertical", on_click=lambda: None)
                with solara.lab.Menu(activator=btn, close_on_content_click=False):
                    with solara.Div(class_="card-menu-content"):
                        solara.Select(
                            "Quantity",
                            values=dm.qty_values,
                            value=dm.qty.value.name,
                            on_value=dm.set_qty,
                            dense=False,
                        )
                        solara.Select("Base State", value=dm.base_state, values=dm.state_values)
                        enable_diff = dm.qty.value in [DDG, DRFU]
                        solara.Select(
                            "Diff State",
                            value=dm.diff_state,
                            values=dm.state_values,
                            disabled=not enable_diff,
                        )
                        solara.Select(
                            "Exposure",
                            value=dm.exposure,
                            values=dm.exposure_values,
                            disabled=dm.qty.value not in [RFU, DRFU],
                        )
                with solara.Tooltip("Toggle global controls sync"):
                    solara.IconButton(
                        "mdi-link-off" if not sync_with_global.value else "mdi-link",
                        on_click=lambda: sync_with_global.set(not sync_with_global.value),
                        color="accent" if not sync_with_global.value else None,
                    )

                if on_delete is not None:
                    # TODO fix tooltip
                    solara.IconButton("mdi-delete", on_click=on_delete, tooltip="Delete View")  # type: ignore

        rv.CardSubtitle(children=[dm.label])  # need more margin if subtitle is used

        margin = 80
        margin += 36  # account for subtitle
        parent_height = int(height.strip("px"))
        # this Div is for pdbemolstar element only, consider moving it there
        with solara.Div(
            style={
                "width": "calc(100% - 0px)",
                "height": f"calc(100% - {margin}px)",  # not sure if this height does anything right now
                "position": "relative",
                "padding": "0 16px",  # 16px on each side = 32px total
                "box-sizing": "border-box",  # Include padding in width calculation
            },
        ):
            if local_view_type.value == "peptides_table":
                df = apply_quantity_scaling(dm.get_peptide_df(), dm.qty.value)
                solara.DataFrame(df)
            if local_view_type.value == "residues_table":
                df = apply_quantity_scaling(dm.get_residue_df(), dm.qty.value)
                solara.DataFrame(df)
            elif local_view_type.value == "peptides_chart":
                chart = alt_peptides(
                    dm.get_peptide_df(), qty=dm.qty.value, height=parent_height - margin
                )
                chart = chart.configure(
                    padding=5,
                    autosize=alt.AutoSizeParams(type="fit", contains="content", resize=True),
                )
                # embed_options = {
                #     # "mode": "vega-lite",
                #     # "renderer": "svg",
                #     # "theme": "dark" if dark_effective else "default",
                #     "actions": False,
                # }
                # alt.JupyterChart.element(chart=chart.interactive(), embed_options=embed_options)  # type: ignore
                solara.FigureAltair(chart.interactive()).key(f"peptide_chart-{dark_effective}")

            elif local_view_type.value == "residues_chart":
                chart = alt_residues(
                    dm.get_residue_df(), qty=dm.qty.value, height=parent_height - margin, pad=0.1
                )
                chart = chart.configure(
                    padding=5,
                    autosize=alt.AutoSizeParams(type="fit", contains="content", resize=True),
                )
                # alt.JupyterChart.element(
                #     chart=chart
                # )  # , embed_options=embed_options)  # type: ignore
                solara.FigureAltair(chart).key(f"residue_chart-{dark_effective}")

            elif local_view_type.value == "structure":
                color_data = pdbemolstar_colors(
                    dm.get_residue_df(), qty=dm.qty.value, mapping=dm.structure_mapping
                )
                tooltips = pdbemolstar_tooltips(
                    dm.get_residue_df(), qty=dm.qty.value, mapping=dm.structure_mapping
                )
                PDBeMolstar.element(  # type: ignore
                    custom_data=dm.pdbe_molstar_custom_data,
                    hide_water=True,
                    color_data=color_data,
                    tooltips=tooltips,
                    height=f"{parent_height - margin}px",
                    # height=height,
                    theme="light" if not dark_effective else "dark",
                ).key(f"PDBEmolstar-{dark_effective}")


@solara.component  # type: ignore
def Sidebar(
    view_cards: solara.Reactive[list[dict]],
    grid_layout: solara.Reactive[list[dict]],
    global_dm: DataManager,
):
    new_view_type = solara.use_reactive(view_values[0]["value"])
    dprint("rerender in sidebar")

    # TODO remove
    def is_synced_reactive(reactive: str) -> bool:
        return True
        # return all(
        #     getattr(view_card["dm"], reactive).value == getattr(global_dm, reactive).value
        #     for view_card in view_cards.value
        # )

    with solara.Sidebar():
        with solara.Card("Controls"):
            solara.Select(
                "Quantity",
                values=global_dm.qty_values,
                value=global_dm.qty.value.name,
                on_value=global_dm.set_qty,
                dense=False,
                classes=["out-of-sync"] if not is_synced_reactive("qty") else [],
            )
            solara.Select(
                "Base State",
                value=global_dm.base_state,
                values=global_dm.state_values,
                classes=["out-of-sync"] if not is_synced_reactive("base_state") else [],
            )
            solara.Select(
                "Diff State",
                value=global_dm.diff_state,
                values=global_dm.state_values,
                disabled=not global_dm.is_delta,
                classes=["out-of-sync"] if not is_synced_reactive("diff_state") else [],
            )
            solara.Select(
                "Exposure",
                value=global_dm.exposure,
                values=global_dm.exposure_values,
                disabled=global_dm.qty.value not in [RFU, DRFU],
                classes=["out-of-sync"] if not is_synced_reactive("exposure") else [],
            )

            regression_option = "lasso_regression" if global_dm.is_delta else "ridge_regression"
            solara.Select(  # type: ignore
                "Residue Reduction",
                values=["weighted_average", regression_option],
                value=global_dm.residue_reduction.value,
                on_value=global_dm.residue_reduction.set,  # type: ignore
                dense=False,
                classes=["out-of-sync"] if not is_synced_reactive("residue_reduction") else [],
            )
            solara.InputFloat(
                label="Alpha",
                value=global_dm.alpha,
                disabled=global_dm.residue_reduction.value == "weighted_average",
                classes=["out-of-sync"] if not is_synced_reactive("alpha") else [],
            )
        with solara.Card("Add View"):

            def add_view():
                """Add a new view card with the specified view type."""
                new_card_entry = new_card(new_view_type.value)
                new_cards = view_cards.value[:] + [new_card_entry]

                new_layout = find_free_grid_position(grid_layout.value)
                if new_layout is None:
                    return  # No free position found, do not add a new view
                view_cards.set(new_cards)
                grid_layout.set(grid_layout.value[:] + [new_layout])

            with solara.Row():
                solara.Select(
                    "View Type",
                    value=new_view_type,  # type: ignore
                    values=view_values,  # type: ignore
                    dense=False,
                )
                solara.IconButton(
                    "mdi-plus",
                    on_click=add_view,
                )  # type: ignore


# %%
@solara.component  # type: ignore
def DataSetView(dataset_id: str):
    """Display a dataset view.

    Args:
        dataset: ID of the dataset to display
    """
    dprint("rerender in dataset_view")

    def load_dataset():
        local_db = DataBase(cfg.database_dir)
        # remote_db = RemoteDataBase(cfg.remote_url, database_dir=cfg.database_dir / "remote_cache")

        if dataset_id in IN_MEMORY_DATASETS:
            dataset = IN_MEMORY_DATASETS[dataset_id]
        elif dataset_id in local_db.datasets:
            dataset = local_db.load_dataset(dataset_id)
        # elif: TODO implement remote db (local cache)
        hdx_states = load_hdx_dataset(dataset)

        global_dm = DataManager(hdx_states=hdx_states)
        return global_dm

    global_dm = solara.use_memo(load_dataset, dependencies=[dataset_id])  # type: ignore

    def make_cards():
        view_cards = [new_card(view_type) for view_type in initial_types]
        initial_grid = default_grid_layout()

        return view_cards, initial_grid

    # use memo to run once
    initial_cards, initial_grid = solara.use_memo(make_cards, dependencies=[])  # type: ignore
    view_cards = solara.use_reactive(initial_cards)
    grid_layout = solara.use_reactive(initial_grid)

    Sidebar(view_cards, grid_layout, global_dm)

    def make_grid_card(layout, view_card):
        def on_delete(id=view_card["id"]):
            """Remove a view card by its ID."""
            card_ids = [card["id"] for card in view_cards.value]
            delete_idx = card_ids.index(id)
            to_remove = view_cards.value[delete_idx]

            if to_remove is None:
                return

            view_cards.value = [card for card in view_cards.value if card["id"] != id]

            new_layout, idx, moved = [], 0, False
            for i, layout in enumerate(grid_layout.value):
                if i == delete_idx:
                    moved = True
                    continue
                # adjust index, set items past the deleted card to 'moved' such they stay in place
                # TODO doesn't seem to work, resulting layout 'moved' is always False
                new_layout.append(layout | {"i": str(idx), "moved": moved})
                idx += 1

            grid_layout.value = new_layout

        height_pixels = layout["h"] * 40 - 10
        card = ViewCard(
            data_manager=global_dm,
            view_type=view_card["view_type"],
            width="100%",
            height=f"{height_pixels}px",
            on_delete=on_delete,
        )

        return card

    def make_grid_items():
        """Create grid items from view cards and their layouts."""
        return [
            make_grid_card(layout, view_card)
            for layout, view_card in zip(grid_layout.value, view_cards.value)
        ]

    grid_items = solara.use_memo(  # type: ignore
        make_grid_items, dependencies=[view_cards.value, grid_layout.value]
    )

    solara.GridDraggable(
        items=grid_items,
        grid_layout=grid_layout.value,
        resizable=True,
        draggable=not pin_cards.value,
        on_grid_layout=grid_layout.set,
        col_num=24,
    )


# used for appbar color
@solara.component  # type: ignore
def Layout(children):
    dark_effective = solara.lab.use_dark_effective()
    return solara.AppLayout(
        children=children,
        toolbar_dark=dark_effective,
        color="None",  # if dark_effective else "primary",
    )


def Home():
    db = DataBase(DATABASE_DIR.value)
    with solara.Card():
        solara.Markdown(
            "## Welcome to InstaGibbs!\nChoose an HDX-MS dataset from the table below to open in InstaGibbs."
        )

        with solara.v.SimpleTable():  # type: ignore
            with solara.v.Html(tag="thead"):  # type: ignore
                with tr():
                    th("Dataset")
                    th("Open in InstaGibbs")
                for d in db.datasets:
                    with tr():
                        td(d)
                        td(
                            solara.Link(
                                path_or_route=f"/?dataset_id={d}",
                                children=[solara.Button(icon_name="mdi-open-in-new", icon=True)],
                            )
                        )


# TODO use element portal to place this component at the root level
# and check if it already exists
@solara.component  # type: ignore
def AltairThemeSetter():
    dark_effective = solara.lab.use_dark_effective()

    def set_alt_theme():
        if dark_effective:
            alt.theme.enable("dark")
        else:
            alt.theme.enable("default")

    solara.use_memo(set_alt_theme, dependencies=[dark_effective])  # type: ignore
    return None


@solara.component  # type: ignore
def Main(dataset_id: str | None = None):
    """Main component for database mode."""
    settings_dialog = solara.use_reactive(False)
    about_dialog = solara.use_reactive(False)

    dark_effective = solara.lab.use_dark_effective()

    AltairThemeSetter()

    title = "InstaGibbs" + f" / {dataset_id}" if dataset_id is not None else ""

    solara.Title(title)
    with solara.AppBar():
        if dataset_id is not None:
            with solara.Tooltip("Pin view cards"):
                solara.Button(
                    icon_name="mdi-pin" if pin_cards.value else "mdi-pin-off",
                    icon=True,
                    on_click=lambda: pin_cards.set(not pin_cards.value),
                )

        with solara.Tooltip("Settings"):
            solara.Button(
                icon_name="mdi-settings",
                icon=True,
                on_click=lambda: settings_dialog.set(True),
            )

        with solara.Tooltip("About"):
            solara.Button(
                icon_name="mdi-information-outline",
                icon=True,
                on_click=lambda: about_dialog.set(True),
            )
        with solara.Tooltip("Toggle dark/light theme"):
            solara.lab.ThemeToggle()

        with solara.Tooltip("Home"):
            with solara.Link(path_or_route="/"):
                solara.Button(icon_name="mdi-home", icon=True)  # , classes=["mx-2"])

    if settings_dialog.value:
        with rv.Dialog(
            v_model=settings_dialog.value,
            on_v_model=settings_dialog.set,
            max_width=500,
        ):
            with solara.Card("Settings"):
                solara.Markdown("Settings is work in progress. ")

    if about_dialog.value:
        with rv.Dialog(
            v_model=about_dialog.value,
            on_v_model=about_dialog.set,
            max_width=500,
        ):
            with solara.Card("About instagibbs"):
                solara.Markdown(about_md)

    # TODO DATABASE_DIR from cfg
    if DATABASE_DIR.value is not None:
        database = DataBase(DATABASE_DIR.value)
        if dataset_id is None:
            Home()
        elif dataset_id not in set(database.datasets) | set(IN_MEMORY_DATASETS.keys()):
            solara.Error(f"Dataset {dataset_id} not found")
        else:
            with solara.Div(style={"margin-top": "-36px"}):
                # fix key to prevent rerender on opening dialogs
                # why is this needed? also doesnt work at the moment
                # seems like the dialogs dont play well with the grid layout
                DataSetView(dataset_id).key(f"dataset_view-{dataset_id}-{dark_effective}")
    else:
        solara.Error(
            "Database directory not configured. Please set database_dir in config or use --database-dir option."
        )


@solara.component  # type: ignore
def Page():
    router = solara.use_router()  # type: ignore
    if router.search is None:
        query_dict = {}
    else:
        query_dict = {k: v for k, v in parse_qsl(router.search)}

    dataset_id = query_dict.get("dataset_id", None)

    Main(dataset_id=cfg.dataset_id or dataset_id)


# %%
