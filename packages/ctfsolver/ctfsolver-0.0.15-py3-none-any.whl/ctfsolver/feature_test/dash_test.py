# dash_cytoscape_graph.py
import dash
from dash import html, dcc, Output, Input
import dash_cytoscape as cyto

# Example data: mimic a network flow
graph_data = {
    "192.168.0.2": ["8.8.8.8", "192.168.0.3"],
    "192.168.0.3": ["10.0.0.1"],
    "8.8.8.8": [],
}

# Convert to cytoscape elements
elements = []

for source, targets in graph_data.items():
    elements.append({"data": {"id": source, "label": source}})
    for target in targets:
        elements.append({"data": {"id": target, "label": target}})
        elements.append({"data": {"source": source, "target": target}})
# print(elements)


example = [
    {"data": {"id": "192.168.0.2", "label": "192.168.0.2"}},
    {"data": {"source": "192.168.0.2", "target": "8.8.8.8"}},
]

# App setup
app = dash.Dash(__name__)
app.title = "Interactive Network Graph"

app.layout = html.Div(
    [
        html.H1("Packet Flow Visualization", style={"color": "white"}),
        cyto.Cytoscape(
            id="cytoscape-graph",
            elements=elements,
            layout={"name": "cose"},  # force-directed layout
            style={"width": "100%", "height": "700px"},
            stylesheet=[
                {
                    "selector": "node",
                    "style": {
                        "content": "data(label)",
                        "text-valign": "center",
                        "color": "white",
                        "background-color": "#0074D9",
                        "font-size": 14,
                    },
                },
                {"selector": "edge", "style": {"line-color": "#AAAAAA", "width": 2}},
            ],
        ),
        html.Div(
            id="node-click-output",
            style={"padding": "20px", "color": "white", "backgroundColor": "#111"},
        ),
    ],
    style={"backgroundColor": "#222", "padding": "20px"},
)


@app.callback(
    Output("node-click-output", "children"), Input("cytoscape-graph", "tapNodeData")
)
def display_node_info(data):
    if data:
        print("Node clicked:", data)
        return f"Clicked on node: {data['label']}"
    return "Click a node to see its info."


if __name__ == "__main__":
    app.run(debug=True)
