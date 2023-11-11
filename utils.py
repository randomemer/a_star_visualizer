import random
from typing import Any

import matplotlib.pyplot as plt
import networkx as nx


def interpolated_cell_color(value):
    red = (255, 0, 0)
    green = (0, 255, 0)

    r = int(red[0] * (1 - value) + green[0] * value)
    g = int(red[1] * (1 - value) + green[1] * value)
    b = int(red[2] * (1 - value) + green[2] * value)

    return (r, g, b)


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
