
import pygame
import kociemba
import random
import time

# define colors
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 128, 0)
WHITE = (255, 255, 255)
colorList = [YELLOW, WHITE, BLUE, RED, GREEN, ORANGE]

# define adjacent faces
adjacent_faces = {
    0: [4, 1, 5, 3],  # Left face: Up, Front, Down, Back
    1: [4, 0, 5, 2],  # Front face: Up, Left, Down, Right
    2: [4, 3, 5, 1],  # Right face: Up, Back, Down, Front
    3: [4, 2, 5, 0],  # Back face: Up, Right, Down, Left
    4: [3, 2, 1, 0],  # Up face: Back, Right, Front, Left
    5: [1, 2, 3, 0]  # Down face: Front, Right, Back, Left
}

# define face indices
face_indices = {
    "Left": 0,
    "Front": 1,
    "Right": 2,
    "Back": 3,
    "Up": 4,
    "Down": 5
}

MOVE_REVERSALS = {
    "U": "U'",
    "U'": "U",
    "D": "D'",
    "D'": "D",
    "L": "L'",
    "L'": "L",
    "R": "R'",
    "R'": "R",
    "F": "F'",
    "F'": "F",
    "B": "B'",
    "B'": "B",
}


def kociemba_solver(cube):
    # Convert the cube state to a string format that kociemba can solve
    cube_state = cube.stringify()
    solution = kociemba.solve(cube_state)
    solution_steps = solution.split()
    return solution_steps


