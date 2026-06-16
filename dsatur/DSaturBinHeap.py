"""DSatur implementation using a binary heap with lazy invalidation for priority tracking."""

import networkx as nx
from heapq import heappush, heappop

from dsatur.DSaturBase import DSaturBase
from constants import DSATUR_UNCOLORED_MARKER

class DSaturBinHeap(DSaturBase):
    """DSatur using binary heap with lazy invalidation."""

    def __init__(self, G: nx.Graph) -> None:
        """Initialize binary heap arrays and tracking metadata structures.

        Args:
            G (nx.Graph): The input undirected graph to color.

        Returns:
            None
        """
        super().__init__(G)
        self.heap: list[tuple[int, int, int, int]] = []
        self.node_version: dict[int, int] = {v: 0 for v in self.nodes}

    def _push_or_update(self, v: int) -> None:
        """Increment version token and push updated node state to binary heap.

        Args:
            v (int): The node node ID.

        Returns:
            None
        """
        self.node_version[v] += 1
        token: int = self.node_version[v]

        heappush(
            self.heap,
            (-self.saturation[v], -self.uncolored_deg[v], v, token),
        )

    def _pop_min_payload(self) -> tuple[int, int, int, int]:
        """Pop the minimum item directly from the standard binary heap array.

        Returns:
            tuple[int, int, int, int]: The raw sorting tuple payload.
        """
        return heappop(self.heap)

    def solve(self) -> tuple[dict[int, int], list[tuple[int, int, int]]]:
        """Run DSatur using the shared heap-driven priority tracking loop.

        Returns:
            tuple[dict[int, int], list[tuple[int, int, int]]]: Final coloring results and steps.
        """
        for v in self.nodes:
            self._push_or_update(v)

        while self.uncolored_nodes:
            while True:
                _, _, best_node, token = self._pop_min_payload()
                if best_node in self.uncolored_nodes and token == self.node_version[best_node]:
                    break

            selected_color, _ = self._assign_smallest_available_color(best_node)

            for neighbor in self.G.neighbors(best_node):
                if self.color[neighbor] == DSATUR_UNCOLORED_MARKER:
                    self._update_uncolored_neighbor(neighbor=neighbor, selected_color=selected_color)
                    self._push_or_update(neighbor)

        return self.color, self.steps