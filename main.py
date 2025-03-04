# Rubiks Cube Project by Lance Tan, Pablo Sabogal, Nic Wilkie
import pygame, sys
import kociemba
from RubiksCube import RubiksCube

pygame.font.init()

#General function to draw buttons

def draw_button(screen, text, button_x, button_y, size):
    button_color = (255, 99, 71)
    text_color = (255, 255, 255)
    font = pygame.font.Font(None, size)
    button_width = len(text) * size/2
    button_height = 75
    button_surface = pygame.Surface((button_width, button_height))
    button_surface.fill(button_color)
    text_surface = font.render(text, True, text_color)
    text_x = (button_width - text_surface.get_width()) // 2
    text_y = (button_height - text_surface.get_height()) // 2
    # Blit the text surface onto the button surface
    button_surface.blit(text_surface, (text_x, text_y))
    button_surface.blit(text_surface, (100, 100))
    b = screen.blit(button_surface, (button_x, button_y))
    return b

#General function to draw text
def draw_text(surface, text, font, color, pos):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=pos)
    b = surface.blit(text_surface, text_rect)
    return b

def draw():
    screen.fill(background_color)
    cube.draw(screen)
    draw_button(screen, "Kociemba", 320, 600, 50)
    draw_button(screen, "Beginner Method", 30, 600, 35)
    draw_button(screen, "Scramble", 550, 600, 50)
    draw_text(screen, title_text, big_font, text_color_black, (400, 30))
    draw_text(screen, alg_log_text, font, text_color_black, (185, 180))
    draw_move_list()
    pygame.display.flip()

def draw_move_list():
    count = 0
    for line in move_list_text:
        y = 100 + 20 * count
        draw_text(screen, line, small_font, text_color_black, (650, y))
        count += 1

def append_move_list(solve_type, size):
    if len(move_list_text) == 10:
        move_list_text.pop(0)
    text = solve_type
    text += " - Moves: "
    text += str(size)
    move_list_text.append(text)

background_color = (255, 255, 255)

screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption('Rubiks Cube Solver')

# setup move log text vars
small_font = pygame.font.SysFont(None, 30)
font = pygame.font.Font(None, 50)
big_font = pygame.font.Font(None, 75)
text_color_black = (0, 0, 0)
text = ""
title_text = "Rubiks Cube Solver"
alg_log_text = ""
move_list_text = []
prime1 = "Prime On"
not_prime1 = "Prime Off"
prime_text = "Prime Off"
U_rotation = "Up rotation press U"
D_rotation = "Down rotation press D"
R_rotation = "Right rotation press R"
L_rotation = "Left rotation press L"
F_rotation = "Forward rotation press F"
B_rotation = "Backward rotation press B"

screen.fill(background_color)
#Make the cube object
cube = RubiksCube(50, 300)
print(cube.isSolved())
active = True
prime = False
sort_running = False

while active:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            active = False

        # temp code for testing rotations
        # Press key for rotation, press space to switch from prime to not prime
        if event.type == pygame.KEYDOWN:
            # Prime toggle
            if event.key == pygame.K_SPACE:
                prime = not prime
                if prime:
                    print("Prime")
                    prime_text = prime1
                else:
                    print("Not Prime")
                    prime_text = not_prime1
            # Basic moves
            if event.key == pygame.K_u:
                if prime == False:
                    text = cube.faceTurn("U")
                else:
                    text = cube.faceTurn("U'")

            if event.key == pygame.K_d:
                if prime == False:
                    text = cube.faceTurn("D")
                else:
                    text = cube.faceTurn("D'")

            if event.key == pygame.K_l:
                if prime == False:
                    text = cube.faceTurn("L")
                else:
                    text = cube.faceTurn("L'")

            if event.key == pygame.K_r:
                if prime == False:
                    text = cube.faceTurn("R")
                else:
                    text = cube.faceTurn("R'")

            if event.key == pygame.K_f:
                if prime == False:
                    text = cube.faceTurn("F")
                else:
                    text = cube.faceTurn("F'")

            if event.key == pygame.K_b:
                if prime == False:
                    text = cube.faceTurn("B")
                else:
                    text = cube.faceTurn("B'")

            if event.key == pygame.K_x:
                if prime == False:
                    cube.cubeRotation("x", 0)
                else:
                    cube.cubeRotation("x", 1)
            if event.key == pygame.K_y:
                if prime == False:
                    cube.cubeRotation("y", 0)
                else:
                    cube.cubeRotation("y", 1)
            if event.key == pygame.K_k:
                if prime == False:
                    cube.rotation(0)
                else:
                    cube.rotation(1)
            if event.key == pygame.K_o:
                cube.percentSolved()

            # Slice moves
            if event.key == pygame.K_s:
                cube.faceTurn("S")
            if event.key == pygame.K_m:
                cube.faceTurn("M")
            if event.key == pygame.K_e:
                cube.faceTurn("E")
            if event.key == pygame.K_p:
                cube.solve_cube(screen)
                print(cube.solve_cube(screen))
            check = cube.stringify()
            print(check)
            # Wide moves
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not sort_running:
                # Buttons
                mouse_x, mouse_y = event.pos
                if scramble.collidepoint(mouse_x, mouse_y):
                    sort_running = True
                    cube.scramble()
                    alg_log_text = "Scrambled"
                    sort_running = False
                if kociemba.collidepoint(mouse_x, mouse_y):
                    sort_running = True
                    alg_log_text = "Running Kociemba"
                    draw()
                    moves = cube.solve_cube(screen)
                    append_move_list("Kociemba", len(moves))
                    sort_running = False
                if other.collidepoint(mouse_x, mouse_y):
                    sort_running = True
                    alg_log_text = "Running BM"
                    draw()
                    moves = cube.algo1(screen)
                    append_move_list("BM", len(moves))
                    sort_running = False
        if cube.isSolved():
            alg_log_text = "Solved"
    #Draw everything on the screen
    screen.fill(background_color)
    cube.draw(screen)
    kociemba = draw_button(screen, "Kociemba", 320, 600, 50)
    other = draw_button(screen, "Beginner Method", 30, 600, 35)
    scramble = draw_button(screen, "Scramble", 550, 600, 50)
    title = draw_text(screen, title_text, big_font, text_color_black, (400, 30))
    alg_log = draw_text(screen, alg_log_text, font, text_color_black, (185, 180))
    prime_main = draw_text(screen, prime_text, small_font, text_color_black, (475, 380))
    R_main = draw_text(screen, R_rotation, small_font, text_color_black, (110, 550))
    D_main = draw_text(screen, D_rotation, small_font, text_color_black, (380, 550))
    F_main = draw_text(screen, F_rotation, small_font, text_color_black, (663, 500))
    L_main = draw_text(screen, L_rotation, small_font, text_color_black, (110, 500))
    U_main = draw_text(screen, U_rotation, small_font, text_color_black, (380, 500))
    B_main = draw_text(screen, B_rotation, small_font, text_color_black, (665, 550))
    draw_move_list()
    pygame.display.flip()

pygame.quit()
