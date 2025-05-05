import random
from dataclasses import dataclass
from abc import ABCMeta
from enum import Enum, IntEnum
from typing import List, Optional


class Strategy(Enum):
    RANDOM_SINGLE = 0
    RANDOM_MULTIPLE = 1
    CLOSEST_RUN_AWAY = 2
    ONLY_ONE_RUN_AWAY = 3
    DEEP_LEARNING = 77


CAT = 'C'
MICE, SQUIRREL, BIRD = 'M', 'S', 'B'

ANIMALS_START_IDX = 6

NUM_SHORTCUT_MOVES = 4
SHORTCUT_POSITIONS = {
    MICE: ANIMALS_START_IDX + 5,
    SQUIRREL: ANIMALS_START_IDX + 15,
    BIRD: ANIMALS_START_IDX + 25
}

NUM_FIELDS = 50

BLACK = "BLACK"
GREEN = "GREEN"


class GameResult(IntEnum):
    CHASED = -2
    IN_PROGRESS = -1
    FINISHED = NUM_FIELDS  # 0 index is start field, 50th index  (is 50th field that player steps on))


class GameOverfinishedException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


@dataclass
class MovesPool:
    num_cat_moves: int
    num_animal_moves: int


class ShortcutApplied(IntEnum):
    NO = 0
    YES = 1


class Creature(metaclass=ABCMeta):
    def __init__(
        self,
        name: str,
        position: int,
        game_result: GameResult,
        shortcut_position: int
    ):
        super().__init__()
        self.name = name
        self.position = position
        self.game_result = game_result
        self.shortcut_position = shortcut_position
        self._shortcut_applied = ShortcutApplied.NO

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
            "shortcut_applied": self._shortcut_applied
        }


class Cat(Creature):
    def __init__(self, position, game_result):
        super().__init__(CAT, position, game_result, float("nan"))


class Animal(Creature):
    def __init__(self, name, position, game_result, shortcut_position):
        super().__init__(name, position, game_result, shortcut_position)
        self._shortcut_applied = False

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


def dump_data(epoch, actors: List[Creature], game_id: int, strategy: Strategy):
    import datetime
    import csv
    props = ["name", "position", "game_result", "shortcut_position", "shortcut_applied"]
    header = ["epoch", *props, "game_id", "strategy", "timestamp"]
    timestamp = int(datetime.datetime.now().timestamp() * 1000)
    if epoch == -1 and game_id == 0:
        open_arg = 'w'
    else:
        open_arg = 'a'
    with open('results.csv', open_arg, newline='')  as csvfile:
        writer = csv.writer(csvfile)
        if open_arg == 'w':
            writer.writerow(header)
        for actor in actors:
            data = [epoch]
            data += [actor.asdict()[p] for p in props]
            data += [game_id, strategy.name, timestamp]
            writer.writerow(data)


def render_board(actors: List[Animal]):
    board = ['' for _ in range(NUM_FIELDS + 1)]
    for actor in actors:
        if actor.game_result != GameResult.CHASED:
            board[actor.position] += actor.name
        else:
            board[actor.position] += actor.name.lower()
    logger.debug(str(board))


def animal_overfinished(chosen_animal: Animal, num_moves):
    return chosen_animal.position + num_moves > GameResult.FINISHED


def overfinished_logic(actors: List[Animal], animal_moves, chosen_animal_name, num_moves):
    animal_moves[chosen_animal_name] = 1
    num_remaining_animal_moves = num_moves - 1
    animals_for_redraw = [
        actor for actor in actors 
        if actor.name != chosen_animal_name
        and actor.name != CAT
        and actor.game_result not in (GameResult.CHASED, GameResult.FINISHED)
    ]
    if len(animals_for_redraw) > 0:
        chosen_animal_again = random.choice(animals_for_redraw)
        animal_moves[chosen_animal_again.name] = 1
        num_remaining_animal_moves -= 1
        if num_remaining_animal_moves > 0:
            raise NotImplementedError(f"{num_remaining_animal_moves=}")
    return animal_moves


def get_animal_closest_to_cat(cat: Cat, animals_in_game: List[Animal]):
    closest_animal: Optional[Animal] = None
    random.shuffle(animals_in_game)
    for a in animals_in_game:
        if a.name != CAT:
            if closest_animal is None:
                closest_animal = a
            else:
                diff = a.position - cat.position
                if diff > 0 and closest_animal.position - cat.position < diff:
                    closest_animal = a
                else:
                    # TODO: think if it is possible - cat must have "jump over" some animal - is it allowed in the game
                    pass
    return closest_animal


def check_overfinished(chosen_animal: Animal, moves_pool, animal_moves):
    if animal_overfinished(chosen_animal, moves_pool.num_animal_moves):
        animal_moves = overfinished_logic(actors, animal_moves, chosen_animal.name, moves_pool.num_animal_moves)
    else:
        animal_moves[chosen_animal.name] = moves_pool.num_animal_moves    
    return animal_moves


def any_two_animals_on_the_same_position_that_is_not_start(animals_in_game: List[Animal]):
    for a in animals_in_game:
        for a_ in animals_in_game:
            if a != a_:
                if a.position == a_.position and a.position != ANIMALS_START_IDX:
                    return True
    return False


def all_animals_on_start_position(animals_in_game: List[Animal]):
    return all(a.position == ANIMALS_START_IDX for a in animals_in_game)


