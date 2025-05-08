from dataclasses import dataclass
from abc import ABCMeta
from utils import NUM_SNACKS, GameResult, ShortcutApplied, GameOverfinishedException, CAT, NUM_SHORTCUT_MOVES


@dataclass
class MovesPool:
    num_cat_moves: int
    num_animal_moves: int


class Creature(metaclass=ABCMeta):
    def __init__(
        self,
        name: str,
        position: int,
        game_result: GameResult,
        shortcut_position: int,
    ):
        super().__init__()
        self.name = name
        self.position = position
        self.game_result = game_result
        self.shortcut_position = shortcut_position
        self._shortcut_applied = ShortcutApplied.NO
        self._snacks_cnt = None

    def move(self, num_moves):
        self.position += num_moves
        if self.position < GameResult.FINISHED:
            pass  # do nothing special :p
        elif self.position == GameResult.FINISHED:
            self.game_result = GameResult.FINISHED
        else:
            self.position -= 1
            self.game_result = GameResult.FINISHED
            raise GameOverfinishedException("self.position + num_moves < GameResult.FINISHED")
    
    def asdict(self):
        return {
            "name": self.name,
            "position": self.position,
            "game_result": self.game_result,
            "shortcut_position": self.shortcut_position,
            "shortcut_applied": self._shortcut_applied,
            "snacks_cnt": self._snacks_cnt
        }


class Cat(Creature):
    def __init__(self, position, game_result, num_snacks):
        super().__init__(CAT, position, game_result, float("nan"))
        self._snacks_cnt = num_snacks

    def apply_snack(self):
        self._snacks_cnt -= 1
        if self._snacks_cnt < 0:
            raise ValueError("Too much snacks consumed - snacks counter < 0!")


class Animal(Creature):
    def __init__(self, name, position, game_result, shortcut_position):
        super().__init__(name, position, game_result, shortcut_position)
        self._shortcut_applied = False
        self._snacks_cnt = float("nan")

    def _obtain_shortcut_if_applicable(self, num_moves) -> int:
        for num_move in range(1, num_moves + 1):
            if self.position + num_move  == self.shortcut_position:
                self._shortcut_applied = ShortcutApplied.YES
                new_num_moves = num_move  # step into shortcut
                new_num_moves += NUM_SHORTCUT_MOVES  # move through shortcut
                new_num_moves += num_moves - num_move  # move remaining moves
                num_moves = new_num_moves
        return num_moves

    def move(self, num_moves):
        num_moves = self._obtain_shortcut_if_applicable(num_moves)
        return super().move(num_moves)
