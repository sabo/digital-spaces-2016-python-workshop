"""
Library for the Pyokemon example. This file contains the classes for Move, Pyokemon, and Trainers, 
"""
import copy
import random

from math import ceil, floor
# Python 3.5 has an 'inf' in the math module, which has the property
# inf > n == True for all n. Basically infinity.
# Unfortunatly, most people are still on 2.7 or 3.4, so we use maxsize as
# a standin. Think "practically infinite".
from sys import maxsize

# The keys are the type of attack. The values are dictionaries,
# where the keys are the defending type
# and the values are the effectiveness coefficient.
pktypes = {
           "Fire": {"Water": 0.5, "Ground": 0.5, "Grass": 2},
           "Water": {"Grass": 0.5, "Electric": 0.5, "Fire": 2},
           "Grass": {"Fire": 0.5, "Flying": 0.5, "Water": 2},
           "Ground": {"Flying": 0.5, "Electric": 2, "Fire": 2},
           "Flying": {"Electric": 0.5, "Ground": 2, "Grass": 2},
           "Electric": {"Ground": 0.5, "Flying": 2, "Water": 2},
           "Normal": {}  # Multiplier of 1 for everybody
          }


class Move(object):
    """
    Represents and validates a move.
    
    :param name: The name of the move
 
    """
    def __init__(self, name, pktype, power, pp):
        self.name = name
        self.power = power
        self._max_pp = self._pp = pp
        if pktype not in pktypes.keys():
            raise TypeError("Invalid move type")
        else:
            self.pktype = pktype

    @property
    def pp(self): return self._pp

    @pp.setter
    def pp(self, newpp):
        self._pp = newpp
        if self._pp < 0:
            self._pp = 0

    def restore_pp(self):
        self._pp = self._max_pp

Tackle = Move("Tackle", "Normal", 10, 20)
Struggle = Move("Struggle", "Normal", 1, maxsize)
Splash = Move("Splash", "Water", 10, 10)
Ember = Move("Ember", "Fire", 10, 10)
VineWhip = Move("Vine Whip", "Grass", 10, 10)
Earthquake = Move("Earthquake", "Ground", 15, 5)
Gust = Move("Gust", "Flying", 15, 5)
Shock = Move("Shock", "Electric", 15, 5)


class Pyokemon(object):
    """
    The class that all Pyokemans derive from.
    """
    def __init__(self, max_hp=0, attack=0, defense=0, speed=0, level=None):
        self._species = None
        self._nickname = None
        self._pktype = None
        self._xp = 0
        self._max_hp = max_hp
        self._level = level
        self._attack = attack
        self._defense = defense
        self._speed = speed
        self._moves = []
        for _ in range(level):
            self.levelup()
        self._hp = self._max_hp

    # (SEMI-)PRIVATE PROPERTIES
    # Unlike, say, Java or Golang, Python does not have a concept of a "private" property for its objects and modules.
    # By convention, properties, objects, and functions with an underscore (_) at the beginning of their names are treated
    # as private, but this is only a convention -- nothing stops a programmer from defying that
    # convention and directly changing those values.
    
    # To get something that works kind of like a private property, we can take advantage of Python's 
    # property decorator. This allows us to override the 'setter' behavior. Here, we set the setters of
    # properties that should remain static to be no-ops.
    @property
    def species(self): return self._species

    @species.setter
    # This intentionally does nothing.
    def species(self, _): pass

    @property
    def pktype(self): return self._pktype

    @pktype.setter
    def pktype(self, _): pass

    @property
    def attack(self): return self._attack

    @attack.setter
    def attack(self, _): pass

    @property
    def defense(self): return self._defense

    @defense.setter
    def defense(self, _): pass

    @property
    def speed(self): return self._speed

    @speed.setter
    def speed(self, _): pass

    @property
    def level(self): return self._level

    @level.setter
    def level(self, _): pass

    @property
    def moves(self): return self._moves

    @moves.setter
    def moves(self, _): pass

    @property
    def max_hp(self): return self._max_hp

    @max_hp.setter
    def max_hp(self, _): pass

    # MUTABLE PROPERTIES
    # We can use the same idiom as above to enforce certain bounds on the values we accept,
    # or trigger other behavior once certain conditions are met.
    # Again, nothing stops a programmer from manually setting, say, _xp; this is just for convenience.

    @property
    def xp(self): return self._xp

    @xp.setter
    def xp(self, xp):
        self._xp = xp
        while self._xp >= self._level * 100:
            self._xp -= (self._level * 100)
            self.levelup()

    @property
    def hp(self): return self._hp

    @hp.setter
    def hp(self, hp):
        """
        Makes sure hp is never greater than _max_hp, or less than 0
        """
        self._hp = hp
        if self._hp < 0:
            self._hp = 0
        elif self._hp > self._max_hp:
            self._hp = self._max_hp

    @property
    def nickname(self): return self._nickname

    @nickname.setter
    def nickname(self, n):
        self._nickname = n

    @property
    def name(self):
        if self._nickname:
            return self._nickname
        else:
            return self._species

    # General methods.
    def levelup(self):
        """Increments a pokemon's level by one."""
        if self._level < 100:
            self._level += 1
            self._attack = ceil((self._attack + 2)*0.99)
            self._speed = ceil((self._speed + 2)*0.99)
            self._defense = ceil((self._defense + 2) * 0.99)
            self._max_hp = min(200, self._max_hp + floor(self._max_hp * 0.1))

    def heal(self):
        """Fully heals a pyokemon and restores the PP of all its moves."""
        self._hp = self._max_hp
        for move in self._moves:
            move.restore_pp()

    def learn(self, move):
        """Teaches a pyokemon a move."""
        if not isinstance(move, Move):
            raise TypeError("Can't teach something that isn't a move")
        if len(self._moves) >= 5:
            raise ValueError("I already know 4 moves. Delete one move first.")
        else:
            self._moves.append(copy.copy(move))

    def forget(self, move_name):
        for move in self._moves:
            if move.name == move_name:
                self._moves.remove(move)
        else:
            raise KeyError("I don't know any move called {}!".format(move_name))

    def random_move(self):
        # Returns a random move that this pokemon knows.
        moves = [m for m in self._moves if m.pp > 0]
        if len(moves) == 0:
            return Struggle
        else:
            return random.choice(moves)


