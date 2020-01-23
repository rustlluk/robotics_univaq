import numpy as np
from pyswip import Prolog
from robots.lego_robot import LegoRobot

RESOLUTION = {"1":[20, 18, 28, 1, 20, 30, 19, 29, 0.1], "0.5":[10, 37, 57, 2, 40, 60, 39, 59, 0.05], "12": [20, 8, 8, 1, 10, 10, 9, 9, 0.1],}
CPU_ = {"slow": [2], "fast": [1.5]}
RES = "12"
CPU = "slow"
directions = {"west": [1, 1.57], "east": [1, -1.57],
              "south": [0, -1.57], "north": [0, 1.57]}
END = False
column = RESOLUTION[RES][5]-1
prolog = Prolog()
prolog.consult("prolog/state_machine.pl")
prolog.assertz("obs(0)")
prolog.assertz("bottom_corner("+str(RESOLUTION[RES][4]-1)+")")
prolog.assertz("column("+str(column)+")")

"""
def update_map(one_id):
    for row_id, row in enumerate(world2):
        for col_id, col in enumerate(row):
            if col == 1:
                if one_id != [row_id, col_id]:
                    world2[row_id][col_id] = 0
                    pygame.draw.rect(screen, (255, 255, 102), pygame.Rect(col_id * RESOLUTION[RES][0] + 150, row_id * RESOLUTION[RES][0] + 100, RESOLUTION[RES][0], RESOLUTION[RES][0]))
                    world2[row_id][col_id] = 4
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
            elif col == 21:
                pygame.draw.rect(screen, (51, 204, 51), pygame.Rect(col_id * RESOLUTION[RES][0] + 150, row_id * RESOLUTION[RES][0] + 100, RESOLUTION[RES][0], RESOLUTION[RES][0]))
                world2[row_id][col_id] = 2
    pygame.display.flip()
"""


def find_closest(pos, last_pos, b1, b2, direction):
    global END, column
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
        world2[min_id[0]][min_id[1]] = 5  # 51
    elif world2[min_id[0]][min_id[1]] == 3:
        world2[min_id[0]][min_id[1]] = 31  # 31
    elif world2[min_id[0]][min_id[1]] == 2:
        world2[min_id[0]][min_id[1]] = 21  # 21
    else:
        world2[min_id[0]][min_id[1]]=1

    if b1 or b2:
        prolog.retractall("obs(_)")
        prolog.assertz("obs(1)")
        if direction == "west":
            x = 0
            y = -1
        elif direction == "east":
            x = 0
            y = 1
        elif direction == "south":
            x = 1
            y = 0
        elif direction == "north":
            x = -1
            y = 0

        world2[min_id[0]+x][column] = 2
    else:
        prolog.retractall("obs(_)")
        prolog.assertz("obs(0)")

    if color == 84:
        world2[min_id[0]][min_id[1]] = 3
        END = True

    return min_id


def pygame_loop(last_pos, direction = ""):
    b1 = r.touch_right()
    b2 = r.touch_left()
    pos = r.position()
    min_id = find_closest(pos, last_pos, b1, b2, direction)
    #update_map(min_id)
    return min_id#, (b1 or b2)


def line_follower():
    if 4 < color < 9:  # black
        r.rotate_right(50, 0.25)
    elif 75 < color < 84:  # white
        r.rotate_left(50, 0.25)
    else:
        if (last_pos[1] <= RESOLUTION[RES][3] + 1 and (
                last_pos[0] >= RESOLUTION[RES][1] - 1 or last_pos[0] <= RESOLUTION[RES][3] + 1)) or (
                last_pos[1] >= RESOLUTION[RES][2] - 1 and (
                last_pos[0] >= RESOLUTION[RES][1] - 1 or last_pos[0] <= RESOLUTION[RES][3] + 1)):
            r.move_forward(20, 0.5)
        else:
            r.move_forward(50, 0.25)


def manual_control():
    key = input("Press a key please\n")
    if key.lower() == "a":
        r.rotate_left(50, 0.5)
    elif key.lower() == "d":
        r.rotate_right(50, 0.5)
    elif key.lower() == "w":
        r.move_forward(50, 1)
    elif key.lower() == "s":
        r.move_backward(50, 1)
    r.stop()


def get_to_position():
    r.rotate_right(50, 2.5)
    while 77 < r.color() < 84:
        r.rotate_right(10, 0.25)
    r.rotate_left(50, 2)
    r.stop()


