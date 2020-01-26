from robots.lego_robot import LegoRobot
from pyvrep import VRep
import time
import pygame
import numpy as np
from pyswip import Prolog

# Resolution is used for easier change of the map
RESOLUTION = {"12": [20, 3, 5, 1, 5, 7, 4, 6, 0.1],}
RES = "12"
# Global variables
END = False  # end of the simulation
column = RESOLUTION[RES][5]-1  # initial setting of the column where the robot should move
LINES = 0  # Number of black lines discovered

def find_closest(pos, last_pos, b1, b2, direction):
    """
    Find the position of the robot in world array and assign right numbers for GUI
    :param pos: array [x,y], position of robot in metres
    :param last_pos: array [x,y], last position of the robot, in indexes
    :param b1: 0/1 - state of right touch sensor
    :param b2: 0/1 - state of the left touch sensor
    :param direction: string, direction of the robot
    :return: array [x,y] - position of the robot, in indexes
    """
    global END, column

    # Find the position of the robot by making distance between position and position in given indexes
    min = float("inf")
    for row_id, row in enumerate(world):
        for col_id, col in enumerate(row):
            dist = np.linalg.norm(np.array(col) - np.array(pos[0:2]))  # Euclidean norm
            if dist<min:
                min = dist
                min_id = [row_id, col_id]

    if follow:  # Line following
        change = 1  # If new line needs to be added
        if (min_id[1] < last_pos[1]) and (min_id[0] >= RESOLUTION[RES][1]):  # west
            x = 1
            y = 0
        elif min_id[1] > last_pos[1] and (min_id[0] <= RESOLUTION[RES][3]):  # east
            x = -1
            y = 0
        elif min_id[0] < last_pos[0] and (min_id[1] <= RESOLUTION[RES][3]):  # north
            x = 0
            y = -1
        elif min_id[0] > last_pos[0] and (min_id[1] >= RESOLUTION[RES][2]):  # south
            x = 0
            y = 1
        else:
            change = 0  # if robot did not move

        if change:
            LINES += 1
            if min_id[0]==RESOLUTION[RES][6] or min_id[1]==0 or min_id[0]==0 or min_id[1] == RESOLUTION[RES][7]:  # if robot is on last/first line
                world2[min_id[0]][min_id[1]] = 5
            else:
                world2[min_id[0] + x][min_id[1] + y] = 5

    # Add 'X1' if there is already something on the map
    if world2[min_id[0]][min_id[1]] == 5:
        world2[min_id[0]][min_id[1]] = 51
    elif world2[min_id[0]][min_id[1]] == 3:
        world2[min_id[0]][min_id[1]] = 31
    elif world2[min_id[0]][min_id[1]] == 2:
        world2[min_id[0]][min_id[1]] = 21
    else:
        world2[min_id[0]][min_id[1]]=1

    # Button handling
    if b1 or b2:
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

    if color == 84:  # Red point
        world2[min_id[0]][min_id[1]] = 3
        END = True  # end run

    return min_id


def pygame_loop(last_pos, direction = ""):
    """
    Loop for GUI
    :param last_pos: previous robot position, array [x,y] in indexes
    :param direction: string, direction
    :return: position of the robot, array [x,y], in indexes
    """
    b1 = r.touch_right()  # right touch
    b2 = r.touch_left()  # left touch
    pos = r.position()  # position
    min_id = find_closest(pos, last_pos, b1, b2, direction)
    return min_id, (b1 or b2)


def line_follower():
    """
    Function to follow the line
    :return:
    """
    if color == 0:  # Black
        r.rotate_right(50)
    elif color == -1:  # White
        r.rotate_left(50)
    else:
        # Robot is in last 3 columns of the map => slow down
        if (last_pos[1] <= RESOLUTION[RES][3] + 1 and (
                last_pos[0] >= RESOLUTION[RES][1] - 1 or last_pos[0] <= RESOLUTION[RES][3] + 1)) or (
                last_pos[1] >= RESOLUTION[RES][2] - 1 and (
                last_pos[0] >= RESOLUTION[RES][1] - 1 or last_pos[0] <= RESOLUTION[RES][3] + 1)):
            r.move_forward(50)
        else: # else run faster
            r.move_forward(70)


def get_to_position():
    """
    Help function to get to right position after line following
    :return:
    """

    r.rotate_right(1, 1)  # get from black
    while r.color() == -1:  # drive until right black is reached
        r.rotate_right(1)
    r.rotate_left(50, 0.5)  # get straight up
    r.stop()


