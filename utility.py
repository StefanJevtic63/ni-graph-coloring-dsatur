from __future__ import annotations

import sys
from os import path
from typing import Any

from matplotlib import patches, pyplot as plt
from matplotlib.axes import Axes
from matplotlib.widgets import Button
import networkx as nx
from networkx.algorithms.bipartite import sets as bipartite_sets

from constants import (
    APP_DEFAULT_FRAME_PAUSE_SECONDS, APP_STATUS_FAILURE_TEXT, APP_STATUS_SUCCESS_TEXT,

    DSATUR_FIRST_COLOR_ID, DSATUR_UNCOLORED_MARKER,

    CLI_ERR_INVALID_PAUSE_VALUE, CLI_ERR_MISSING_PAUSE_VALUE, CLI_ERR_NONPOSITIVE_PAUSE_VALUE,
    CLI_ERR_UNKNOWN_ARGUMENT_PREFIX, CLI_PAUSE_FLAG_LONG, CLI_PAUSE_FLAG_SHORT, CLI_USAGE,
    CLI_EXAMPLE_INVALID_ARGS,

    IO_FILE_NOT_FOUND_PREFIX, IO_FILE_READ_ENCODING, IO_INPUT_DEFAULT_EXTENSION, IO_INPUT_EXAMPLES_DIR_PATH,
    IO_SELECTOR_FILE_BIPARTITE, IO_SELECTOR_FILE_DENSE, IO_SELECTOR_FILE_WHEEL, IO_SELECTOR_FILE_PETERSON,

    UI_DRAW_EDGE_COLOR, UI_DRAW_EDGE_WIDTH, UI_DRAW_FONT_COLOR, UI_DRAW_FONT_WEIGHT,
    UI_DRAW_NODE_SIZE, UI_FIGURE_SIZE, UI_FRAME_TITLE_FONT_SIZE, UI_GRAPH_AXIS_INDEX,
    UI_GRID_SHAPE, UI_GRID_WIDTH_RATIOS, UI_INFO_ASSIGNED_COLOR_Y, UI_INFO_AXIS_INDEX,
    UI_INFO_EMPTY_VALUE, UI_INFO_LABEL_ASSIGNED_COLOR, UI_INFO_LABEL_MOST_SATURATED, 
    UI_INFO_LABEL_SATURATION, UI_INFO_MOST_SATURATED_Y, UI_INFO_PANEL_XLIM,
    UI_INFO_PANEL_YLIM, UI_INFO_SATURATION_Y, UI_INFO_STATUS_TITLE, UI_INFO_TEXT_X,
    UI_INFO_TITLE_Y, UI_LAYOUT_SEED, UI_LEGEND_FONT_SIZE, UI_LEGEND_FRAME_ALPHA,
    UI_LEGEND_LOC, UI_LEGEND_TITLE_USED_COLORS, UI_PALETTE,
    UI_PLOT_AXIS_OFF, UI_TEXT_FONT_SIZE, UI_UNCOLORED_COLOR, UI_VERTICAL_ALIGN_TOP,
    UI_POPUP_BG_FAILURE, UI_POPUP_BG_SUCCESS, UI_POPUP_BTN_GAP, UI_POPUP_BTN_H,
    UI_POPUP_BTN_START_Y, UI_POPUP_BTN_W, UI_POPUP_BTN_X, UI_POPUP_FIGURE_SIZE,
    UI_POPUP_FONT_SIZE, UI_POPUP_NEXT_LABEL, UI_POPUP_NEXT_LABEL_H, UI_POPUP_NEXT_LABEL_Y,
    UI_POPUP_STATUS_H, UI_POPUP_STATUS_W, UI_POPUP_STATUS_X, UI_POPUP_STATUS_Y,
    UI_POPUP_TEXT_COLOR_FAILURE, UI_POPUP_WAIT_SECONDS, UI_POPUP_TEXT_COLOR_SUCCESS, 
    UI_POPUP_TEXT_X, UI_POPUP_TEXT_Y, UI_SELECTOR_BTN_GAP, UI_SELECTOR_BTN_HEIGHT, 
    UI_SELECTOR_BTN_TOP, UI_SELECTOR_BTN_WIDTH, UI_ANIM_TIGHT_RECT, UI_COLOR_NAMES, 
    UI_PAUSE_BTN_H, UI_PAUSE_BTN_LABEL, UI_PAUSE_BTN_W, UI_PAUSE_BTN_X, UI_PAUSE_BTN_Y, 
    UI_RESUME_BTN_LABEL, UI_SELECTOR_BTN_X, UI_SELECTOR_FIGURE_SIZE, UI_SELECTOR_LABEL_BIPARTITE, 
    UI_SELECTOR_LABEL_DENSE, UI_SELECTOR_LABEL_WHEEL, UI_SELECTOR_LABEL_PETERSON, UI_SELECTOR_TITLE, 
    UI_SELECTOR_TITLE_FONT_SIZE, UI_SELECTOR_TITLE_X, UI_SELECTOR_TITLE_Y,
)