class Charmander(Pyokemon):
    def __init__(self, level):
        super().__init__(max_hp=10, attack=1, defense=1, speed=2, level=level)
        self._species = "Charmander"
        self._pktype = "Fire"
        self.learn(Tackle)
        self.learn(Ember)


class Squirtle(Pyokemon):
    def __init__(self, level):
        super().__init__(max_hp=10, attack=1, defense=2, speed=1, level=level)
        self._species = "Squirtle"
        self._pktype = "Water"
        self.learn(Tackle)
        self.learn(Splash)


class Bulbasaur(Pyokemon):
    def __init__(self, level):
        super().__init__(max_hp=10, attack=2, defense=1, speed=1, level=level)
        self._species = "Bulbasaur"
        self._pktype = "Grass"
        self.learn(Tackle)
        self.learn(VineWhip)


class Diglett(Pyokemon):
    def __init__(self, level):
        super().__init__(max_hp=15, attack=2, defense=2, speed=1, level=level)
        self._species = "Diglett"
        self._pktype = "Ground"
        self.learn(Tackle)
        self.learn(Earthquake)


class Pidgey(Pyokemon):
    def __init__(self, level):
        super().__init__(max_hp=15, attack=1, defense=2, speed=2, level=level)
        self._species = "Pidgey"
        self._pktype = "Flying"
        self.learn(Tackle)
        self.learn(Gust)


class Pikachu(Pyokemon):
    def __init__(self, level):
        super().__init__(max_hp=15, attack=2, defense=1, speed=2, level=level)
        self._species = "Pikachu"
        self._pktype = "Electric"
        self.learn(Tackle)
        self.learn(Shock)


class TooManyPyokemans(Exception):
    """
    This is an example of a custom exception. When something unexpected or
    incorrect occurs within a program, such as attempting to write to a file
    that doesn't exist or a network connection error, the program may raise
    an exception.
    You can think of this as kinda like raising an objection in court. If
    something out-of-bounds occurs in questioning a witness, the lawyer
    raises an objection, which a higher authority (the judge) is forced to
    consider. Likewise, when a subroutine in a program encounters some
    out-of-bounds behavior, it raises an exception, which an authority 'above'
    it (whether that's some other part of the program or the user) must
    respond to."""
    pass


class Trainer(object):
    """Class for trainers/players"""
    def __init__(self, name):
        self._name = name
        self._roster = []

    @classmethod
    def interview(cls):
        name = input("What is your name?> ")
        t = cls(name)
        print("-" * 80)
        print("\nHello there {}! Welcome to Pyokemon: The Text Adventure!".format(t.name))
        # Get the user's choice for their starter pyokemon.
        print("It's dangerous to go alone! Choose a starter pyokemon.\n" +
              "Your choices are:\n",
              "\t1) Charmander, a Fire-type pyokemon\n",
              "\t2) Squirtle, a Water-type pyokemon\n",
              "\t3) Bulbasaur, a Grass-type pyokemon\n")
        starter = input("Type the number for your choice> ")
        # If it was an invalid choice -- if it wasn't a digit or was too long -- correct
        while not (starter.isdigit() and len(starter) == 1):
            print("Sorry, \"{}\" is not a valid choice. Try again.".format(starter))
            starter = input("Type the number for your choice> ")

        # Process their choice
        pkmn_choice = {
                1: Charmander,
                2: Squirtle,
                3: Bulbasaur}[int(starter)]
        pkmn = pkmn_choice(5)
        # Ask for the nickname
        nickname = input("What would you like to name your {}?> ".format(pkmn.name))
        pkmn.nickname = nickname

        # Add it to the user's roster.
        t.add_pkmn(pkmn)
        # Return the user
        print("You're all set. Now go on out there and catch some pyokemon.")
        return t

    @property
    def name(self):
        return self._name

    @property
    def roster(self):
        return self._roster

    def add_pkmn(self, pkmn):
        if not isinstance(pkmn, Pyokemon):
            raise TypeError("Tried to add something that isn't a pyokemon to your roster!")
        elif len(self._roster) >= 6:
            raise TooManyPyokemans("You've already got a full roster!")

        if pkmn in self._roster:
            raise TooManyPyokemans("That there {} is already in your roster!".format(pkmn.name))

        self._roster.append(pkmn)
