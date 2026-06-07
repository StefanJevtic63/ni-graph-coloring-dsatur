#!/usr/bin/env python3
"""Graph coloring using DSatur with step-by-step visualization.

Usage:
    python main.py <input_file>

Example:
    python main.py wheel.txt

Input format:
    n m         <- number of vertices and edges
    u1 v1       <- edge from node u1 to node v1 (undirected)
    ...
    um vm       <- edge from node um to node vm (undirected)
"""

import sys
import networkx as nx
from os import path

from constants import (
    APP_EXIT_FAILURE_CODE, 
    DSATUR_FIRST_COLOR_ID, DSATUR_UNCOLORED_MARKER,
)

from utility import (
    animate_dsatur, read_graph_from_file, parse_cli_args_wrapper, 
    show_coloring_popup, validate, 
)

def dsatur_with_steps(
    G: nx.Graph,
) -> tuple[dict[int, int], list[tuple[int, int, int]]]:
    """Run DSatur and return both final coloring and per-iteration steps.

    Each step is represented as:
        (selected_vertex, assigned_color, selected_saturation)

    Args:
        G (nx.Graph): Input graph to color.

    Returns:
        tuple[dict[int, int], list[tuple[int, int, int]]]: Final coloring and per-iteration steps.
    """
    nodes: list[int] = list(G.nodes())

    color: dict[int, int] = {v: DSATUR_UNCOLORED_MARKER for v in nodes}
    uncolored_nodes: set[int] = set(nodes)

    saturation: dict[int, int] = {v: 0 for v in nodes}
    neighbor_colors: dict[int, set[int]] = {v: set() for v in nodes}
    uncolored_deg: dict[int, int] = {v: int(G.degree(v)) for v in nodes}
    
    steps: list[tuple[int, int, int]] = []

    for _ in range(1, len(nodes) + 1):
        # Node with (max saturation, max degree in uncolored subgraph)
        best: int = max(
            uncolored_nodes,
            key=lambda v: (saturation[v], uncolored_deg[v]),
        )
        selected_saturation: int = saturation[best]

        # Assign the smallest color not used by any neighbor
        color_selected: int = DSATUR_FIRST_COLOR_ID
        while color_selected in neighbor_colors[best]:
            color_selected += 1
        color[best] = color_selected
        uncolored_nodes.remove(best)

        steps.append((best, color_selected, selected_saturation))

        # Update saturation and uncolored degree of neighbors
        for neighbor in G.neighbors(best):
            if color[neighbor] == DSATUR_UNCOLORED_MARKER:
                uncolored_deg[neighbor] -= 1
                if color_selected not in neighbor_colors[neighbor]:
                    neighbor_colors[neighbor].add(color_selected)
                    saturation[neighbor] += 1

    return color, steps

def main() -> None:
    """Main routing controller orchestrating workflow based on CLI standard inputs.

    Returns:
        None
    """
    args: list[str] = sys.argv[1:]
    input_path, speed = parse_cli_args_wrapper(args)

    if input_path is None or speed is None:
        sys.exit(APP_EXIT_FAILURE_CODE)
        return

    current_file: str = input_path

    while True:
        # After clicking on the button to load a new graph, we read it from the file again to reset any previous coloring state. 
        G: nx.Graph = read_graph_from_file(current_file) 
        color, steps = dsatur_with_steps(G)

        completed: bool = animate_dsatur(
            title=path.basename(current_file), 
            G=G, 
            steps=steps, 
            frame_pause_seconds=speed
        )
        is_valid: bool = validate(G=G, color=color)

        next_file: str | None = show_coloring_popup(success=completed and is_valid)
        if next_file is None:
            break
        current_file = next_file


if __name__ == "__main__":
    main()
