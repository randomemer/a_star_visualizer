import asyncio
import heapq
import tkinter as tk
import tkinter.ttk as ttk
from typing import List, Set, Tuple

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import constants
import utils


class AStarVisualizer(tk.Tk):
    graph: nx.Graph | None = None

    # Algorithm vars
    pq: List[Tuple[int, int, List[int]]] = []  # (priority, current_node, path)
    visited: Set[int] = set()
    path: List[int] | None = None

    def __init__(self) -> None:
        super().__init__()

        # Window Intialization
        self.title("A* Star Visualizer")
        self.geometry("1280x720")

        default_font = ("Candara", 12)
        self.option_add("*Font", default_font)

        # Generator vars
        self.node_count = tk.IntVar(self, 10)
        self.min_weight = tk.IntVar(self, 1)
        self.max_weight = tk.IntVar(self, 10)
        self.edge_prob = tk.DoubleVar(self, 20)

        # Controls Vars
        self.status = tk.StringVar(self, "idle")
        self.status.trace_add("write", self.__on_status_change)

        self.paused = tk.BooleanVar(self, False)
        self.paused.trace_add("write", self.__on_pause_change)

        self.start_node = tk.IntVar(self)
        self.end_node = tk.IntVar(self)

        # UI Initialization
        self.scroll_canvas = tk.Canvas(
            self, borderwidth=0, highlightthickness=0, yscrollincrement=5
        )

        self.frame = tk.Frame(self.scroll_canvas, padx=20, pady=20)
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=self.scroll_canvas.yview
        )

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.frame_id = self.scroll_canvas.create_window(
            0, 0, window=self.frame, anchor=tk.NW
        )

        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scroll_canvas.bind("<Configure>", self._on_canvas_configure)
        self.frame.bind("<Configure>", self._on_frame_configure)
        self.scroll_canvas.bind_all("<Button>", self._on_vscroll)

        self.gf = tk.LabelFrame(self.frame, text="Graph Generator", padx=15, pady=15)
        self.frame.grid_columnconfigure(0, weight=1)
        self.gf.grid(row=0, column=0, sticky=tk.W + tk.E, pady=(0, 20))

        self.cf = tk.LabelFrame(
            self.frame, text="Visualizer Controls", padx=15, pady=15
        )
        self.cf.grid(row=1, column=0, sticky=tk.W + tk.E, pady=(0, 20))

        self.fig, self.ax = plt.subplots()
        self.fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.fig, self.frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=2, column=0, sticky=tk.W + tk.E)

        self.__load_assets()

        self.__generator_frame(self.gf)
        self.__controls_frame(self.cf)

    def __load_assets(self) -> None:
        """
        Load all necessary assets for the visualizer.
        """

        self.play_img = utils.load_image("./assets/play.png", (48, 48))
        self.pause_img = utils.load_image("./assets/pause.png", (48, 48))
        self.stop_img = utils.load_image("./assets/stop.png", (48, 48))

    def __generator_frame(self, parent: tk.LabelFrame) -> None:
        for widget in parent.winfo_children():
            widget.destroy()

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
        ttk.Spinbox(epf, textvariable=self.edge_prob, from_=0, to=100).grid(
            row=1, column=0
        )
        epf.grid(row=0, column=3, padx=(0, 15))

        # Button to generate graph
        gbf = tk.Button(
            parent, text="Generate Graph", command=lambda: self.__generate_graph()
        )
        gbf.grid(row=0, column=4)

    def __controls_frame(self, parent: tk.LabelFrame) -> None:
        for widget in parent.winfo_children():
            widget.destroy()

        total_nodes = 0 if not self.graph else self.graph.number_of_nodes() - 1

        # Control Buttons
        cbf = tk.Frame(parent)
        cbf.pack()

        #  Start Node Frame
        snf = tk.Frame(cbf)
        tk.Label(snf, text="Start Node").grid(row=0, column=0, sticky=tk.W)
        self.start_entry = ttk.Spinbox(
            snf,
            textvariable=self.start_node,
            from_=1,
            to=total_nodes,
            state="normal" if self.status.get() in ("ready", "done") else "disabled",
        )
        self.start_entry.grid(row=1, column=0)
        snf.pack(side=tk.LEFT, padx=(0, 15))

        # End Node Frame
        enf = tk.Frame(cbf)
        tk.Label(enf, text="End Node").grid(row=0, column=0, sticky=tk.W)
        self.end_entry = ttk.Spinbox(
            enf,
            textvariable=self.end_node,
            from_=0,
            to=total_nodes,
            state="normal" if self.status.get() in ("ready", "done") else "disabled",
        )
        self.end_entry.grid(row=1, column=0)
        enf.pack(side=tk.LEFT, padx=(0, 15))

        # Play / Pause Button
        self.pause_btn = tk.Button(
            cbf,
            image=self.play_img,
            command=self.__on_pause_click,
            state="normal" if self.status.get() != "idle" else "disabled",
        )
        self.pause_btn.pack(side=tk.LEFT, padx=(0, 15))

        # Stop Button
        self.stop_btn = tk.Button(
            cbf,
            image=self.stop_img,
            command=self.__on_stop_click,
            state="normal" if self.status.get() != "idle" else "disabled",
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 15))

    def __generate_graph(self) -> None:
        """
        Generates the graph based on user input and displays it using matplotlib.
        """
        self.graph = utils.generate_graph(
            self.node_count.get(),
            self.min_weight.get(),
            self.max_weight.get(),
            self.edge_prob.get() / 100,
        )

        if self.status.get() != "ready":
            self.status.set("ready")
        self.__draw_graph()

    def __draw_graph(self) -> None:
        if not self.graph:
            return

        self.graph_pos = nx.spring_layout(self.graph)
        self.ax.clear()

        nx.draw_networkx(
            self.graph,
            self.graph_pos,
            ax=self.ax,
            font_color=constants.WHITE,
            node_color=constants.PURPLE,
        )

        weights = nx.get_edge_attributes(self.graph, "weight")
        nx.draw_networkx_edge_labels(
            self.graph, pos=self.graph_pos, ax=self.ax, edge_labels=weights
        )

        self.fig.tight_layout()
        self.canvas.draw()

    def __update_graph(self) -> None:
        """
        Updates the graph with new state from the algorithm
        """
        cur_path_edges: Set[Tuple[int]] = set()
        cur_path_nodes = set(self.path)

        # Make a set of edges which represent the current path
        for i in range(1, len(self.path)):
            edge = (self.path[i - 1], self.path[i])
            cur_path_edges.add(tuple(sorted(edge)))

        node_colors, edge_colours = [], []

        for node in self.graph.nodes:
            color = constants.PURPLE
            if node in self.visited:
                color = constants.GREY
            if node in cur_path_nodes:
                color = constants.CERISE
            node_colors.append(color)

        for edge in self.graph.edges:
            color = constants.BLACK
            if edge in cur_path_edges:
                color = constants.SANDY_BROWN
            edge_colours.append(color)

        self.ax.clear()
        nx.draw_networkx(
            self.graph,
            self.graph_pos,
            ax=self.ax,
            font_color=constants.WHITE,
            node_color=node_colors,
            edge_color=edge_colours,
        )

        weights = nx.get_edge_attributes(self.graph, "weight")
        nx.draw_networkx_edge_labels(
            self.graph, pos=self.graph_pos, ax=self.ax, edge_labels=weights
        )

        self.fig.tight_layout()
        self.canvas.draw()

    def __on_pause_click(self, *args):
        if self.status.get() == "ready":
            self.loop = asyncio.get_event_loop()
            self.loop.run_until_complete(self.__start())

        self.paused.set(not self.paused.get())

    def __on_pause_change(self, *args):
        is_paused = self.paused.get()

        img = self.pause_img if is_paused else self.play_img
        self.pause_btn.config(image=img)

    def __on_stop_click(self, *args):
        self.status.set("idle")
        # TODO: Reset State Here

    def __on_status_change(self, *args):
        match self.status.get():
            case "idle":
                pass

            case "ready":
                self.__controls_frame(self.cf)

            case "running":
                self.__controls_frame(self.cf)

            case "done":
                self.__controls_frame(self.cf)

    def __a_star_algorithm(self):
        start, end = self.start_node.get(), self.end_node.get()

        self.pq = [(0, start, [])]
        self.visited = set()
        res = None

        while self.pq:
            (cost, cur, path) = heapq.heappop(self.pq)

            if cur not in self.visited:
                path = path + [cur]

                if cur == end:
                    yield path
                    break
                else:
                    self.visited.add(cur)

                    for neigh in self.graph.neighbors(cur):
                        if neigh not in self.visited:
                            priority = len(path) + self._heuristic(cur, end)
                            heapq.heappush(self.pq, (priority, neigh, path))

                    yield path
            else:
                yield None

    def _heuristic(self, node: int, goal: int) -> float:
        return nx.shortest_path_length(self.graph, node, goal)

    async def __start(self):
        """Start the algorithm."""
        self.status.set("running")

        gen = self.__a_star_algorithm()
        self.path = None

        while True:
            try:
                if not self.paused.get():
                    cur_path = next(gen)
                    if cur_path:
                        self.path = cur_path
            except StopIteration:
                break

            self.update_idletasks()
            self.__update_graph()
            await asyncio.sleep(1)

        self.status.set("done")

    def _on_vscroll(self, event: tk.Event) -> None:
        """Handle vertical scroll events on the canvas."""
        scroll = -1 if event.num == 4 else 1
        self.scroll_canvas.yview_scroll(5 * scroll, "units")
        self.scroll_canvas.update_idletasks()

    def _on_canvas_configure(self, event: tk.Event) -> None:
        self.scroll_canvas.itemconfig(self.frame_id, width=event.width)

    def _on_frame_configure(self, _: tk.Event) -> None:
        """Callback for setting scroll region on the canvas"""
        self.scroll_canvas.config(scrollregion=self.scroll_canvas.bbox(tk.ALL))


if __name__ == "__main__":
    try:
        print("Running visualizer...")
        app = AStarVisualizer()
        app.mainloop()

    except Exception as err:
        print(f"Caught an Exception : {err}")

    finally:
        print("Visualizer Exited")
