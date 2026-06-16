"""DSatur implementation using a Fibonacci heap with direct node mapping for O(n log n + m) complexity."""

import networkx as nx
from FibonacciHeap.FibonacciHeap import FibonacciHeap, Node

from dsatur.DSaturBase import DSaturBase
from constants import DSATUR_UNCOLORED_MARKER

class DSaturFibHeap(DSaturBase):
    """DSatur graph coloring solver using a FibonacciHeap with direct node pointer mapping.
    
    This implementation aims to achieve the theoretical time complexity of O(n log n + m)
    by utilizing a lookup map to perform direct,
    amortized O(1) decrease_key operations on mutated neighbor nodes.
    """

    def __init__(self, G: nx.Graph) -> None:
        """Initialize the Fibonacci Heap, core data structures, and the pointer lookup map.

        Args:
            G (nx.Graph): The input undirected graph to color.
        """
        super().__init__(G)
        self.fib_heap: FibonacciHeap = FibonacciHeap()
        
        # Maps graph node ID to its corresponding Node object instance inside the heap
        self.node_mapping: dict[int, Node] = {}

    def _make_key(self, v: int) -> tuple[int, int]:
        """Generate the sorting priority tuple key for a given node.
        
        The tuple is constructed as (-saturation, node_id).
        Since the Fibonacci Heap is a min-heap, decrementing these components 
        (i.e., when saturation increases) reduces the overall 
        tuple value, making it naturally compatible with the decrease_key operation.

        Args:
            v (int): The target graph node ID.

        Returns:
            tuple[int, int]: A priority payload tuple containing:
                - Negative saturation degree (primary sorting key).
                - The unique node ID (secondary key ensuring strict order).
        """
        return (-self.saturation[v], v)

    def _add_node_to_heap(self, v: int) -> None:
        """Create a heap Node object instance, register its reference, and insert it.

        Args:
            v (int): The graph node ID to inject into the heap.
        """
        initial_key: tuple[int, int] = self._make_key(v)
        node_obj: Node = Node(initial_key)
        
        self.node_mapping[v] = node_obj
        self.fib_heap.insert(node_obj)

    def _update_node_in_heap(self, v: int) -> None:
        """Directly adjust an active node's structural priority using decrease_key.

        Args:
            v (int): The graph node ID whose priority needs updating.
        """
        node_obj: Node = self.node_mapping[v]
        new_key: tuple[int, int] = self._make_key(v)
        self.fib_heap.decrease_key(node_obj, new_key)

    def _pop_min_node_id(self) -> int:
        """Extract the minimum Node from the heap, unregister its reference, and return its ID.

        Returns:
            int: The unique graph node ID tracking the highest priority.

        Raises:
            IndexError: If an extraction is attempted on an empty heap structure.
        """
        min_node: Node | None = self.fib_heap.extract_min()
        if min_node is None:
            raise IndexError("Cannot pop from an empty FibonacciHeap.")
        
        # The underlying key structure is a tuple: (-saturation, node_id)
        payload: tuple[int, int] = min_node.key
        node_id: int = payload[1]
        
        del self.node_mapping[node_id]
        return node_id
    
    def solve(self) -> tuple[dict[int, int], list[tuple[int, int, int]]]:
        """Run DSatur using direct priority updates.
        
        Returns:
            tuple[dict[int, int], list[tuple[int, int, int]]]: A tuple containing:
                - A mapping of graph node IDs to their assigned colors.
                - A chronological list of steps taken during the coloring process.
        """
        for v in self.nodes:
            self._add_node_to_heap(v)

        while self.uncolored_nodes:
            best_node = self._pop_min_node_id()
            selected_color, _ = self._assign_smallest_available_color(best_node)

            for neighbor in self.G.neighbors(best_node):
                if self.color[neighbor] == DSATUR_UNCOLORED_MARKER:
                    self._update_uncolored_neighbor(neighbor=neighbor, selected_color=selected_color)
                    self._update_node_in_heap(neighbor)

        return self.color, self.steps
    