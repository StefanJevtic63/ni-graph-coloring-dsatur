"""DSatur implementation using a standard list-based approach for priority tracking."""

from dsatur.DSaturBase import DSaturBase
from constants import DSATUR_UNCOLORED_MARKER


class DSaturStandard(DSaturBase):
    """Classic DSatur implementation with O(n^2) time complexity,
    where n is the number of nodes in the graph."""

    def solve(self) -> tuple[dict[int, int], list[tuple[int, int, int]]]:
        """Run standard sequential DSatur by scanning all uncolored nodes.

        Returns:
            tuple[dict[int, int], list[tuple[int, int, int]]]: Final coloring results and steps.
        """
        while self.uncolored_nodes:
            # Lexicographically select the uncolored node with the highest saturation degree
            best_node: int = max(
                self.uncolored_nodes,
                key=lambda v: (self.saturation[v], self.uncolored_deg[v], -v), 
            )

            selected_color, _ = self._assign_smallest_available_color(best_node)

            for neighbor in self.G.neighbors(best_node):
                if self.color[neighbor] == DSATUR_UNCOLORED_MARKER:
                    self._update_uncolored_neighbor(neighbor, selected_color)

        return self.color, self.steps
