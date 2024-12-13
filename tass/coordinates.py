import random
from dataclasses import dataclass
from typing import Self


@dataclass
class Coordinates:
    start_x: int
    end_x: int
    start_y: int
    end_y: int

    @classmethod
    def new(cls) -> Self:
        start_x = random.randint(200, 300)
        start_y = random.randint(300, 400)
        end_x = start_x + random.randint(1, 10)
        end_y = start_y + random.randint(50, 100)
        return cls(start_x=start_x, end_x=end_x, start_y=start_y, end_y=end_y)
