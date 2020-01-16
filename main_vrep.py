from lego_robot import LegoRobot
from pyvrep import VRep
import time
import pygame
import numpy as np

RESOLUTION = {"1":[20, 18, 28, 1, 20, 30, 19, 29, 0.1], "0.5":[10, 37, 57, 2, 40, 60, 39, 59, 0.05]}
RES = "1"


def update_map(one_id):
    for row_id, row in enumerate(world2):
        for col_id, col in enumerate(row):
            if col == 1:
                if one_id != [row_id, col_id]:
                    world2[row_id][col_id] = 0
                    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(col_id * RESOLUTION[RES][0] + 150, row_id * RESOLUTION[RES][0] + 100, RESOLUTION[RES][0], RESOLUTION[RES][0]))
                else:
                    pygame.draw.rect(screen, (51, 204, 51), pygame.Rect(col_id * RESOLUTION[RES][0] + 150, row_id * RESOLUTION[RES][0] + 100, RESOLUTION[RES][0], RESOLUTION[RES][0]))
            elif col == 5:
                pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(col_id * RESOLUTION[RES][0] + 150, row_id * RESOLUTION[RES][0] + 100, RESOLUTION[RES][0], RESOLUTION[RES][0]))
            elif col == 51:
                pygame.draw.rect(screen, (51, 204, 51), pygame.Rect(col_id * RESOLUTION[RES][0] + 150, row_id * RESOLUTION[RES][0] + 100, RESOLUTION[RES][0], RESOLUTION[RES][0]))
                world2[row_id][col_id] = 5
            elif col == 2:
                pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(col_id * RESOLUTION[RES][0] + 150, row_id * RESOLUTION[RES][0] + 100, RESOLUTION[RES][0], RESOLUTION[RES][0]))
            elif col == 3:
                pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(col_id * RESOLUTION[RES][0] + 150, row_id * RESOLUTION[RES][0] + 100, RESOLUTION[RES][0], RESOLUTION[RES][0]))
            elif col == 31:
                pygame.draw.rect(screen, (51, 204, 51), pygame.Rect(col_id * RESOLUTION[RES][0] + 150, row_id * RESOLUTION[RES][0] + 100, RESOLUTION[RES][0], RESOLUTION[RES][0]))
                world2[row_id][col_id] = 3
    pygame.display.flip()


def find_closest(pos, last_pos):
    min = float("inf")
    for row_id, row in enumerate(world):
        for col_id, col in enumerate(row):
            dist = np.linalg.norm(np.array(col) - np.array(pos[0:2]))
            if dist<min:
                min = dist
                min_id = [row_id, col_id]

    if follow:
        change = 1
        if (min_id[1] < last_pos[1]) and (min_id[0] >= RESOLUTION[RES][1]):
            x = 1
            y = 0
        elif min_id[1] > last_pos[1] and (min_id[0] <= RESOLUTION[RES][3]):
            x = -1
            y = 0
        elif min_id[0] < last_pos[0] and (min_id[1] <= RESOLUTION[RES][3]):
            x = 0
            y = -1
        elif min_id[0] > last_pos[0] and (min_id[1] >= RESOLUTION[RES][2]):
            x = 0
            y = 1
        else:
            change = 0
        if change:
            if min_id[0]==RESOLUTION[RES][6] or min_id[1]==0 or min_id[0]==0 or min_id[1] == RESOLUTION[RES][7]:
                world2[min_id[0]][min_id[1]] = 5
            else:
                world2[min_id[0] + x][min_id[1] + y] = 5

    if world2[min_id[0]][min_id[1]] == 5:
        world2[min_id[0]][min_id[1]] = 51
    elif world2[min_id[0]][min_id[1]] == 3:
        world2[min_id[0]][min_id[1]] = 31
    else:
        world2[min_id[0]][min_id[1]]=1

    if b1 or b2:
        if min_id != last_pos:
            if min_id[1] < last_pos[1]:
                x = 0
                y = -1
            elif min_id[1] > last_pos[1]:
                x = 0
                y = 1
            elif min_id[0] > last_pos[0]:
                x = 1
                y = 0
            elif min_id[0] < last_pos[0]:
                x = -1
                y = 0
            world2[min_id[0]+x][min_id[1]+y] = 2

    if color == 85:
        world2[min_id[0]][min_id[1]] = 3

    return min_id


pygame.init()
screen = pygame.display.set_mode((900, 600))
screen.fill((255, 255, 255))
pygame.display.update()
world = []
for row in range(RESOLUTION[RES][4]):
    world.append([])
    for col in range(RESOLUTION[RES][5]):
        world[row].append([0, 0])
world2 = np.zeros((RESOLUTION[RES][4], RESOLUTION[RES][5]))

with VRep.connect("127.0.0.1", 19997) as api:
    r = LegoRobot(api)

    bottom_right = r.position()

    world[RESOLUTION[RES][6]][RESOLUTION[RES][7]][0] = 1.42
    world[RESOLUTION[RES][6]][RESOLUTION[RES][7]][1] = -0.98

    for col in range(RESOLUTION[RES][7],-1,-1):
        for row in range(RESOLUTION[RES][6], -1, -1):
            if not (col == RESOLUTION[RES][7] and row == RESOLUTION[RES][6]):
                if col != RESOLUTION[RES][7]:
                    world[row][col][0] = world[row][col+1][0] - RESOLUTION[RES][8]
                    world[row][col][1] = world[row][col + 1][1]
                else:
                    world[row][col][0] = world[row+1][col][0]
                    world[row][col][1] = world[row + 1][col][1] + RESOLUTION[RES][8]
    world2[RESOLUTION[RES][6]][RESOLUTION[RES][7]] = 1
    update_map([-1, -1])

    follow = False
    last_pos = [RESOLUTION[RES][6], RESOLUTION[RES][7]]

    r.stop()
    r.rotate_left()
    time.sleep(0.05)
    while True:
        if follow:
            pos = r.position()
            min_id = find_closest(pos, last_pos)
            last_pos = min_id
            update_map(min_id)

            if r.color()==5:
                r.rotate_right(5)
            elif r.color()==-1:
                r.rotate_left(5)
            time.sleep(0.05)
            r.move_forward()
            time.sleep(0.075)
        else:
            color = r.color()
            b1 = r.touch_right()
            b2 = r.touch_left()
            pos = r.position()
            min_id = find_closest(pos, last_pos)
            last_pos = min_id
            update_map(min_id)
            if color == 5:
                follow = True
