# Graph Coloring with DSatur heuristic

This project is an interactive desktop application for the step-by-step visualization and demonstration of the graph coloring problem with **DSatur (Degree Saturation)** heuristic. The application allows users to visually track how the algorithm makes decisions based on node saturation degrees, featuring animation pausing capabilities and dynamic graph switching through a Graphical User Interface (GUI).

## Project Goal

The primary goal of this project is educational: to provide a visual breakdown of greedy heuristics within graph theory. Instead of just displaying the final result, the application renders the real-time metrics that dictate the algorithm's next move (such as saturation degree and the remaining degree of uncolored nodes).

This project was developed as part of the **Scientific Computing** course within the Master's program at the **Faculty of Mathematics, University of Belgrade**.

---

## About the DSatur Algorithm

**DSatur** (short for *Degree Saturation*) is a heuristic graph coloring algorithm introduced by Daniel Brélaz in 1979. Graph coloring—assigning colors to nodes such that no two adjacent nodes share the same color using the minimum total number of colors—is an NP-hard problem. In this project, the standard implementation operates in $\mathcal{O}(n^2)$ time (where $n$ is the number of nodes), while the heap-based variants improve node-selection updates with priority queues to target near-logarithmic update behavior.

### Implementation Variants

The repository includes three DSatur solver variants, all of which share the same graph metadata initialization and step recording logic from the common base class. By default, the application utilizes the `DSaturFibHeap` implementation for execution due to its superior theoretical complexity on sparse graphs.

- **`DSaturStandard`**: the classic sequential version. At every step, it scans all currently uncolored nodes and selects the one with the highest saturation degree, using the remaining uncolored degree and the node id as tie-breakers. This is the simplest implementation and has $\mathcal{O}(n^2)$ time complexity.
- **`DSaturBinHeap`**: a heap-optimized version built on Python's `heapq` binary heap. It stores priorities as `(-saturation, -uncolored_degree, node_id, version_token)` and uses lazy invalidation so outdated heap entries can be ignored when they are popped. This reduces selection overhead to $\mathcal{O}(\log n)$ per update and gives an overall complexity of $\mathcal{O}((n + m) \log n)$.
- **`DSaturFibHeap`**: a heap-optimized version backed by Python's `FibonacciHeap` package. It keeps a direct dictionary mapping (`node_mapping`) from graph node id to heap node object, enabling constant-time lookup of the corresponding heap entry before applying `decrease_key` updates. Priorities are stored as `(-saturation, node_id)`, and this implementation targets $\mathcal{O}(m + n \log n)$ behavior.

All variants use the same coloring rule: once a node is selected, it receives the smallest available color not used by its colored neighbors, and the saturation/remaining-degree information of its uncolored neighbors is updated immediately.

### How the Algorithm Works:

1. **Initialization:** Initially, all nodes are uncolored, and their saturation degree is set to `0`.
2. **Node Selection:** From the set of uncolored nodes, the algorithm selects the node with the **highest degree of saturation** (the number of unique colors used by its direct neighbors).
   - *Tie-breaker in `DSaturStandard` and `DSaturBinHeap`:* if multiple nodes share the same saturation, the node with the **highest degree in the subgraph induced by remaining uncolored nodes** is preferred; if still tied, lower node id wins.
   - *Tie-breaker in `DSaturFibHeap`:* priority is based on `(-saturation, node_id)`, so ties on saturation are broken directly by node id.
3. **Color Assignment:** The selected node is assigned the **lowest possible color ID** (e.g., 1, 2, 3...) that is not currently being used by any of its neighbors.
4. **State Update:** For all uncolored neighbors of the newly colored node, the saturation degree is updated, and their remaining uncolored degree is decremented.
5. **Termination:** Steps 2–4 repeat until all nodes in the graph are successfully colored.

---

## Application Features

- **Optimized Performance:** Uncolored nodes are tracked in a dynamic `set`, while heap variants maintain priority queues for efficient node selection updates (`heapq` with lazy invalidation, or `FibonacciHeap` with direct `node_mapping` lookups).
- **Interactive Animation:** A side-by-side rendering of the graph and an information panel that displays the currently selected node, its saturation, and its assigned color at every step.
- **Playback Control:** Ability to toggle between `Pause` and `Resume` states at any point during the animation.
- **GUI Selector Popup:** Automatically prompts the user after an animation finishes, allowing seamless switching to other graph examples (Wheel, Bipartite, Dense, Petersen).
- **Flexible CLI Arguments:** Users can easily customize the input graph and execution pause directly via the command-line interface.

---

## Running the Program

### Prerequisites
Install the required dependencies (listed in the `requirements.txt` file):
```bash
pip install -r requirements.txt
```

### Execution Modes

1. Run without arguments:
```bash
python main.py
```
When started this way, the program opens a selector window where the user can choose one of the available example graphs by clicking a button.

2. Run with an explicit input file:
```bash
python main.py wheel.txt
```
When started this way, the input graph is explicitly loaded from the `wheel.txt` file.

3. Run with custom animation pause:
```bash
python main.py wheel.txt --pause 1
```
The `--pause` parameter controls the pause between animation steps (in seconds).

Note: the following command format is valid, but `-1` itself is not accepted because pause must be positive:
```bash
python main.py wheel.txt --pause -1
```

---

## Input File Format

Graph files are plain text files that define an undirected graph using whitespace-separated integers.

Format:

1. First line (or first two tokens):
`n m`
where `n` is the number of nodes, and `m` is the number of edges.
2. Next `m` lines (or `2m` tokens):
`u v`
Each pair `u v` represents one undirected edge between nodes `u` and `v`.

Example (wheel.txt):

```text
7 12
1 2
2 3
3 4
4 5
5 6
6 1
7 1
7 2
7 3
7 4
7 5
7 6
```

Additional notes:

- nodes are expected to be indexed from `1` to `n`.
- Self-loops (`u == v`) are ignored by the parser.
- Extra spaces and line breaks are allowed, since parsing is token-based.