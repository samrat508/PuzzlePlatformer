# This is a sample Python script.
import random

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import numpy as np

# creates empty dungeon, size can be modified
dungeon = [[0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0]]
startx = random.randint(0,len(dungeon)-1)
starty = random.randint(0,len(dungeon)-1)
total_length = 5
def generate_dungeon(x, y, path_length):
    #starting point marked
    dungeon[x][y] = path_length
    #filling out the path
    i = path_length - 1
    while i > 0:
        direction = random.randint(1,4)
        match direction:
            case 1: #left
                x -= 1
                if (x < 0 or x >= len(dungeon)-1 or dungeon[x][y] != 0):
                    x += 1
                else:
                    dungeon[x][y] = i
                    i -= 1
            case 2: #right
                x += 1
                if x < 0 or x >= len(dungeon)-1 or dungeon[x][y] != 0:
                    x -= 1
                else:
                    dungeon[x][y] = i
                    i -= 1
            case 3: #down
                y -= 1
                if (y < 0 or y >= len(dungeon)-1 or dungeon[x][y] != 0):
                    y += 1
                else:
                    dungeon[x][y] = i
                    i -= 1
            case 4: #up
                y += 1
                if (y < 0 or y >= len(dungeon)-1) or dungeon[x][y] != 0:
                    y -= 1
                else:
                    dungeon[x][y] = i
                    i -= 1
    z = 0
    while(z < len(dungeon)):
        print(dungeon[z])
        z += 1
    return dungeon
if __name__ == '__main__':
    generate_dungeon(startx,starty,total_length)