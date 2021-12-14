import pygame
from spritesheetutil import SpriteSheetUtil
from csv import writer
from skimage import color as skc, transform as skt
import numpy as np
import random
import torch
from collections import deque
from model import Linear_QNet, QTrainer


######################
# Game configuration #
######################

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 720
SPRITE_SIZE = 48
TOTAL_SPRITES_H = SCREEN_WIDTH // SPRITE_SIZE
TOTAL_SPRITES_V = SCREEN_HEIGHT // SPRITE_SIZE
SPRITE_CHANGE_INTERVAL = 5
BLINKING_BASE_INTERVAL = 20
BOT_CHANGE_DIRECTION_INTERVAL = 80
PACMAN_CHANGE_DIRECTION_INTERVAL = 12
#KILLER_MODE_DURATION = 600
KILLER_MODE_DURATION = 20
ANIM_FRAME_DURATION = 10
#RESPAWN_TIME = 300
RESPAWN_TIME = 10
ALLOWANCE_THRESHOLD = 0.35
BLINKING_WARNING_THRESHOLD = 200
EATEN_ENEMY_REWARD = 200
COIN_VALUE = 10
MIN_COLLISION_DISTANCE = 25
FPS = 60
TRAVERSAL_FUNCTIONS_AMOUNT = 2

####################
# NN configuration #
####################

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

random_level_name = 'random_level'
levels = [random_level_name, 'level1', 'level2', 'level3']
level_idx = 0

results_filename = 'results.csv'

colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
icon = pygame.image.load('resources/icon.png')

transition_font = pygame.font.Font('freesansbold.ttf', 32)
hud_font = pygame.font.Font('freesansbold.ttf', 24)

spritesheet_util = SpriteSheetUtil('pacman.png')

ghost_sprites = [spritesheet_util.get_image(1, 83, 16, 16, 3),
    spritesheet_util.get_image(601, 269, 16, 16, 3),
    spritesheet_util.get_image(601, 641, 16, 16, 3),
    spritesheet_util.get_image(401, 83, 16, 16, 3)]
pacman_death_anim = [spritesheet_util.get_image(201, 692, 16, 16, 3),
    spritesheet_util.get_image(218, 692, 16, 16, 3),
    spritesheet_util.get_image(235, 692, 16, 16, 3),
    spritesheet_util.get_image(252, 692, 16, 16, 3),
    spritesheet_util.get_image(269, 692, 16, 16, 3),
    spritesheet_util.get_image(286, 692, 16, 16, 3),
    spritesheet_util.get_image(201, 709, 16, 16, 3),
    spritesheet_util.get_image(218, 709, 16, 16, 3),
    spritesheet_util.get_image(235, 709, 16, 16, 3),
    spritesheet_util.get_image(252, 709, 16, 16, 3),
    spritesheet_util.get_image(269, 709, 16, 16, 3),
    spritesheet_util.get_image(286, 709, 16, 16, 3)]
ghost_killer_mode_sprite = spritesheet_util.get_image(201, 168, 16, 16, 3)
blank_sprite = spritesheet_util.get_image(286, 709, 16, 16, 3)
wall_sprite = spritesheet_util.get_image(801, 604, 48, 48, 1)
coin_sprite = spritesheet_util.get_image(536, 586, 8, 8, 2)
cherry_sprite = spritesheet_util.get_image(601, 489, 16, 16, 3)
strawberry_sprite = spritesheet_util.get_image(618, 489, 16, 16, 3)
booster_sprite = spritesheet_util.get_image(669, 489, 16, 16, 3)
pacman_sprite1 = spritesheet_util.get_image(303, 709, 16, 16, 3)
pacman_sprite2 = spritesheet_util.get_image(303, 692, 16, 16, 3)

n_games = 0
epsilon = 0
gamma = 0.9
memory = deque(maxlen = MAX_MEMORY)
device = torch.device('cuda')
model = Linear_QNet(TOTAL_SPRITES_H * TOTAL_SPRITES_V * 12 * 12, 256, 5, device)
trainer = QTrainer(model, lr = LR, gamma = gamma, device = device)

def find_dist(pos1, pos2):
    return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5

def find_next_cell(path_matrix):
    cell = (-1, -1)
    for i in range(len(path_matrix)):
        for j in range(len(path_matrix[0])):
            if path_matrix[i][j] == 1:
                cell = (j, i)
            elif path_matrix[i][j] == 2:
                return (j, i)
    return cell

def get_direction(coord1, coord2):
    if coord1 - coord2 > 0:
        return 1
    if coord1 - coord2 < 0:
        return -1
    return 0

def apply_ghost_sprites(ghosts, sprites):
    ind = 0
    for ghost in ghosts:
        ghost.set_sprite(sprites[ind % len(sprites)])
        ind += 1

def append_row_to_csv(filename, list_of_elem):
    with open(filename, 'a+', newline = '') as write_obj:
        csv_writer = writer(write_obj)
        csv_writer.writerow(list_of_elem)

def get_state(maze, ghosts, pacman, coins, boosters):
    # level = maze.get_level()
    # state = np.zeros((TOTAL_SPRITES_V, TOTAL_SPRITES_H))
    # for i in range(len(level)):
    #     for j in range(len(level[i])):
    #         if level[i][j] == '#':
    #             state[i][j] = 1
    # for ghost in ghosts:
    #     if ghost.get_visibility_state():
    #         ghost_pos = maze.coord_to_floored_block_position(ghost.get_pos())
    #         state[ghost_pos[1]][ghost_pos[0]] = 2
    # pacman_pos = maze.coord_to_floored_block_position(pacman.get_pos())
    # state[pacman_pos[1]][pacman_pos[0]] = 3
    # for coin in coins:
    #     if coin.get_visibility_state():
    #         coin_pos = maze.coord_to_floored_block_position(coin.get_pos())
    #         state[coin_pos[1]][coin_pos[0]] = 4
    # for booster in boosters:
    #     if booster.get_visibility_state():
    #         booster_pos = maze.coord_to_floored_block_position(booster.get_pos())
    #         state[booster_pos[1]][booster_pos[0]] = 5
    # return state.flatten()
    screen_state = pygame.surfarray.array3d(pygame.display.get_surface())
    image_processed = skc.rgb2gray(screen_state)
    image_processed = skt.resize(image_processed, (TOTAL_SPRITES_H * 12, TOTAL_SPRITES_V * 12))
    return np.array(image_processed).flatten()

def remember(state, action, reward, next_state, game_over):
    global memory
    memory.append((state, action, reward, next_state, game_over))

def train_long_memory():
    if len(memory) > BATCH_SIZE:
        mini_sample = random.sample(memory, BATCH_SIZE)
    else:
        mini_sample = memory
    states, actions, rewards, next_states, game_overs = zip(*mini_sample)
    trainer.train_step(states, actions, rewards, next_states, game_overs)

def train_short_memory(state, action, reward, next_state, game_over):
    trainer.train_step(state, action, reward, next_state, game_over)

def get_action(state):
    global epsilon
    epsilon = 180 - n_games
    final_move = np.zeros(5)
    if random.randint(0, 400) < epsilon:
        move = random.randint(0, 4)
        final_move[move] = 1
    else:
        state0 = torch.tensor(state, dtype = torch.float, device = device)
        prediction = model(state0)
        move = torch.argmax(prediction).item()
        final_move[move] = 1
    return final_move