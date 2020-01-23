from robots.lego_robot_vrep import LegoRobot
from pyvrep import VRep
import time
import pygame
import numpy as np
from pyswip import Prolog
import threading

# Resolution is used for easier change of the map
RESOLUTION = {"12": [20, 8, 8, 1, 10, 10, 9, 9, 0.1],}
# CPU parameters is used to help to erase problems with changing speed of simulation
CPU_ = {"slow": [2], "fast": [1.5]}

RES = "12"
CPU = "slow"

# Global variables
END = False  # end of the simulation
START = False  # start of the simulation
CHANGE = False  # if to change the GUI
column = RESOLUTION[RES][5]-1  # initial setting of the column where the robot should move

# Prolog connection and insertion of the dynamical terms
prolog = Prolog()
prolog.consult("prolog/state_machine.pl")
prolog.assertz("obs(0)")
prolog.assertz("bottom_corner("+str(RESOLUTION[RES][4]-1)+")")
prolog.assertz("column("+str(column)+")")


def update_map(one_id):
    """
    Function to update GUI
    :param one_id: id of the current robot possition, array [x,y]
    :return: None
    """

    for row_id, row in enumerate(world2):  # Enumerate the whole world
        for col_id, col in enumerate(row):  # Enumerate its columns
            if col == 1:  # Robots
                if one_id != [row_id, col_id]:  # Old position of the robot
                    world2[row_id][col_id] = 0  # Delete robot
                    # Redraw robot
                    pygame.draw.rect(screen, (255, 255, 102), pygame.Rect(col_id * RESOLUTION[RES][0] + 150, row_id * RESOLUTION[RES][0] + 100, RESOLUTION[RES][0], RESOLUTION[RES][0]))
                    world2[row_id][col_id] = 4 #??
                else:
                    pygame.draw.rect(screen, (51, 204, 51), pygame.Rect(col_id * RESOLUTION[RES][0] + 150, row_id * RESOLUTION[RES][0] + 100, RESOLUTION[RES][0], RESOLUTION[RES][0]))
            elif col == 5:  # Line
                pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(col_id * RESOLUTION[RES][0] + 150, row_id * RESOLUTION[RES][0] + 100, RESOLUTION[RES][0], RESOLUTION[RES][0]))
            elif col == 51:  # Line and robot - draw robot and set as line for next redraw
                pygame.draw.rect(screen, (51, 204, 51), pygame.Rect(col_id * RESOLUTION[RES][0] + 150, row_id * RESOLUTION[RES][0] + 100, RESOLUTION[RES][0], RESOLUTION[RES][0]))
                world2[row_id][col_id] = 5
            elif col == 2:  # Obstacle
                pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(col_id * RESOLUTION[RES][0] + 150, row_id * RESOLUTION[RES][0] + 100, RESOLUTION[RES][0], RESOLUTION[RES][0]))
            elif col == 3:  # Red points
                pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(col_id * RESOLUTION[RES][0] + 150, row_id * RESOLUTION[RES][0] + 100, RESOLUTION[RES][0], RESOLUTION[RES][0]))
            elif col == 31: # Red point and robot - draw robot and set as red point for next redraw
                pygame.draw.rect(screen, (51, 204, 51), pygame.Rect(col_id * RESOLUTION[RES][0] + 150, row_id * RESOLUTION[RES][0] + 100, RESOLUTION[RES][0], RESOLUTION[RES][0]))
                world2[row_id][col_id] = 3
            elif col == 21:  # obstacle and robot - draw robot and set as obstacle for next redraw
                pygame.draw.rect(screen, (51, 204, 51), pygame.Rect(col_id * RESOLUTION[RES][0] + 150, row_id * RESOLUTION[RES][0] + 100, RESOLUTION[RES][0], RESOLUTION[RES][0]))
                world2[row_id][col_id] = 2
    pygame.display.flip()  # redraw


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
        prolog.retractall("obs(_)")
        prolog.assertz("obs(1)")  # Add obs(1) to prolog
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

    if color == 84:  # Red point
        world2[min_id[0]][min_id[1]] = 3
        END = True  # end run

    return min_id


def button_fce():
    """
    Function running in second thread for GUI
    :return:
    """
    global text_, CHANGE
    while not END:
        for event in pygame.event.get():
            pass
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if 700 < mouse[0] < 850 and 200 < mouse[1] < 350:  # If mouse over button and clicked change to START/PAUSE
            if click[0] == 1:
                if text_ == "PAUSE":
                    #api.simulation.pause()
                    CHANGE = True
                    text_ = "START"
                else:
                    #api.simulation.start()
                    text_ = "PAUSE"
                    CHANGE = True
                pygame.draw.rect(screen, (0, 0, 0), (700, 200, 150, 100))
                font = pygame.font.Font('freesansbold.ttf', 32)
                text = font.render(text_, True, (255, 255, 255))
                textRect = text.get_rect()
                textRect.center = (775, 250)
                screen.blit(text, textRect)


