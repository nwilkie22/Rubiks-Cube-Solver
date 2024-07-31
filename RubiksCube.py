import pygame
import random

# define colors
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 128, 0)
WHITE = (255, 255, 255)
colorList = [BLUE, GREEN, YELLOW, RED, WHITE, ORANGE]

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

class RubiksCube(pygame.sprite.Sprite):
    def __init__(self, xpos, ypos, size = 30):
        pygame.sprite.Sprite.__init__(self)
        self.xpos = xpos
        self.ypos = ypos
        self.size = size
        # stores all the face objects in this order
        # "left", "front", "right", "back", "up", "down"
        self.faces = []
        self.init_faces()

    def init_faces(self):
        temp_color_list = colorList

        # L -> B faces
        for i in range(4):
            color = temp_color_list.pop()
            # we need to loop this 6 times changing the position as required for the six faces
            face = Face(self.xpos + i * self.size * 3, self.ypos, self.size, color)
            self.faces.append(face)

        # up face
        color = temp_color_list.pop()
        print("recalculating: xpos: " + str(self.xpos) + " + self.size: " + str(self.size))
        face = Face(self.xpos + self.size * 3, self.ypos - self.size * 3, self.size, color)
        self.faces.append(face)

        # down face
        color = temp_color_list.pop()
        print("recalculating: ypos: " + str(self.ypos) + " - self.size: " + str(self.size))
        face = Face(self.xpos + self.size * 3, self.ypos + self.size * 3, self.size, color)
        self.faces.append(face)


        #self.faces[1].squares[0].recolor(RED)  --- For Debugging Face Turn

    def recalculate_faces(self):
        # L -> B
        for i in range(4):
            self.faces[i].xpos = self.xpos + i * self.size * 3
            self.faces[i].ypos = self.ypos
            print("Face " + str(i) + " pos " + str(self.faces[i].xpos) + " + " + str(self.faces[i].ypos))
        # up
        self.faces[4].xpos = self.xpos + self.size * 3
        self.faces[4].ypos = self.ypos - self.size * 3
        print("Face 4 pos " + str(self.faces[4].xpos) + " + " + str(self.faces[4].ypos))
        # down
        self.faces[5].xpos = self.xpos + self.size * 3
        self.faces[5].ypos = self.ypos + self.size * 3
        print("Face 5 pos " + str(self.faces[5].xpos) + " + " + str(self.faces[5].ypos))
        print()

        for face in self.faces:
            print("Face: " + str(face.initial_color))
            face.recalculate_squares()

    def draw(self, screen):
        for face in self.faces:
            face.drawFace(screen)

    # ROTATIO
    # reference for moves
    # https://jperm.net/3x3/moves
    def cubeRotation(self, rotation_type, direction):
        # does not move any squares in relation to each other
        # just changes which face is at the front
        # 3 rotation types: x: R direction, y: U direction, and z: F direction
        # 2 directions: 0: Up/Left, 1: Down/Right
        # initial order: 0, 1, 2, 3, 4, 5

        # rotation types
        if rotation_type == "x":  # Rotating around the x-axis
            if direction == 0:  # Left
                new_order = [1, 2, 3, 0, 4, 5]
            elif direction == 1:  # Right
                new_order = [3, 0, 1, 2, 4, 5]
            else:
                raise ValueError("Invalid direction")

        elif rotation_type == "y":  # Rotating around the y-axis
            if direction == 0:  # Up
                new_order = [0, 5, 2, 4, 1, 3]
            elif direction == 1:  # Down
                new_order = [0, 4, 2, 5, 3, 1]
            else:
                raise ValueError("Invalid direction.")

        elif rotation_type == "z":  # Rotating around the z-axis
            if direction == 0:  # Left
                new_order = [4, 1, 5, 3, 2, 0]
            elif direction == 1:  # Right
                new_order = [5, 1, 4, 3, 2, 0]
            else:
                raise ValueError("Invalid direction.")

        else:
            raise ValueError("Invalid rotation type.")

        # reorder the "faces" array to reflect the rotation
        new_faces = []
        for num in new_order:
            new_faces.append(self.faces[num])
        self.faces = new_faces

        for face in self.faces:
            print("Face: " + str(face.initial_color))

        self.recalculate_faces()

    def squareSwap(self, colors_to_move, squares_to_move_to):
        temp = [squares_to_move_to[0].color, squares_to_move_to[1].color, squares_to_move_to[2].color]
        for i in range(3):
            print("Color: " + str(colors_to_move[0]) + " moving to: " + str(squares_to_move_to[0].color))
            squares_to_move_to[i].color = colors_to_move[i]
        return temp

    def faceRotate(self, face, direction):
        # 0: clockwise 1: counter-clockwise
        if direction == 0:
            new_order = [2, 1, 8, 1, 4, 7, 0, 3, 6]
        elif direction == 1:
            new_order = [6, 3, 0, 7, 4, 1, 8, 5, 2]
        else:
            raise ValueError("Invalid direction.")

        new_squares = []
        for num in new_order:
            new_squares.append(face.squares[num])
        print()
        print("FACE ROTATE")
        for square in face.squares:
            print("Square: " + str(square.color))
        print()
        face.squares = new_squares

    def faceTurn(self, rotation_type, direction):
        # rotate a face (will affect adjacent faces)
        # rotation type is in relation to the front face (see https://jperm.net/3x3/moves)
        # 6 rotation types: U: up, D: down, R: right, L: left, F: front, B: back
        # 2 directions: 0: clockwise, 1: counterclockwise

        current_face = self.faces[1]
        # UP
        if rotation_type == "U":
            colors_to_move = [current_face.squares[0].color, current_face.squares[3].color, current_face.squares[6].color]

            # part 1
            if direction == 0:
                next_face = self.faces[0]
            elif direction == 1:
                next_face = self.faces[2]
            else:
                raise ValueError("Invalid direction.")

            squares_to_move_to = [next_face.squares[0], next_face.squares[3], next_face.squares[6]]
            colors_to_move = self.squareSwap(colors_to_move, squares_to_move_to)

            # part 2
            next_face = self.faces[3]
            squares_to_move_to = [next_face.squares[0], next_face.squares[3], next_face.squares[6]]
            colors_to_move = self.squareSwap(colors_to_move, squares_to_move_to)

            # part 3
            if direction == 0:
                next_face = self.faces[2]
            else:
                next_face = self.faces[0]
            squares_to_move_to = [next_face.squares[0], next_face.squares[3], next_face.squares[6]]
            colors_to_move = self.squareSwap(colors_to_move, squares_to_move_to)

            # part 4
            next_face = self.faces[1]
            squares_to_move_to = [next_face.squares[0], next_face.squares[3], next_face.squares[6]]
            self.squareSwap(colors_to_move, squares_to_move_to)

        # DOWN
        elif rotation_type == "D":
            colors_to_move = [current_face.squares[2].color, current_face.squares[5].color, current_face.squares[8].color]

            # part 1
            if direction == 0:
                next_face = self.faces[2]
            elif direction == 1:
                next_face = self.faces[0]
            else:
                raise ValueError("Invalid direction.")

            squares_to_move_to = [next_face.squares[2], next_face.squares[5], next_face.squares[8]]
            colors_to_move = self.squareSwap(colors_to_move, squares_to_move_to)

            # part 2
            next_face = self.faces[3]
            squares_to_move_to = [next_face.squares[2], next_face.squares[5], next_face.squares[8]]
            colors_to_move = self.squareSwap(colors_to_move, squares_to_move_to)

            # part 3
            if direction == 0:
                next_face = self.faces[0]
            else:
                next_face = self.faces[2]
            squares_to_move_to = [next_face.squares[2], next_face.squares[5], next_face.squares[8]]
            colors_to_move = self.squareSwap(colors_to_move, squares_to_move_to)

            # part 4
            next_face = self.faces[1]
            squares_to_move_to = [next_face.squares[2], next_face.squares[5], next_face.squares[8]]
            self.squareSwap(colors_to_move, squares_to_move_to)

        # RIGHT
        elif rotation_type == "R":
            colors_to_move = [current_face.squares[6].color, current_face.squares[7].color, current_face.squares[8].color]

            # part 1
            if direction == 0:
                next_face = self.faces[4]
            elif direction == 1:
                next_face = self.faces[5]
            else:
                raise ValueError("Invalid direction.")

            squares_to_move_to = [next_face.squares[6], next_face.squares[7], next_face.squares[8]]
            colors_to_move = self.squareSwap(colors_to_move, squares_to_move_to)

            # part 2
            next_face = self.faces[3]
            squares_to_move_to = [next_face.squares[6], next_face.squares[7], next_face.squares[8]]
            colors_to_move = self.squareSwap(colors_to_move, squares_to_move_to)

            # part 3
            if direction == 0:
                next_face = self.faces[5]
            else:
                next_face = self.faces[4]
            squares_to_move_to = [next_face.squares[6], next_face.squares[7], next_face.squares[8]]
            colors_to_move = self.squareSwap(colors_to_move, squares_to_move_to)

            # part 4
            next_face = self.faces[1]
            squares_to_move_to = [next_face.squares[6], next_face.squares[7], next_face.squares[8]]
            self.squareSwap(colors_to_move, squares_to_move_to)

        #LEFT
        elif rotation_type == "L":
            colors_to_move = [current_face.squares[0].color, current_face.squares[1].color, current_face.squares[2].color]

            # part 1
            if direction == 0:
                next_face = self.faces[5]
            elif direction == 1:
                next_face = self.faces[4]
            else:
                raise ValueError("Invalid direction.")

            squares_to_move_to = [next_face.squares[0], next_face.squares[1], next_face.squares[2]]
            colors_to_move = self.squareSwap(colors_to_move, squares_to_move_to)

            # part 2
            next_face = self.faces[3]
            squares_to_move_to = [next_face.squares[0], next_face.squares[1], next_face.squares[2]]
            colors_to_move = self.squareSwap(colors_to_move, squares_to_move_to)

            # part 3
            if direction == 0:
                next_face = self.faces[4]
            else:
                next_face = self.faces[5]
            squares_to_move_to = [next_face.squares[0], next_face.squares[1], next_face.squares[2]]
            colors_to_move = self.squareSwap(colors_to_move, squares_to_move_to)

            # part 4
            next_face = self.faces[1]
            squares_to_move_to = [next_face.squares[0], next_face.squares[1], next_face.squares[2]]
            self.squareSwap(colors_to_move, squares_to_move_to)

        # FRONT
        elif rotation_type == "F":
            self.faceRotate(current_face, 0)

            side_face = self.faces[2]
            colors_to_move = [side_face.squares[0].color, side_face.squares[1].color, side_face.squares[2].color]

            # part 1
            if direction == 0:
                next_face = self.faces[5]
            elif direction == 1:
                next_face = self.faces[4]
            else:
                raise ValueError("Invalid direction.")

            squares_to_move_to = [next_face.squares[0], next_face.squares[3], next_face.squares[6]]
            colors_to_move = self.squareSwap(colors_to_move, squares_to_move_to)

            # part 2
            next_face = self.faces[0]
            squares_to_move_to = [next_face.squares[6], next_face.squares[7], next_face.squares[8]]
            colors_to_move = self.squareSwap(colors_to_move, squares_to_move_to)

            # part 3
            if direction == 0:
                next_face = self.faces[4]
            else:
                next_face = self.faces[5]
            squares_to_move_to = [next_face.squares[2], next_face.squares[5], next_face.squares[8]]
            colors_to_move = self.squareSwap(colors_to_move, squares_to_move_to)

            # part 4
            next_face = self.faces[2]
            squares_to_move_to = [next_face.squares[0], next_face.squares[1], next_face.squares[2]]
            self.squareSwap(colors_to_move, squares_to_move_to)

        # BACK
        elif rotation_type == "B":
            back_face = self.faces[3]
            self.faceRotate(back_face, 0)

            side_face = self.faces[2]
            colors_to_move = [side_face.squares[6].color, side_face.squares[7].color, side_face.squares[8].color]

            # part 1
            if direction == 0:
                next_face = self.faces[4]
            elif direction == 1:
                next_face = self.faces[5]
            else:
                raise ValueError("Invalid direction.")

            squares_to_move_to = [next_face.squares[0], next_face.squares[3], next_face.squares[6]]
            colors_to_move = self.squareSwap(colors_to_move, squares_to_move_to)

            # part 2
            next_face = self.faces[0]
            squares_to_move_to = [next_face.squares[0], next_face.squares[1], next_face.squares[2]]
            colors_to_move = self.squareSwap(colors_to_move, squares_to_move_to)

            # part 3
            if direction == 0:
                next_face = self.faces[5]
            else:
                next_face = self.faces[4]
            squares_to_move_to = [next_face.squares[2], next_face.squares[5], next_face.squares[8]]
            colors_to_move = self.squareSwap(colors_to_move, squares_to_move_to)

            # part 4
            next_face = self.faces[2]
            squares_to_move_to = [next_face.squares[6], next_face.squares[7], next_face.squares[8]]
            self.squareSwap(colors_to_move, squares_to_move_to)

        # ERROR
        else:
            raise ValueError("Invalid rotation type.")

        # ensure that colors are updated correctly
        self.recalculate_faces()



    # This function is just doing two moves at once so it should be easy once we figure out face turn
    def wideMove(self):
        print()

    def sliceMove(self):
        print()

    # HELPER FUNCTIONS
    def printfaces(self):
        for face in self.faces:
            print(face.squares[0].color)
    def isSolved(self):
        for face in self.faces:
            for square in face.squares:
                test_color = face.squares[0].color
                if square.color != test_color:
                    return False
        return True


class Face(pygame.sprite.Sprite):
    def __init__(self, xpos, ypos, size, initial_color):
        pygame.sprite.Sprite.__init__(self)
        self.xpos = xpos
        self.ypos = ypos
        self.size = size
        self.initial_color = initial_color
        self.squares = []
        self.init_squares()

    def init_squares(self):
        color = self.initial_color
        for i in range(3):
            for j in range(3):
                # square creation
                square = Square(self.xpos + i * self.size, self.ypos + j * self.size, self.size, self.initial_color)
                self.squares.append(square)

    def recalculate_squares(self):
        count = 0
        for square in self.squares:
            square.xpos = self.xpos + (count // 3) * self.size
            square.ypos = self.ypos + (count % 3) * self.size
            print("square " + str(count) + " pos: " + (str(square.xpos)) + ", " + (str(square.ypos)))
            count += 1
        print()

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
