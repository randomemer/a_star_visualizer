import os
import random
from typing import Tuple

import matplotlib.pyplot as plt
import networkx as nx
from PIL import Image, ImageTk


def load_image(file_path: str, dim: Tuple[int, int] | None) -> ImageTk:
    try:
        path = os.path.abspath(file_path)
        image = Image.open(path)

        if dim:
            image = image.resize(dim)

        photo_image = ImageTk.PhotoImage(image)
        return photo_image

    except Exception as e:
        print(f"Error loading image: {e}")
        return None


def generate_graph(
    num_cities: int, min_distance: int, max_distance: int, edge_probability: float
) -> nx.Graph:
    graph = nx.Graph()

    # Create nodes for cities
    cities = [i for i in range(num_cities)]
    graph.add_nodes_from(cities)

    # Create edges with random distances between cities with a certain probability
    for city1 in cities:
        for city2 in cities:
            if city1 != city2 and random.random() < edge_probability:
                distance = random.randint(min_distance, max_distance)
                graph.add_edge(city1, city2, weight=distance)

    return graph


def default_node_val():
    return float("inf")
