import pygame, pytmx, sys

# PyGame Init
pygame.init()
size = width, height = 1000, 600
display = pygame.display.set_mode(size)
pygame.display.set_caption('SDD Platformer')
clock = pygame.time.Clock()

# Tiled Setup
tiled_map = pytmx.load_pygame('Assets/Maps/Level1.tmx', pixelalpha=True)
collision = tiled_map.get_layer_by_name('Tiles')
obstacle_collision = tiled_map.get_layer_by_name('Obstacles')
player = pygame.image.load("Assets/Sprites/Player.png").convert_alpha()
player = pygame.transform.scale(player, (80, 110))
background = pygame.image.load("Assets/Sprites/Background.png")
background = pygame.transform.scale(background, (1000, 600))
camera = tiled_map.get_object_by_name("Player")

# Game Setup
fall_speed = 1
jumping = False

# Define Functions
def check_collision(player_rect):
    tiles = []
    obstacle_tiles = []
    for x, y, tile in collision.tiles():
        if (tile):
            tiles.append(pygame.Rect([(x * tiled_map.tilewidth), (y * tiled_map.tileheight), tiled_map.tilewidth, tiled_map.tileheight]));

    for x, y, tile in obstacle_collision.tiles():
        if (tile):
            obstacle_tiles.append(pygame.Rect([(x * tiled_map.tilewidth), (y * tiled_map.tileheight + 50), tiled_map.tilewidth, tiled_map.tileheight]));
    if player_rect.collidelistall(obstacle_tiles):
        pygame.quit()
        sys.exit()
    
    check = False
    if (player_rect.collidelistall(tiles)):
        check = True
    return check

def game_loop():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        global fall_speed
        global jumping
        player_position_change = [0, fall_speed]
        fall_speed += 1

        x = tiled_map.get_object_by_name("Player").x
        y = tiled_map.get_object_by_name("Player").y + player_position_change[1]
        w = tiled_map.get_object_by_name("Player").width
        h = tiled_map.get_object_by_name("Player").height
        player_rect = pygame.Rect([x,y,w,h])
        collision = check_collision(player_rect)
        
        key_states = pygame.key.get_pressed()
        if key_states[pygame.K_a] or key_states[pygame.K_LEFT]:
            player_position_change[0] -= 10
        elif key_states[pygame.K_d] or key_states[pygame.K_RIGHT]:
            player_position_change[0] += 10
            
        if collision:
            player_position_change[1] = 0
            fall_speed = 0
            if key_states[pygame.K_w] or key_states[pygame.K_UP]:
                fall_speed = -15
        
        x = tiled_map.get_object_by_name("Player").x + player_position_change[0]
        y = tiled_map.get_object_by_name("Player").y - 5
        player_rect = pygame.Rect([x,y,w,h])
        collision_test = check_collision(player_rect)
        
        if collision_test:
            player_position_change[0] = 0
        
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
        
        pygame.display.update()
        pygame.display.flip()
        clock.tick(30)
        
game_loop()