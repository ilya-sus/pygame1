import pygame
import pyganim
import sys
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450
tile_width = tile_height = 50

pygame.init()
size = [SCREEN_WIDTH, SCREEN_HEIGHT]
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Платформер")

coin_sound = pygame.mixer.Sound("data/claim_coin_mus.mp3")
start_music = pygame.mixer.Sound("data/start_screen_mus.mp3")
final_music = pygame.mixer.Sound("data/gameover_mus.mp3")
win_music = pygame.mixer.Sound("data/level_clear_mus.mp3")

maps_list, level_list = [open('data/map_1.txt').readlines()], ['map_1.txt', 'map_2.txt']
level_musics = ["data/level_1_mus.mp3", "data/level_1_mus.mp3"]
Level = len(level_list)
World = 1
clock = pygame.time.Clock()
FPS = 60
castle_x = 0
Win = False
end = False


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


fon = load_image('fon.png')
fon = pygame.transform.smoothscale(fon, (3500, 450))


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    return list(level_map)


tile_images = {'platform': 'block.png', 'box': 'box.png', 'lt_up_pipe': 'lt_up_pipe.png',
               'floor': 'floor.png', 'lt_dn_pipe': 'lt_dn_pipe.png', 'rt_up_pipe': 'rt_up_pipe.png',
               'rt_dn_pipe': 'rt_dn_pipe.png', 'castle': 'castle.png', 'coin': 'coin.png'}


class Player(pygame.sprite.Sprite):
    global platform_list
    right = True

    def __init__(self, x, y):
        self.image = pygame.Surface((45, 45))
        self.total_x = self.total_y = 0
        self.rect_x = x
        self.rect_y = y
        self.move = 'stay'
        self.k = 0
        self.coins = 0
        super().__init__()

        self.stay = [("data/mario0.png", 1)]
        self.block_hit_list = []
        self.castle_hit_list = []
        self.coins_hit_list = []

        self.imagesr = [(load_image("mario1.png"), 100), (load_image("mario2.png"), 100),
                        (load_image("mario3.png"), 100), (load_image("mario2.png"), 100)]

        self.imagesl = [(load_image("mario1_l.png"), 100), (load_image("mario2_l.png"), 100),
                        (load_image("mario3_l.png"), 100), (load_image("mario2_l.png"), 100)]

        self.imagesup = [(load_image("mario5.png"), 1)]

        self.imagesup_l = [(load_image("mario5_l.png"), 1)]

        self.rect = self.image.get_rect()
        self.image.set_colorkey((0, 0, 0))

        def make_Anim(anim_lst):
            Anim = pyganim.PygAnimation(anim_lst)
            return Anim

        self.AnimStay = pyganim.PygAnimation(self.stay)
        self.AnimStay.play()

        self.AnimRight = make_Anim(self.imagesr)
        self.AnimRight.play()

        self.AnimLeft = make_Anim(self.imagesl)
        self.AnimLeft.play()

        self.AnimUp = make_Anim(self.imagesup)
        self.AnimUp.play()

        self.AnimUp_l = make_Anim(self.imagesup_l)
        self.AnimUp_l.play()

        self.change_x = 0
        self.change_y = 0

    def update(self):
        self.calc_grav()

        if self.move == 'stay':
            self.image.fill((0, 0, 0))
            self.AnimStay.blit(self.image, (0, 0))

        elif self.move == 'right':
            self.image.fill((0, 0, 0))
            self.AnimRight.blit(self.image, (0, 0))

        elif self.move == 'left':
            self.image.fill((0, 0, 0))
            self.AnimLeft.blit(self.image, (0, 0))

        elif self.move == 'up':
            if self.change_x == -9:
                self.image.fill((0, 0, 0))
                self.AnimUp_l.blit(self.image, (0, 0))

            elif self.change_x == 9:
                self.image.fill((0, 0, 0))
                self.AnimUp.blit(self.image, (0, 0))

        if (SCREEN_WIDTH / 2 > player.total_x) or (player.total_x > (LEVEL_WIDTH - SCREEN_WIDTH / 2)):
            self.rect.x += self.change_x

        self.block_hit_list = pygame.sprite.spritecollide(self, platform_list, False)

        for block in self.block_hit_list:
            if block in coins_list:
                block.kill()
                coin_sound.set_volume(0.2)
                coin_sound.play(0)
                self.coins += 1
            else:
                if self.change_x > 0:
                    self.rect.right = block.rect.left

                elif self.change_x < 0:
                    self.rect.left = block.rect.right
                self.change_x = 0
                self.stop()

        self.rect.y += self.change_y
        self.block_hit_list = pygame.sprite.spritecollide(self, platform_list, False)

        for block in self.block_hit_list:
            if block in coins_list:
                block.kill()
                self.coins += 1
            else:
                if self.change_y > 0:
                    self.rect.bottom = block.rect.top

                elif self.change_y < 0:
                    self.rect.top = block.rect.bottom

            self.change_y = 0

        self.total_x += self.change_x

    def jump(self):
        self.rect.y += 10
        platform_hit_list = pygame.sprite.spritecollide(self, platform_list, False)
        self.rect.y -= 10

        if len(platform_hit_list) > 0 or self.rect.bottom >= LEVEL_HEIGHT:
            self.change_y = -16

    def calc_grav(self):
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += 0.8

        if self.rect.y >= LEVEL_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = LEVEL_HEIGHT - self.rect.height

    def plr_move(self, ls):
        if (SCREEN_WIDTH / 2 >= player.total_x) or (player.total_x <= (LEVEL_WIDTH - SCREEN_WIDTH / 2)):
            self.change_x = ls

    def stop(self):
        self.change_x = 0
        self.move = 'stay'

    def draw(self, surf):
        surf.blit(self.image, (self.total_x, self.total_y))

    def die(self):
        pygame.mixer.music.load("data/gameover_mus.mp3")
        pygame.mixer.music.play(loops=0, start=0.0, fade_ms=0)
        final_screen()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(all_sprites, platform_list)
        self.image = load_image(tile_images[tile_type])

        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class UsableTile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, group):
        super().__init__(all_sprites, platform_list, group)
        self.image = load_image(tile_images[tile_type])
        global castle_x
        if group == castle_list:
            castle_x = pos_x * 50

        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


