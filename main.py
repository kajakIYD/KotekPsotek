import random
from dataclasses import dataclass
from typing import List
from utils import *
from classes import Animal, Creature, Cat
import logic


def dump_data(
        epoch,
        actors: List[Creature],
        game_id: int,
        strategy: Strategy,
        max_num_snacks: int, shortcuts_positions: dict
    ):
    import datetime
    import csv
    props = ["name", "position", "game_result", "shortcut_position", "shortcut_applied", "snacks_cnt"]
    header = ["epoch", *props, "game_id", "strategy", "max_num_snacks", "shortcuts_positions", "timestamp"]
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
            data += [game_id, strategy.name, max_num_snacks, shortcuts_positions, timestamp]
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
    SNACKS_LOGIC_STRATEGIES = [None, SnacksLogicStrategy.SIMPLEST_MOST_INTUITIVE]
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
    for shortcuts_positions in SHORTCUT_POSITIONS:
        for num_snacks in NUM_SNACKS:
            for snacks_logic_strategy in SNACKS_LOGIC_STRATEGIES:
                for strategy in STRATEGIES:
                    if (snacks_logic_strategy is None and num_snacks > 0)  or (snacks_logic_strategy is not None and num_snacks == 0):
                        # Impossible combinations, skip them
                        continue
                    cnt = 0
                    while cnt < NUM_GAMES_PER_STRATEGY:

                        logger.info(f"***********************{game_id=} {strategy=}***********************")
                        if cnt % 25 == 0 or game_id == NUM_GAMES_PER_STRATEGY - 1:
                            print(f"{cnt+1} / {NUM_GAMES_PER_STRATEGY} - {strategy} | {snacks_logic_strategy} | {num_snacks=}")

                        actors = [
                            Cat(0, GameResult.IN_PROGRESS, num_snacks),
                            Animal(MICE,  ANIMALS_START_IDX, GameResult.IN_PROGRESS, shortcuts_positions[MICE]),
                            Animal(SQUIRREL,  ANIMALS_START_IDX, GameResult.IN_PROGRESS, shortcuts_positions[SQUIRREL]),
                            Animal(BIRD,  ANIMALS_START_IDX, GameResult.IN_PROGRESS, shortcuts_positions[BIRD]),
                        ]

                        dump_data(-1, actors, game_id, strategy, num_snacks, shortcuts_positions)
                        epoch = 0
                        while not logic.game_finished(actors):
                            dice_1 = random.choice([GREEN, BLACK])
                            dice_2 = random.choice([GREEN, BLACK])
                            actors, moves_pool = logic.apply_strategy(actors, strategy, snacks_logic_strategy, dice_1, dice_2)    
                            logger.debug(f"actors - {moves_pool}")
                            render_board(actors)
                            dump_data(epoch, actors, game_id, strategy, num_snacks, shortcuts_positions)
                            epoch += 1
                        game_id += 1
                        cnt += 1
