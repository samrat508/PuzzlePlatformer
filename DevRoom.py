import sys
import pygame

#
# init
#

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((1000, 625))
pygame.display.set_caption("Grid Movement Game")

# move speed and tile size
TILE_SIZE = 50
SPEED = 5

# =========
# assets
# ========

player_img = pygame.image.load('assets/Char1-1.png').convert()
player_img.set_colorkey((0, 0, 0))
movinggus = pygame.transform.smoothscale(player_img, (TILE_SIZE, TILE_SIZE))

door_img = pygame.image.load('assets/Path1.png').convert()
btn_off_img = pygame.image.load('assets/FloorButtonOff.png').convert_alpha()
btn_on_img = pygame.image.load('assets/FloorButtonOnV2.png').convert_alpha()
treasure_img = pygame.image.load('assets/Treasure1.png').convert_alpha()
switchLeftOff = pygame.image.load('assets/MountedLeverLeftOff.png').convert_alpha()
switchLeftOn = pygame.image.load('assets/MountedLeverLeftOn.png').convert_alpha()

movinggus = pygame.transform.scale(player_img, (TILE_SIZE, TILE_SIZE))
door = pygame.transform.scale(door_img, (TILE_SIZE, TILE_SIZE))
buttonUnPressed = pygame.transform.scale(btn_off_img, (TILE_SIZE, TILE_SIZE))
buttonPressed = pygame.transform.scale(btn_on_img, (TILE_SIZE, TILE_SIZE))
treasure = pygame.transform.scale(treasure_img, (TILE_SIZE, TILE_SIZE))
switchLeftOff = pygame.transform.scale(switchLeftOff, (TILE_SIZE, TILE_SIZE))
switchLeftOn = pygame.transform.scale(switchLeftOn, (TILE_SIZE, TILE_SIZE))

font = pygame.font.Font(None, size=30)
concrete_walking = pygame.mixer.Sound('assets/concrete.mp3')

# ===========
# game state
# ============

gus_x = 0
gus_y = 2 * TILE_SIZE
startinggusx = 0
startinggusy = 2 * TILE_SIZE
stepCount = 0

target_x = gus_x
target_y = gus_y
last_grid_x = gus_x
last_grid_y = gus_y

room1 = True
room2 = False
room3 = False

switchactive = False
switchTextBoolean = False
button = False
switch_activation_time = 0
interact = False


# ========
# objects
# =========


#
# grid
#
def draw_grid(surface, width, height, tile_size):
    grid_color = (100, 100, 100)
    for x in range(0, width, tile_size):
        pygame.draw.line(surface, grid_color, (x, 0), (x, height))
    for y in range(0, height, tile_size):
        pygame.draw.line(surface, grid_color, (0, y), (width, y))


# ==========
# game loop
# ===========
running = True
while running:


    is_moving = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:
                print("space down ")
                interact = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                print("space up")
                interact = False

            if gus_x == target_x and gus_y == target_y:
                last_grid_x = gus_x
                last_grid_y = gus_y

                if event.key == pygame.K_d and target_x < 1000 - TILE_SIZE:
                    target_x += TILE_SIZE
                elif event.key == pygame.K_a and target_x > 0:
                    target_x -= TILE_SIZE
                elif event.key == pygame.K_s and target_y < 625 - TILE_SIZE:
                    target_y += TILE_SIZE
                elif event.key == pygame.K_w and target_y > 0:
                    target_y -= TILE_SIZE



    if gus_x < target_x:
        gus_x += SPEED
        is_moving = True
    elif gus_x > target_x:
        gus_x -= SPEED
        is_moving = True

    if gus_y < target_y:
        gus_y += SPEED
        is_moving = True
    elif gus_y > target_y:
        gus_y -= SPEED
        is_moving = True


    #
    # hitboxes
    #

    hitbox = movinggus.get_bounding_rect()
    hitbox.x += gus_x
    hitbox.y += gus_y

    #
    # sound
    #
    if is_moving and concrete_walking:
        if concrete_walking.get_num_channels() == 0:
            concrete_walking.play()

    elif concrete_walking:
        concrete_walking.stop()

        # ==========
        # room logic
        # ===========
        ######################
        #STEP COUNT #########
        #####################
    if room1:

        door_rect = pygame.Rect(950, 300, TILE_SIZE, TILE_SIZE)

        if hitbox.colliderect(door_rect):
            room1 = False
            room2 = True

            gus_x = TILE_SIZE
            gus_y = 300

            target_x = gus_x
            target_y = gus_y
            last_grid_x = gus_x
            last_grid_y = gus_y
            is_moving = False
        lava = pygame.Rect(500, 0, TILE_SIZE * 5, TILE_SIZE)
        ground = pygame.Rect(0, 500, 1000, 125)

        lava_collision = hitbox.colliderect(lava)
        ground_collision = hitbox.colliderect(ground)

        if ground_collision:
            gus_x, gus_y = last_grid_x, last_grid_y
            target_x, target_y = last_grid_x, last_grid_y
            is_moving = False

        if lava_collision:
            gus_x, gus_y = startinggusx, startinggusy
            target_x, target_y = startinggusx, startinggusy
            is_moving = False

        #
        # switch logic
        #

        switch = pygame.Rect(0, 250, TILE_SIZE, TILE_SIZE)

        if hitbox.colliderect(switch) and interact and can_toggle_switch:
            switchactive = not switchactive
            switchTextBoolean = switchactive
            switch_activation_time = pygame.time.get_ticks()

            can_toggle_switch = False

        if not interact:
            can_toggle_switch = True

        if switchTextBoolean:
            if pygame.time.get_ticks() - switch_activation_time >= 2000:
                switchTextBoolean = False

    elif room2:

        door_rect = pygame.Rect(0, 300, TILE_SIZE, TILE_SIZE)

        if hitbox.colliderect(door_rect):
            room1 = True
            room2 = False

            gus_x = 1000 - (TILE_SIZE * 2)
            gus_y = 300

            target_x = gus_x
            target_y = gus_y
            last_grid_x = gus_x
            last_grid_y = gus_y
            is_moving = False

    screen.fill((150, 150, 150))
    draw_grid(screen, 1000, 625, TILE_SIZE)

    # ============
    # RENDERING
    # ============

        ######################
        #STEP COUNT #########
        #####################

    if room1:
        l_col = hitbox.colliderect(lava)
        g_col = hitbox.colliderect(ground)
        s_col = hitbox.colliderect(switch)

        pygame.draw.rect(screen, (255 * l_col, 255, 0), lava)
        pygame.draw.rect(screen, (5 * g_col, 5 * g_col, 5 * g_col), ground)

        if not switchactive:
            screen.blit(switchLeftOff, (switch.x, switch.y))
        else:
            screen.blit(switchLeftOn, (switch.x, switch.y))

        screen.blit(door, (950, 300))

        if switchTextBoolean:
            switchText = font.render("Switch Activated! Something Happened!", True, (0, 0, 0))
            screen.blit(switchText, (320, 200))


    elif room2:

        screen.fill((50, 50, 150))

        draw_grid(screen, 1000, 625, TILE_SIZE)

        screen.blit(door, (0, 300))

        screen.blit(buttonUnPressed, (500, 300))

    screen.blit(movinggus, (gus_x, gus_y))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