class RubiksCube(pygame.sprite.Sprite):
    def __init__(self, xpos, ypos, size=30):
        pygame.sprite.Sprite.__init__(self)
        self.xpos = xpos
        self.ypos = ypos
        self.size = size
        # stores all the face objects in this order
        # "left", "front", "right", "back", "up", "down"
        self.faces = []
        self.init_faces()
        self.move_list = []

    def init_faces(self):
        temp_color_list = colorList

        # L -> B faces
        for i in range(4):
            color = temp_color_list.pop()
            face = Face(self.xpos + i * self.size * 3, self.ypos, self.size, color)
            self.faces.append(face)

        # up face
        color = temp_color_list.pop()
        face = Face(self.xpos + self.size * 3, self.ypos - self.size * 3, self.size, color)
        self.faces.append(face)

        # down face
        color = temp_color_list.pop()
        face = Face(self.xpos + self.size * 3, self.ypos + self.size * 3, self.size, color)
        self.faces.append(face)

    # update faces
    def recalculate_faces(self):
        # L -> B faces
        for i in range(4):
            self.faces[i].xpos = self.xpos + i * self.size * 3
            self.faces[i].ypos = self.ypos

        # up face
        self.faces[4].xpos = self.xpos + self.size * 3
        self.faces[4].ypos = self.ypos - self.size * 3

        # down face
        self.faces[5].xpos = self.xpos + self.size * 3
        self.faces[5].ypos = self.ypos + self.size * 3

        for face in self.faces:
            face.recalculate_squares()

    # updates screen
    def draw(self, screen):
        for face in self.faces:
            face.drawFace(screen)

    def cubeRotation(self, rotation_type, direction):
        # 2 rotation types: x: R direction, y: U direction
        # 2 directions: 0: Normal Direction, 1: Prime Direction
        # initial order: 0, 1, 2, 3, 4, 5

        # rotation types
        if rotation_type == "x":  # Rotating around the x-axis
            if direction == 0:  # X
                new_order = [0, 5, 2, 4, 1, 3]
            elif direction == 1:  # X'
                new_order = [0, 4, 2, 5, 3, 1]
            else:
                raise ValueError("Invalid direction")

        elif rotation_type == "y":  # Rotating around the y-axis
            if direction == 0:  # Y
                new_order = [1, 2, 3, 0, 4, 5]
            elif direction == 1:  # Y'
                new_order = [3, 0, 1, 2, 4, 5]
            else:
                raise ValueError("Invalid direction.")

        else:
            raise ValueError("Invalid rotation type.")

        # reorder the "faces" array to reflect the rotation
        new_faces = []
        for num in new_order:
            new_faces.append(self.faces[num])
        self.faces = new_faces

        if rotation_type == "x":
            if direction == 0:
                rotations = [(0, 1), (2, 0), (3, 1), (3, 1), (5, 1), (5, 1)]
                for current_face, orientation in rotations:
                    self.faceRotate(self.faces[current_face], orientation)
            if direction == 1:
                rotations = [(0, 0), (2, 1), (3, 1), (3, 1), (4, 1), (4, 1)]
                for current_face, orientation in rotations:
                    self.faceRotate(self.faces[current_face], orientation)
        if rotation_type == "y":
            if direction == 0:
                rotations = [(4, 0), (5, 1)]
                for current_face, orientation in rotations:
                    self.faceRotate(self.faces[current_face], orientation)
            if direction == 1:
                rotations = [(4, 1), (5, 0)]
                for current_face, orientation in rotations:
                    self.faceRotate(self.faces[current_face], orientation)

        self.recalculate_faces()

    # swaps square colors to turn the cube
    def squareSwap(self, colors_to_move, squares_to_move_to, swapped):
        temp = [squares_to_move_to[0].color, squares_to_move_to[1].color, squares_to_move_to[2].color]
        for i in range(3):
            squares_to_move_to[i].color = colors_to_move[i]
        if swapped:
            temp2 = squares_to_move_to[0].color
            squares_to_move_to[0].color = squares_to_move_to[2].color
            squares_to_move_to[2].color = temp2
        return temp

    # rotates the front face clockwise or counter clockwise
    def faceRotate(self, face, direction):
        # 0: clockwise 1: counter-clockwise
        if direction == 0:
            new_order = [2, 5, 8, 1, 4, 7, 0, 3, 6]
        elif direction == 1:
            new_order = [6, 3, 0, 7, 4, 1, 8, 5, 2]
        else:
            raise ValueError("Invalid direction.")

        new_squares = []

        # updates squares after rotation
        for num in new_order:
            new_squares.append(face.squares[num])

        face.squares = new_squares

    # Rotates side, used for different turns
    def rotation(self, direction):
        current_face = self.faces[1]
        if direction == 0:
            self.faceRotate(current_face, 0)
        elif direction == 1:
            self.faceRotate(current_face, 1)
        else:
            raise ValueError("Invalid direction")

        side_face = self.faces[2]
        colors_to_move = [side_face.squares[0].color, side_face.squares[1].color, side_face.squares[2].color]
        #Clockwise
        if direction == 0:
            next_face = self.faces[5]
            move_to = [next_face.squares[0], next_face.squares[3], next_face.squares[6]]
            temp = [move_to[0].color, move_to[1].color, move_to[2].color]
            move_to[0].color = colors_to_move[2]
            move_to[1].color = colors_to_move[1]
            move_to[2].color = colors_to_move[0]
            colors_to_move = temp

            next_face = self.faces[0]
            move_to = [next_face.squares[6], next_face.squares[7], next_face.squares[8]]
            temp = [move_to[0].color, move_to[1].color, move_to[2].color]
            move_to[0].color = colors_to_move[0]
            move_to[1].color = colors_to_move[1]
            move_to[2].color = colors_to_move[2]
            colors_to_move = temp

            next_face = self.faces[4]
            move_to = [next_face.squares[2], next_face.squares[5], next_face.squares[8]]
            temp = [move_to[0].color, move_to[1].color, move_to[2].color]
            move_to[0].color = colors_to_move[2]
            move_to[1].color = colors_to_move[1]
            move_to[2].color = colors_to_move[0]
            colors_to_move = temp

            next_face = self.faces[2]
            move_to = [next_face.squares[0], next_face.squares[1], next_face.squares[2]]
            temp = [move_to[0].color, move_to[1].color, move_to[2].color]
            move_to[0].color = colors_to_move[0]
            move_to[1].color = colors_to_move[1]
            move_to[2].color = colors_to_move[2]
        #Counterclockwise
        if direction == 1:
            next_face = self.faces[4]
            move_to = [next_face.squares[2], next_face.squares[5], next_face.squares[8]]
            temp = [move_to[0].color, move_to[1].color, move_to[2].color]
            move_to[0].color = colors_to_move[0]
            move_to[1].color = colors_to_move[1]
            move_to[2].color = colors_to_move[2]
            colors_to_move = temp

            next_face = self.faces[0]
            move_to = [next_face.squares[6], next_face.squares[7], next_face.squares[8]]
            temp = [move_to[0].color, move_to[1].color, move_to[2].color]
            move_to[0].color = colors_to_move[2]
            move_to[1].color = colors_to_move[1]
            move_to[2].color = colors_to_move[0]
            colors_to_move = temp

            next_face = self.faces[5]
            move_to = [next_face.squares[0], next_face.squares[3], next_face.squares[6]]
            temp = [move_to[0].color, move_to[1].color, move_to[2].color]
            move_to[0].color = colors_to_move[0]
            move_to[1].color = colors_to_move[1]
            move_to[2].color = colors_to_move[2]
            colors_to_move = temp

            next_face = self.faces[2]
            move_to = [next_face.squares[0], next_face.squares[1], next_face.squares[2]]
            temp = [move_to[0].color, move_to[1].color, move_to[2].color]
            move_to[0].color = colors_to_move[2]
            move_to[1].color = colors_to_move[1]
            move_to[2].color = colors_to_move[0]

        self.recalculate_faces()

    # Specifies type of turn to perform (U, R, L, D, F, etc)
    def faceTurn(self, rotation_type):
        if rotation_type == "U":
            self.cubeRotation("x", 1)
            self.rotation(0)
            self.cubeRotation("x", 0)
            self.move_list.append(rotation_type)

        elif rotation_type == "U'":
            self.cubeRotation("x", 1)
            self.rotation(1)
            self.cubeRotation("x", 0)
            self.move_list.append(rotation_type)

        elif rotation_type == "U2":
            self.cubeRotation("x", 1)
            self.rotation(0)
            self.rotation(0)
            self.cubeRotation("x", 0)
            self.move_list.append(rotation_type)

        elif rotation_type == "D":
            self.cubeRotation("x", 0)
            self.rotation(0)
            self.cubeRotation("x", 1)
            self.move_list.append(rotation_type)

        elif rotation_type == "D'":
            self.cubeRotation("x", 0)
            self.rotation(1)
            self.cubeRotation("x", 1)
            self.move_list.append(rotation_type)

        elif rotation_type == "D2":
            self.cubeRotation("x", 0)
            self.rotation(0)
            self.rotation(0)
            self.cubeRotation("x", 1)
            self.move_list.append(rotation_type)

        elif rotation_type == "L":
            self.cubeRotation("y", 1)
            self.rotation(0)
            self.cubeRotation("y", 0)
            self.move_list.append(rotation_type)

        elif rotation_type == "L'":
            self.cubeRotation("y", 1)
            self.rotation(1)
            self.cubeRotation("y", 0)
            self.move_list.append(rotation_type)

        elif rotation_type == "L2":
            self.cubeRotation("y", 1)
            self.rotation(0)
            self.rotation(0)
            self.cubeRotation("y", 0)
            self.move_list.append(rotation_type)

        elif rotation_type == "R":
            self.cubeRotation("y", 0)
            self.rotation(0)
            self.cubeRotation("y", 1)
            self.move_list.append(rotation_type)

        elif rotation_type == "R'":
            self.cubeRotation("y", 0)
            self.rotation(1)
            self.cubeRotation("y", 1)
            self.move_list.append(rotation_type)

        elif rotation_type == "R2":
            self.cubeRotation("y", 0)
            self.rotation(0)
            self.rotation(0)
            self.cubeRotation("y", 1)
            self.move_list.append(rotation_type)

        elif rotation_type == "F":
            self.rotation(0)
            self.move_list.append(rotation_type)

        elif rotation_type == "F'":
            self.rotation(1)
            self.move_list.append(rotation_type)

        elif rotation_type == "F2":
            self.rotation(0)
            self.rotation(0)
            self.move_list.append(rotation_type)

        elif rotation_type == "B":
            self.cubeRotation("x", 1)
            self.cubeRotation("x", 1)
            self.rotation(0)
            self.cubeRotation("x", 0)
            self.cubeRotation("x", 0)
            self.move_list.append(rotation_type)

        elif rotation_type == "B'":
            self.cubeRotation("x", 1)
            self.cubeRotation("x", 1)
            self.rotation(1)
            self.cubeRotation("x", 0)
            self.cubeRotation("x", 0)
            self.move_list.append(rotation_type)

        elif rotation_type == "B2":
            self.cubeRotation("x", 1)
            self.cubeRotation("x", 1)
            self.rotation(0)
            self.rotation(0)
            self.cubeRotation("x", 0)
            self.cubeRotation("x", 0)
            self.move_list.append(rotation_type)

        return rotation_type

    # HELPER FUNCTIONS
    # prints color of faces
    def printfaces(self):
        for face in self.faces:
            print(face.squares[0].color)

    # function to determine if cube is solved
    def isSolved(self):
        for face in self.faces:
            for square in face.squares:
                test_color = face.squares[0].color
                if square.color != test_color:
                    return False
        return True

    # function to randomly scramble cube
    def scramble(self):
        possible_moves = ["U", "U'", "D", "D'", "L", "L'", "R", "R'", "F", "F'", "B", "B'"]
        for i in range(random.randint(200, 500)):
            random_element = random.choice(possible_moves)
            self.faceTurn(random_element)

    # #in order for kociemba to work the cube must be read in the following format:
    '''      |************|
             |*U1**U2**U3*|
             |************|
             |*U4**U5**U6*|
             |************|
             |*U7**U8**U9*|
             |************|
 ************|************|************|************
 *L1**L2**L3*|*F1**F2**F3*|*R1**R2**R3*|*B1**B2**B3*
 ************|************|************|************
 *L4**L5**L6*|*F4**F5**F6*|*R4**R5**R6*|*B4**B5**B6*
 ************|************|************|************
 *L7**L8**L9*|*F7**F8**F9*|*R7**R8**R9*|*B7**B8**B9*
 ************|************|************|************
             |************|
             |*D1**D2**D3*|
             |************|
             |*D4**D5**D6*|
             |************|
             |*D7**D8**D9*|
             |************|'''
    #If we were to iterate by each face and square it would access the face column by column not row by row so we
    #must transpose the cube for kociemba to work
    def stringify(self):
        position_order = [
            # Up
            (4, 0), (4, 3), (4, 6),
            (4, 1), (4, 4), (4, 7),
            (4, 2), (4, 5), (4, 8),
            # Left
            (2, 0), (2, 3), (2, 6),
            (2, 1), (2, 4), (2, 7),
            (2, 2), (2, 5), (2, 8),
            # Front
            (1, 0), (1, 3), (1, 6),
            (1, 1), (1, 4), (1, 7),
            (1, 2), (1, 5), (1, 8),
            # Right
            (5, 0), (5, 3), (5, 6),
            (5, 1), (5, 4), (5, 7),
            (5, 2), (5, 5), (5, 8),
            # Back
            (0, 0), (0, 3), (0, 6),
            (0, 1), (0, 4), (0, 7),
            (0, 2), (0, 5), (0, 8),
            # Down
            (3, 0), (3, 3), (3, 6),
            (3, 1), (3, 4), (3, 7),
            (3, 2), (3, 5), (3, 8),
        ]
        color_map = {
            (0, 255, 0): "F",  # Green
            (0, 0, 255): "B",  # Blue
            (255, 255, 0): "D",  # Yellow
            (255, 0, 0): "R",  # Red
            (255, 128, 0): "L",  # Orange
            (255, 255, 255): "U"  # White
        }
        cube = ""
        for face_idx, square_idx in position_order:
            face = self.faces[face_idx]
            square = face.squares[square_idx]
            cube += color_map[square.color]
        return cube

    # used for kociemba to check if cube is solved
    def solve_cube(self, screen):
        self.move_list = []
        solution_steps = kociemba_solver(self)
        for step in solution_steps:
            self.faceTurn(step)
            self.draw(screen)
            pygame.display.flip()
            pygame.time.wait(500)
            if (self.stringify() == "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"):
                break
        return self.move_list

    # determines percent of white cross solved
    def percentSolved(self):
        total = 0.0

        for face in self.faces:
            middle_color = face.squares[4].color
            unsolved_count = sum(1 for square in face.squares if square.color != middle_color)
            face_percentage = unsolved_count / 9
            total += face_percentage

        average_percentage = total / 9
        return 1 - average_percentage

    # function to solve white cross
    def whiteCross(self):
        count = 0.0
        arr = [1, 3, 5, 7]
        for i in arr:
            if self.faces[4].squares[i].color == WHITE:
                count += 1.0
        if self.faces[0].squares[3].color == ORANGE:
            count += 1.0
        if self.faces[1].squares[3].color == GREEN:
            count += 1.0
        if self.faces[2].squares[3].color == RED:
            count += 1.0
        if self.faces[3].squares[3].color == BLUE:
            count += 1.0
        return count / 8

    # reverses parameter move
    def reverse_move(self, move):
        result = MOVE_REVERSALS[move]
        return result

    # creates sequence of moves
    def generate_random_sequence(self, length):
        possible_moves = ["U", "D", "L", "R", "F", "B", "U'", "D'", "L'", "R'", "F'", "B'"]
        return [random.choice(possible_moves) for _ in range(length)]

    # performs moves listed in sequence
    def sequence(self, sequence):
        for move in sequence:
            self.faceTurn(move)
            self.move_list.pop()

    # Determines the best sequence for solving the white cross
    def best_sequence(self, sequence, screen):
        for move in sequence:
            self.draw(screen)
            pygame.display.flip()
            pygame.time.wait(10)
            self.faceTurn(move)

    def reverse_sequence(self, sequence):
        # Apply the moves in reverse order to undo the sequence
        for move in reversed(sequence):
            self.faceTurn(self.reverse_move(move))
            self.move_list.pop()

    # Function to solve the entire cube
    def algo1(self, screen):
        self.solve_white_cross(screen)
        self.solve_white_corners(screen)
        self.second_layer(screen)
        self.yellow_cross(screen)
        self.swap_yellow_edges(screen)
        self.position_yellow_corners(screen)
        self.rotate_yellow_corners(screen)
        return self.move_list

    # function to solve white cross
    def solve_white_cross(self, screen):
        percent_solved = self.whiteCross()
        count = 1
        max_attempts = 2000  # max attempt number

        while percent_solved < 1.0:

            attempt_count = 0
            best_percent = percent_solved
            best_sequence = None

            while attempt_count < max_attempts:
                # max random sequence length
                sequence_length = random.randint(1, 20)
                sequence = self.generate_random_sequence(sequence_length)

                self.sequence(sequence)
                new_percent = self.whiteCross()

                if new_percent > best_percent:
                    best_percent = new_percent
                    best_sequence = sequence

                self.reverse_sequence(sequence)

                attempt_count += 1

            if best_sequence:
                # Apply the best sequence found
                self.best_sequence(best_sequence, screen)
                percent_solved = best_percent

            count += 1

    # function to solve white corners, place them into correct place and rotate into correct orientation
    def solve_white_corners(self, screen):

        def update_cube():
            self.draw(screen)
            pygame.display.flip()
            pygame.time.wait(10)
        #For corner on the top right
        def corner_alg():
            self.faceTurn("R'")
            update_cube()
            self.faceTurn("D'")
            update_cube()
            self.faceTurn("R")
            update_cube()
            self.faceTurn("D")
            update_cube()
        #Break inf loop
        def corner_fix_alg():
            self.faceTurn("D'")
            update_cube()
            self.faceTurn("R'")
            update_cube()
            self.faceTurn("D")
            update_cube()
            self.faceTurn("R")
            update_cube()

        def white_face_create():
            count = 0
            count2 = 0
            count3 = 0
            while (self.faces[4].squares[0].color != WHITE or self.faces[4].squares[2].color != WHITE or
                   self.faces[4].squares[6].color != WHITE or self.faces[4].squares[8].color != WHITE) and (count3 < 3):
                while (self.faces[4].squares[8].color == WHITE and count2 < 4):
                    self.cubeRotation("y", 0)
                    update_cube()
                    count2 += 1
                count2 = 0
                #logic to check if corner is the white one
                if self.faces[2].squares[2].color == WHITE:
                    if self.faces[4].squares[8].color != WHITE:
                        corner_alg()
                if self.faces[5].squares[6].color == WHITE:
                    if self.faces[4].squares[8].color != WHITE:
                        for _ in range(3):
                            corner_alg()
                if self.faces[1].squares[8].color == WHITE:
                    if self.faces[4].squares[8].color != WHITE:
                        for _ in range(5):
                            corner_alg()
                if count < 4:
                    self.faceTurn("D")
                    count += 1
                else:
                    self.cubeRotation("y", 0)
                    count = 0
                update_cube()
                count3 += 1

        def white_corner_fix():
            count4 = 0
            while count4 < 3:
                count5 = 0
                #if in loop run algo to break loop
                while self.faces[4].squares[8].color != WHITE and count5 < 4:
                    self.cubeRotation("y", 0)
                    update_cube()
                    count5 += 1
                if (self.faces[1].squares[6].color != self.faces[1].squares[3].color) and self.faces[4].squares[
                    8].color == WHITE:
                    corner_alg()
                    if self.faces[2].squares[2].color != self.faces[2].squares[4].color:
                        self.faceTurn("D")
                        update_cube()
                        self.cubeRotation("y", 0)
                    elif self.faces[3].squares[2].color != self.faces[3].squares[4].color:
                        self.faceTurn("D")
                        update_cube()
                        self.cubeRotation("y", 0)
                        self.cubeRotation("y", 0)
                    elif self.faces[0].squares[2].color != self.faces[0].squares[4].color:
                        self.faceTurn("D")
                        update_cube()
                        self.cubeRotation("y", 0)
                        self.cubeRotation("y", 0)
                        self.cubeRotation("y", 0)
                    corner_fix_alg()
                if self.faces[1].squares[6].color == self.faces[1].squares[3].color:
                    self.cubeRotation("y", 0)
                    update_cube()
                count4 += 1

        def get_unstuck1():
            self.faceTurn("F")
            update_cube()
            self.faceTurn("D")
            update_cube()
            self.faceTurn("F'")
            update_cube()

        def get_unstuck2():
            self.faceTurn("R'")
            update_cube()
            self.faceTurn("D")
            update_cube()
            self.faceTurn("R")
            update_cube()

        def is_solved():
            solved = True
            if self.faces[4].squares[0].color != WHITE:
                solved = False
            if self.faces[4].squares[2].color != WHITE:
                solved = False
            if self.faces[4].squares[6].color != WHITE:
                solved = False
            if self.faces[4].squares[8].color != WHITE:
                solved = False
            if (self.faces[0].squares[0].color or self.faces[0].squares[6].color) != self.faces[0].squares[3].color:
                solved = False
            if (self.faces[1].squares[0].color or self.faces[1].squares[6].color) != self.faces[1].squares[3].color:
                solved = False
            if (self.faces[2].squares[0].color or self.faces[2].squares[6].color) != self.faces[2].squares[3].color:
                solved = False
            if (self.faces[3].squares[0].color or self.faces[3].squares[6].color) != self.faces[3].squares[3].color:
                solved = False
            return solved

        while not is_solved():
            white_face_create()
            white_corner_fix()
            if self.faces[2].squares[0].color == WHITE:
                get_unstuck1()
            if self.faces[1].squares[6].color == WHITE:
                get_unstuck2()

    # function to solve second layer
    def second_layer(self, screen):
        self.cubeRotation("x", 0)
        self.cubeRotation("x", 0)
        #fast solve
        def update_cube():
            self.draw(screen)
            pygame.display.flip()
            pygame.time.wait(10)
        #logic to see if second layer is filled
        def is_solved():
            solved = True
            if (self.faces[0].squares[1].color != self.faces[0].squares[4].color) or (
                    self.faces[0].squares[7].color != self.faces[0].squares[4].color):
                solved = False
            if (self.faces[1].squares[1].color != self.faces[1].squares[4].color) or (
                    self.faces[1].squares[7].color != self.faces[1].squares[4].color):
                solved = False
            if (self.faces[2].squares[1].color != self.faces[2].squares[4].color) or (
                    self.faces[2].squares[7].color != self.faces[2].squares[4].color):
                solved = False
            if (self.faces[3].squares[1].color != self.faces[3].squares[4].color) or (
                    self.faces[3].squares[7].color != self.faces[3].squares[4].color):
                solved = False
            return solved
        #For when you place into left middle
        def left_alg():
            arr = ["U'", "L'", "U'", "L", "U", "F", "U", "F'", "U'"]
            for element in arr:
                self.faceTurn(element)
                update_cube()
        # For when you place into right middle
        def right_alg():
            arr = ["U", "R", "U", "R'", "U'", "F'", "U'", "F", "U"]
            for element in arr:
                self.faceTurn(element)
                update_cube()
        #Same as right but is used to break out of inf loop
        def wrong_orientation():
            arr = ["U", "R", "U", "R'", "U'", "F'", "U'", "F", "U"]
            for element in arr:
                self.faceTurn(element)
                update_cube()
        #If cube above middle equal middle then run algo to right place otherwise turn to see if it equals the next face
        def checkFront():
            for i in range(3):
                if self.faces[1].squares[4].color == self.faces[1].squares[3].color:
                    if self.faces[4].squares[5].color == self.faces[0].squares[4].color:
                        left_alg()
                        return False
                    if self.faces[4].squares[5].color == self.faces[2].squares[4].color:
                        right_alg()
                        return False
                else:
                    self.faceTurn("U")
                    update_cube()
                if self.faces[1].squares[4].color == self.faces[1].squares[3].color:
                    if self.faces[4].squares[5].color == self.faces[0].squares[7].color:
                        left_alg()
                        return False
                    if self.faces[4].squares[5].color == self.faces[2].squares[1].color:
                        right_alg()
                        return False
            return True
        #Check to see if middle left or right are swapped with left or right face
        def checkAdjacent():
            for i in range(3):
                if (self.faces[1].squares[7].color == self.faces[2].squares[4].color) or (
                        self.faces[2].squares[1].color == self.faces[1].squares[4].color):
                    wrong_orientation()
                elif (self.faces[1].squares[7].color == self.faces[3].squares[4].color) or (
                        self.faces[3].squares[1].color == self.faces[1].squares[4].color):
                    wrong_orientation()
                self.cubeRotation("y", 0)
                update_cube()
        #if yellow is in middle
        def checkYellow():
            for i in range(4):
                if self.faces[i].squares[1] == YELLOW:
                    wrong_orientation()
                if self.faces[i].squares[7] == YELLOW:
                    wrong_orientation()

        count = 0
        while not is_solved():
            #if in inf loop break it
            if count % 50 == 0:
                wrong_orientation()
            checkFront()
            checkAdjacent()
            checkYellow()
            count += 1
        update_cube()

    def yellow_cross(self, screen):
        # Helper function to update the cube display
        def update_cube():
            self.draw(screen)
            pygame.display.flip()
            pygame.time.wait(10)

        # Initial update of the cube display
        update_cube()

        # Function to check if the yellow cross is solved
        def is_solved():
            solved = True
            arr = [1, 3, 5, 7]
            for i in arr:
                if self.faces[4].squares[i].color != YELLOW:
                    solved = False
            return solved

        # Algorithm to form the yellow cross
        def cross_alg():
            self.faceTurn("F")
            update_cube()
            self.faceTurn("R")
            update_cube()
            self.faceTurn("U")
            update_cube()
            self.faceTurn("R'")
            update_cube()
            self.faceTurn("U'")
            update_cube()
            self.faceTurn("F'")
            update_cube()

        # Check if the yellow cross is solved
        yellow_cross = is_solved()
        while yellow_cross == False:
            correct_pos = []
            # Check which edges of the top face are yellow
            if self.faces[4].squares[1].color == YELLOW:
                correct_pos.append(1)
            if self.faces[4].squares[3].color == YELLOW:
                correct_pos.append(3)
            if self.faces[4].squares[5].color == YELLOW:
                correct_pos.append(5)
            if self.faces[4].squares[7].color == YELLOW:
                correct_pos.append(7)

            if len(correct_pos) == 4:
                yellow_cross = True
            else:
                if len(correct_pos) == 0 or (1 in correct_pos and 7 in correct_pos) or (
                        5 in correct_pos and 7 in correct_pos):
                    cross_alg()
                if (3 in correct_pos and 5 in correct_pos) or (3 in correct_pos and 7 in correct_pos):
                    self.cubeRotation("y", 1)
                    cross_alg()
                    self.cubeRotation("y", 0)
                if (1 in correct_pos and 3 in correct_pos):
                    self.cubeRotation("y", 1)
                    self.cubeRotation("y", 1)
                    cross_alg()
                    self.cubeRotation("y", 1)
                    self.cubeRotation("y", 1)
                if (1 in correct_pos and 5 in correct_pos):
                    self.cubeRotation("y", 0)
                    cross_alg()
                    self.cubeRotation("y", 1)

    def swap_yellow_edges(self, screen):
        # Helper function to update the cube display
        def update_cube():
            self.draw(screen)
            pygame.display.flip()
            pygame.time.wait(10)

        # Initial update of the cube display
        update_cube()

        # Function to check if the yellow edges are correctly positioned
        def is_solved():
            solved = True
            if self.faces[0].squares[3].color != self.faces[0].squares[4].color:
                solved = False
            if self.faces[1].squares[3].color != self.faces[1].squares[4].color:
                solved = False
            if self.faces[2].squares[3].color != self.faces[2].squares[4].color:
                solved = False
            if self.faces[3].squares[3].color != self.faces[3].squares[4].color:
                solved = False
            return solved

        # Algorithm to swap yellow edges
        def swap_alg():
            arr = ["R", "U", "R'", "U", "R", "U", "U", "R'", "U"]
            for element in arr:
                self.faceTurn(element)
                update_cube()

        # Loop until the yellow edges are correctly positioned
        while not is_solved():
            for i in range(4):
                if is_solved():
                    break
                if self.faces[1].squares[3].color == self.faces[0].squares[4].color:
                    swap_alg()
                    break
                elif self.faces[2].squares[3].color == self.faces[0].squares[4].color:
                    self.faceTurn("U")
                    update_cube()
                    swap_alg()
                    self.cubeRotation("y", 0)
                    update_cube()
                    self.cubeRotation("y", 0)
                    update_cube()
                    swap_alg()
                elif self.faces[1].squares[3].color == self.faces[2].squares[4].color:
                    # reversed_swap_alg()
                    pass
                self.cubeRotation("y", 0)
                update_cube()
                if is_solved():
                    break
        update_cube()

    def position_yellow_corners(self, screen):
        # Helper function to update the cube display
        def update_cube():
            self.draw(screen)
            pygame.display.flip()
            pygame.time.wait(10)

        # Function to check if the front right corner is correctly positioned
        def checkCloseRightCorner():
            face_colors = {self.faces[4].squares[4].color, self.faces[1].squares[4].color,
                           self.faces[2].squares[4].color}
            corner_colors = {self.faces[4].squares[8].color, self.faces[1].squares[6].color,
                             self.faces[2].squares[0].color}
            return face_colors == corner_colors

        # Algorithm to swap yellow corners
        def swap_alg():
            arr = ["U", "R", "U'", "L'", "U", "R'", "U'", "L"]
            for element in arr:
                self.faceTurn(element)
                update_cube()

        # Initial update of the cube display
        update_cube()

        counter = 0
        correctCorner = False

        # Position the yellow corners correctly
        while correctCorner == False:
            if counter < 4:
                self.cubeRotation("y", 0)
                update_cube()
                correctCorner = checkCloseRightCorner()
                counter += 1
            else:
                swap_alg()
                break

        correctCorner = False
        while correctCorner == False:
            self.cubeRotation("y", 0)
            update_cube()
            correctCorner = checkCloseRightCorner()

        for i in range(4):
            self.cubeRotation("y", 0)
            update_cube()
            correctCorner = checkCloseRightCorner()
            if correctCorner == False:
                self.cubeRotation("y", 1)
                update_cube()
                swap_alg()
            else:
                break

    def rotate_yellow_corners(self, screen):
        # Helper function to update the cube display
        def update_cube():
            self.draw(screen)
            pygame.display.flip()
            pygame.time.wait(10)

        # Algorithm to rotate yellow corners
        def alg():
            moves = ["R", "U", "U", "R'", "U'", "R", "U'", "R'", "L'", "U", "U", "L", "U", "L'", "U", "L"]
            for move in moves:
                self.faceTurn(move)
                update_cube()
        # Loop until the cube is solved
        while self.isSolved() == False:
            if YELLOW in {self.faces[4].squares[0].color, self.faces[4].squares[2].color,
                          self.faces[4].squares[6].color, self.faces[4].squares[8].color}:
                if self.faces[2].squares[0].color == YELLOW or self.faces[2].squares[6].color == YELLOW:
                    alg()
                elif self.faces[1].squares[6].color == YELLOW and self.faces[3].squares[0].color == YELLOW:
                    alg()
                else:
                    self.cubeRotation("y", 0)
            else:
                alg()
        # Adjust the cube orientation if necessary
        if self.faces[4].squares[4].color == YELLOW:
            self.cubeRotation("x", 0)
            self.cubeRotation("x", 0)
        for i in range(4):
            if self.faces[1].squares[4].color != GREEN:
                self.cubeRotation("y", 0)
                update_cube()


