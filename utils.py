from enum import Enum, IntEnum


CAT = 'C'
MICE, SQUIRREL, BIRD = 'M', 'S', 'B'

ANIMALS_START_IDX = 6

NUM_SHORTCUT_MOVES = 4
SHORTCUT_POSITIONS = [
    {
        MICE: ANIMALS_START_IDX + 5,
        SQUIRREL: ANIMALS_START_IDX + 15,
        BIRD: ANIMALS_START_IDX + 25
    },
    {
        MICE: ANIMALS_START_IDX + 9,
        SQUIRREL: ANIMALS_START_IDX + 19,
        BIRD: ANIMALS_START_IDX + 29
    },
    {
        MICE: ANIMALS_START_IDX + 13,
        SQUIRREL: ANIMALS_START_IDX + 23,
        BIRD: ANIMALS_START_IDX + 33
    },
]

NUM_SNACKS = [
    0,
    3,
    4,
    5,
    6
]

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
    DEEP_Q_NETWORK = 66
    DEEP_REINFORCEMENT_LEARNING = 77


class GameResult(IntEnum):
    CHASED = -2
    IN_PROGRESS = -1
    FINISHED = NUM_FIELDS  # 0 index is start field, 50th index  (is 50th field that player steps on))


class SnacksLogicStrategy(Enum):
    CLOSE_AT_1_FIELD_ANIMAL_IN_FRONT_OF_CAT_PRIORITIZED = 1
    CLOSE_AT_1_FIELD_ANIMAL_AT_BACK_OF_CAT_PRIORITIZED = -1

    SIMPLEST_MOST_INTUITIVE = 0

    CLOSE_AT_2_FIELDS_OR_LESS_ANIMAL_IN_FRONT_OF_CAT_PRIORITIZED = 2
    CLOSE_AT_2_FIELDS_OR_LESS_ANIMAL_AT_BACK_OF_CAT_PRIORITIZED = 2
