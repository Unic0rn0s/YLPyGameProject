import os
import random
import pygame
from pygame.locals import *
from objects import World, Player, Button, load_level, draw_text, sounds, Wave

SIZE = WIDTH, HEIGHT = 1000, 650
tile_size = 50

pygame.init()
win = pygame.display.set_mode(SIZE)
pygame.display.set_caption('Pixel Knight')
clock = pygame.time.Clock()
score_font = pygame.font.SysFont('Chiller', 50)
FPS = 50

# Звук навыков
wave_fx = pygame.mixer.Sound('sounds/wave.wav')
wave_fx.set_volume(0.3)
time_freeze_fx = pygame.mixer.Sound('sounds/time_freeze.wav')
time_freeze_fx.set_volume(0.3)

# Фон
bg1 = pygame.image.load('assets/BG1.png')
bg2 = pygame.image.load('assets/BG2.png')
bg = bg1
menu = pygame.image.load('assets/menu.png')
you_won = pygame.image.load('assets/won.png')


# Первый уровень
level = 1
max_level = len(os.listdir('levels/'))
data = load_level(level)

player_pos = (10, 340)


# Создание мира
water_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
decor_group = pygame.sprite.Group()
potion_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
bridge_group = pygame.sprite.Group()
wave_group = pygame.sprite.Group()
groups = [water_group, lava_group, decor_group, potion_group, enemies_group,
          exit_group, platform_group, bridge_group, wave_group]
world = World(win, data, groups)
player = Player(win, player_pos, world, groups)

# Кнопки
play = pygame.image.load('assets/play.png')
replay = pygame.image.load('assets/replay.png')
home = pygame.image.load('assets/home.png')
exit = pygame.image.load('assets/exit.png')

play_btn = Button(play, (128, 64), WIDTH // 2 - WIDTH // 16, HEIGHT // 1.6)
replay_btn = Button(replay, (45, 42), WIDTH // 2 - 110, HEIGHT // 2 + 20)
home_btn = Button(home, (45, 42), WIDTH // 2 - 20, HEIGHT // 2 + 20)
exit_btn = Button(exit, (45, 42), WIDTH // 2 + 70, HEIGHT // 2 + 20)


# Сброс уровня
def reset_level(level):
    global cur_score
    cur_score = 0

    data = load_level(level)
    if data:
        for group in groups:
            group.empty()
        world = World(win, data, groups)
        player.reset(win, player_pos, world, groups)
    return world


score = 0
cur_score = 0
time_freeze = False
time_freeze_count = 0
main_menu = True
game_over = False
level_won = False
game_won = False
running = True

while running:
    pressed_keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if pressed_keys[K_r]:
            if score >= 10:
                time_freeze_fx.play()
                score -= 10
                cur_score -= 10
                draw_text(win, f'{score}', ((WIDTH // tile_size - 2) * tile_size, tile_size // 2 + 10))
                time_freeze = True
        if pressed_keys[K_e]:
            if score >= 7:
                wave_fx.play()
                score -= 7
                cur_score -= 7
                draw_text(win, f'{score}', ((WIDTH // tile_size - 2) * tile_size, tile_size // 2 + 10))
                wave = Wave(player.rect.x + 7, player.rect.y + 40, player.direction)
                groups[-1].add(wave)

    # Отрисовка
    win.blit(bg, (0, 0))
    world.draw()
    for group in groups:
        group.draw(win)

    if main_menu:
        win.blit(menu, (WIDTH // 4, HEIGHT // 4))
        play_game = play_btn.draw(win)
        if play_game:
            main_menu = False
            game_over = False
            game_won = False
            score = 0
    else:
        if not game_over and not game_won:
            enemies_group.update(player)
            platform_group.update()
            exit_group.update(player)
            wave_group.update()
            for i in groups[-1]:
                coll = pygame.sprite.spritecollide(i, world.groups[4], True)
                if coll:
                    i.kill()

            if pygame.sprite.spritecollide(player, potion_group, True):
                sounds[0].play()
                cur_score += 1
                score += 1
            draw_text(win, f'{score}', ((WIDTH // tile_size - 2) * tile_size, tile_size // 2 + 10))
        game_over, level_won = player.update(pressed_keys, game_over, level_won, game_won)

        if game_over and not game_won:
            time_freeze = False
            replay = replay_btn.draw(win)
            home = home_btn.draw(win)
            exit = exit_btn.draw(win)
            if replay:
                score -= cur_score
                world = reset_level(level)
                game_over = False
            if home:
                game_over = True
                main_menu = True
                bg = bg1
                level = 1
                world = reset_level(level)
            if exit:
                running = False

        if level_won:
            if level <= max_level:
                level += 1
                game_level = f'levels/level{level}_data'
                if os.path.exists(game_level):
                    data = []
                    world = reset_level(level)
                    level_won = False
                    score += cur_score
                bg = random.choice([bg1, bg2])
            else:
                win.fill((50, 50, 50))
                game_won = True
                bg = bg1
                win.blit(you_won, (WIDTH // 4, HEIGHT // 4))
                win.blit(score_font.render(f'Score: {score}', True, (255, 204, 0)), (450, 450))
                home = home_btn.draw(win)
                if home:
                    game_over = True
                    main_menu = True
                    level_won = False
                    level = 1
                    world = reset_level(level)
    pygame.display.flip()
    if time_freeze:
        clock.tick(FPS - 25)
        time_freeze_count += 1
    else:
        clock.tick(FPS)
    if time_freeze_count == 100:
        time_freeze_count = 0
        time_freeze = False

pygame.quit()
