import heapq

import pygame
from pygame_button import Button

import constants
import utils
from cell import Cell
from node import Node


class AStarVisualizer:
    running = True
    search_status = "idle"
    interval = 500  # Interval of 250 ms between each step

    def __init__(
        self, screen: pygame.Surface, maze: list[list[int]], allow_diagonal=False
    ) -> None:
        self.screen = screen
        self.clock = pygame.time.Clock()

        self.maze = maze

        # Adding a stop condition
        self.outer_iterations = 0
        self.max_iterations = len(self.maze[0]) * len(self.maze) // 2

        # what squares do we search
        self.directions = (
            constants.DIAGONAL_SQUARES if allow_diagonal else constants.ADJACENT_SQUARES
        )

    def start(self) -> None:
        updated_at = pygame.time.get_ticks()
        self.search_status = "searching"

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Starting path finding
            cur_time = pygame.time.get_ticks()

            if (
                self.search_status == "searching"
                and cur_time - updated_at >= self.interval
            ):
                self.search_status = self.next()
                updated_at = cur_time

            self.draw_maze()
            pygame.display.flip()

            self.clock.tick(60)

    def setup_maze(self):
        start = (0, 0)
        end = (len(self.maze) - 1, len(self.maze[0]) - 1)

        # Create start and end node
        start_node = Node(None, start)
        start_node.g = start_node.h = start_node.f = 0
        end_node = Node(None, end)
        end_node.g = end_node.h = end_node.f = 0

        self.start_node = start_node
        self.end_node = end_node

        # Initialize both open and closed list
        self.open_list = []
        self.closed_list = []

        # Heapify the open_list and Add the start node
        heapq.heapify(self.open_list)
        heapq.heappush(self.open_list, start_node)

        # Construct a board of cells for pygame
        self.cells: list[list[Cell]] = []

        w = constants.CELL_SIZE * len(self.maze[0])
        h = constants.CELL_SIZE * len(self.maze)
        x_offset = (self.screen.get_width() - w) / 2
        y_offset = (self.screen.get_height() - h) / 2

        for i in range(len(self.maze)):
            cell_row = []
            for j in range(len(self.maze[0])):
                cell = Cell(
                    x=x_offset + j * constants.CELL_SIZE,
                    y=y_offset + i * constants.CELL_SIZE,
                    is_block=bool(self.maze[i][j]),
                )
                cell_row.append(cell)

            self.cells.append(cell_row)

    def draw_maze(self):
        self.screen.fill(constants.BACKGROUND)

        for row in self.cells:
            for cell in row:
                color = constants.WALL_CELL if cell.is_block else constants.EMPTY_CELL

                pygame.draw.rect(
                    self.screen,
                    color,
                    (cell.x, cell.y, constants.CELL_SIZE, constants.CELL_SIZE),
                )

                if cell.node:
                    pygame.draw.circle(
                        self.screen,
                        utils.interpolated_cell_color(
                            self.cur_distance(cell.node) / self.max_distance()
                        ),
                        cell.centre,
                        constants.CELL_CIRCLE_SIZE / 2,
                    )

        # Draw shortest path if search completed
        if self.search_status == "completed":
            cur = self.get_cell_from_node(self.end_node)
            while cur.node.parent:
                parent = self.get_cell_from_node(cur.node.parent)
                pygame.draw.line(self.screen, "black", cur.centre, parent.centre, 3)
                cur = parent

    def on_play_btn_click(self):
        self.search_status = "paused"

    def next(self) -> str:
        if len(self.open_list) == 0:
            return "failed"

        self.outer_iterations += 1

        if self.outer_iterations > self.max_iterations:
            # if we hit this point return the path such as it is
            # it will not contain the destination
            print("Giving up on pathfinding too many iterations")
            return "failed"

        # Get the current node
        current_node = heapq.heappop(self.open_list)
        self.closed_list.append(current_node)

        # Ref to board cell
        x, y = current_node.position
        self.cells[x][y].node = current_node

        # Found the goal
        if current_node == self.end_node:
            return "completed"

        # Generate children
        children = []

        for new_position in self.directions:  # Adjacent squares
            # Get node position
            node_position = (
                current_node.position[0] + new_position[0],
                current_node.position[1] + new_position[1],
            )

            # Make sure within range
            if (
                node_position[0] > (len(self.maze) - 1)
                or node_position[0] < 0
                or node_position[1] > (len(self.maze[len(self.maze) - 1]) - 1)
                or node_position[1] < 0
            ):
                continue

            # Make sure walkable terrain
            if self.maze[node_position[0]][node_position[1]] != 0:
                continue

            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:
            # Child is on the closed list
            if (
                len(
                    [
                        closed_child
                        for closed_child in self.closed_list
                        if closed_child == child
                    ]
                )
                > 0
            ):
                continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.position[0] - self.end_node.position[0]) ** 2) + (
                (child.position[1] - self.end_node.position[1]) ** 2
            )
            child.f = child.g + child.h

            # Child is already in the open list
            if (
                len(
                    [
                        open_node
                        for open_node in self.open_list
                        if child.position == open_node.position
                        and child.g > open_node.g
                    ]
                )
                > 0
            ):
                continue

            # Add the child to the open list
            heapq.heappush(self.open_list, child)

        return "searching"

    def get_cell_from_node(self, node: Node) -> Cell:
        i, j = node.position
        return self.cells[i][j]

    def cur_distance(self, node: Node):
        a, b = self.start_node.position
        x, y = node.position
        return (a - x) ** 2 + (b - y) ** 2

    def max_distance(self):
        a, b = self.start_node.position
        x, y = self.end_node.position

        return (a - x) ** 2 + (b - y) ** 2


if __name__ == "__main__":
    try:
        print("Init pygame...")
        pygame.init()
        screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("A* Algorithm Visualizer")

        print("Running visualizer...")
        obj = AStarVisualizer(screen, constants.MAZE)

        obj.setup_maze()
        obj.start()

    except Exception as err:
        print(f"Caught an Exception : {err}")

    finally:
        pygame.quit()