from typing import Callable

def parse_cli_args_wrapper(args: list[str]) -> tuple[str | None, float | None]:
    """Wrapper for parse_cli_args to catch and display errors, then exit.

    Args:
        args (list[str]): List of CLI arguments (excluding script name).

    Returns:
        tuple[str | None, float | None]: Parsed input file (or None if not provided) and pause in seconds per frame.
    """
    try:
        input_arg, pause = parse_cli_args(args)
    except ValueError as exc:
        print(str(exc))
        print(CLI_EXAMPLE_INVALID_ARGS)
        return None, None

    input_path: str | None = None

    if input_arg is None:
        input_path = choose_example_file()
        if input_path is None:
            print("No graph selected.")
            return None, None
    else:
        try:
            input_path = resolve_input_file(file_path=input_arg)
        except FileNotFoundError as exc:
            print(str(exc))
            return None, None

    return input_path, pause

def parse_cli_args(args: list[str]) -> tuple[str | None, float | None]:
    """Parse CLI arguments for input file and pause, with error handling.

    Args:
        args (list[str]): List of CLI arguments (excluding script name).

    Returns:
        tuple[str | None, float | None]: Parsed input file (or None if not provided) and pause in seconds per frame.
    """
    input_file: str | None = None
    pause: float = APP_DEFAULT_FRAME_PAUSE_SECONDS

    idx: int = 0
    while idx < len(args):
        token: str = args[idx]
        if token in {CLI_PAUSE_FLAG_LONG, CLI_PAUSE_FLAG_SHORT}:
            if idx + 1 >= len(args):
                raise ValueError(CLI_ERR_MISSING_PAUSE_VALUE)
            try:
                pause = float(args[idx + 1])
            except ValueError as exc:
                raise ValueError(CLI_ERR_INVALID_PAUSE_VALUE) from exc
            if pause <= 0:
                raise ValueError(CLI_ERR_NONPOSITIVE_PAUSE_VALUE)
            idx += 2
        elif token.startswith("-"):
            raise ValueError(f"{CLI_ERR_UNKNOWN_ARGUMENT_PREFIX}: {token}. {CLI_USAGE}")
        else:
            if input_file is not None:
                raise ValueError(f"{CLI_ERR_UNKNOWN_ARGUMENT_PREFIX}: {token}. {CLI_USAGE}")
            input_file = token
            idx += 1

    return input_file, pause

