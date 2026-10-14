import sys
import pygame

pygame.init()
clock = pygame.time.Clock()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
TILE_SIZE = 50
SPEED = 5

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Grid Movement Game")

# move speed and tile size
TILE_SIZE = 50
SPEED = 5
stepCount = 0

# =========
# assets
# ========

playerdown = pygame.image.load('assets/Char1-1.png').convert()
playerright = pygame.image.load('assets/Char1-2.png').convert()
playerup = pygame.image.load('assets/Char1-3.png').convert()
playerleft = pygame.image.load('assets/Char1-4.png').convert()

playerdown.set_colorkey((0, 0, 0))
playerright.set_colorkey((0, 0, 0))
playerup.set_colorkey((0, 0, 0))
playerleft.set_colorkey((0, 0, 0))

movinggus = pygame.transform.smoothscale(playerdown, (TILE_SIZE, TILE_SIZE))

door_img = pygame.image.load('assets/Path1.png').convert()
btn_off_img = pygame.image.load('assets/FloorButtonOff.png').convert_alpha()
btn_on_img = pygame.image.load('assets/FloorButtonOnV2.png').convert_alpha()
treasure_img = pygame.image.load('assets/Treasure1.png').convert_alpha()
switchLeftOff = pygame.image.load('assets/MountedLeverLeftOff.png').convert_alpha()
switchLeftOn = pygame.image.load('assets/MountedLeverLeftOn.png').convert_alpha()

movinggus = pygame.transform.scale(playerdown, (TILE_SIZE, TILE_SIZE))
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

switchactive = False
switchTextBoolean = False
button = False
switch_activation_time = 0


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

            if gus_x == target_x and gus_y == target_y:
                last_grid_x = gus_x
                last_grid_y = gus_y

                if event.key == pygame.K_d and target_x < SCREEN_WIDTH - TILE_SIZE:

                    movinggus = pygame.transform.scale(playerright, (TILE_SIZE, TILE_SIZE))
                    target_x += TILE_SIZE
                    stepCount += 1

                elif event.key == pygame.K_a and target_x > 0:
                    movinggus = pygame.transform.scale(playerleft, (TILE_SIZE, TILE_SIZE))
                    target_x -= TILE_SIZE
                    stepCount += 1

                elif event.key == pygame.K_s and target_y < SCREEN_HEIGHT - TILE_SIZE:
                    movinggus = pygame.transform.scale(playerdown, (TILE_SIZE, TILE_SIZE))
                    target_y += TILE_SIZE
                    stepCount += 1

                elif event.key == pygame.K_w and target_y > 0:
                    movinggus = pygame.transform.scale(playerup, (TILE_SIZE, TILE_SIZE))
                    target_y -= TILE_SIZE
                    stepCount += 1

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

    screen.fill((150, 150, 150))
    draw_grid(screen, SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE)

    # ============
    # RENDERING
    # ============



    step_surface = font.render(f'Steps: {stepCount}', True, (255, 255, 255))
    screen.blit(step_surface, (50, 50))

    screen.blit(movinggus, (gus_x, gus_y))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
