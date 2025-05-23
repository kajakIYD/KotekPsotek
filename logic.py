from typing import List, Optional
from classes import Animal, Creature, Cat, MovesPool
from utils import GREEN, GameOverfinishedException, GameResult, CAT, ANIMALS_START_IDX, BIRD, SQUIRREL, MICE, Strategy
import random



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
    if len(animals_in_game) == 1:
        closest_animal = animals_in_game[0]
    else:
        for a in animals_in_game:
            if a.name != CAT:
                if closest_animal is None:
                    closest_animal = a
                else:
                    diff = a.position - cat.position
                    if 0 < diff < closest_animal.position - cat.position:
                        closest_animal = a
                    else:
                        # TODO: think if it is possible - cat must have "jump over" some animal - is it allowed in the game
                        pass
    return closest_animal


def check_overfinished(actors: List[Creature], chosen_animal: Animal, moves_pool, animal_moves):
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
        animal_moves = check_overfinished(actors, chosen_animal, moves_pool, animal_moves)
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

def snacks_logic(actors: List[Creature], snacks_logic_strategy: str = "close_at_2_fields_or_less"):
    cat: Cat = [c for c in actors if c.name == CAT][0]
    distance_to_cat = {}
    if snacks_logic_strategy == "close_at_2_fields_or_less":
        for a in actors:
            if a.name != CAT:
                distance = a.position - cat.position
                if -2 <= distance <= 2:  # <= 2 to prevent situation, when animal will go on field with cat (cat is further than animal - is it even possible?)
                    cat.apply_snack()
                    break
    else:
        raise NotImplementedError(f"{snacks_logic_strategy=} not implemented")
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
    actors = snacks_logic(actors)
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