def choose_example_file() -> str | None:
    """Open clickable rectangle buttons and return selected input file path.
    
    Returns:
        str | None: The full path of the selected example file, or None if no selection was made.
    """
    fig = plt.figure(figsize=UI_SELECTOR_FIGURE_SIZE)
    fig.suptitle(
        UI_SELECTOR_TITLE, 
        x=UI_SELECTOR_TITLE_X, 
        y=UI_SELECTOR_TITLE_Y, 
        fontsize=UI_SELECTOR_TITLE_FONT_SIZE, 
        fontweight=UI_DRAW_FONT_WEIGHT
    )

    buttons: list[Button] = []
    selected: dict[str, str | None] = {"file": None}

    def _make_click_handler(file_name: str) -> Callable[[Any], None]:
        """Helper to create a click handler that captures the file_name in its closure.
        
        Args:
            file_name (str): The name of the file associated with the button.
            
        Returns:
            Callable[[Any], None]: A function that can be used as a click handler for a button."""
        def _on_click(_: Any) -> None:
            """Click handler that sets the selected file path and closes the figure.
            
            Args:
                _: Any: The event object passed by Matplotlib (unused).
                
            Returns:
                None
            """
            selected["file"] = path.join(IO_INPUT_EXAMPLES_DIR_PATH, file_name)
            plt.close(fig)

        return _on_click

    selector_pairs: list[tuple[str, str]] = _build_selector_pairs()
    for idx, (label, file_name) in enumerate(selector_pairs):
        y: float = UI_SELECTOR_BTN_TOP - idx * (UI_SELECTOR_BTN_HEIGHT + UI_SELECTOR_BTN_GAP)
        btn_ax: Axes = fig.add_axes((UI_SELECTOR_BTN_X, y, UI_SELECTOR_BTN_WIDTH, UI_SELECTOR_BTN_HEIGHT))
        button = Button(btn_ax, label)
        button.on_clicked(_make_click_handler(file_name))
        buttons.append(button)

    plt.show()
    return selected["file"]

def show_coloring_popup(success: bool) -> str | None:
    """Show combined status + graph selector popup.

    Automatically appears after the animation closes. Returns the full path of
    the selected next input file, or None if the user closed the window.

    Args:
        success (bool): True if the graph was successfully colored, False otherwise.

    Returns:
        str | None: The full path of the selected next input file, or None if no selection was made.
    """
    if success:
        msg: str = APP_STATUS_SUCCESS_TEXT
        bg_color: str = UI_POPUP_BG_SUCCESS
        txt_color: str = UI_POPUP_TEXT_COLOR_SUCCESS
    else:
        msg = APP_STATUS_FAILURE_TEXT
        bg_color = UI_POPUP_BG_FAILURE
        txt_color = UI_POPUP_TEXT_COLOR_FAILURE

    selected: dict[str, str | None] = {"file": None}

    fig = plt.figure(figsize=UI_POPUP_FIGURE_SIZE)
    fig.patch.set_facecolor(bg_color)

    # --- Status section ---
    ax_status: Axes = fig.add_axes(
        (UI_POPUP_STATUS_X, UI_POPUP_STATUS_Y, UI_POPUP_STATUS_W, UI_POPUP_STATUS_H)
    )
    ax_status.set_facecolor(bg_color)
    ax_status.axis(UI_PLOT_AXIS_OFF)
    ax_status.text(
        UI_POPUP_TEXT_X,
        UI_POPUP_TEXT_Y,
        msg.upper(),
        ha="center",
        va="center",
        fontsize=UI_POPUP_FONT_SIZE,
        fontweight=UI_DRAW_FONT_WEIGHT,
        color=txt_color,
    )

    # --- "Choose next graph" label ---
    ax_label: Axes = fig.add_axes(
        (UI_POPUP_STATUS_X, UI_POPUP_NEXT_LABEL_Y, UI_POPUP_STATUS_W, UI_POPUP_NEXT_LABEL_H)
    )
    ax_label.axis(UI_PLOT_AXIS_OFF)
    ax_label.text(
        UI_POPUP_TEXT_X,
        UI_POPUP_TEXT_Y,
        UI_POPUP_NEXT_LABEL,
        ha="center",
        va="center",
        fontsize=UI_TEXT_FONT_SIZE + 1,
        fontweight=UI_DRAW_FONT_WEIGHT,
    )

    def _make_handler(file_name: str):
        """Helper to create a click handler that captures the file_name in its closure.
        
        Args:
            file_name (str): The name of the file associated with the button.
            
        Returns:
            Callable[[Any], None]: A function that can be used as a click handler for a button."""
        def _handler(_: Any) -> None:
            """Click handler that sets the selected file path and closes the figure.
            
            Args:
                _: Any: The event object passed by Matplotlib (unused).
                
            Returns:
                None
            """
            selected["file"] = path.join(IO_INPUT_EXAMPLES_DIR_PATH, file_name)
            plt.close(fig)
        return _handler

    # --- Selector buttons ---
    selector_pairs: list[tuple[str, str]] = _build_selector_pairs()
    buttons: list[Button] = []

    for idx, (label, file_name) in enumerate(selector_pairs):
        y: float = UI_POPUP_BTN_START_Y - idx * (UI_POPUP_BTN_H + UI_POPUP_BTN_GAP)
        btn_ax: Axes = fig.add_axes((UI_POPUP_BTN_X, y, UI_POPUP_BTN_W, UI_POPUP_BTN_H))
        btn = Button(btn_ax, label)
        btn.on_clicked(_make_handler(file_name))
        buttons.append(btn)

    plt.show(block=True)
    return selected["file"]

