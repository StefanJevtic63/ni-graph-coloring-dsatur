from pathlib import Path
from typing import Literal

DSATUR_UNCOLORED_MARKER: int = -1
DSATUR_FIRST_COLOR_ID: int = 1

APP_DEFAULT_FRAME_PAUSE_SECONDS: float = 1.1
APP_EXIT_FAILURE_CODE: int = 1
APP_SEPARATOR_WIDTH: int = 48
APP_STATUS_SUCCESS_TEXT: str = "Graph was successfully colored"
APP_STATUS_FAILURE_TEXT: str = "Graph was unable to be colored"

IO_INPUT_EXAMPLES_DIR_PATH: str = str(Path.cwd() / "input_examples")
IO_INPUT_DEFAULT_EXTENSION: str = ".txt"
IO_FILE_READ_ENCODING: str = "utf-8"
IO_FILE_NOT_FOUND_PREFIX: str = "Input file not found: "

CLI_SPEED_FLAG_LONG: str = "--speed"
CLI_SPEED_FLAG_SHORT: str = "-s"
CLI_USAGE: str = "Usage: python main.py <input_file> [--speed <seconds>]"
CLI_EXAMPLE_INVALID_ARGS: str = "Invalid arguments! Example: python main.py bipartite.txt --speed 0.6"

CLI_ERR_MISSING_SPEED_VALUE: str = "Missing value after --speed / -s."
CLI_ERR_INVALID_SPEED_VALUE: str = "Speed must be a number, e.g., --speed 0.7"
CLI_ERR_NONPOSITIVE_SPEED_VALUE: str = "Speed must be > 0 seconds per iteration."
CLI_ERR_UNKNOWN_ARGUMENT_PREFIX: str = "Unknown argument"

UI_PALETTE: list[str] = [
    "#e6194b", "#3cb44b", "#4363d8", "#f58231",
    "#911eb4", "#42d4f4", "#f032e6", "#bfef45",
]

UI_COLOR_NAMES: list[str] = ["Red", "Green", "Blue", "Orange", "Purple", "Cyan", "Magenta", "Yellow"]

UI_UNCOLORED_COLOR: str = "#c7c7c7"
UI_LAYOUT_SEED: int = 42

UI_DRAW_NODE_SIZE: int = 750
UI_DRAW_FONT_COLOR: str = "white"
UI_DRAW_FONT_WEIGHT: Literal["bold"] = "bold"
UI_DRAW_EDGE_COLOR: str = "#444444"
UI_DRAW_EDGE_WIDTH: float = 1.8
UI_FRAME_TITLE_FONT_SIZE: int = 12
UI_TEXT_FONT_SIZE: int = 10

UI_FIGURE_SIZE: tuple[float, float] = (11, 6.5)
UI_GRID_SHAPE: tuple[int, int] = (1, 2)
UI_GRID_WIDTH_RATIOS: list[float] = [4.5, 2.0]
UI_GRAPH_AXIS_INDEX: tuple[int, int] = (0, 0)
UI_INFO_AXIS_INDEX: tuple[int, int] = (0, 1)

UI_INFO_PANEL_XLIM: tuple[float, float] = (0.0, 1.0)
UI_INFO_PANEL_YLIM: tuple[float, float] = (0.0, 1.0)
UI_INFO_EMPTY_VALUE: str = "-"
UI_INFO_TEXT_X: float = 0.0
UI_INFO_TITLE_Y: float = 0.95
UI_INFO_MOST_SATURATED_Y: float = 0.84
UI_INFO_ASSIGNED_COLOR_Y: float = 0.76
UI_INFO_SATURATION_Y: float = 0.68
UI_VERTICAL_ALIGN_TOP: str = "top"

UI_INFO_STATUS_TITLE: str = "DSatur Status"
UI_INFO_LABEL_ITERATION: str = "Iteration"
UI_INFO_LABEL_MOST_SATURATED: str = "Most Saturated Node"
UI_INFO_LABEL_ASSIGNED_COLOR: str = "Assigned Color"
UI_INFO_LABEL_SATURATION: str = "Node Saturation"

UI_LEGEND_TITLE_USED_COLORS: str = "Used Colors"
UI_LEGEND_LOC: str = "lower left"
UI_LEGEND_FRAME_ALPHA: float = 0.9
UI_LEGEND_FONT_SIZE: int = 9
UI_PLOT_AXIS_OFF: str = "off"

UI_POPUP_FIGURE_SIZE: tuple[float, float] = (8.0, 5.8)
UI_POPUP_TEXT_X: float = 0.5
UI_POPUP_TEXT_Y: float = 0.5
UI_POPUP_FONT_SIZE: int = 20
UI_POPUP_BG_SUCCESS: str = "#e8f8ec"
UI_POPUP_BG_FAILURE: str = "#fdeaea"
UI_POPUP_TEXT_COLOR_SUCCESS: str = "#1f7a3e"
UI_POPUP_TEXT_COLOR_FAILURE: str = "#9f1d1d"

UI_POPUP_STATUS_X: float = 0.05
UI_POPUP_STATUS_Y: float = 0.67
UI_POPUP_STATUS_W: float = 0.90
UI_POPUP_STATUS_H: float = 0.27
UI_POPUP_NEXT_LABEL: str = "Choose next graph:"
UI_POPUP_NEXT_LABEL_Y: float = 0.56
UI_POPUP_NEXT_LABEL_H: float = 0.08
UI_POPUP_BTN_X: float = 0.15
UI_POPUP_BTN_W: float = 0.70
UI_POPUP_BTN_H: float = 0.09
UI_POPUP_BTN_START_Y: float = 0.43
UI_POPUP_BTN_GAP: float = 0.025
UI_POPUP_WAIT_SECONDS: float = 0.05

UI_SELECTOR_FIGURE_SIZE: tuple[float, float] = (6.8, 5.4)
UI_SELECTOR_TITLE: str = "Choose input graph"
UI_SELECTOR_TITLE_X: float = 0.5
UI_SELECTOR_TITLE_Y: float = 0.95
UI_SELECTOR_TITLE_FONT_SIZE: int = 16
UI_SELECTOR_BTN_X: float = 0.18
UI_SELECTOR_BTN_WIDTH: float = 0.64
UI_SELECTOR_BTN_HEIGHT: float = 0.12
UI_SELECTOR_BTN_GAP: float = 0.05
UI_SELECTOR_BTN_TOP: float = 0.72
UI_SELECTOR_LABEL_WHEEL: str = "Wheel"
UI_SELECTOR_LABEL_BIPARTITE: str = "Bipartite"
UI_SELECTOR_LABEL_CYCLE: str = "Cycle"
UI_SELECTOR_LABEL_PETERSON: str = "Peterson"

UI_PAUSE_BTN_X: float = 0.38
UI_PAUSE_BTN_Y: float = 0.02
UI_PAUSE_BTN_W: float = 0.24
UI_PAUSE_BTN_H: float = 0.07
UI_PAUSE_BTN_LABEL: str = "Pause"
UI_RESUME_BTN_LABEL: str = "Resume"
UI_ANIM_TIGHT_RECT: tuple[float, float, float, float] = (0.0, 0.12, 1.0, 1.0)

IO_SELECTOR_FILE_WHEEL: str = "wheel.txt"
IO_SELECTOR_FILE_BIPARTITE: str = "bipartite.txt"
IO_SELECTOR_FILE_CYCLE: str = "cycle.txt"
IO_SELECTOR_FILE_PETERSON: str = "peterson.txt"