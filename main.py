import heapq
import tkinter as tk
import tkinter.ttk as ttk
from collections import defaultdict
from typing import Tuple

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
    f_values = defaultdict(utils.default_node_val)
    g_values = defaultdict(utils.default_node_val)
    came_from = {}

    def __init__(self) -> None:
        super().__init__()

        self.title("A* Star Visualizer")
        self.geometry("1280x720")

        self.status = tk.StringVar(self, "idle")
        self.status.trace_add("write", self.__on_status_change)

        self.frame = tk.Frame(self, padx=20, pady=20)
        self.frame.pack()

        default_font = ("Candara", 12)
        self.option_add("*Font", default_font)

        gf = self.__generator_frame()
        gf.grid(row=0, column=0, sticky=tk.W + tk.E, pady=(0, 20))

        cf = self.__controls_frame()
        cf.grid(row=1, column=0, sticky=tk.W + tk.E, pady=(0, 20))

        self.fig, self.ax = plt.subplots()
        self.fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.fig, self.frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=2, column=0, sticky=tk.W + tk.E)

    def __generator_frame(self) -> tk.LabelFrame:
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

    def __controls_frame(self) -> tk.LabelFrame:
        parent = tk.LabelFrame(self.frame, text="Visualizer Controls", padx=15, pady=15)
        total_nodes = 0 if not self.graph else self.graph.number_of_nodes() - 1

        # Controls Vars
        self.paused = tk.BooleanVar(self)
        self.paused.trace_add("write", self.__on_pause_change)

        self.start_node = tk.IntVar(self)
        self.end_node = tk.IntVar(self)

        # Control Buttons
        cbf = tk.Frame(parent)
        cbf.pack()

        #  Start Node Frame
        snf = tk.Frame(cbf)
        tk.Label(snf, text="Start Node").grid(row=0, column=0, sticky=tk.W)
        self.start_entry = ttk.Spinbox(
            snf, textvariable=self.start_node, from_=1, to=total_nodes
        )
        self.start_entry.grid(row=1, column=0)
        snf.pack(side=tk.LEFT, padx=(0, 15))

        # End Node Frame
        enf = tk.Frame(cbf)
        tk.Label(enf, text="End Node").grid(row=0, column=0, sticky=tk.W)
        self.end_entry = ttk.Spinbox(
            enf, textvariable=self.end_node, from_=0, to=total_nodes
        )
        self.end_entry.grid(row=1, column=0)
        enf.pack(side=tk.LEFT, padx=(0, 15))

        # Play / Pause Button
        self.play_img = utils.load_image("./assets/play.png", (48, 48))
        self.pause_img = utils.load_image("./assets/pause.png", (48, 48))
        self.pause_btn = tk.Button(
            cbf, image=self.play_img, command=self.__on_pause_click
        )
        self.pause_btn.pack(side=tk.LEFT, padx=(0, 15))

        # Stop Button
        self.stop_img = utils.load_image("./assets/stop.png", (48, 48))
        self.stop_btn = tk.Button(
            cbf, image=self.stop_img, command=self.__on_stop_click
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 15))

        return parent

    def __generate_graph(self) -> None:
        self.graph = utils.generate_graph(
            self.node_count.get(),
            self.min_weight.get(),
            self.max_weight.get(),
            self.edge_prob.get(),
        )

        print(self.graph.nodes)

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

    def __on_pause_click(self, *args):
        self.paused.set(not self.paused.get())

    def __on_pause_change(self, *args):
        is_paused = self.paused.get()

        img = self.pause_img if is_paused else self.play_img
        self.pause_btn.config(image=img)

    def __on_stop_click(self, *args):
        self.status.set("idle")
        # TODO: Reset State Here

    def __on_status_change(self, *args):
        print("Changed", self.status.get())

    def __a_star_algorithm(self):
        start = self.start_node.get()
        end = self.end_node.get()

        self.g_values[start] = 0
        self.f_values[start] = self.__heuristic(start)

        heapq.heappush(self.pq, (self.f_values))

    def __heuristic(self, node: Tuple[int, int], goal: Tuple[int, int]) -> float:
        return ((node[0] - goal[0]) ** 2 + (node[1] - goal[1]) ** 2) ** 0.5


if __name__ == "__main__":
    try:
        print("Running visualizer...")
        app = AStarVisualizer()
        app.mainloop()

    except Exception as err:
        print(f"Caught an Exception : {err}")

    finally:
        print("Visualizer Exited")