def read_graph_from_file(file_path: str) -> nx.Graph:
    """Read and parse a graph from a text file.

    Args:
        file_path (str): Path to the target text file.

    Returns:
        nx.Graph: A NetworkX undirected graph instance.
    """
    cleaned_path: str = file_path.strip()
    with open(file=cleaned_path, mode="r", encoding=IO_FILE_READ_ENCODING) as f:
        content: str = f.read()
    return _parse_graph(content)

def resolve_input_file(file_path: str) -> str:
    """Resolve user input path using direct and input_examples lookup.

    Args:
        file_path (str): The file path or name provided by the user.

    Returns:
        str: The resolved absolute or verified relative file path.

    Raises:
        FileNotFoundError: If the file cannot be found in any candidate path.
    """
    if not file_path.lower().endswith(IO_INPUT_DEFAULT_EXTENSION):
        file_path += ".txt"
    
    full_path: str = path.join(IO_INPUT_EXAMPLES_DIR_PATH, file_path)
    if path.isfile(full_path):
        return full_path

    raise FileNotFoundError(IO_FILE_NOT_FOUND_PREFIX + full_path)

def validate(G: nx.Graph, color: dict[int, int]) -> bool:
    """Return True if no adjacent nodes share the same color.

    Args:
        G (nx.Graph): The NetworkX graph instance.
        color (dict[int, int]): A dictionary mapping nodes to their assigned colors.

    Returns:
        bool: True if the coloring is valid, False otherwise.
    """
    return all(color[u] != color[v] for u, v in G.edges())

