#!/usr/bin/env python3
"""Graph coloring using DSatur with step-by-step visualization.
Defaults to Fibonacci heap implementation for priority tracking, 
but also includes a binary heap and a standard list-based approach for comparison.

Usage:
    python main.py <input_file>

Example:
    python main.py wheel.txt

Input format:
    n m         <- number of nodes and edges
    u1 v1       <- edge from node u1 to node v1 (undirected)
    ...
    um vm       <- edge from node um to node vm (undirected)
"""

import sys
import networkx as nx
from os import path

from dsatur.DSaturStandard import DSaturStandard
from dsatur.DSaturBinHeap import DSaturBinHeap
from dsatur.DSaturFibHeap import DSaturFibHeap

from constants import (APP_EXIT_FAILURE_CODE)
from utility import (
    animate_dsatur, read_graph_from_file, parse_cli_args_wrapper, 
    show_coloring_popup, validate, 
)

def dsatur(
    G: nx.Graph,
) -> tuple[dict[int, int], list[tuple[int, int, int]]]:
    """Run classic DSatur and return final coloring with per-iteration steps.

    Args:
        G (nx.Graph): The networkx graph target object.

    Returns:
        tuple[dict[int, int], list[tuple[int, int, int]]]: Final coloring dictionary and step tracking steps.
    """
    return DSaturStandard(G).solve()


def dsatur_binary_heap(
    G: nx.Graph,
) -> tuple[dict[int, int], list[tuple[int, int, int]]]:
    """Run DSatur with binary heap and return final coloring with steps.

    Args:
        G (nx.Graph): The networkx graph target object.

    Returns:
        tuple[dict[int, int], list[tuple[int, int, int]]]: Final coloring dictionary and step tracking steps.
    """
    return DSaturBinHeap(G).solve()


def dsatur_fibonacci_heap(
    G: nx.Graph,
) -> tuple[dict[int, int], list[tuple[int, int, int]]]:
    """Run DSatur with Fibonacci heap and return final coloring with steps.

    Args:
        G (nx.Graph): The networkx graph target object.

    Returns:
        tuple[dict[int, int], list[tuple[int, int, int]]]: Final coloring dictionary and step tracking steps.
    """
    return DSaturFibHeap(G).solve()

def main() -> None:
    """Main routing controller orchestrating workflow based on CLI standard inputs.

    Returns:
        None
    """
    args: list[str] = sys.argv[1:]
    input_path, pause = parse_cli_args_wrapper(args)

    if input_path is None or pause is None:
        sys.exit(APP_EXIT_FAILURE_CODE)
        return

    current_file: str = input_path

    while True:
        # After clicking on the button to load a new graph, 
        # we read it from the file again to reset any previous coloring state. 
        G: nx.Graph = read_graph_from_file(current_file) 
        
        # color, steps = dsatur(G)
        #color, steps = dsatur_binary_heap(G)
        color, steps = dsatur_fibonacci_heap(G)

        completed: bool = animate_dsatur(
            title=path.basename(current_file), 
            G=G, 
            steps=steps, 
            frame_pause_seconds=pause
        )
        is_valid: bool = validate(G=G, color=color)

        next_file: str | None = show_coloring_popup(success=completed and is_valid)
        if next_file is None:
            break
        current_file = next_file


if __name__ == "__main__":
    main()
