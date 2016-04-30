import random
from math import ceil, floor
from time import sleep

import pyokemans as pk


def strategy_run(attacker, defender):
    """Running away has a flat 75% chance of success,
    although obviously we could change that here.
    """
    if random.randint(0, 4) >= 3:
        # 75% chance
        print("Got away safely!")
        return True
    else:
        print("Can't escape!")
        # The attacker attacks!
        strategy_attack(attacker, defender)
        return False


def strategy_attack(attacker, defender, move=None):
    """Handles an attack.
    """
    if not move:
        # Choose a random move
        move = attacker.random_move()
    # Reduce move's PP by one
    move.pp -= 1

    print("\n{} used {}!".format(attacker.name, move.name))
    
    # Calculate whether it hit or not. This just seemed like it worked OK.
    hit_chance = random.expovariate(defender.speed / attacker.speed)
    if hit_chance < 0.25:
        print("{}'s {} missed!".format(attacker.name, move.name))
        return False

    # Get the effectiveness, if any
    damage_multiplier = pk.pktypes[move.pktype].get(defender.pktype, 1)
    if damage_multiplier == 2:
        status = 'supereffective'
    elif damage_multiplier == 0.5:
        status = 'ineffective'
    else:
        status = 'a hit'

    # Same-type attack bonus: Add an extra third to the multiplier if the attacker is
    # using a move of their own type.
    if move.pktype == attacker.pktype:
        damage_multiplier += 0.33
        
    # Calculate the damage:
    # We take the ceiling (smallest integer greater than the value)
    # of a random integer between 0 and the attacker's attack score
    # plus the power of the move itself
    # times the damage multiplier
    # divided by the defender's defense score.
    damage = ceil(
            (random.randint(floor(attacker.attack/2), attacker.attack) + move.power) *
            (damage_multiplier / defender.defense)
            )
    
    # Take that amount off the defender's hit points.
    defender.hp -= damage

    print("It's {}! Does {} damage!".format(status, damage))
    if defender.hp == 0:
        # If they faint, return True
        # TODO this is probably a bad idea and we should return something
        # more useful or meaningful
        return True
    else:
        return False


def fight_round(p1, p2, p1move=None, p2move=None):
    """
    Handles one fight turn.
    Returns whoever faints first, or None.
    """
    # Pick a random move if either one was not specified.
    if not p1move:
        p1move = p1.random_move()
    if not p2move:
        p2move = p2.random_move()

    # Given p1 and p2, pick one who attacks first.
    # Random integer between 0 and 10 plus their speed.
    p1sp = random.randint(0, 10) + p1.speed
    p2sp = random.randint(0, 10) + p2.speed
    
    if p1sp > p2sp:
        # Recall that strategy_attack returns True if the defender faints.
        # We return the object of the defender if they do faint.
        if strategy_attack(p1, p2, move=p1move):
            return p2
        if strategy_attack(p2, p1, move=p2move):
            return p1
    else:
        if strategy_attack(p2, p1, move=p2move):
            return p1
        if strategy_attack(p1, p2, move=p1move):
            return p2
    # If no one faints, we return None.
    return None


def strategy_switch(trainer):
    """Handles switching out the active pyokemon, whether as a move or due to a fainting"""
    # Get all pokemon with hitpoints
    valid_pkmn = [pk for pk in trainer.roster if pk.hp > 0]
    # If there are none, return None
    if valid_pkmn == []:
        return None
    
    print("Choose a pyokemon to send out!")
    choices = enumerate(valid_pkmn)

    def list_pkmn():
        for idx, pkmn in choices:
            print("\t{}) {}: species {}, type {}, {} HP remaining"
                  .format(idx+1, pkmn.name, pkmn.species, pkmn.pktype, pkmn.hp))

    list_pkmn()
    pkmn_choice = input("Enter number for your choice, or 'list' to see your choices> ")
    new_pkmn = None
    while not new_pkmn:
        if not (pkmn_choice.isdigit() and len(pkmn_choice) == 1):
            if pkmn_choice == 'list':
                list_pkmn()
            else:
                print("Sorry, that's not a valid choice.")
        else:
            try:
                new_pkmn = valid_pkmn[int(pkmn_choice) - 1]
                break
            except IndexError:
                print("Sorry, that's not a valid choice")
        pkmn_choice = input("Enter number for your choice, or 'list' to see your choices> ")
    return new_pkmn


def choose_move(valid_moves):
    if valid_moves == []:
        print("No moves left!")
        return pk.Struggle

    print("Choose a move!")
    choices_moves = enumerate(valid_moves)

    def list_moves():
        for idx, mv in choices_moves:
            print("\t{}) {}: type {}, power {}, remaining move points: {}"
                  .format(idx + 1, mv.name, mv.pktype, mv.power, mv.pp))

    list_moves()
    move_choice = input("Enter number of move, or 'list' to see your choices> ")
    move = None
    while not move:
        if not (move_choice.isdigit() and len(move_choice) == 1):
            if move_choice == 'list':
                list_moves()
            else:
                print("Sorry, that's not a move.")
        else:
            try:
                move = valid_moves[int(move_choice) - 1]
                break
            except IndexError:
                print("Sorry, that's not a move.")

        move_choice = input("Enter number of move, or 'list' to see your choices> ")

    return move


