import sys, pygame

pygame.init()

size = width, height = 320, 420
display = pygame.display.set_mode(size)

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a or event.key == pygame.K_LEFT:
				continue
			if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
				continue
			if event.key == pygame.K_s or event.key == pygame.K_DOWN:
				continue
			if event.key == pygame.K_w or event.key == pygame.K_UP:
				continue
	pygame.display.update()