def get_animal_moves(actors: List[Creature], strategy: Strategy, moves_pool: MovesPool):
    # TODO: do some agent-based deep learning not random xD
    animal_moves = {
        BIRD: 0,
        SQUIRREL: 0,
        MICE: 0
    }
    if moves_pool.num_animal_moves > 0:
        animals_in_game = [actor for actor in actors if actor.name != CAT and actor.game_result == GameResult.IN_PROGRESS]
        if strategy == Strategy.RANDOM_SINGLE:
            chosen_animal = random.choice(animals_in_game)
        elif strategy == Strategy.CLOSEST_RUN_AWAY:
            cat = [a for a in actors if a.name == CAT][0]
            chosen_animal = get_animal_closest_to_cat(cat, animals_in_game)
        elif strategy == Strategy.ONLY_ONE_RUN_AWAY:
            if all_animals_on_start_position(animals_in_game):
                # first epoch
                chosen_animal = random.choice(animals_in_game)
            else:
                if any_two_animals_on_the_same_position_that_is_not_start(animals_in_game):
                    raise ValueError(f"There is no way that applying {strategy=} results in that condition, - either only one left or all left on the board")
                # The one that run the most far is the chosen one - rest stays in place for whole game xD
                chosen_animal = sorted(animals_in_game, key=lambda a: a.position)[-1]
        else:
            raise NotImplementedError(strategy)
        animal_moves = check_overfinished(chosen_animal, moves_pool, animal_moves)
    return animal_moves


def chase(actors: List[Creature]):
    # TODO: chase done only when last cat position is the same as animal position? or intermediate positions do count too?
    cat = [actor for actor in actors if isinstance(actor, Cat)][0]
    for actor in actors:
        if actor.name != CAT:
            if actor.position == cat.position:
                actor.game_result = GameResult.CHASED
    if all([actor.game_result == GameResult.CHASED for actor in actors if not isinstance(actor, Cat)]):
        cat.game_result = GameResult.FINISHED
    return actors


def move(actors: List[Animal], strategy, moves_pool: MovesPool):
    animal_moves = get_animal_moves(
        actors, strategy, moves_pool
    )
    for actor in actors:
        if actor.name == CAT:
            try:
                actor.move(moves_pool.num_cat_moves)
            except GameOverfinishedException:
                pass  # it is ok that cat instead of consuming 2 moves consumes only once since it has finished game 
        else:
            actor.move(animal_moves[actor.name])
    return actors


def get_moves_pool(dice_1, dice_2) -> MovesPool:
    num_cat_moves = 0
    num_animal_moves = 0
    for dice in [dice_1, dice_2]:
        if dice == GREEN:
            num_animal_moves += 1                 
        else:
            num_cat_moves += 1
    return MovesPool(num_cat_moves, num_animal_moves)


def apply_strategy(actors, strategy, dice_1, dice_2):
    moves_pool = get_moves_pool(dice_1, dice_2)
    actors = move(actors, strategy, moves_pool)
    actors = chase(actors)
    return actors, moves_pool


def get_animals_in_game(actors: List[Animal]):
    animals_in_game = []
    for animal in actors:
        if animal.name != CAT:
            if animal.game_result not in (GameResult.CHASED, GameResult.FINISHED):
                animals_in_game.append(animal)
            else:
                pass
    return animals_in_game


def game_finished(actors: List[Animal]):
    animals_chased = all([actor.game_result != GameResult.IN_PROGRESS for actor in actors if actor.name != CAT])
    animals_finished = all([actor.game_result == GameResult.FINISHED for actor in actors if actor.name != CAT])
    cat_finished = all([actor.game_result == GameResult.FINISHED for actor in actors if actor.name == CAT])
    return animals_chased or animals_finished or cat_finished


if __name__ == "__main__":
    NUM_GAMES_PER_STRATEGY = 1000
    import os
    try:
        os.remove("board.log")
    except FileNotFoundError:
        pass

    from loguru import logger
    if NUM_GAMES_PER_STRATEGY > 1:
        logger.remove()  # remove sink that handles writing to terminal window
    logger.add(f"board.log")

    game_id = 0
    STRATEGIES = (Strategy.RANDOM_SINGLE, Strategy.CLOSEST_RUN_AWAY, Strategy.ONLY_ONE_RUN_AWAY)
    for strategy in STRATEGIES:
        cnt = 0
        while cnt < NUM_GAMES_PER_STRATEGY:

            logger.info(f"***********************{game_id=} {strategy=}***********************")
            if cnt % 25 == 0 or game_id == NUM_GAMES_PER_STRATEGY - 1:
                print(f"{cnt+1} / {NUM_GAMES_PER_STRATEGY} - {strategy}")

            actors = [
                Cat(0, GameResult.IN_PROGRESS),
                Animal(MICE,  ANIMALS_START_IDX, GameResult.IN_PROGRESS, SHORTCUT_POSITIONS[MICE]),
                Animal(SQUIRREL,  ANIMALS_START_IDX, GameResult.IN_PROGRESS, SHORTCUT_POSITIONS[SQUIRREL]),
                Animal(BIRD,  ANIMALS_START_IDX, GameResult.IN_PROGRESS, SHORTCUT_POSITIONS[BIRD]),
            ]

            dump_data(-1, actors, game_id, strategy)
            epoch = 0
            while not game_finished(actors):
                dice_1 = random.choice([GREEN, BLACK])
                dice_2 = random.choice([GREEN, BLACK])
                actors, moves_pool = apply_strategy(actors, strategy, dice_1, dice_2)    
                logger.debug(f"actors - {moves_pool}")
                render_board(actors)
                dump_data(epoch, actors, game_id, strategy)
                epoch += 1
            game_id += 1
            cnt += 1