def strategy_capture(wild_pkmn, trainer):
    # Chance is directly tied to the wild pokemon's current HP.
    # If they are at full strength, catching them is impossible.
    # If they are at 75%, the chance is 25%.
    chance = (1 - (wild_pkmn.hp / wild_pkmn.max_hp))
    print("Chance: {}".format(chance))
    roll = random.random()
    print("Rolled: {}".format(roll))
    if roll <= chance:
        print("Wild {} was caught!".format(wild_pkmn.name))
        if len(trainer.roster) < 6:
            wild_pkmn.heal()
            nickname = input("What would you like to call your new {}?> ".format(wild_pkmn.name))
            wild_pkmn.nickname = nickname
            trainer.add_pkmn(wild_pkmn)
            return True
        else:
            # If they already have 6 pyokemon, they just go away. We throw an error to make sure they know why.
            raise pk.TooManyPyokemans("You already have 6! Too bad.")
    else:
        return False


def wild_battle(trainer):
    """
    Plays out a battle with a random wild pyokemon.
    """
    # Choose a wild pokemon from our extras.
    wild_pyokemon_species = random.choice([pk.Diglett, pk.Pidgey, pk.Pikachu])
    # Level between 2 and 10
    wild_level = random.randint(2, 10)
    # Actually create the wild pyokemon object at the level chosen.
    wild_pkmn = wild_pyokemon_species(wild_level)

    print("A wild {} appeared!".format(wild_pkmn.name))
    roster = [pkmn for pkmn in trainer.roster if pkmn.hp > 0]

    try:
        trainer_pkmn = roster[0]
    except IndexError:
        print("You have no healthy pyokemon! Go to a pyokemon center and heal your team.")
        return

    print("Go, {}!".format(trainer_pkmn.name))
    # Should go on forever, until we return.
    while True:

        print("\nRun, fight, capture, switch, or status?")
        strategy = input("> ").lower()
        while strategy not in ['run', 'fight', 'capture', 'status', 'switch']:
            print("Sorry, invalid move.",
                  "Please type either 'run', 'fight', 'capture', 'switch', or 'status'.")
            strategy = input("> ").lower()

        if strategy == 'run':
            if strategy_run(wild_pkmn, trainer_pkmn):
                # We succeeded! We break out of the while loop and exit the function.
                break

        elif strategy == 'capture':
            if strategy_capture(wild_pkmn, trainer):
                break
            else:
                print("Capture failed!")
                strategy_attack(wild_pkmn, trainer_pkmn)

        elif strategy == 'switch':
            new_pkmn = strategy_switch(trainer)
            if new_pkmn == trainer_pkmn:
                print("{} is already out!".format(new_pkmn.name))
                # Continue restarts the loop from the top
                continue
            else:
                # Replace trainer
                trainer_pkmn = new_pkmn
                print("Go, {}!".format(trainer_pkmn.name))
                strategy_attack(wild_pkmn, trainer_pkmn)

        elif strategy == 'status':
            print("Your level {} {} has {} HP remaining.".format(trainer_pkmn.level, trainer_pkmn.name, trainer_pkmn.hp))
            print("The wild level {} {} has {} HP remaining.".format(wild_pkmn.level, wild_pkmn.name, wild_pkmn.hp))
            continue

        elif strategy == 'fight':
            valid_moves = [move for move in trainer_pkmn.moves if move.pp > 0]
            move = choose_move(valid_moves)

            fainter = fight_round(trainer_pkmn, wild_pkmn, p1move=move)
            if fainter:
                print("{} fainted!".format(fainter.name))

        # Strategy ends here. If a branch doesn't contain a "break" or "continue", they end up here.
        if trainer_pkmn.hp == 0:
            new_pkmn = strategy_switch(trainer)
            if new_pkmn:
                trainer_pkmn = new_pkmn
                print("Go, {}!".format(trainer_pkmn.name))
            else:
                print("You have no healthy pyokemon!",
                      "Go to a pyokemon center and heal your team.")
                break

        if wild_pkmn.hp == 0:
            # Give an XP bonus equal to ten times the level.
            oldl = trainer_pkmn.level
            xpgain = wild_pkmn.level * 10
            print("{} gained {} XP!".format(trainer_pkmn.name, xpgain))
            trainer_pkmn.xp += xpgain
            if trainer_pkmn.level > oldl:
                print("{} is now level {}!".format(trainer_pkmn.name, trainer_pkmn.level))
            break

def pyokemon_center(trainer):
    """
    Pyokemon center. Heals your entire roster and restores the PP of all their moves.
    Also, contains a suprise egg.
    """
    def _pyokemon_center(trainer):
        print("Hello! Welcome to the Pyokemon Center! We'll heal your pyokemons up good.")
        for pkmn in trainer.roster:
            for _ in range(0, 5):
                print('.', end="", flush=True)
                sleep(0.2)
            pkmn.heal()
            print("\nYour {} is feeling much better now!\n".format(pkmn.name))
        print("You're good to go! Have fun!")
    
    def _deutschen_pyokemon_center(trainer):
        print("You walk into the Pyokemon Center. For some reason, everyone here is german.")
        print("-"*80)
        print("GUTEN TAG! WILKOMMEN TO DAS PYOKEMONZENTRUM")
        for pkmn in trainer.roster:
            for _ in range(0, 5):
                print('.', end="", flush=True)
                sleep(0.2)
            pkmn.heal()
            print("\nYOUR {} IS FEELING ITSELF MUCH BESSER NOW\n".format(pkmn.name))
        print("ALLE DEINE POKEMON SIND SEHR GUT. TSCHAÜ!")

    if random.random() <= 0.1:
        _deutschen_pyokemon_center(trainer)
    else:
        _pyokemon_center(trainer)
