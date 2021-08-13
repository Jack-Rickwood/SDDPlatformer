import pygame, pytmx, sys

# Pygame Setup
pygame.init()
pygame.font.init()
size = width, height = 1000, 600
display = pygame.display.set_mode(size)
pygame.display.set_caption('SDD Platformer')
clock = pygame.time.Clock()
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()
pygame.mixer.music.load("Assets/Audio/Main.mp3")

# Declaring Global Variables
fall_speed = 1
anim_count = 0
frame_index = 0
default_pose_timer = 0
current_level = 0
tiled_map = None
collision = None
obstacle_collision = None
win_collision = None
player = None
player_backup = None
background = pygame.image.load("Assets/Sprites/Background.png")
background = pygame.transform.scale(background, (1000, 600))
camera = None
player_position_change = None

# Handles intial setup for tiled (the map editor used). Desired level is passed in as an argument
def tiled_setup(level):
    global current_level
    global tiled_map
    global collision
    global obstacle_collision
    global win_collision
    global player
    global player_backup
    global camera
    current_level = level
    # Loads the map
    tiled_map = pytmx.load_pygame('Assets/Maps/Level' + str(level) + '.tmx', pixelalpha=True)
    collision = tiled_map.get_layer_by_name('Tiles')
    obstacle_collision = tiled_map.get_layer_by_name('Obstacles')
    win_collision = tiled_map.get_layer_by_name('Goal')
    # Loads the player
    player = pygame.image.load("Assets/Sprites/Player.png").convert_alpha()
    player = pygame.transform.scale(player, (player.get_size()[0] * 4, player.get_size()[1] * 4))
    player_backup = player
    # Sets up the camera
    camera = tiled_map.get_object_by_name("Player")

# Handles animations, takes the prefix to the animation
# (the path without frame number), the number of frames,
# and whether to flip along the x axis as arguments.
def play_anim(path_prefix, frames, flip):
    global anim_count
    global frame_index
    global player
    anim_count += 1

    # Only executes every third time the function is called. This is to ensure the animtion does not play too fast.
    if anim_count == 2:
        anim_count = 0
        frame_index += 1

        # Checks if the animation has finished and it needs to restart
        if frame_index >= frames + 1:
            frame_index = 0
            return

        # Updates the player sprite to the next animation frame in the sequence
        path = "Assets/Sprites" + path_prefix + str(frame_index) + ".png"
        current_frame = pygame.image.load(path).convert_alpha()
        current_frame = pygame.transform.flip(current_frame, flip, False)
        player = pygame.transform.scale(current_frame, (current_frame.get_size()[0] * 4, current_frame.get_size()[1] * 4))

# Main loop for the win screen
def win():
    global player
    player = pygame.image.load("Assets/Sprites/Win_Anim/Player_Win_1.png")
    while True:
        global display
        # Wipes the screen
        display.blit(background, (0, 0))
        # Plays the win animation
        play_anim("/Win_Anim/Player_Win_", 8, False)
        # Draws the charater sprite
        display.blit(player, (width / 2 - 80, height / 2 - 100))

        # Draws the 'You win!' text
        green = (0,150,0)
        title_text = pygame.font.SysFont('Times New Bold', 200)
        title_text_surface = title_text.render("You Win!", True, green)
        title_text_outline_surface = title_text.render("You Win!", True, (50,50,50))
        title_text_outline_surface_2 = title_text.render("You Win!", True, (0,0,0))
        display.blit(title_text_outline_surface_2,(width / 2 - 310, height / 4 + 15))
        display.blit(title_text_outline_surface,(width / 2 - 305, height / 4 + 15))
        display.blit(title_text_surface,(width / 2 - 300, height / 4 + 15))

        # Handles input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Updates the display
        pygame.display.update()
        pygame.display.flip()
        clock.tick(20)

