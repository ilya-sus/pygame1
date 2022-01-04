import pygame
import sys
import os


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
pygame.init()
size = [SCREEN_WIDTH, SCREEN_HEIGHT]
screen = pygame.display.set_mode(size)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


bg = load_image('bg.jpg')
bg = pygame.transform.smoothscale(bg, (1000, 600))


class Player(pygame.sprite.Sprite):
    right = True

    def __init__(self):
        self.images = []
        self.imagesl = []
        self.k = 0
        super().__init__()

        self.images.append(load_image("mario0.png"))
        self.images.append(load_image("mario1.png"))
        self.images.append(load_image("mario2.png"))
        self.images.append(load_image("mario3.png"))
        self.imagesl.append(load_image("mario0_l.png"))
        self.imagesl.append(load_image("mario1_l.png"))
        self.imagesl.append(load_image("mario2_l.png"))
        self.image = load_image("mario0.png")

        self.rect = self.image.get_rect()

        self.change_x = 0
        self.change_y = 0

    def update(self):
        self.calc_grav()
        self.rect.x += self.change_x
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                self.rect.left = block.rect.right

        self.rect.y += self.change_y

        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom

            self.change_y = 0

    def jump(self):
        self.rect.y += 10
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 10

        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.change_y = -16

    def calc_grav(self):
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += 0.95

        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height

    def go_left(self):
        while self.k != 2:
            self.change_x = - 9
            if self.right:
                self.right = False
            self.k += 1
            self.image = self.imagesl[self.k]
        self.k = 0

    def go_right(self):
        if self.k != 2:
            self.change_x = 9
            if not self.right:
                self.right = True
            self.k += 1
            self.image = self.images[self.k]
        else:
            self.k = 0

    def stop(self):
        self.change_x = 0
        if self.right:
            self.image = self.images[0]
        else:
            self.image = self.imagesl[0]


class Platform(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()
        self.image = load_image('block.jpg')
        self.image = pygame.transform.smoothscale(load_image('block.jpg'), (210, 32))
        self.rect = self.image.get_rect()


class Level(object):
    def __init__(self, player):
        self.platform_list = pygame.sprite.Group()
        self.player = player

    def update(self):
        self.platform_list.update()

    def draw(self, screen):
        screen.blit(bg, (0, 0))
        self.platform_list.draw(screen)


class Level_01(Level):
    def __init__(self, player):
        Level.__init__(self, player)
        level = [
            [210, 32, 10, 520],
            [210, 32, 200, 400],
            [210, 32, 600, 300],
        ]
        for platform in level:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("Платформер")
    player = Player()
    level_list = []
    level_list.append(Level_01(player))
    current_level_no = 0
    current_level = level_list[current_level_no]

    active_sprite_list = pygame.sprite.Group()
    player.level = current_level

    player.rect.x = 340
    player.rect.y = SCREEN_HEIGHT - player.rect.height
    active_sprite_list.add(player)

    running = True

    clock = pygame.time.Clock()
    FPS = 60

    while running:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.go_left()
                if event.key == pygame.K_RIGHT:
                    player.go_right()
                if event.key == pygame.K_UP:
                    player.jump()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0:
                    player.stop()
                if event.key == pygame.K_RIGHT and player.change_x > 0:
                    player.stop()

        active_sprite_list.update()
        current_level.update()

        if player.rect.right > SCREEN_WIDTH:
            player.rect.right = SCREEN_WIDTH

        if player.rect.left < 0:
            player.rect.left = 0

        current_level.draw(screen)
        active_sprite_list.draw(screen)

        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()
