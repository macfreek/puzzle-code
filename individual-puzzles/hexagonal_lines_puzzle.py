#!/usr/bin/env python3

"""
Given a board with 19 tiles, ordered in 5 lines in 3 directions each:

   ⬣ ⬣ ⬣
  ⬣ ⬣ ⬣ ⬣
 ⬣ ⬣ ⬣ ⬣ ⬣
  ⬣ ⬣ ⬣ ⬣
   ⬣ ⬣ ⬣

with each tile containing 3 line segements in each of the 3 directions:

    ---
   / | \
  / \ / \
  \ / \ /
   \ | /
    ---

Each of each these line segements has a certain colour (represented by a number in this script).
The goal is to rearrange the tiles so that continuous lines of equal colour occurs.

Given which lines should have equal colours, generate all possible solutions.

Some (arbitrary) nomenclature:

                           \                    /  
                             \                /    
       ----------              \            /      
                                 \        /        
                                   \    /          
       direction X       direction Y    direction Z

Lines in X direction:
     ---    A
    -----   B
   -------  C
    -----   D
     ---    E

Lines in Y direction:
      H  I  J
    G  \  \  \ 
  F  \  \  \  \ 
   \  \  \  \  \ 
    \  \  \  \ 
     \  \  \ 

Lines in Z direction:
        K  L  M
      /  /  /  N 
    /  /  /  /  O  
  /  /  /  /  /   
   /  /  /  /     
    /  /  /       

Board with tile positions:
      AHK AIL AJM
    BGK BHL BIM BJN
  CFK CGL CHM CIN CJO
    DFL DGM DHN DIO
      EFM EGN EGO

"""

from collections import Counter
import itertools

def generate_lines(available_symbols, required):
    """Given available line segements (in a given direction), 
    return possible line configurations.
    
    Input:
      available_symbols: Counter with line segments on the tiles
      required: tuple with 5 true/false values.
    Output:
      tuple with line symbol for required lines, and 0 for "any" line.
    """
    def generate_lines_(available_symbols, line_lengths):
        if len(line_lengths) == 0:
            yield []
        elif line_lengths[0] is None:
            for sub_line in generate_lines_(available_symbols, line_lengths[1:]):
                yield [0] + sub_line
        else:
            for line_symbol, free_symbols in available_symbols.items():
                if free_symbols < line_lengths[0]:
                    continue
                remaining_symbols = Counter(available_symbols)
                remaining_symbols[line_symbol] -= line_lengths[0]
                for sub_line in generate_lines_(remaining_symbols, line_lengths[1:]):
                    yield [line_symbol] + sub_line
        
    line_lengths = tuple(line_length if required else None 
            for required, line_length in zip(required, (3,4,5,4,3)))
    for line_config in generate_lines_(available_symbols, line_lengths):
        yield line_config

def line_config_to_tile_options(available_tiles, x_lines, y_lines, z_lines):
    """Given the available tiles, and line configs, 
    return for each board position a list of possible tiles."""
    available_x = set(tile[0] for tile in available_tiles)
    available_y = set(tile[1] for tile in available_tiles)
    available_z = set(tile[2] for tile in available_tiles)
    
    # board positions
    #      AHK AIL AJM
    #    BGK BHL BIM BJN
    #  CFK CGL CHM CIN CJO
    #    DFL DGM DHN DIO
    #      EFM EGN EGO
    # equals:
    #      020 031 042
    #    110 121 132 143
    #  200 211 222 233 244
    #    301 312 323 334
    #      402 413 414
    board_positions = (
               (0,2,0),  (0,3,1),  (0,4,2), 
          (1,1,0),  (1,2,1),  (1,3,2),  (1,4,3), 
     (2,0,0),  (2,1,1),  (2,2,2),  (2,3,3),  (2,4,4), 
          (3,0,1),  (3,1,2),  (3,2,3),  (3,3,4), 
               (4,0,2),  (4,1,3),  (4,1,4), 
    )
    board_options = []
    for board_pos in board_positions:
        x = x_lines[board_pos[0]]
        y = y_lines[board_pos[1]]
        z = z_lines[board_pos[2]]
        x = available_x if x == 0 else [x]
        y = available_y if y == 0 else [y]
        z = available_z if z == 0 else [z]
        tiles = [''.join(tile) for tile in itertools.product(x,y,z)]
        tiles = list(filter(lambda tile: tile in available_tiles, tiles))
        board_options.append(tiles)
    return board_options

def generate_board(board_options, available_tiles):
    """Given the line restrictions, place the available tiles on the board."""
    if len(board_options) == 0:
        yield []
    else:
        for tile_option in board_options[0]:
            if tile_option not in available_tiles:
                continue
            remaining_tiles = available_tiles[:]
            remaining_tiles.remove(tile_option)
            for sub_board in generate_board(board_options[1:], remaining_tiles):
                yield [tile_option] + sub_board

def main():
    # Define available colours
    any_color = '0'
    x_options = set(['1', '5', '9'])
    y_options = set(['2', '6', '7'])
    z_options = set(['3', '4', '8'])
    # Define which lines need to be formed
    # 1 means: yes, a line is required.  0 mean: any color suffices
    x_lines = (1, 1, 0, 1, 1)  # lines A, B, C, D, E.
    y_lines = (1, 1, 0, 1, 1)  # lines F, G, H, I, J.
    z_lines = (1, 1, 0, 1, 1)  # lines K, L, M, N, O.
    # Define available tiles
    available_tiles = Counter({
        '123': 0,
        '124': 1,
        '128': 0,
        '163': 0,
        '164': 1,
        '168': 0,
        '173': 1,
        '174': 0,
        '178': 1,
        '523': 1,
        '524': 1,
        '528': 1,
        '563': 1,
        '564': 1,
        '568': 1,
        '573': 1,
        '574': 1,
        '578': 0,
        '923': 1,
        '924': 1,
        '928': 1,
        '963': 1,
        '964': 1,
        '968': 0,
        '973': 1,
        '974': 1,
        '978': 0,
    })
    available_tiles = list(available_tiles.elements())
    assert len(available_tiles) == 19
    available_x = Counter(tile[0] for tile in available_tiles)
    available_y = Counter(tile[1] for tile in available_tiles)
    available_z = Counter(tile[2] for tile in available_tiles)
    assert set(available_x.keys()) == set(x_options)
    assert set(available_y.keys()) == set(y_options)
    assert set(available_z.keys()) == set(z_options)
    for x_config in generate_lines(available_x, x_lines):
        for y_config in generate_lines(available_y, y_lines):
            for z_config in generate_lines(available_z, z_lines):
                board_options = line_config_to_tile_options(available_tiles, x_config, y_config, z_config)
                # print(board_options)
                available_board_count = 0
                for board in generate_board(board_options, available_tiles):
                    print(x_config, y_config, z_config)
                    print(board)
                    available_board_count += 1
                # if available_board_count == 0:
                #     print(x_config, y_config, z_config, available_board_count, "solutions")

if __name__ == '__main__':
    main()