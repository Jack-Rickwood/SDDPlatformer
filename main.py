import pygame, pytmx, sys

# Pygame Setup
pygame.init()
pygame.font.init()
size = width, height = 1000, 600
display = pygame.display.set_mode(size)
pygame.display.set_caption('SDD Platformer')
clock = pygame.time.Clock()

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

# Define Functions
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
    tiled_map = pytmx.load_pygame('Assets/Maps/Level' + str(level) + '.tmx', pixelalpha=True)
    collision = tiled_map.get_layer_by_name('Tiles')
    obstacle_collision = tiled_map.get_layer_by_name('Obstacles')
    win_collision = tiled_map.get_layer_by_name('Goal')
    player = pygame.image.load("Assets/Sprites/Player.png").convert_alpha()
    player = pygame.transform.scale(player, (player.get_size()[0] * 4, player.get_size()[1] * 4))
    player_backup = player
    camera = tiled_map.get_object_by_name("Player")

def play_anim(path_prefix, frames, flip):
    global anim_count
    global frame_index
    global player
    anim_count += 1
    
    if anim_count == 2:
        anim_count = 0
        frame_index += 1
        
        if frame_index >= frames + 1:
            frame_index = 0
            return
        
        path = "Assets/Sprites" + path_prefix + str(frame_index) + ".png"
        current_frame = pygame.image.load(path).convert_alpha()
        current_frame = pygame.transform.flip(current_frame, flip, False)
        player = pygame.transform.scale(current_frame, (current_frame.get_size()[0] * 4, current_frame.get_size()[1] * 4))

def win():
    global player
    player = pygame.image.load("Assets/Sprites/Win_Anim/Player_Win_1.png")
    while True:
        global display

        display.blit(background, (0, 0))

        play_anim("/Win_Anim/Player_Win_", 8, False)

        display.blit(player, (width / 2 - 80, height / 2 - 100))

        green = (0,150,0)
        title_text = pygame.font.SysFont('Times New Bold', 200)
        title_text_surface = title_text.render("You Win!", True, green)
        title_text_outline_surface = title_text.render("You Win!", True, (50,50,50))
        title_text_outline_surface_2 = title_text.render("You Win!", True, (0,0,0))
        display.blit(title_text_outline_surface_2,(width / 2 - 310, height / 4 + 15))
        display.blit(title_text_outline_surface,(width / 2 - 305, height / 4 + 15))
        display.blit(title_text_surface,(width / 2 - 300, height / 4 + 15))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        pygame.display.update()
        pygame.display.flip()
        clock.tick(20)

def check_collision(player_rect):
    tiles = []
    obstacle_tiles = []
    win_tiles = []
    
    for x, y, tile in collision.tiles():
        if (tile):
            tiles.append(pygame.Rect([(x * tiled_map.tilewidth), (y * tiled_map.tileheight), tiled_map.tilewidth, tiled_map.tileheight]));

    for x, y, tile in obstacle_collision.tiles():
        if (tile):
            obstacle_tiles.append(pygame.Rect([(x * tiled_map.tilewidth), (y * tiled_map.tileheight + 50), tiled_map.tilewidth, tiled_map.tileheight]));

    for x, y, tile in win_collision.tiles():
        if (tile):
            win_tiles.append(pygame.Rect([(x * tiled_map.tilewidth), (y * tiled_map.tileheight), tiled_map.tilewidth, tiled_map.tileheight]));

    if (player_rect.collidelistall(win_tiles)):
        global current_level
        if current_level == 3:
            win()
        else:
            tiled_setup(current_level + 1)
            
    if player_rect.collidelistall(obstacle_tiles):
        global fall_speed
        global player_position_change
        player_position_change = [0, 0]
        fall_speed = 0
        tiled_setup(current_level)
    
    check = False
    if (player_rect.collidelistall(tiles)):
        check = True
    
    return check