def animate_dsatur(
    title: str,
    G: nx.Graph,
    steps: list[tuple[int, int, int]],
    frame_pause_seconds: float = APP_DEFAULT_FRAME_PAUSE_SECONDS,
) -> bool:
    """Animate DSatur coloring on a single graph from empty to fully colored.

    Args:
        title (str): Title or name of the graph to display.
        G (nx.Graph): The NetworkX graph instance.
        steps (list[tuple[int, int, int]]): A list of tuples containing animation 
            history where each tuple represents: (node, assigned_color, saturation).
        frame_pause_seconds (float, optional): Duration to pause on each frame. Defaults to 1.

    Returns:
        bool: True if all iterations were rendered; False if interrupted.
    """
    pos: dict[int, Any] = _choose_layout(G)
    nodes: list[int] = list(G.nodes())

    fig = plt.figure(figsize=UI_FIGURE_SIZE)
    grid = fig.add_gridspec(*UI_GRID_SHAPE, width_ratios=UI_GRID_WIDTH_RATIOS)
    ax_graph: Axes = fig.add_subplot(grid[UI_GRAPH_AXIS_INDEX])
    ax_info: Axes = fig.add_subplot(grid[UI_INFO_AXIS_INDEX])

    current_coloring: dict[int, int] = {v: DSATUR_UNCOLORED_MARKER for v in nodes}
    used_colors: set[int] = set()

    # --- Pause button ---
    state: dict[str, Any] = {"paused": False}
    btn_pause_ax: Axes = fig.add_axes((UI_PAUSE_BTN_X, UI_PAUSE_BTN_Y, UI_PAUSE_BTN_W, UI_PAUSE_BTN_H))
    btn_pause = Button(btn_pause_ax, UI_PAUSE_BTN_LABEL)
    state["btn"] = btn_pause  # keep reference to prevent garbage collection

    def _toggle_pause(_: Any) -> None:
        """Hendler for pause button click. Toggles the paused state and updates button label.
        
        Args:
            _: Any: The event object passed by Matplotlib (unused).
        
        Returns:
            None
        """
        state["paused"] = not state["paused"]
        btn_pause.label.set_text(UI_RESUME_BTN_LABEL if state["paused"] else UI_PAUSE_BTN_LABEL)
        fig.canvas.draw_idle()

    btn_pause.on_clicked(_toggle_pause)

    def _wait_frame() -> bool:
        """Pause for frame_pause_seconds then block while paused. Returns False if window closed.
        
        Returns:
            bool: False if the figure window was closed during the pause or while paused, True otherwise.
        """
        plt.pause(frame_pause_seconds)
        while state["paused"]:
            if not plt.fignum_exists(fig.number):
                return False
            plt.pause(UI_POPUP_WAIT_SECONDS)
        return plt.fignum_exists(fig.number)

    ax_graph.clear()
    ax_info.clear()

    _draw_graph_frame(
        ax=ax_graph,
        G=G,
        pos=pos,
        coloring=current_coloring,
        title=title,
    )
    _draw_info_panel(
        ax_info=ax_info,
        used_colors=used_colors,
    )
    fig.subplots_adjust(
        left=UI_ANIM_TIGHT_RECT[0],
        bottom=UI_ANIM_TIGHT_RECT[1],
        right=UI_ANIM_TIGHT_RECT[2],
        top=UI_ANIM_TIGHT_RECT[3],
    )

    if not plt.fignum_exists(fig.number):
        return False
    if not _wait_frame():
        return False

    for node, assigned_color, selected_saturation in steps:
        if not plt.fignum_exists(fig.number):
            return False

        current_coloring[node] = assigned_color
        used_colors.add(assigned_color)

        ax_graph.clear()
        ax_info.clear()

        _draw_graph_frame(
            ax=ax_graph,
            G=G,
            pos=pos,
            coloring=current_coloring,
            title=title,
        )
        _draw_info_panel(
            ax_info=ax_info,
            selected_node=node,
            selected_color=assigned_color,
            selected_saturation=selected_saturation,
            used_colors=used_colors,
        )
        fig.subplots_adjust(
            left=UI_ANIM_TIGHT_RECT[0],
            bottom=UI_ANIM_TIGHT_RECT[1],
            right=UI_ANIM_TIGHT_RECT[2],
            top=UI_ANIM_TIGHT_RECT[3],
        )

        if not plt.fignum_exists(fig.number):
            return False

        if not _wait_frame():
            return False

    if not plt.fignum_exists(fig.number):
        return False

    plt.close(fig)
    return True

