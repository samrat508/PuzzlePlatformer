# Simon Says file, based on the skeleton, DevRoom, and teleportation room created by Sage Petersen
# Modified by Jordan Pope
# Start date 4.14.2026
import time
import pygame
import random
from datetime import datetime
d0 = datetime(2008, 8, 18)
d1 = datetime.now()
delta = d1 - d0
can_start = False
is_solved = False
player_input = []
sequence_list = [random.randint(1, 3),
                 random.randint(1, 3),
                 random.randint(1, 3),
                 random.randint(1, 3),
                 random.randint(1, 3)]
print(sequence_list)
# ============================
# Creating assets
# ============================
blue_button_unpressed_img = pygame.image.load('assets/FloorButtonBlueOn.png').convert_alpha()
blue_button_pressed_img = pygame.image.load('assets/FloorButtonBlueOff.png').convert_alpha()
green_button_unpressed_img = pygame.image.load('assets/FloorButtonGreenOn.png').convert_alpha()
green_button_pressed_img = pygame.image.load('assets/FloorButtonGreenOff.png').convert_alpha()
red_button_unpressed_img = pygame.image.load('assets/FloorButtonRedOn.png').convert_alpha()
red_button_pressed_img = pygame.image.load('assets/FloorButtonRedOff.png').convert_alpha()
start_button_pressed_img = pygame.image.load('assets/FloorButtonOff.png').convert_alpha()
start_button_unpressed_img = pygame.image.load('assets/FloorButtonOnV2.png').convert_alpha()
pressed_states = [False, False, False, False]
blue_chime = pygame.mixer.Sound('assets/chimeTone1.wav')
green_chime = pygame.mixer.Sound('assets/chimeTone2.wav')
red_chime = pygame.mixer.Sound('assets/chimeTone3.wav')
error_noise = pygame.mixer.Sound('assets/ErrorSound.wav')

def render(surface, hitbox, event, tile_size):
    global is_solved
    global can_start
    global sequence_list
    global pressed_states
    global player_input
    blue_button_pressed = pygame.transform.scale(blue_button_pressed_img, (tile_size, tile_size))
    blue_button_unpressed = pygame.transform.scale(blue_button_unpressed_img, (tile_size, tile_size))
    green_button_unpressed = pygame.transform.scale(green_button_unpressed_img, (tile_size, tile_size))
    green_button_pressed = pygame.transform.scale(green_button_pressed_img, (tile_size, tile_size))
    red_button_unpressed = pygame.transform.scale(red_button_unpressed_img, (tile_size, tile_size))
    red_button_pressed = pygame.transform.scale(red_button_pressed_img, (tile_size, tile_size))
    start_button_pressed = pygame.transform.scale(start_button_pressed_img, (tile_size, tile_size))
    start_button_unpressed = pygame.transform.scale(start_button_unpressed_img, (tile_size, tile_size))
    buttons = [
        {"id": "start_button", "rect": pygame.Rect(tile_size * 7, tile_size * 6, tile_size, tile_size), "pressed sprite": start_button_pressed, "unpressed sprite": start_button_unpressed},
            {"id": "blue_button", "rect": pygame.Rect(tile_size * 5, tile_size * 5, tile_size, tile_size), "pressed sprite": blue_button_pressed, "unpressed sprite": blue_button_unpressed, "chime": blue_chime},
            {"id": "green_button", "rect": pygame.Rect(tile_size * 7, tile_size * 5, tile_size, tile_size), "pressed sprite": green_button_pressed, "unpressed sprite": green_button_unpressed, "chime": green_chime},
            {"id": "red_button", "rect": pygame.Rect(tile_size * 9, tile_size * 5, tile_size, tile_size), "pressed sprite": red_button_pressed, "unpressed sprite": red_button_unpressed, "chime": red_chime}
        ]
    #=======
    # Button logic
    #=======
    for index, btn in enumerate(buttons):
        if hitbox.colliderect(btn["rect"]):
            pressed_states[index] = True
        elif pressed_states[index] and not hitbox.colliderect(btn["rect"]):
            if index != 0:
                btn["chime"].play()
                if can_start:
                    player_input.append(index)
                    print(player_input)
            if index == 0:
                i = 0
                while i < len(sequence_list):
                    if sequence_list[i] == 1:
                        blue_chime.play()
                        time.sleep(.5)
                    if sequence_list[i] == 2:
                        green_chime.play()
                        time.sleep(.5)
                    if sequence_list[i] == 3:
                        red_chime.play()
                        time.sleep(.5)
                    time.sleep(.5)
                    i += 1
                can_start = True
            pressed_states[index] = False
        if len(player_input) == len(sequence_list):
            if player_input == sequence_list:
                is_solved = True
            else:
                is_solved = False
                error_noise.play()
                player_input = []

    # ============
    # RENDERING
    # ============
    for index, btn in enumerate(buttons):
        if pressed_states[index]:
            surface.blit(btn["pressed sprite"], (btn["rect"].x, btn["rect"].y))
        else:
            surface.blit(btn["unpressed sprite"], (btn["rect"].x, btn["rect"].y))



def set_solved(solved):
    global is_solved
    is_solved = solved
    return is_solved
def get_solved():
    global is_solved
    return is_solved
