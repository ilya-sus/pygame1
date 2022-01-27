import pygame
import pyganim
import sys
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450
tile_width = tile_height = 50

active_sprite_list = pygame.sprite.Group()
platform_list = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
castle_list = pygame.sprite.Group()
coins_list = pygame.sprite.Group()
floor_list = pygame.sprite.Group()

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
live = 3
coins = 0

score1 = []

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

fon1 = load_image('bg1.jpg')
fon1 = pygame.transform.smoothscale(fon1, (800, 450))


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    return list(level_map)


tile_images = {'platform': 'block.png', 'box': 'box.png', 'lt_up_pipe': 'lt_up_pipe.png',
               'floor': 'floor.png', 'lt_dn_pipe': 'lt_dn_pipe.png', 'rt_up_pipe': 'rt_up_pipe.png',
               'rt_dn_pipe': 'rt_dn_pipe.png', 'castle': 'castle.png', 'coin': 'coin.png'}


class Player(pygame.sprite.Sprite):
    global platform_list, coins
    right = True

    def __init__(self, x, y):
        self.image = pygame.Surface((45, 45))
        self.total_x = self.total_y = 0
        self.rect_x = x
        self.rect_y = y
        self.move = 'stay'
        self.k = 0
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
        global coins
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
                coins += 1
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
                coins += 1
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
        global coins
        pygame.mixer.music.load("data/gameover_mus.mp3")
        pygame.mixer.music.play(loops=0, start=0.0, fade_ms=0)
        counters.lives(True)
        coins = 0
        if live == 0:
            final_screen()
        else:
            game(0)


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
        time1 = int(pygame.time.get_ticks() / 1000) - 4
        text = 'Time:' + str(time1)
        time = font.render(text, True, (255, 255, 255))
        return [time, time1]

    def coin(self):
        font = pygame.font.SysFont('comicsansms', 26)
        text = 'Coins x' + str(int(player.coins))
        coin = font.render(text, True, (255, 255, 255))
        return coin

    def score(self):
        font = pygame.font.SysFont('comicsansms', 26)
        score1 = int(coins)
        text = 'Score:' + str(score1)
        score = font.render(text, True, (255, 255, 255))
        return [score, score1]

    def lives(self, minus):
        global live
        if minus:
            live -= 1
        font = pygame.font.SysFont('comicsansms', 26)
        text = "Осталось жизней - " + str(live)
        time = font.render(text, True, (255, 255, 255))
        return time


def start_screen():
    pygame.mixer.music.load("data/start_screen_mus.mp3")
    pygame.mixer.music.play(-1)

    fon1 = pygame.transform.scale(load_image('start_screen.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(fon1, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return True

        pygame.display.flip()
        clock.tick(FPS)


def final_screen():
    pygame.mixer.music.load("data/gameover_mus.mp3")
    pygame.mixer.music.play(-1)
    k = 0

    gameover = pygame.transform.scale(load_image('gameover.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(gameover, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                sys.exit()
        if k == 0:
            font = pygame.font.SysFont('comicsansms', 26)
            text = 'Твоё время - ' + str(counters.timer()[1])
            time = font.render(text, True, (255, 255, 255))
            screen.blit(time, (0, 0))
            k += 1

        pygame.display.flip()
        clock.tick(FPS)


def win(lvl):
    pygame.mixer.music.load("data/level_clear_mus.mp3")
    pygame.mixer.music.play()

    for sprite in active_sprite_list:
        sprite.kill()

    for sprite in platform_list:
        sprite.kill()

    if lvl == 0:
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont('comicsansms', 26)
        text = 'Уровень 1 Пройден'
        lvl_up = font.render(text, True, (255, 255, 255))
        screen.blit(lvl_up, (300, 225))
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()

                elif event.type == pygame.KEYDOWN or \
                        event.type == pygame.MOUSEBUTTONDOWN:
                    game(1)
    else:
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont('comicsansms', 26)
        text = 'Вы победили!!!'
        lvl_up = font.render(text, True, (255, 255, 255))
        screen.blit(lvl_up, (300, 225))

        screen.blit(counters.timer()[0], (200, 0))
        screen.blit(counters.score()[0], (550, 0))

        try:
            f = open("best_score.txt")
            for i in f.readlines():
                if int(i.split()[0]) > int(counters.timer()[1]) and int(i.split()[2]) <= counters.score()[1]:
                    open('best_score.txt', 'w').close()
                    f = open("best_score.txt")
                    f.write(f'{counters.timer()[1]} - {counters.score()[1]}')

        except IOError:
            print("No file")

        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()

                elif event.type == pygame.KEYDOWN or \
                        event.type == pygame.MOUSEBUTTONDOWN:
                    sys.exit()


def game(lvl):
    global player, LEVEL_WIDTH, LEVEL_HEIGHT, counters

    for sprite in active_sprite_list:
        sprite.kill()
    for sprite in platform_list:
        sprite.kill()

    player, LEVEL_WIDTH, LEVEL_HEIGHT = draw(load_level(level_list[lvl]))
    LEVEL_WIDTH = (LEVEL_WIDTH + 1) * 50
    LEVEL_HEIGHT = LEVEL_HEIGHT * 50

    running = True
    camera = Camera()
    counters = Counters()

    active_sprite_list.add(player)

    if lvl == 0 and live == 3:
        if start_screen():
            pygame.mixer.music.load("data/level_1_mus.mp3")
            pygame.mixer.music.play(-1)
    else:
        if lvl == 0:
            pygame.mixer.music.load("data/level_1_mus.mp3")
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.load("data/level_2_mus.mp3")
            pygame.mixer.music.play(-1)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

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
            if lvl == 0:
                win(0)
            else:
                win(1)
            running = False

        if lvl == 0:
            screen.blit(fon, (0, 0))
        else:
            screen.blit(fon1, (0, 0))

        platform_list.draw(screen)
        active_sprite_list.draw(screen)

        screen.blit(counters.timer()[0], (400, 0))
        screen.blit(counters.lives(False), (0, 0))
        screen.blit(counters.score()[0], (600, 0))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


game(0)