def wander_through(last_pos):
    global color, column
    direction = "north"
    while not END:
        color = r.color()
        pos = pygame_loop(last_pos, direction)
        prolog.retractall("position(_)")
        prolog.assertz("position("+str(pos)+")")
        state = list(prolog.query("stateMachine(X)"))[0]["X"]
        if state == "state1":
            if direction == "south":
                r.move_backward(50, 1)
                r.rotate_left(50, 3.1)
                r.move_forward(50, 3.1)
                column += 1
                prolog.retractall("column(_)")
                prolog.assertz("column("+str(column)+")")
                r.rotate_right(50, 3.1)
                r.move_forward(50, 6)
                while world2[pos[0]][pos[1]-1] == 2:
                    r.move_forward(50, 0.25)
                    pos = pygame_loop(pos, direction)
                r.move_forward(50, 1.5)
                r.rotate_right(50, 3.1)
                column -= 1
                prolog.retractall("column(_)")
                prolog.assertz("column("+str(column)+")")
                r.move_forward(50, 3.1)
                r.rotate_left(50, 3.1)
            elif direction == "north":
                r.move_backward(50, 1)
                r.rotate_right(50, 3.1)
                r.move_forward(50, 3.1)
                column += 1
                prolog.retractall("column(_)")
                prolog.assertz("column("+str(column)+")")
                r.rotate_left(50, 3.1)
                r.move_forward(50, 6)
                while world2[pos[0]][pos[1] - 1] == 2:
                    r.move_forward(50, 0.25)
                    pos = pygame_loop(pos, direction)
                r.move_forward(50, 1.5)
                r.rotate_left(50, 3.1)
                column -= 1
                prolog.retractall("column(_)")
                prolog.assertz("column("+str(column)+")")
                r.move_forward(50, 3.1)
                r.rotate_right(50, 3.1)
        elif state == "state2":
            r.rotate_left(50, 3.1)
            r.move_forward(50, 3.1)
            r.rotate_left(50, 3.1)
            direction = "south"
            r.move_forward(50, 3.1)
            column -= 1
            prolog.retractall("column(_)")
            prolog.assertz("column(" + str(column) + ")")
        elif state == "state3":
            r.rotate_right(50, 3.1)
            r.move_forward(50, 3.1)
            r.rotate_right(50, 3.1)
            direction = "north"
            r.move_forward(50, 3.1)
            column -= 1
            prolog.retractall("column(_)")
            prolog.assertz("column(" + str(column) + ")")
        elif state == "state4":
            if direction == "north":
                r.rotate_left(50, 0.25)
            else:
                r.rotate_right(50, 0.25)
        elif state == "state5":
            if direction == "north":
                r.rotate_right(50, 0.25)
            else:
                r.rotate_left(50, 0.25)
        elif state == "state6":
            r.move_forward(50, 0.25)
        last_pos = pos


world = []
for row in range(RESOLUTION[RES][4]):
    world.append([])
    for col in range(RESOLUTION[RES][5]):
        world[row].append([0, 0])
world2 = np.zeros((RESOLUTION[RES][4], RESOLUTION[RES][5]))

r = LegoRobot()
world[RESOLUTION[RES][6]][RESOLUTION[RES][7]][0] = 0
world[RESOLUTION[RES][6]][RESOLUTION[RES][7]][1] = 0

for col in range(RESOLUTION[RES][7], -1, -1):
    for row in range(RESOLUTION[RES][6], -1, -1):
        if not (col == RESOLUTION[RES][7] and row == RESOLUTION[RES][6]):
            if col != RESOLUTION[RES][7]:
                world[row][col][0] = world[row][col+1][0] + RESOLUTION[RES][8]
                world[row][col][1] = world[row][col + 1][1]
            else:
                world[row][col][0] = world[row+1][col][0]
                world[row][col][1] = world[row + 1][col][1] + RESOLUTION[RES][8]

world2[RESOLUTION[RES][6]][RESOLUTION[RES][7]] = 1
update_map([-1, -1])

follow = False
can_follow = True
follow_start = None
wander = False

last_pos = [RESOLUTION[RES][6], RESOLUTION[RES][7]]
color = 0

manual = False

while not END:
    last_pos = pygame_loop(last_pos)
    if not manual:
        if follow:
            color = r.color()
            line_follower()
            if last_pos == follow_start and np.count_nonzero(np.where(world2==5))>5:
                follow = False
                r.stop()
                get_to_position()
                wander = True
        elif wander:
            #get_to_position()
            r.move_forward(50, 0.5)
            wander_through(last_pos)
            wander = False
            break
        else:
            color = r.color()
            if color == 0 and can_follow:
                follow_start = last_pos
                follow = True
                can_follow = False
    else:
        manual_control()
r.stop()
input()
#api.simulation.pause()


