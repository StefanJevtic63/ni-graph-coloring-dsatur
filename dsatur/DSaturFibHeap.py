"""DSatur implementation using a Fibonacci heap with lazy invalidation for priority tracking."""

import networkx as nx
from FibonacciHeap.FibonacciHeap import FibonacciHeap, Node

from dsatur.DSaturHeapBase import DSaturHeapBase


class DSaturFibHeap(DSaturHeapBase):
    """DSatur using FibonacciHeap class with lazy invalidation."""

    def __init__(self, G: nx.Graph) -> None:
        """Initialize custom Fibonacci Heap instances and metadata structures.

        Args:
            G (nx.Graph): The input undirected graph to color.

        Returns:
            None
        """
        super().__init__(G)
        self.fib_heap: FibonacciHeap = FibonacciHeap()

    def _extract_payload(self, min_item: Node) -> tuple[int, int, int, int]:
        """Extract tuple payload from FibonacciHeap Node.

        Args:
            min_item (Node): The node instance extracted from the heap.

        Returns:
            tuple[int, int, int, int]: The raw sorting tuple payload.
        """
        return min_item.key

    def _push(self, payload: tuple[int, int, int, int]) -> None:
        """Push payload as a Node into FibonacciHeap.

        Args:
            payload (tuple[int, int, int, int]): The priority metadata context.

        Returns:
            None
        """
        self.fib_heap.insert(Node(payload))

    def _pop(self) -> tuple[int, int, int, int]:
        """Pop minimum Node and return its tuple payload.

        Returns:
            tuple[int, int, int, int]: The priority metadata tuple payload.

        Raises:
            IndexError: If an extraction is attempted on an empty heap.
        """
        min_node: Node | None = self.fib_heap.extract_min()
        if min_node is None:
            raise IndexError("Cannot pop from an empty FibonacciHeap.")
        return self._extract_payload(min_node)

    def _push_or_update(self, v: int) -> None:
        """Increment version token and push updated node state to Fibonacci heap.

        Args:
            v (int): The node node ID.

        Returns:
            None
        """
        self.node_version[v] += 1
        token: int = self.node_version[v]
        self._push(
            (-self.saturation[v], -self.uncolored_deg[v], v, token),
        )

    def _pop_min_payload(self) -> tuple[int, int, int, int]:
        """Pop the minimum item from the custom Fibonacci Heap instance wrapper.

        Returns:
            tuple[int, int, int, int]: The raw sorting tuple payload.
        """
        return self._pop()