def game_loop():
    while True:
        global default_pose_timer
        global player
        
        global fall_speed
        global player_position_change
        player_position_change = [0, fall_speed]
        if fall_speed <= 28:
            fall_speed += 1

        x = tiled_map.get_object_by_name("Player").x
        y = tiled_map.get_object_by_name("Player").y + player_position_change[1]
        w = tiled_map.get_object_by_name("Player").width
        h = tiled_map.get_object_by_name("Player").height
        player_rect = pygame.Rect([x,y,w,h])
        collision = check_collision(player_rect)
        key_states = pygame.key.get_pressed()

        if collision:
            player_position_change[1] = 0
            fall_speed = 0
            if key_states[pygame.K_w] or key_states[pygame.K_UP]:
                fall_speed = -15
        
        if key_states[pygame.K_a] or key_states[pygame.K_LEFT]:
            player_position_change[0] -= 10
            if player_position_change[1] == 0 and fall_speed == 1:
                play_anim("/Running_Anim/Player_Running_", 6, True)
        elif key_states[pygame.K_d] or key_states[pygame.K_RIGHT]:
            player_position_change[0] += 10
            if player_position_change[1] == 0 and fall_speed == 1:
                play_anim("/Running_Anim/Player_Running_", 6, False)
        
        x = tiled_map.get_object_by_name("Player").x + player_position_change[0]
        y = tiled_map.get_object_by_name("Player").y - 5
        player_rect = pygame.Rect([x,y,w,h])
        collision_test = check_collision(player_rect)
        
        if collision_test:
            player_position_change[0] = 0
        elif player_position_change[1] != 0:
            play_anim("/Jumping_Anim/Player_Jumping_", 1, False)

        if player_position_change[0] == 0 and player_position_change[1] == 0:
            default_pose_timer += 1
            if default_pose_timer == 2:
                default_pose_timer = 0
                player = player_backup

        tiled_map.get_object_by_name("Player").x += player_position_change[0]
        tiled_map.get_object_by_name("Player").y += player_position_change[1]

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

        black = (20, 20, 20)
        light_blue = (173, 216, 230)
        button = pygame.Rect(width * 0.8, 10, width * 0.2 - 10, 50)
        pygame.draw.rect(display, light_blue, button)
        pygame.draw.rect(display, black, button, 3)
        text = pygame.font.SysFont('Arial Rounded MT', 30)
        text_surface = text.render("Return to Menu", True, (0, 0, 0))
        display.blit(text_surface,(width * 0.8 + 20, 28))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if button.collidepoint(mouse_pos):
                    return
        
        pygame.display.update()
        pygame.display.flip()
        clock.tick(30)

def title_screen():
    while True:
        global display
        
        display.blit(background, (0, 0))

        blue = (0, 51, 102)
        black = (20, 20, 20)
        pygame.draw.rect(display, blue, (width / 4, 25, width / 2, height - 50))
        pygame.draw.rect(display, black, (width / 4, 25, width / 2, height - 50), 5)
        
        player_sprite = pygame.image.load("Assets/Sprites/Title_Player.png").convert_alpha()
        player_sprite = pygame.transform.scale(player_sprite, (player_sprite.get_size()[0] * 10, player_sprite.get_size()[1] * 10))
        display.blit(player_sprite, ((width / 2) - (player_sprite.get_size()[0] / 2), (height / 2) - (player_sprite.get_size()[1] / 2) - 110))

        light_blue = (173, 216, 230)
        level1_button = pygame.Rect(width / 4 + 25, height / 2 + 60, width / 2 - 50, 40)
        pygame.draw.rect(display, light_blue, level1_button)
        pygame.draw.rect(display, black, level1_button, 3)
        level1_text = pygame.font.SysFont('Arial Rounded MT', 35)
        level1_text_surface = level1_text.render("Level 1", True, (0, 0, 0))
        display.blit(level1_text_surface,(width / 2 - 42, 368))

        level2_button = pygame.Rect(width / 4 + 25, height / 2 + 110, width / 2 - 50, 40)
        pygame.draw.rect(display, light_blue, level2_button)
        pygame.draw.rect(display, black, level2_button, 3)
        level2_text = pygame.font.SysFont('Arial Rounded MT', 35)
        level2_text_surface = level2_text.render("Level 2", True, (0, 0, 0))
        display.blit(level2_text_surface,(width / 2 - 42, 418))

        level3_button = pygame.Rect(width / 4 + 25, height / 2 + 160, width / 2 - 50, 40)
        pygame.draw.rect(display, light_blue, level3_button)
        pygame.draw.rect(display, black, level3_button, 3)
        level3_text = pygame.font.SysFont('Arial Rounded MT', 35)
        level3_text_surface = level3_text.render("Level 3", True, (0, 0, 0))
        display.blit(level3_text_surface,(width / 2 - 42, 468))

        light_red = (255, 127, 127)
        quit_button = pygame.Rect(width / 4 + 25, height / 2 + 210, width / 2 - 50, 40)
        pygame.draw.rect(display, light_red, quit_button)
        pygame.draw.rect(display, black, quit_button, 3)
        quit_text = pygame.font.SysFont('Arial Rounded MT', 35)
        quit_text_surface = quit_text.render("Quit", True, (0, 0, 0))
        display.blit(quit_text_surface,(width / 2 - 30, 518))

        orange = (255, 165, 0)
        title_text = pygame.font.SysFont('Times New Bold', 100)
        title_text_surface = title_text.render("Stig's Glock", True, orange)
        title_text_outline_surface = title_text.render("Stig's Glock", True, (50,50,50))
        title_text_outline_surface_2 = title_text.render("Stig's Glock", True, (0,0,0))
        display.blit(title_text_outline_surface_2,(width / 2 - 210, height / 4 + 15))
        display.blit(title_text_outline_surface,(width / 2 - 205, height / 4 + 15))
        display.blit(title_text_surface,(width / 2 - 200, height / 4 + 15))

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
        
        pygame.display.update()
        pygame.display.flip()

while True:
    current_level = title_screen()
    tiled_setup(current_level)
    game_loop()