def pygame_loop(last_pos, direction = ""):
    """
    Loop for GUI
    :param last_pos: previous robot position, array [x,y] in indexes
    :param direction: string, direction
    :return: position of the robot, array [x,y], in indexes
    """
    global CHANGE
    #  Pause/start simulation
    if CHANGE and text_ == "START":
        api.simulation.pause()
        CHANGE = False
    elif CHANGE and text_ == "PAUSE":
        api.simulation.start()
        CHANGE = False
    b1 = r.touch_right()  # right touch
    b2 = r.touch_left()  # left touch
    pos = r.position()  # position
    min_id = find_closest(pos, last_pos, b1, b2, direction)
    update_map(min_id)
    return min_id#, (b1 or b2)


def line_follower():
    """
    Function to follow the line
    :return:
    """
    if color == 0:  # Black
        r.rotate_right(0.5)
    elif color == -1:  # White
        r.rotate_left(0.5)
    else:
        # Robot is in last 3 columns of the map => slow down
        if (last_pos[1] <= RESOLUTION[RES][3] + 1 and (
                last_pos[0] >= RESOLUTION[RES][1] - 1 or last_pos[0] <= RESOLUTION[RES][3] + 1)) or (
                last_pos[1] >= RESOLUTION[RES][2] - 1 and (
                last_pos[0] >= RESOLUTION[RES][1] - 1 or last_pos[0] <= RESOLUTION[RES][3] + 1)):
            r.move_forward(2)
        else: # else run faster
            r.move_forward(10)


def manual_control():
    """
    Allows to control the robot manually
    :return:
    """
    key = input("Press a key please\n")
    if key.lower() == "a":  # left
        r.rotate_left(10)
    elif key.lower() == "d":  # right
        r.rotate_right(10)
    elif key.lower() == "w":  # forward
        r.move_forward(25)
    elif key.lower() == "s":  # backward
        r.move_backward(25)
    time.sleep(0.1)
    r.stop()


def get_to_position():
    """
    Help function to get to right position after line following
    :return:
    """

    r.rotate_right(1)  # get from black
    time.sleep(1)
    while r.color() == -1:  # drive until right black is reached
        r.rotate_right(1)
    r.rotate_left(2)  # get straight up
    time.sleep(0.5)
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
        pos = pygame_loop(last_pos, direction)
        # Assert new position to prolog
        prolog.retractall("position(_)")
        prolog.assertz("position("+str(pos)+")")
        # Get state from prolog
        state = list(prolog.query("stateMachine(X)"))[0]["X"]
        if state == "state1":  # Obstacle
            if direction == "south":  # going south => back, left, forward, right, forward, right
                r.move_backward(2)
                time.sleep(0.5)
                r.rotate_left(2.25)
                time.sleep(CPU_[CPU][0])
                r.move_forward(3)
                time.sleep(CPU_[CPU][0])
                column += 1
                prolog.retractall("column(_)")
                prolog.assertz("column("+str(column)+")")
                r.rotate_right(2)
                time.sleep(CPU_[CPU][0])
                r.move_forward(6)
                time.sleep(CPU_[CPU][0])
                while world2[pos[0]][pos[1]-1] == 2:
                    r.move_forward(1)
                    pos = pygame_loop(pos, direction)
                r.move_forward(2)
                time.sleep(CPU_[CPU][0])
                r.rotate_right(2)
                time.sleep(CPU_[CPU][0])
                column -= 1
                prolog.retractall("column(_)")
                prolog.assertz("column("+str(column)+")")
                r.move_forward(2)
                time.sleep(CPU_[CPU][0])
                r.rotate_left(1.5)
                time.sleep(CPU_[CPU][0])
            elif direction == "north":  # going north => back, right, forward, left, forward, left
                r.move_backward(2)
                time.sleep(0.5)
                r.rotate_right(2.25)
                time.sleep(CPU_[CPU][0])
                r.move_forward(3)
                time.sleep(CPU_[CPU][0])
                column += 1
                prolog.retractall("column(_)")
                prolog.assertz("column("+str(column)+")")
                r.rotate_left(2.25)
                time.sleep(CPU_[CPU][0])
                r.move_forward(6)
                time.sleep(CPU_[CPU][0])
                while world2[pos[0]][pos[1] - 1] == 2:
                    r.move_forward(1)
                    pos = pygame_loop(pos, direction)
                r.move_forward(2)
                time.sleep(CPU_[CPU][0])
                r.rotate_left(2)
                time.sleep(CPU_[CPU][0])
                column -= 1
                prolog.retractall("column(_)")
                prolog.assertz("column("+str(column)+")")
                r.move_forward(2)
                time.sleep(CPU_[CPU][0])
                r.rotate_right(1.5)
                time.sleep(CPU_[CPU][0])
        elif state == "state2":  # Upper of the map => left, forward, left
            r.rotate_left(2)
            time.sleep(CPU_[CPU][0])
            r.move_forward(2)
            time.sleep(2)
            r.rotate_left(2)
            time.sleep(CPU_[CPU][0])
            direction = "south"
            r.move_forward(1)
            time.sleep(0.25)
            column -= 1
            prolog.retractall("column(_)")
            prolog.assertz("column(" + str(column) + ")")
        elif state == "state3":  # Bottom of the map  => right, forward, right
            r.rotate_right(2)
            time.sleep(CPU_[CPU][0])
            r.move_forward(2)
            time.sleep(2)
            r.rotate_right(2)
            time.sleep(CPU_[CPU][0])
            direction = "north"
            r.move_forward(1)
            time.sleep(0.25)
            column -= 1
            prolog.retractall("column(_)")
            prolog.assertz("column(" + str(column) + ")")
        elif state == "state4":  # going to much to the right
            if direction == "north":
                r.rotate_left(0.25)
            else:
                r.rotate_right(0.25)
        elif state == "state5":  # going to much to the left
            if direction == "north":
                r.rotate_right(0.25)
            else:
                r.rotate_left(0.25)
        elif state == "state6":  # else okay and go straight
            r.move_forward(4)
        last_pos = pos

