import uuid
from itertools import product

import solara

DEFAULT_GRID_ELEMENT_HEIGHT = 10
DEFAULT_GRID_ELEMENT_WIDTH = 4


def new_card(view_type: str) -> dict:
    card_entry = {
        "id": uuid.uuid4(),
        "view_type": view_type,
    }
    return card_entry


def default_grid_layout() -> list[dict]:
    return [
        {
            "h": DEFAULT_GRID_ELEMENT_HEIGHT,
            "i": "0",
            "moved": False,
            "w": 14,
            "x": 0,
            "y": 0,
        },
        {
            "h": DEFAULT_GRID_ELEMENT_HEIGHT,
            "i": "1",
            "moved": False,
            "w": 14,
            "x": 0,
            "y": 12,
        },
        {
            "h": 2 * DEFAULT_GRID_ELEMENT_HEIGHT,
            "i": "2",
            "moved": False,
            "w": 10,
            "x": 7,
            "y": 0,
        },
    ]


def grid_elements(layout: dict) -> set:
    """Generate a set of grid elements based on the layout."""
    x_grid = range(layout["x"], layout["x"] + layout["w"])
    y_grid = range(layout["y"], layout["y"] + layout["h"])
    return set(product(x_grid, y_grid))


def find_free_grid_position(
    current_layout: list[dict],
    width=DEFAULT_GRID_ELEMENT_WIDTH,
    height=DEFAULT_GRID_ELEMENT_HEIGHT,
    grid_width: int = 12,
):
    existing_grid_elements = set()
    for layout in current_layout:
        existing_grid_elements.update(grid_elements(layout))

    # for x, y in product(range(grid_width - width + 1), range(100)):
    for y, x in product(range(100), range(grid_width - width + 1)):
        new_layout = {
            "h": height,
            "i": str(len(current_layout)),
            "moved": False,
            "w": width,
            "x": x,
            "y": y,
        }

        new_grid_elements = grid_elements(new_layout)

        if existing_grid_elements.isdisjoint(new_grid_elements):
            return new_layout
    else:
        return None


def td(*args):
    return solara.v.Html(tag="td", children=list(args))  # type: ignore


def th(title: str):
    return solara.v.Html(tag="th", children=[title])  # type: ignore


def tr():
    return solara.v.Html(tag="tr")  # type: ignore
