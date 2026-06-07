"""Base abstract class for DSatur implementations, containing shared data structures and helper methods."""

import networkx as nx
from abc import ABC, abstractmethod

from constants import DSATUR_FIRST_COLOR_ID, DSATUR_UNCOLORED_MARKER


class DSaturBase(ABC):
    """Base DSatur solver with shared data initialization and update helpers."""

    def __init__(self, G: nx.Graph) -> None:
        """Initialize graph-related metadata structures and step trackers.

        Args:
            G (nx.Graph): The input undirected graph to color.
        """
        self.G: nx.Graph = G
        self.nodes: set[int] = set(G.nodes())

        self.color: dict[int, int] = {v: DSATUR_UNCOLORED_MARKER for v in self.nodes}
        self.uncolored_nodes: set[int] = set(self.nodes)

        # Saturation degree of each node (number of distinct colors in its neighborhood)
        self.saturation: dict[int, int] = {v: 0 for v in self.nodes}

        # For each node, track the set of colors used by its neighbors to efficiently compute saturation and available colors.
        self.neighbor_colors: dict[int, set[int]] = {v: set() for v in self.nodes}

        # Uncolored degree of each node (number of uncolored neighbors), used for tie-breaking in selection.
        self.uncolored_deg: dict[int, int] = {v: int(G.degree(v)) for v in self.nodes}

        self.steps: list[tuple[int, int, int]] = []

    def _assign_smallest_available_color(self, best_node: int) -> tuple[int, int]:
        """Color selected node with the lowest available color and record a step.

        Args:
            best_node (int): The node ID selected for coloring.

        Returns:
            tuple[int, int]: A tuple containing the assigned color ID and the
                saturation degree of the node at the moment of coloring.
        """
        selected_saturation: int = self.saturation[best_node]

        selected_color: int = DSATUR_FIRST_COLOR_ID
        while selected_color in self.neighbor_colors[best_node]:
            selected_color += 1

        self.color[best_node] = selected_color
        self.uncolored_nodes.remove(best_node)
        self.steps.append((best_node, selected_color, selected_saturation))

        return selected_color, selected_saturation

    def _update_uncolored_neighbor(self, neighbor: int, selected_color: int) -> None:
        """Update degree and saturation metadata for one uncolored neighbor.

        Args:
            neighbor (int): The neighbor node ID to update.
            selected_color (int): The color ID assigned to the adjacent node.

        Returns:
            None
        """
        self.uncolored_deg[neighbor] -= 1

        if selected_color not in self.neighbor_colors[neighbor]:
            self.neighbor_colors[neighbor].add(selected_color)
            self.saturation[neighbor] += 1

    @abstractmethod
    def solve(self) -> tuple[dict[int, int], list[tuple[int, int, int]]]:
        """Run DSatur and return final coloring and coloring steps.

        Returns:
            tuple[dict[int, int], list[tuple[int, int, int]]]: A tuple containing:
                - The final coloring dictionary {node_id: color_id}.
                - A list of execution step metadata tuples (node, color, saturation).
        """
        pass