def _parse_graph(text: str) -> nx.Graph:
    """Parse an undirected graph from whitespace-separated tokens.

    Args:
        text (str): The raw string content containing graph data.

    Returns:
        nx.Graph: A NetworkX undirected graph instance.
    """
    tokens: list[str] = text.split()
    idx: int = 0
    
    n, idx = _get_token_by_index(tokens, idx)
    m, idx = _get_token_by_index(tokens, idx)

    G: nx.Graph = nx.Graph()
    G.add_nodes_from(range(1, n + 1))
    for _ in range(m):
        u, idx = _get_token_by_index(tokens, idx)
        v, idx = _get_token_by_index(tokens, idx)
        
        if u != v:
            G.add_edge(u, v)
    return G


def _get_token_by_index(tokens: list[str], idx: int) -> tuple[int, int]:
    """Helper to safely get a token by index, raising a ValueError if out of bounds.

    Args:
        tokens (list[str]): The list of tokens to access.
        idx (int): The index of the desired token.

    Returns:
        tuple[int, int]: The token at the specified index and the next index.

    Raises:
        ValueError: If the index is out of bounds for the tokens list.
    """
    if idx >= len(tokens):
        raise ValueError(f"Expected more tokens in input, but reached end of list at index {idx}.")
    token: int = int(tokens[idx])
    idx += 1

    return token, idx


def _choose_layout(G: nx.Graph) -> dict[Any, Any]:
    """Choose an appropriate visual layout for the graph.

    Args:
        G (nx.Graph): The NetworkX graph instance.

    Returns:
        dict[Any, Any]: Positions of nodes mapped to coordinate pairs.
    """
    if nx.is_bipartite(G):
        try:
            top: set[Any]
            top, _ = bipartite_sets(G)
            return nx.bipartite_layout(G, top)
        except Exception as e:
            print(e)
            pass
    return nx.spring_layout(G, seed=UI_LAYOUT_SEED)

def _draw_graph_frame(
    ax: Axes,
    G: nx.Graph,
    pos: dict[Any, Any],
    coloring: dict[Any, int],
    title: str,
) -> None:
    """Draw the current state of the graph coloring on a Matplotlib axis.

    Args:
        ax (Axes): The Matplotlib axis where the graph will be drawn.
        G (nx.Graph): The NetworkX graph instance.
        pos (dict[Any, Any]): Positions of the nodes.
        coloring (dict[Any, int]): Current node color mapping.
        title (str): Title of the graph.

    Returns:
        None
    """
    node_colors: list[str] = []
    for v in G.nodes():
        c: int = coloring[v]
        if c == DSATUR_UNCOLORED_MARKER:
            node_colors.append(UI_UNCOLORED_COLOR)
        else:
            node_colors.append(_color_id_to_palette(c))

    nx.draw_networkx(
        G,
        pos=pos,
        ax=ax,
        node_color=node_colors,
        node_size=UI_DRAW_NODE_SIZE,
        font_color=UI_DRAW_FONT_COLOR,
        font_weight=UI_DRAW_FONT_WEIGHT,
        edge_color=UI_DRAW_EDGE_COLOR,
        width=UI_DRAW_EDGE_WIDTH,
    )
    ax.set_title(
        title,
        fontsize=UI_FRAME_TITLE_FONT_SIZE,
        fontweight=UI_DRAW_FONT_WEIGHT,
    )
    ax.axis(UI_PLOT_AXIS_OFF)