# Checks for player collisions, and act on them based on the type.
def check_collision(player_rect):
    tiles = []
    obstacle_tiles = []
    win_tiles = []

    # Converts each 'collision' tile (tiles that stop descent) to a pygame rectangle and adds them to a list
    for x, y, tile in collision.tiles():
        if (tile):
            tiles.append(pygame.Rect([(x * tiled_map.tilewidth), (y * tiled_map.tileheight), tiled_map.tilewidth, tiled_map.tileheight]));

    # Converts each 'obstacle' tile (tiles that kill you) to a pygame rectangle and adds them to a list
    for x, y, tile in obstacle_collision.tiles():
        if (tile):
            obstacle_tiles.append(pygame.Rect([(x * tiled_map.tilewidth), (y * tiled_map.tileheight + 50), tiled_map.tilewidth, tiled_map.tileheight]));

    # Converts each 'goal' tile (tiles that take you to the next level) to a pygame rectangle and adds them to a list
    for x, y, tile in win_collision.tiles():
        if (tile):
            win_tiles.append(pygame.Rect([(x * tiled_map.tilewidth), (y * tiled_map.tileheight), tiled_map.tilewidth, tiled_map.tileheight]));

    # Checks if the player is colliding with any of the 'goal' tiles.
    if (player_rect.collidelistall(win_tiles)):
        global current_level
        if current_level == 3:
            # Go to the 'You win!' screen
            win()
        else:
            # Load the next level
            tiled_setup(current_level + 1)

    # Checks if the player is colliding with any of the 'obstacle' tiles. 
    if player_rect.collidelistall(obstacle_tiles):
        global fall_speed
        global player_position_change
        # Stops any player motion, and reloads the level
        player_position_change = [0, 0]
        fall_speed = 0
        tiled_setup(current_level)

    # Returns if the player is colliding with any 'collision' tiles
    check = False
    if (player_rect.collidelistall(tiles)):
        check = True
    
    return check

# Main loop that runs while the player is in-game
def game_loop():
    while True:
        global default_pose_timer
        global player
        
        global fall_speed
        global player_position_change
        player_position_change = [0, fall_speed]

        # If fall speed is not above a terminal velocity, increase it
        if fall_speed <= 28:
            fall_speed += 1

        # Get player coordinates
        x = tiled_map.get_object_by_name("Player").x
        y = tiled_map.get_object_by_name("Player").y + player_position_change[1]
        w = tiled_map.get_object_by_name("Player").width
        h = tiled_map.get_object_by_name("Player").height
        player_rect = pygame.Rect([x,y,w,h])
        collision = check_collision(player_rect)
        key_states = pygame.key.get_pressed()

        # Handles input
        if collision:
            player_position_change[1] = 0
            fall_speed = 0
            # If the player is on the ground and presses up, make them jump (by making fall speed negative)
            if key_states[pygame.K_w] or key_states[pygame.K_UP]:
                fall_speed = -15
        if key_states[pygame.K_a] or key_states[pygame.K_LEFT]:
            player_position_change[0] -= 10
            # Change x position by 10 if the player moves left
            if player_position_change[1] == 0 and fall_speed == 1:
                play_anim("/Running_Anim/Player_Running_", 6, True)
        elif key_states[pygame.K_d] or key_states[pygame.K_RIGHT]:
            player_position_change[0] += 10
            # Change x position by 10 if the player moves right
            if player_position_change[1] == 0 and fall_speed == 1:
                play_anim("/Running_Anim/Player_Running_", 6, False)
        
        x = tiled_map.get_object_by_name("Player").x + player_position_change[0]
        y = tiled_map.get_object_by_name("Player").y - 5
        player_rect = pygame.Rect([x,y,w,h])
        collision_test = check_collision(player_rect)

        # Calls the collision test function and stores the result in a variable
        if collision_test:
            player_position_change[0] = 0
        elif player_position_change[1] != 0:
            play_anim("/Jumping_Anim/Player_Jumping_", 1, False)

        # Reset the player sprite to the default pose if they aren't in motion
        if player_position_change[0] == 0 and player_position_change[1] == 0:
            default_pose_timer += 1
            if default_pose_timer == 2:
                default_pose_timer = 0
                player = player_backup

        # Changes the sprites position to reflect any desired movement
        tiled_map.get_object_by_name("Player").x += player_position_change[0]
        tiled_map.get_object_by_name("Player").y += player_position_change[1]

        # Draws the map to the screen, layer by layer, tile by tile.
        # This takes into account the positioning of the 'camera'
        display.blit(background, (0, 0))
        for layer in tiled_map.visible_layers:
            if layer == tiled_map.get_layer_by_name("Obstacles"):
                for x, y, gid, in layer:
                    tile = tiled_map.get_tile_image_by_gid(gid)
                    if not tile == None:
                        display.blit(tile, (x * tiled_map.tilewidth - camera.x + width / 2, y * tiled_map.tileheight - camera.y + (height + 80) / 2))
            elif isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = tiled_map.get_tile_image_by_gid(gid)
                    if not tile == None:
                        display.blit(tile, (x * tiled_map.tilewidth - camera.x + width / 2, y * tiled_map.tileheight - camera.y + height / 2))
            elif isinstance(layer, pytmx.TiledObjectGroup):
                for object in layer:
                    if (object.type=='Player'):
                        display.blit(player, (object.x - camera.x + width / 2, object.y - camera.y + height / 2))

        # Draws the quit to menu button
        black = (20, 20, 20)
        light_blue = (173, 216, 230)
        button = pygame.Rect(width * 0.8, 10, width * 0.2 - 10, 50)
        pygame.draw.rect(display, light_blue, button)
        pygame.draw.rect(display, black, button, 3)
        text = pygame.font.SysFont('Arial Rounded MT', 30)
        text_surface = text.render("Return to Menu", True, (0, 0, 0))
        display.blit(text_surface,(width * 0.8 + 20, 28))

        # Handles input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if button.collidepoint(mouse_pos):
                    return

        # Updates the display
        pygame.display.update()
        pygame.display.flip()
        clock.tick(30)

