from enum import Enum, IntEnum


CAT = 'C'
MICE, SQUIRREL, BIRD = 'M', 'S', 'B'

ANIMALS_START_IDX = 6

NUM_SHORTCUT_MOVES = 4
SHORTCUT_POSITIONS = {
    MICE: ANIMALS_START_IDX + 5,
    SQUIRREL: ANIMALS_START_IDX + 15,
    BIRD: ANIMALS_START_IDX + 25
}

BLACK = "BLACK"
GREEN = "GREEN"

NUM_FIELDS = 50


class GameOverfinishedException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class ShortcutApplied(IntEnum):
    NO = 0
    YES = 1


class Strategy(Enum):
    RANDOM_SINGLE = 0
    RANDOM_MULTIPLE = 1
    CLOSEST_RUN_AWAY = 2
    ONLY_ONE_RUN_AWAY = 3
    DEEP_LEARNING = 77


class GameResult(IntEnum):
    CHASED = -2
    IN_PROGRESS = -1
    FINISHED = NUM_FIELDS  # 0 index is start field, 50th index  (is 50th field that player steps on))