def _draw_info_panel(
    ax_info: Axes,
    selected_node: Any | None = None,
    selected_color: int | None = None,
    selected_saturation: int | None = None,
    used_colors: set[int] = set(),
) -> None:
    """Draw the metadata and stats panel next to the graph visualization.

    Args:
        ax_info (Axes): The Matplotlib axis for the information text.
        selected_node (Any | None): The node selected in the current step.
        selected_color (int | None): The color assigned to the selected node.
        selected_saturation (int | None): The saturation degree of the selected node.
        used_colors (set[int]): Set of unique colors used so far.

    Returns:
        None
    """
    ax_info.axis(UI_PLOT_AXIS_OFF)
    ax_info.set_xlim(*UI_INFO_PANEL_XLIM)
    ax_info.set_ylim(*UI_INFO_PANEL_YLIM)

    if selected_node is None:
        node_text: str = UI_INFO_EMPTY_VALUE
        color_text: str = UI_INFO_EMPTY_VALUE
        saturation_text: str = UI_INFO_EMPTY_VALUE
    else:
        node_text = str(selected_node)
        color_text = _color_id_to_name(selected_color) if selected_color is not None else UI_INFO_EMPTY_VALUE
        saturation_text = str(selected_saturation) if selected_saturation is not None else UI_INFO_EMPTY_VALUE

    # Status title
    ax_info.text(
        UI_INFO_TEXT_X,
        UI_INFO_TITLE_Y,
        UI_INFO_STATUS_TITLE,
        fontsize=UI_FRAME_TITLE_FONT_SIZE,
        fontweight=UI_DRAW_FONT_WEIGHT,
        va=UI_VERTICAL_ALIGN_TOP,
    )

    # Most saturated node
    ax_info.text(
        UI_INFO_TEXT_X,
        UI_INFO_MOST_SATURATED_Y,
        f"{UI_INFO_LABEL_MOST_SATURATED}: {node_text}",
        fontsize=UI_TEXT_FONT_SIZE,
    )

    # Assigned color
    ax_info.text(
        UI_INFO_TEXT_X,
        UI_INFO_ASSIGNED_COLOR_Y,
        f"{UI_INFO_LABEL_ASSIGNED_COLOR}: {color_text}",
        fontsize=UI_TEXT_FONT_SIZE,
    )

    # Node saturation
    ax_info.text(
        UI_INFO_TEXT_X,
        UI_INFO_SATURATION_Y,
        f"{UI_INFO_LABEL_SATURATION}: {saturation_text}",
        fontsize=UI_TEXT_FONT_SIZE,
    )

    legend_handles: list[patches.Patch] = []
    for c in sorted(used_colors):
        legend_handles.append(
            patches.Patch(
                color=_color_id_to_palette(c),
                label=_color_id_to_name(c),
            )
        )

    if legend_handles:
        ax_info.legend(
            handles=legend_handles,
            loc=UI_LEGEND_LOC,
            framealpha=UI_LEGEND_FRAME_ALPHA,
            fontsize=UI_LEGEND_FONT_SIZE,
            title=UI_LEGEND_TITLE_USED_COLORS,
        )

def _color_id_to_name(color_id: int) -> str:
    """Return human-readable color name for a DSatur color integer ID.
    
    Args:
        color_id (int): The integer ID of the color assigned by DSatur.

    Returns:
        str: A human-readable name for the color, derived from a predefined palette.
    """
    return UI_COLOR_NAMES[(color_id - DSATUR_FIRST_COLOR_ID) % len(UI_COLOR_NAMES)]

def _color_id_to_palette(color_id: int) -> str:
    """Return the color code for a DSatur color integer ID.
    
    Args:
        color_id (int): The integer ID of the color assigned by DSatur.

    Returns:
        str: The color code from the predefined palette.
    """
    return UI_PALETTE[(color_id - DSATUR_FIRST_COLOR_ID) % len(UI_PALETTE)]

def _build_selector_pairs() -> list[tuple[str, str]]:
    """Return ordered (button_label, example_filename) pairs.
    
    Returns:
        list[tuple[str, str]]: A list of tuples where each tuple contains a 
                               button label and the corresponding example file name.       
    """
    return [
        (UI_SELECTOR_LABEL_WHEEL, IO_SELECTOR_FILE_WHEEL),
        (UI_SELECTOR_LABEL_BIPARTITE, IO_SELECTOR_FILE_BIPARTITE),
        (UI_SELECTOR_LABEL_PETERSON, IO_SELECTOR_FILE_PETERSON),
        (UI_SELECTOR_LABEL_DENSE, IO_SELECTOR_FILE_DENSE),
    ]