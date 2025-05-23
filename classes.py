from dataclasses import dataclass
from abc import ABCMeta, abstractmethod
from typing import Dict, List, Union
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
        shortcut_positions: List[int],
    ):
        super().__init__()
        self.name = name
        self.position = position
        self.game_result = game_result
        self.shortcut_positions = shortcut_positions
        self._shortcut_applied = ShortcutApplied.NO
        self._snacks_cnt = None

    def move(self, num_moves):
        num_moves = self._obtain_shortcut_if_applicable(num_moves)
        self.position += num_moves
        if self.position < GameResult.FINISHED:
            pass  # do nothing special :p
        elif self.position == GameResult.FINISHED:
            self.game_result = GameResult.FINISHED
        else:
            self.position -= 1
            self.game_result = GameResult.FINISHED
            raise GameOverfinishedException("self.position + num_moves < GameResult.FINISHED")
    
    @abstractmethod
    def _obtain_shortcut_if_applicable(self, num_moves) -> int:
        raise NotImplementedError("_obtain_shortcut_if_applicable")

    def asdict(self):
        return {
            "name": self.name,
            "position": self.position,
            "game_result": self.game_result,
            "shortcut_position": self.shortcut_positions,
            "shortcut_applied": self._shortcut_applied,
            "snacks_cnt": self._snacks_cnt
        }


class Cat(Creature):
    def __init__(self, position, game_result, num_snacks, shortcuts_positions: Dict[str, int]):
        _shortcuts_positions = [v for k, v in shortcuts_positions.items()]
        super().__init__(CAT, position, game_result, _shortcuts_positions)
        self._snacks_cnt = num_snacks
        self._shortcuts_applied = [ShortcutApplied.NO for _ in self.shortcut_positions]

    def _obtain_shortcut_if_applicable(self, num_moves) -> int:
        for num_move in range(1, num_moves + 1):
            for idx, s_p in enumerate(self.shortcut_positions):
                if self.position + num_move == s_p:
                    self._shortcuts_applied[idx] = ShortcutApplied.YES
                    new_num_moves = num_move  # step into shortcut
                    new_num_moves += NUM_SHORTCUT_MOVES  # move through shortcut
                    new_num_moves += num_moves - num_move  # move remaining moves
                    num_moves = new_num_moves
                    break
        return num_moves
        

    def apply_snack(self):
        self._snacks_cnt -= 1
        if self._snacks_cnt < 0:
            return False
        else:
            self.position = 0
            return True


class Animal(Creature):
    def __init__(self, name, position, game_result, shortcut_position: int):
        assert isinstance(shortcut_position, int), "Animal has only one shortcut"
        super().__init__(name, position, game_result, [shortcut_position])
        self._shortcut_applied = False
        self._snacks_cnt = float("nan")

    def _obtain_shortcut_if_applicable(self, num_moves) -> int:
        shortcut_position = self.shortcut_positions[0]
        for num_move in range(1, num_moves + 1):
            if self.position + num_move  == shortcut_position:
                self._shortcut_applied = ShortcutApplied.YES
                new_num_moves = num_move  # step into shortcut
                new_num_moves += NUM_SHORTCUT_MOVES  # move through shortcut
                new_num_moves += num_moves - num_move  # move remaining moves -> TODO: it is not always the case, that we want to move same animal after shortcut (what if cat is there?)
                num_moves = new_num_moves
        return num_moves
