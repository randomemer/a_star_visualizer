from node import Node


def return_path(current_node: Node):
    path = []
    current = current_node
    while current is not None:
        path.append(current.position)
        current = current.parent
    return path[::-1]  # Return reversed path


def interpolated_cell_color(value):
    red = (255, 0, 0)
    green = (0, 255, 0)

    r = int(red[0] * (1 - value) + green[0] * value)
    g = int(red[1] * (1 - value) + green[1] * value)
    b = int(red[2] * (1 - value) + green[2] * value)

    return (r, g, b)