class Face(pygame.sprite.Sprite):
    def __init__(self, xpos, ypos, size, initial_color):
        pygame.sprite.Sprite.__init__(self)
        self.xpos = xpos
        self.ypos = ypos
        self.size = size
        self.initial_color = initial_color
        self.squares = []
        self.init_squares()
    #builds face
    def init_squares(self):
        color = self.initial_color
        for i in range(3):
            for j in range(3):
                # square creation
                square = Square(self.xpos + j * self.size, self.ypos + i * self.size, self.size, self.initial_color)
                self.squares.append(square)

    def recalculate_squares(self):
        count = 0
        for square in self.squares:
            square.xpos = self.xpos + (count // 3) * self.size
            square.ypos = self.ypos + (count % 3) * self.size
            count += 1

    # draws a 3x3 face
    def drawFace(self, screen):
        top_left_x = self.squares[0].xpos
        top_left_y = self.squares[0].ypos

        for square in self.squares:
            square.drawSquare(screen)

        # draw the outline
        big_rect = pygame.Rect(top_left_x, top_left_y, self.size * 3, self.size * 3)
        pygame.draw.rect(screen, (0, 0, 0), big_rect, 2)


class Square(pygame.sprite.Sprite):
    #x and y for each cube
    def __init__(self, xpos, ypos, size, color):
        pygame.sprite.Sprite.__init__(self)
        self.xpos = xpos
        self.ypos = ypos
        self.size = size
        self.color = color

    def drawSquare(self, screen):
        rect = pygame.Rect(self.xpos, self.ypos, self.size, self.size)
        pygame.draw.rect(screen, self.color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 1)

    def recolor(self, color):
        self.color = color