def draw(level):
    new_player, x, y = None, None, None
    screen.blit(fon, (0, 0))

    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == 'o':
                new_player = Player(0, 0)

            elif level[y][x] == '-':
                Tile('platform', x, y)

            elif level[y][x] == '?':
                Tile('box', x, y)

            elif level[y][x] == 'R':
                Tile('lt_up_pipe', x, y)

            elif level[y][x] == 'r':
                Tile('lt_dn_pipe', x, y)

            elif level[y][x] == 'P':
                Tile('rt_up_pipe', x, y)

            elif level[y][x] == 'p':
                Tile('rt_dn_pipe', x, y)

            elif level[y][x] == 'f':
                UsableTile('floor', x, y, floor_list)

            elif level[y][x] == 'C':
                UsableTile('castle', x, y, castle_list)

            elif level[y][x] == '0':
                UsableTile('coin', x, y, coins_list)

    return new_player, x, y


class Camera:
    def __init__(self):
        pass

    def update(self):
        if ((SCREEN_WIDTH / 2 < player.total_x) and (player.total_x < (LEVEL_WIDTH - SCREEN_WIDTH / 2))) or \
                (player.total_x > (LEVEL_WIDTH - SCREEN_WIDTH / 2)):

            for sprite in platform_list:
                sprite.rect.x += -player.change_x


def terminate():
    pygame.quit()
    sys.exit()


class Counters:
    def __init__(self):
        pass

    def timer(self):
        font = pygame.font.SysFont('comicsansms', 26)
        text = 'Time:' + str(int(pygame.time.get_ticks() / 1000) - 3)
        time = font.render(text, True, (255, 255, 255))
        return time

    def coin(self):
        font = pygame.font.SysFont('comicsansms', 26)
        text = 'Coins x' + str(int(player.coins))
        coin = font.render(text, True, (255, 255, 255))
        return coin

    def score(self):
        font = pygame.font.SysFont('comicsansms', 26)
        text = 'Score:' + str(int(player.coins))
        score = font.render(text, True, (255, 255, 255))
        return score


def start_screen():
    start_music.play(-1)

    fon1 = pygame.transform.scale(load_image('start_screen.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(fon1, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                start_music.stop()
                return True
        pygame.display.flip()
        clock.tick(FPS)


def final_screen():
    fon_music.stop()
    final_music.play(-1)

    gameover = pygame.transform.scale(load_image('gameover.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(gameover, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                sys.exit()

        pygame.display.flip()
        clock.tick(FPS)


def win(lvl):
    global Level

    screen.fill((0, 0, 0))
    font = pygame.font.SysFont('comicsansms', 26)
    text = f'Уровень {lvl} Пройден'
    lvl_up = font.render(text, True, (255, 255, 255))
    screen.blit(lvl_up, (300, 225))
    fon_music.stop()
    win_music.play(-1)
    for _ in range(int(win_music.get_length()) * 2000):
        pygame.display.flip()
    Level += 1


if start_screen():
    for j in range(World):
        for i in range(Level):
            pygame.init()

            win_music.stop()
            fon_music = pygame.mixer.Sound(level_musics[i])
            fon_music.play(-1)

            running = True

            active_sprite_list = pygame.sprite.Group()
            platform_list = pygame.sprite.Group()
            all_sprites = pygame.sprite.Group()
            castle_list = pygame.sprite.Group()
            coins_list = pygame.sprite.Group()
            floor_list = pygame.sprite.Group()

            player, LEVEL_WIDTH, LEVEL_HEIGHT = draw(load_level(level_list[i]))
            LEVEL_WIDTH = (LEVEL_WIDTH + 1) * 50
            LEVEL_HEIGHT = LEVEL_HEIGHT * 50

            active_sprite_list.add(player)
            camera = Camera()
            counters = Counters()

            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        pygame.quit()

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            player.move = 'left'
                            player.plr_move(-6)

                        if event.key == pygame.K_RIGHT:
                            player.move = 'right'
                            player.plr_move(6)

                        if event.key == pygame.K_UP:
                            player.move = 'up'
                            player.jump()

                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_LEFT and player.change_x < 0:
                            player.stop()

                        if event.key == pygame.K_RIGHT and player.change_x > 0:
                            player.stop()

                active_sprite_list.update()
                camera.update()

                if player.rect.right > LEVEL_WIDTH:
                    player.rect.right = LEVEL_WIDTH

                if player.rect.left < 0:
                    player.rect.left = 0

                if player.rect.bottom == 500:
                    player.die()

                if player.total_x >= castle_x - 50:
                    win(int(i) + 1)
                    running = False

                screen.blit(fon, (0, 0))
                platform_list.draw(screen)
                active_sprite_list.draw(screen)

                screen.blit(counters.timer(), (300, 0))
                screen.blit(counters.coin(), (100, 0))
                screen.blit(counters.score(), (600, 0))

                pygame.display.flip()
                clock.tick(FPS)

    pygame.quit()
