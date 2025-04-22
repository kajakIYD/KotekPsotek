import random
from dataclasses import dataclass, asdict
from enum import Enum, IntEnum
from typing import List


CAT = 'C'
MICE, SQUIRREL, BIRD = 'M', 'S', 'B'
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


@dataclass
class Animal:
    name: str
    position: int
    game_result: GameResult

    def move(self, num_moves):
        self.position += num_moves
        if self.position + num_moves < GameResult.FINISHED:
            pass  # do nothing special :p
        elif self.position + num_moves == GameResult.FINISHED:
            self.game_result = GameResult.FINISHED
        else:
            self.position -= 1
            self.game_result = GameResult.FINISHED
            raise GameOverfinishedException("self.position + num_moves < GameResult.FINISHED")


def dump_data(epoch, actors: List[Animal], game_id):
    import datetime
    import csv
    props = ["name", "position", "game_result"]
    header = ["epoch", *props, "game_id", "timestamp"]
    timestamp = int(datetime.datetime.now().timestamp())
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
            data += [asdict(actor)[p] for p in props]
            data += [game_id, timestamp]
            writer.writerow(data)


def render_board(actors: List[Animal]):
    board = ['' for _ in range(NUM_FIELDS)]
    for actor in actors:
        if actor.game_result != GameResult.CHASED:
            board[actor.position] += actor.name
        else:
            board[actor.position] += actor.name.lower()
    logger.debug(str(board))


def animal_overfinished(chosen_animal: Animal, num_moves):
    return chosen_animal.position + num_moves > GameResult.FINISHED
    

class Strategy(Enum):
    RANDOM_SINGLE = 0
    RANDOM_MULTIPLE = 1


def overfinished_logic(actors: List[Animal], animal_moves, chosen_animal_name, num_moves):
    animal_moves[chosen_animal_name] = 1
    num_remaining_animal_moves = num_moves - 1
    animals_for_redraw = [
        actor for actor in actors 
        if actor.name != chosen_animal_name
        and actor.game_result not in (GameResult.CHASED, GameResult.FINISHED)
    ]
    if len(animals_for_redraw) > 0:
        chosen_animal_again = random.choice(animals_for_redraw)
        animal_moves[chosen_animal_again.name] = 1
        num_remaining_animal_moves -= 1
        if num_remaining_animal_moves > 0:
            raise NotImplementedError(f"{num_remaining_animal_moves=}")
    return animal_moves


def get_animal_moves(actors, strategy: Strategy, moves_pool: MovesPool):
    # TODO: do some agent-based deep learning not random xD
    animal_moves = {
        BIRD: 0,
        SQUIRREL: 0,
        MICE: 0
    }
    animals_in_game = [actor for actor in actors if actor.name != CAT and actor.game_result == GameResult.IN_PROGRESS]
    if strategy == Strategy.RANDOM_SINGLE:
        chosen_animal = random.choice(animals_in_game)
        if animal_overfinished(chosen_animal, moves_pool.num_animal_moves):
            animal_moves = overfinished_logic(actors, animal_moves, chosen_animal.name, moves_pool.num_animal_moves)
        else:
            animal_moves[chosen_animal.name] = moves_pool.num_animal_moves    
    else:
        raise NotImplementedError(strategy)
    return animal_moves


def chase(actors: List[Animal]):
    # TODO: chase done only when last cat position is the same as animal position? or intermediate positions do count too?
    cat = [actor for actor in actors if actor.name == CAT][0]
    for actor in actors:
        if actor.name != CAT:
            if actor.position == cat.position:
                actor.game_result = GameResult.CHASED
    return actors


def move(actors: List[Animal], strategy, moves_pool: MovesPool):
    animal_moves = get_animal_moves(
        actors, strategy, moves_pool
    )
    for actor in actors:
        if actor.name == CAT:
            actor.move(moves_pool.num_cat_moves)
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
    NUM_GAMES = 100
    import os
    os.remove("board.log")

    from loguru import logger
    if NUM_GAMES > 0:
        logger.remove()  # remove sink that handles writing to terminal window
    logger.add(f"board.log")

    for game_id in range(NUM_GAMES):
        if game_id % 25 == 0 or game_id == NUM_GAMES - 1:
            print(f"{game_id} / {NUM_GAMES}")
        animals_start_idx = 6

        actors = [
            Animal(CAT, 0, GameResult.IN_PROGRESS),
            Animal(MICE,  animals_start_idx, GameResult.IN_PROGRESS),
            Animal(SQUIRREL,  animals_start_idx, GameResult.IN_PROGRESS),
            Animal(BIRD,  animals_start_idx, GameResult.IN_PROGRESS),
        ]

        strategy = Strategy.RANDOM_SINGLE
        # strategy = "random_multiple"

        dump_data(-1, actors, game_id)
        epoch = 0
        while not game_finished(actors):
            dice_1 = random.choice([GREEN, BLACK])
            dice_2 = random.choice([GREEN, BLACK])
            actors, moves_pool = apply_strategy(actors, strategy, dice_1, dice_2)    
            logger.debug(f"{actors} - {moves_pool}")
            render_board(actors)
            dump_data(epoch, actors, game_id)
            epoch += 1
            