from node import Node
import constants


class Cell:
    """
    A class for a cell on the pygame board
    """

    def __init__(
        self,
        x: int,
        y: int,
        node: Node | None = None,
        size=constants.CELL_SIZE,
        is_block=False,
    ) -> None:
        self.x = x
        self.y = y
        self.size = size

        self.is_block = is_block

        self.centre = (x + size / 2, y + size / 2)
        self.node = node
