"""DSatur implementation using a binary heap with lazy invalidation for priority tracking."""

import networkx as nx
from heapq import heappush, heappop

from dsatur.DSaturHeapBase import DSaturHeapBase


class DSaturBinHeap(DSaturHeapBase):
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
