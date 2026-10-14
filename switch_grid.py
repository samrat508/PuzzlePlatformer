# Switch grid, in depth explination in the level design bible
# 4.17.2026
import pygame
import random
from datetime import datetime

sfx_lever = pygame.mixer.Sound('assets/InteractSound.wav')

#==========================
# Game State
#==========================
d0 = datetime(2008, 8, 18)
d1 = datetime.now()
delta = d1 - d0
is_solved = False
is_pressed = False
def toggle_random():
    rand = random.randint(0, 1)
    if rand == 0:
        return True
    elif rand == 1:
        return False
rand1 = toggle_random()
rand2 = toggle_random()
rand3 = toggle_random()
rand4 = toggle_random()
rand5 = toggle_random()
switch_7_toggle = toggle_random()
switch_9_toggle = toggle_random()
switch_13_toggle = toggle_random()
switch_17_toggle = toggle_random()
switch_19_toggle = toggle_random()
i = 0
states = []
while i < 25:
    if(i == 0 or i == 24):
        states.append(rand1)
    elif i == 10 or i == 14:
        states.append(rand2)
    elif i == 4 or i == 20:
        states.append(rand3)
    elif i == 1 or i == 23:
        states.append(rand4)
    elif i == 2 or i == 17:
        states.append(rand5)
    elif i == 6:
        states.append(switch_7_toggle)
    elif i == 8:
        states.append(switch_9_toggle)
    elif i == 12:
        states.append(switch_13_toggle)
    elif i == 16:
        states.append(switch_17_toggle)
    elif i == 18:
        states.append(switch_19_toggle)
    else:
        states.append(False)
    i += 1
original_states = []
z = 0
while z < len(states):
    original_states.append(states[z])
    print(original_states[z])
    z += 1
