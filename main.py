import random
from dataclasses import dataclass
from typing import List
from utils import *
from classes import Animal, Creature, Cat
import logic


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
    STRATEGIES = (
        Strategy.RANDOM_SINGLE,
        Strategy.CLOSEST_RUN_AWAY,
        Strategy.ONLY_ONE_RUN_AWAY,
    )
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
            while not logic.game_finished(actors):
                dice_1 = random.choice([GREEN, BLACK])
                dice_2 = random.choice([GREEN, BLACK])
                actors, moves_pool = logic.apply_strategy(actors, strategy, dice_1, dice_2)    
                logger.debug(f"actors - {moves_pool}")
                render_board(actors)
                dump_data(epoch, actors, game_id, strategy)
                epoch += 1
            game_id += 1
            cnt += 1
