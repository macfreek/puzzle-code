#!/usr/bin/env python3

"""
Grime dice.
https://singingbanana.com/dice/article.htm

Calculate the changes that one 
"""

from itertools import combinations, product
from collections import defaultdict

# Define available colours
dice_values = {
    "Red": [4, 4, 4, 4, 4, 9],
    "Yellow": [3, 3, 3, 3, 8, 8],
    "Blue": [2, 2, 2, 7, 7, 7],
    "Magenta": [1, 1, 6, 6, 6, 6],
    "Olive": [0, 5, 5, 5, 5, 5],
}

def single_dice_winning_chance(dice1, dice2):
    win1_count = 0
    win2_count = 0
    total_count = len(dice1) * len(dice2)
    for role1 in dice1:
        for role2 in dice2:
            if role1 > role2:
                win1_count += 1
            elif role2 > role1:
                win2_count += 1
    return win1_count/total_count, win2_count/total_count

def double_dice_winning_chance(dice1, dice2):
    win1_count = 0
    win2_count = 0
    double_dice1 = defaultdict(int)
    double_dice2 = defaultdict(int)
    total_count = len(dice1) * len(dice2) * len(dice1) * len(dice2)
    for role1, role2 in product(dice1, repeat=2):
        double_dice1[role1+role2] += 1
    for role1, role2 in product(dice2, repeat=2):
        double_dice2[role1+role2] += 1
    for role1 in double_dice1:
        for role2 in double_dice2:
            if role1 > role2:
                win1_count += (double_dice1[role1] * double_dice2[role2])
            elif role2 > role1:
                win2_count += (double_dice1[role1] * double_dice2[role2])
    return win1_count/total_count, win2_count/total_count

def print_single_dice():
    print("Single dice")
    for dice1, dice2 in combinations(dice_values, 2):
        win1_perc, win2_perc = single_dice_winning_chance(dice_values[dice1], dice_values[dice2])
        if win1_perc > 0.5:
            print(f"{dice1} beats {dice2} by {100*win1_perc:.0f}%")
        else:
            print(f"{dice2} beats {dice1} by {100*win2_perc:.0f}%")

def print_double_dice():
    print("Double dice")
    for dice1, dice2 in combinations(dice_values, 2):
        win1_perc, win2_perc = double_dice_winning_chance(dice_values[dice1], dice_values[dice2])
        if win1_perc > 0.5:
            print(f"{dice1} beats {dice2} by {100*win1_perc:.0f}%")
        else:
            print(f"{dice2} beats {dice1} by {100*win2_perc:.0f}%")

def main():
    print_single_dice()
    print()
    print_double_dice()

if __name__ == '__main__':
    main()