lever_sprite_on = pygame.image.load('./assets/MountedLeverBottomOn.png').convert_alpha()
lever_sprite_off = pygame.image.load("./assets/MountedLeverBottomOff.png").convert_alpha()
reset_button_pressed_sprite = pygame.image.load('./assets/FloorButtonOff.png').convert_alpha()
reset_button_unpressed_sprite = pygame.image.load('./assets/FloorButtonOnV2.png').convert_alpha()
def render(surface, hitbox, event, tile_size):
    global is_pressed
    global is_solved
    global original_states
    global lever_sprite_on
    global lever_sprite_off
    global reset_button_pressed_sprite
    global reset_button_unpressed_sprite
    #============================
    # Creating objects
    #============================
    lever_sprite_on = pygame.transform.scale(lever_sprite_on, (tile_size, tile_size))
    lever_sprite_off = pygame.transform.scale(lever_sprite_off, (tile_size, tile_size))
    reset_button_pressed_sprite = pygame.transform.scale(reset_button_pressed_sprite, (tile_size, tile_size))
    reset_button_unpressed_sprite = pygame.transform.scale(reset_button_unpressed_sprite, (tile_size, tile_size))
    reset_button = pygame.Rect(tile_size * 4, tile_size * 7, tile_size, tile_size)
    switches = [
        {"id:": "Switch1", 'rect': pygame.Rect(tile_size * 6, tile_size * 3, tile_size, tile_size), "x": 1, "y": 1},
    {"id:": "Switch2", "rect": pygame.Rect(tile_size * 7, tile_size * 3, tile_size, tile_size), "x": 2, "y": 1},
    {"id:": "Switch3", "rect": pygame.Rect(tile_size * 8, tile_size * 3, tile_size, tile_size), "x": 3, "y": 1},
    {"id:": "Switch4", "rect": pygame.Rect(tile_size * 9, tile_size * 3, tile_size, tile_size), "x": 4, "y": 1},
    {"id:": "Switch5", "rect": pygame.Rect(tile_size * 10, tile_size * 3, tile_size, tile_size), "x": 5, "y": 1},
    {"id:": "Switch6", "rect": pygame.Rect(tile_size * 6, tile_size * 4, tile_size, tile_size), "x": 1, "y": 2},
    {"id:": "Switch7", "rect": pygame.Rect(tile_size * 7, tile_size * 4, tile_size, tile_size), "x": 2, "y": 2},
    {"id:": "Switch8", "rect": pygame.Rect(tile_size * 8, tile_size * 4, tile_size, tile_size),"x": 3, "y": 2},
    {"id:": "Switch9", "rect": pygame.Rect(tile_size * 9, tile_size * 4, tile_size, tile_size), "x": 4, "y": 2},
    {"id:": "Switch10", "rect": pygame.Rect(tile_size * 10, tile_size * 4, tile_size, tile_size), "x": 5, "y": 2},
    {"id:": "Switch11", "rect": pygame.Rect(tile_size * 6, tile_size * 5, tile_size, tile_size), "x": 1, "y": 3},
    {"id:": "Switch12", "rect": pygame.Rect(tile_size * 7, tile_size * 5, tile_size, tile_size), "x": 2, "y": 3},
    {"id:": "Switch13", "rect": pygame.Rect(tile_size * 8, tile_size * 5, tile_size, tile_size), "x": 3, "y": 3},
    {"id:": "Switch14", "rect": pygame.Rect(tile_size * 9, tile_size * 5, tile_size, tile_size), "x": 4, "y": 3},
    {"id:": "Switch15", "rect": pygame.Rect(tile_size * 10, tile_size * 5, tile_size, tile_size), "x": 5, "y": 3},
    {"id:": "Switch16", "rect": pygame.Rect(tile_size * 6, tile_size * 6, tile_size, tile_size),"x": 1, "y": 4},
    {"id:": "Switch17", "rect": pygame.Rect(tile_size * 7, tile_size * 6, tile_size, tile_size), "x": 2, "y": 4},
    {"id:": "Switch18", "rect": pygame.Rect(tile_size * 8, tile_size * 6, tile_size, tile_size), "x": 3, "y": 4},
    {"id:": "Switch19", "rect": pygame.Rect(tile_size * 9, tile_size * 6, tile_size, tile_size), "x": 4, "y": 4},
    {"id:": "Switch20", "rect": pygame.Rect(tile_size * 10, tile_size * 6, tile_size, tile_size), "x": 5, "y": 4},
    {"id:": "Switch21", "rect": pygame.Rect(tile_size * 6, tile_size * 7, tile_size, tile_size), "x": 1, "y": 5},
    {"id:": "Switch22", "rect": pygame.Rect(tile_size * 7, tile_size * 7, tile_size, tile_size), "x": 2, "y": 5},
    {"id:": "Switch23", "rect": pygame.Rect(tile_size * 8, tile_size * 7, tile_size, tile_size), "x": 3, "y": 5},
    {"id:": "Switch24", "rect": pygame.Rect(tile_size * 9, tile_size * 7, tile_size, tile_size), "x": 4, "y": 5},
    {"id:": "Switch25", "rect": pygame.Rect(tile_size * 10, tile_size * 7, tile_size, tile_size), "x": 5, "y": 5}
    ]
    # ==============================
    # Game Logic
    # ==============================
    for index, switch in enumerate(switches):
        #corner switch logic
        if hitbox.colliderect(switch ["rect"]) and event and switch["x"] == 1 and switch["y"] == 1:
            states[5] = not states[5]
            states[1] = not states[1]
        elif hitbox.colliderect(switch["rect"]) and event and switch["x"] == 5 and switch["y"] == 1:
            states[3] = not states[3]
            states[9] = not states[9]
        elif hitbox.colliderect(switch["rect"]) and event and switch["x"] == 1 and switch["y"] == 5:
            states[15] = not states[15]
            states[21] = not states[21]
        elif hitbox.colliderect(switch["rect"]) and event and switch["x"] == 5 and switch["y"] == 5:
            states[19] = not states[19]
            states[23] = not states[23]
        #top row logic
        elif hitbox.colliderect(switch["rect"]) and event and switch["y"] == 1:
            states[index - 1] = not states[index - 1]
            states[index + 1] = not states[index + 1]
            states[index + 5] = not states[index + 5]
        #bottom row logic
        elif hitbox.colliderect(switch["rect"]) and event and switch["y"] == 5:
            states[index - 1] = not states[index - 1]
            states[index + 1] = not states[index + 1]
            states[index - 5]= not states[index - 5]
        #left column logic
        elif hitbox.colliderect(switch["rect"]) and event and switch["x"] == 1:
            states[index + 1] = not states[index + 1]
            states[index + 5] = not states[index + 5]
            states[index - 5] = not states[index - 5]
        #right column logic
        elif hitbox.colliderect(switch["rect"]) and event and switch["x"] == 5:
            states[index - 1] = not states[index - 1]
            states[index + 5] = not states[index + 5]
            states[index - 5] = not states[index - 5]
        # middle of the grid logic
        elif hitbox.colliderect(switch["rect"]) and event:
            states[index + 1] = not states[index + 1]
            states[index - 1] = not states[index - 1]
            states[index + 5] = not states[index + 5]
            states[index - 5] = not states[index - 5]
        if hitbox.colliderect(switch ["rect"]) and event:
            states[index] = not states[index]
            sfx_lever.play()
            print(index)
            print(switch)
    #button logic
    if hitbox.colliderect(reset_button) and not is_solved:
        z = 0
        while z < len(states):
            states[z] = original_states[z]
            z += 1
        is_pressed = True
    else:
        is_pressed = False
    for index in range(len(states)):
        if not states[index]:
            is_solved = False
            break
        else:
            is_solved = True
    # ============
    # RENDERING
    # ============
    for index, switch in enumerate(switches):
        if states[index]:
            surface.blit(lever_sprite_on, (switch["rect"].x, switch["rect"].y))
        else:
            surface.blit(lever_sprite_off, (switch["rect"].x, switch["rect"].y))
    if is_pressed:
        surface.blit(reset_button_pressed_sprite, (reset_button.x, reset_button.y))
    else:
        surface.blit(reset_button_unpressed_sprite, (reset_button.x, reset_button.y))
def set_solved(solved):
    global is_solved
    is_solved = solved
    return is_solved
def get_solved():
    global is_solved
    return is_solved


