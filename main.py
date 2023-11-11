import heapq
import tkinter as tk
from collections import defaultdict

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import constants
import utils


class AStarVisualizer(tk.Tk):
    graph: nx.Graph | None = None

    # Algorithm vars
    pq = []
    visited = set()
    g_values = defaultdict(utils.default_node_val)
    h_values = defaultdict(utils.default_node_val)
    came_from = {}

    def __init__(self) -> None:
        super().__init__()

        self.title("A* Star Visualizer")
        self.geometry("1280x720")

        self.frame = tk.Frame(self, padx=20, pady=20)
        self.frame.pack()

        default_font = ("Calibri", 12)
        self.option_add("*Font", default_font)

        gf = self.generator_frame()
        gf.grid(row=0, column=0, sticky=tk.W + tk.E, pady=20)

        self.fig, self.ax = plt.subplots()
        self.fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.fig, self.frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=1, column=0, sticky=tk.W + tk.E)
        # self.frame.rowconfigure(1, weight=1)

    def generator_frame(self) -> tk.LabelFrame:
        parent = tk.LabelFrame(self.frame, text="Graph Generator", padx=15, pady=15)

        # Generator vars
        self.node_count = tk.IntVar(self)
        self.min_weight = tk.IntVar(self)
        self.max_weight = tk.IntVar(self)
        self.edge_prob = tk.DoubleVar(self)

        # Node Count Frame
        ncf = tk.Frame(parent)
        tk.Label(ncf, text="Nodes").grid(row=0, column=0, sticky=tk.W)
        tk.Entry(ncf, textvariable=self.node_count).grid(row=1, column=0)
        ncf.grid(row=0, column=0, padx=(0, 15))

        # Min Weight Frame
        mwf = tk.Frame(parent)
        tk.Label(mwf, text="Min Weight").grid(row=0, column=0, sticky=tk.W)
        tk.Entry(mwf, textvariable=self.min_weight).grid(row=1, column=0)
        mwf.grid(row=0, column=1, padx=(0, 15))

        # Max Weight Frame
        mxf = tk.Frame(parent)
        tk.Label(mxf, text="Max Weight").grid(row=0, column=0, sticky=tk.W)
        tk.Entry(mxf, textvariable=self.max_weight).grid(row=1, column=0)
        mxf.grid(row=0, column=2, padx=(0, 15))

        # Edge Probability Frame
        epf = tk.Frame(parent)
        tk.Label(epf, text="Edge Probability (%)").grid(row=0, column=0, sticky=tk.W)
        tk.Entry(epf, textvariable=self.edge_prob).grid(row=1, column=0)
        epf.grid(row=0, column=3, padx=(0, 15))

        # Button to generate graph
        gbf = tk.Button(
            parent, text="Generate Graph", command=lambda: self.__generate_graph()
        )
        gbf.grid(row=0, column=4)

        return parent

    def __generate_graph(self) -> None:
        self.graph = utils.generate_graph(
            self.node_count.get(),
            self.min_weight.get(),
            self.max_weight.get(),
            self.edge_prob.get(),
        )

        self.__draw_graph()

    def __draw_graph(self) -> None:
        if not self.graph:
            return

        self.ax.clear()

        pos = nx.spring_layout(self.graph)
        nx.draw_networkx(
            self.graph, pos, ax=self.ax, node_color="#5a2675", font_color="#ffffff"
        )

        weights = nx.get_edge_attributes(self.graph, "weight")
        nx.draw_networkx_edge_labels(
            self.graph, pos=pos, ax=self.ax, edge_labels=weights
        )

        self.fig.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    try:
        print("Running visualizer...")
        app = AStarVisualizer()
        app.mainloop()

    except Exception as err:
        print(f"Caught an Exception : {err}")

    finally:
        print("Visualizer Exited")
