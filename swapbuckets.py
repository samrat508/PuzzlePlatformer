import sys
import pygame
import random

switchOff_sprite = pygame.image.load('assets/MountedLeverBottomOff.png').convert_alpha()
switchOn_sprite = pygame.image.load('assets/MountedLeverBottomOn.png').convert_alpha()
keySprite_base = pygame.image.load('assets/Key.png').convert_alpha()
cupSprite_base = pygame.image.load('assets/Cup.png').convert_alpha()

sfx_lever = pygame.mixer.Sound('assets/InteractSound.wav')

switchLeftOn = pygame.transform.scale(switchOn_sprite, (64, 64))
switchLeftOff = pygame.transform.scale(switchOff_sprite, (64, 64))
cupSprite = pygame.transform.scale(cupSprite_base, (64, 64))
keySprite = pygame.transform.scale(keySprite_base, (64 // 2, 64 // 2))
is_solved = False
is_moving = False
switchActive = False
button = False
switch_activation_time = 0
interact = False
can_toggle_switch = True
key_visible = True

shuffling = True
shuffle_count = 0
max_shuffles = 5
cupSpeed = 7



cupPosition = [256, 512, 768]
ballIndex = random.randint(0, 2)
cupsArray = []
for i in range(3):
    cupsArray.append({
        "rect": pygame.Rect(cupPosition[i], 384, 64, 64),
        "target_x": cupPosition[i],
        "y_offset": 0,
        "hasBall": (i == ballIndex)
    })

def swap_cups(cups):
    idx1, idx2 = random.sample(range(len(cups)), 2)
    cups[idx1]["target_x"], cups[idx2]["target_x"] = cups[idx2]["target_x"], cups[idx1]["target_x"]

def render(surface, hitbox, event, tile_size):
    # 1. Cup Interaction Logic
    global is_solved
    global switchActive
    global shuffle_count
    global key_visible
    global can_toggle_switch
    global cupsArray
    switch = pygame.Rect(512, 256, tile_size, tile_size)
    if not is_solved and event and switchActive and shuffle_count >= max_shuffles:
        for cup in cupsArray:
            if hitbox.colliderect(cup["rect"]):
                if cup["hasBall"]:
                    key_visible = True
                    is_solved = True
                else:
                    print("Wrong! The switch resets.")
                    switchActive = False
                    shuffle_count = 0
                    key_visible = True
                event = False
                break

        # 2. Switch Logic
    if hitbox.colliderect(switch) and event and can_toggle_switch:
        if not is_solved:
            switchActive = True
            can_toggle_switch = False
            key_visible = False
            shuffle_count = 0
            sfx_lever.play()
    if not event:
        can_toggle_switch = True
    if not switchActive:
        surface.blit(switchLeftOff, (switch.x, switch.y))
    else:
        surface.blit(switchLeftOn, (switch.x, switch.y))
    all_cups_settled = True
    for cup in cupsArray:
        # Handle Smooth Cup Movement
        if cup["rect"].x != cup["target_x"]:
            all_cups_settled = False
            if abs(cup["rect"].x - cup["target_x"]) <= cupSpeed:
                cup["rect"].x = cup["target_x"]
            elif cup["rect"].x < cup["target_x"]:
                cup["rect"].x += cupSpeed
            elif cup["rect"].x > cup["target_x"]:
                cup["rect"].x -= cupSpeed

        # Draw the key beneath the cup if the game is idle
        if cup["hasBall"] and not key_visible:
            key_x = cup["rect"].x + (64 // 4)
            key_y = cup["rect"].y + (64 // 4)
            surface.blit(keySprite, (key_x, key_y))

        surface.blit(cupSprite, (cup["rect"].x, cup["rect"].y))
        # Draw the key visibly if the game is won or hasn't started
        if cup["hasBall"] and key_visible:
            key_x = cup["rect"].x + (tile_size // 4)
            key_y = cup["rect"].y + (tile_size // 4)
            surface.blit(keySprite, (key_x, key_y))
        # Handle shuffling state
    if switchActive and all_cups_settled and shuffle_count < max_shuffles:
        swap_cups(cupsArray)
        shuffle_count += 1
def set_solved(solved):
    global is_solved
    is_solved = solved
    return is_solved
def get_solved():
    global is_solved
    return is_solved