def wander_through(last_pos):
    """
    Main  function for robot wandering
    :param last_pos: previous position of the robot, array [x,y], in indexes
    :return:
    """
    global color, column
    direction = "north"
    while not END:
        color = r.color()
        pos, obs = pygame_loop(last_pos, direction)
        if obs:  # Obstacle
            if direction == "south":  # going south => back, left, forward, right, forward, right
                r.move_backward(50, 1.5)
                r.rotate_left(50, 3.1)
                r.move_forward(50, 4)
                column += 1
                r.rotate_right(50, 3.1)
                r.move_forward(50, 6)
                while world2[pos[0]][pos[1]-1] == 2:
                    r.move_forward(50)
                    pos, obs = pygame_loop(pos, direction)
                r.move_forward(50, 1.5)
                r.rotate_right(50, 3.1)
                column -= 1
                r.move_forward(50, 4)
                r.rotate_left(50, 3.1)
            elif direction == "north":  # going north => back, right, forward, left, forward, left
                r.move_backward(50, 1.5)
                r.rotate_right(50, 3.1)
                r.move_forward(50, 4)
                column += 1
                r.rotate_left(50, 3.1)
                r.move_forward(50, 6)
                while world2[pos[0]][pos[1] - 1] == 2:
                    r.move_forward(50)
                    pos, obs = pygame_loop(pos, direction)
                r.move_forward(50, 1.5)
                r.rotate_left(50, 3.1)
                column -= 1
                r.move_forward(50, 4)
                r.rotate_right(50, 3.1)
        elif 25 < color < 35:  # Upper of the map => left, forward, left
            if direction == "north":
                r.rotate_left(50, 3.1)
                r.move_forward(50, 4)
                r.rotate_left(50, 3.1)
                direction = "south"
                r.move_forward(50, 0.25)
                column -= 1
            elif direction == "south":
                r.rotate_right(50, 3.1)
                r.move_forward(50, 4)
                r.rotate_right(50, 3.1)
                direction = "north"
                r.move_forward(50, 0.25)
                column -= 1
        else:  # else okay and go straight
            r.move_forward(75)
        last_pos = pos

# Pygame init
pygame.init()
screen = pygame.display.set_mode((900, 400))
screen.fill((255, 255, 255))
pygame.display.update()

#Prepare world
world = []  # position of the robot
for row in range(RESOLUTION[RES][4]):
    world.append([])
    for col in range(RESOLUTION[RES][5]):
        world[row].append([0, 0])
# Numbers for GUI
world2 = [[0 for i in range(RESOLUTION[RES][5])] for j in range(RESOLUTION[RES][4])]

r = LegoRobot()
r.stop()  # stop robot - something from simulation makes him move forward
#bottom_right = r.position()

r.odo.x = -0.05
r.odo.y = 0.05

# Set bottom right corner
world[RESOLUTION[RES][6]][RESOLUTION[RES][7]][0] = 0
world[RESOLUTION[RES][6]][RESOLUTION[RES][7]][1] = 0

# Create other position with given resolution
for col in range(RESOLUTION[RES][7], -1, -1):
    for row in range(RESOLUTION[RES][6], -1, -1):
        if not (col == RESOLUTION[RES][7] and row == RESOLUTION[RES][6]):
            if col != RESOLUTION[RES][7]:
                world[row][col][0] = world[row][col+1][0] - RESOLUTION[RES][8]
                world[row][col][1] = world[row][col + 1][1]
            else:
                world[row][col][0] = world[row+1][col][0]
                world[row][col][1] = world[row + 1][col][1] + RESOLUTION[RES][8]
world2[RESOLUTION[RES][6]][RESOLUTION[RES][7]] = 1

# init variables
follow = False
can_follow = True
follow_start = None
wander = False

last_pos = [RESOLUTION[RES][6], RESOLUTION[RES][7]]
color = 0

while not END:
    last_pos = pygame_loop(last_pos)  # GUI update
    if follow:  # Line following
        color = r.color()  # get color
        line_follower()  # do right movement
        if LINES == 17:
            follow = False
            r.stop()
            get_to_position()  # get right position
            wander = True
    elif wander:  # End of following, start wandering
        #get_to_position()
        r.move_forward(5, 0.5)
        wander_through(last_pos)  # Wander
        wander = False  #End wander
        break
    else:  # not following, not wandering
        color = r.color()
        if color == 0 and can_follow:  # Start following
            follow_start = last_pos
            follow = True
            can_follow = False
r.stop()  # Stop robot
input()  # Wait for user input to stop going
#api.simulation.pause()