# Main loop for the title screen
def title_screen():
    while True:
        global display
        # Wipes the screen
        display.blit(background, (0, 0))

        blue = (0, 51, 102)
        black = (20, 20, 20)
        pygame.draw.rect(display, blue, (width / 4, 25, width / 2, height - 50))
        pygame.draw.rect(display, black, (width / 4, 25, width / 2, height - 50), 5)

        # Draws the player sprite, scaling it up to the correct size
        player_sprite = pygame.image.load("Assets/Sprites/Title_Player.png").convert_alpha()
        player_sprite = pygame.transform.scale(player_sprite, (player_sprite.get_size()[0] * 10, player_sprite.get_size()[1] * 10))
        display.blit(player_sprite, ((width / 2) - (player_sprite.get_size()[0] / 2), (height / 2) - (player_sprite.get_size()[1] / 2) - 110))

        # Draws the first button
        light_blue = (173, 216, 230)
        level1_button = pygame.Rect(width / 4 + 25, height / 2 + 60, width / 2 - 50, 40)
        pygame.draw.rect(display, light_blue, level1_button)
        pygame.draw.rect(display, black, level1_button, 3)
        level1_text = pygame.font.SysFont('Arial Rounded MT', 35)
        level1_text_surface = level1_text.render("Level 1", True, (0, 0, 0))
        display.blit(level1_text_surface,(width / 2 - 42, 368))

        # Draws the second button
        level2_button = pygame.Rect(width / 4 + 25, height / 2 + 110, width / 2 - 50, 40)
        pygame.draw.rect(display, light_blue, level2_button)
        pygame.draw.rect(display, black, level2_button, 3)
        level2_text = pygame.font.SysFont('Arial Rounded MT', 35)
        level2_text_surface = level2_text.render("Level 2", True, (0, 0, 0))
        display.blit(level2_text_surface,(width / 2 - 42, 418))

        # Draws the third button
        level3_button = pygame.Rect(width / 4 + 25, height / 2 + 160, width / 2 - 50, 40)
        pygame.draw.rect(display, light_blue, level3_button)
        pygame.draw.rect(display, black, level3_button, 3)
        level3_text = pygame.font.SysFont('Arial Rounded MT', 35)
        level3_text_surface = level3_text.render("Level 3", True, (0, 0, 0))
        display.blit(level3_text_surface,(width / 2 - 42, 468))

        # Draws the quit button
        light_red = (255, 127, 127)
        quit_button = pygame.Rect(width / 4 + 25, height / 2 + 210, width / 2 - 50, 40)
        pygame.draw.rect(display, light_red, quit_button)
        pygame.draw.rect(display, black, quit_button, 3)
        quit_text = pygame.font.SysFont('Arial Rounded MT', 35)
        quit_text_surface = quit_text.render("Quit", True, (0, 0, 0))
        display.blit(quit_text_surface,(width / 2 - 30, 518))

        # Draws the game's title
        orange = (255, 165, 0)
        title_text = pygame.font.SysFont('Times New Bold', 100)
        title_text_surface = title_text.render("Stig's Glock", True, orange)
        title_text_outline_surface = title_text.render("Stig's Glock", True, (50,50,50))
        title_text_outline_surface_2 = title_text.render("Stig's Glock", True, (0,0,0))
        display.blit(title_text_outline_surface_2,(width / 2 - 210, height / 4 + 15))
        display.blit(title_text_outline_surface,(width / 2 - 205, height / 4 + 15))
        display.blit(title_text_surface,(width / 2 - 200, height / 4 + 15))

        # Handles input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if level1_button.collidepoint(mouse_pos):
                    return 1
                elif level2_button.collidepoint(mouse_pos):
                    return 2
                elif level3_button.collidepoint(mouse_pos):
                    return 3
                elif quit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        # Updates the display
        pygame.display.update()
        pygame.display.flip()

# This is the games main loop. First it starts playing the music,
# then it displays the title screen for the player to choose a level.
# Finally, it prepares pygame and loads the specified level.
while True:
    pygame.mixer.music.play(-1,0.0)
    current_level = title_screen()
    tiled_setup(current_level)
    game_loop()