# Pygame init
pygame.init()
screen = pygame.display.set_mode((900, 400))
screen.fill((255, 255, 255))
pygame.display.update()
text_="START"

# Wait for click on start
while not START:
    for event in pygame.event.get():
        pass
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if 700 < mouse[0] < 850 and 200 < mouse[1] < 350:
        if click[0] == 1:
            START = True
            text_ = "PAUSE"
    pygame.draw.rect(screen, (0, 0, 0), (700, 200, 150, 100))
    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render(text_, True, (255, 255, 255))
    textRect = text.get_rect()
    textRect.center = (775, 250)
    screen.blit(text, textRect)
    pygame.display.update()

# RUN thread with GUI
time.sleep(1)
t1 = threading.Thread(target=button_fce)
t1.start()


#Prepare world
world = []  # position of the robot
for row in range(RESOLUTION[RES][4]):
    world.append([])
    for col in range(RESOLUTION[RES][5]):
        world[row].append([0, 0])
# Numbers for GUI
world2 = np.zeros((RESOLUTION[RES][4], RESOLUTION[RES][5]))

with VRep.connect("127.0.0.1", 19997) as api:
    r = LegoRobot(api)
    r.stop()  # stop robot - something from simulation makes him move forward
    #bottom_right = r.position()

    # Set bottom right corner
    world[RESOLUTION[RES][6]][RESOLUTION[RES][7]][0] = 1.42
    world[RESOLUTION[RES][6]][RESOLUTION[RES][7]][1] = -0.98

    # Create other position with given resolution
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

    # init variables
    follow = False
    can_follow = True
    follow_start = None
    wander = False

    last_pos = [RESOLUTION[RES][6], RESOLUTION[RES][7]]
    color = 0

    manual = False

    r.stop()
    if not manual:
        r.rotate_left()  # to hit black line
    while not END:
        last_pos = pygame_loop(last_pos)  # GUI update
        if not manual:
            if follow:  # Line following
                color = r.color()  # get color
                line_follower()  # do right movement
                if last_pos == follow_start and np.count_nonzero(np.where(world2==5))>5:  # check if robot is back at start
                    follow = False
                    r.stop()
                    get_to_position()  # get right position
                    wander = True
            elif wander:  # End of following, start wandering
                #get_to_position()
                r.move_forward(5)
                time.sleep(0.5)
                wander_through(last_pos)  # Wander
                wander = False  #End wander
                break
            else:  # not following, not wandering
                color = r.color()
                if color == 0 and can_follow:  # Start following
                    follow_start = last_pos
                    follow = True
                    can_follow = False
        else:
            manual_control()
    r.stop()  # Stop robot
    t1.join()  # Wait for GUI
    input()  # Wait for user input to stop going
    #api.simulation.pause()


