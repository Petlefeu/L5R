#!/usr/bin/python
#-*- coding: utf-8 -*-
""" Lance de des
VERSION 1.1.0 """

# from pdb import set_trace as st
from random import randint
import sys

def launch_dices(dices_launch, dices_keep, void):
    """ Fonction qui lance les dés """
    dices = []
    void_left = void
    for i in range(dices_launch):
        result = randint(1, 10)
        dices.append(result)
        while result == 10 and void_left > 0:
            void_left -= 1
            result = randint(1, 10)
            dices[i] += result
    dices.sort()
    print dices[(dices_launch-dices_keep):]
    return sum(dices[(dices_launch-dices_keep):])

def usage():
    """ Aide """
    print '%s <dés lancés> <dés gardés> <points de vide>' % sys.argv[0]
    sys.exit(1)

try:
    print launch_dices(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
except IndexError:
    usage()
