from pyvis.network import Network


class GraphVisualizer:
    def __init__(
        self, height="750px", width="100%", bgcolor="#222222", font_color="white"
    ):
        self.net = Network(
            height=height, width=width, bgcolor=bgcolor, font_color=font_color
        )
        self.nodes = set()  # To avoid duplicates
        self.edges = set()  # To avoid duplicates

    def add_node(self, node_id, label=None, **kwargs):
        if node_id not in self.nodes:
            self.net.add_node(node_id, label=label or node_id, **kwargs)
            self.nodes.add(node_id)

    def add_edge(self, source, target, **kwargs):
        if (source, target) not in self.edges:
            self.add_node(source)
            self.add_node(target)
            self.net.add_edge(source, target, **kwargs)
            self.edges.add((source, target))

    def add_graph_data(self, graph_dict):
        """
        Add a dictionary like:
        {
            "A": ["B", "C"],
            "B": ["D"],
        }
        """
        for source, targets in graph_dict.items():
            for target in targets:
                self.add_edge(source, target)

    def show(self, filename="graph.html"):
        self.net.show_buttons(
            filter_=["physics"]
        )  # Optional: enable physics settings panel
        self.net.show(filename, notebook=False)
        print(f"Graph saved to {filename}")


# === Example usage ===
if __name__ == "__main__":
    # Obsidian-style graph data
    data = {
        "Home": ["Page1", "Page2"],
        "Page1": ["NoteA", "NoteB"],
        "Page2": ["NoteC"],
        "NoteC": ["NoteD", "NoteE"],
        "NoteE": ["Page1"],  # Cyclic reference
    }

    graph = GraphVisualizer()
    graph.add_graph_data(data)
    graph.show("pyvis_graph.html")
