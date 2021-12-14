from pacman import Pacman
from ghost import Ghost
from coin import Coin
from booster import Booster
from global_def import *
import random

class Maze:
    def __init__(self, level_name):
        self.level = []
        self.level_name = level_name

    def load(self):
        with open('levels/' + str(self.level_name) + '.txt') as file:
            lines = file.readlines()
            self.level = [[c for c in line.strip()] for line in lines]

    def get_level(self):
        return self.level

    def get_level_name(self):
        return self.level_name

    def set_level(self, level_name):
        self.level_name = level_name

    def coord_to_real_block_position(self, pos):
        block_pos_x = pos[0] / SPRITE_SIZE
        block_pos_y = pos[1] / SPRITE_SIZE
        return (block_pos_x, block_pos_y)

    def coord_to_floored_block_position(self, pos):
        block_pos_x = pos[0] // SPRITE_SIZE
        block_pos_y = pos[1] // SPRITE_SIZE
        return (int(block_pos_x), int(block_pos_y))

    def check_collision(self, pos):
        block_pos = self.coord_to_floored_block_position(pos)
        if (self.level[block_pos[1]][block_pos[0]] == '#'):
            return True
        return False

    def draw_level(self):
        for i in range(len(self.level)):
            for j in range(len(self.level[i])):
                if self.level[i][j] == '#':
                    screen.blit(wall_sprite, (j * SPRITE_SIZE, i * SPRITE_SIZE))
    
    def fix_generated_level(self, generated_level, borders):
        border_h = borders[0]
        border_v = borders[1]
        for i in range(border_v[0], border_v[1]):
            for j in range(border_h[0], border_h[1]):
                if generated_level[i][j] == '.':
                    self.recursive_generation((j, i), generated_level, borders)

    def if_pos_in_range(self, pos, direction, borders):
        adjx = pos[0]
        adjy = pos[1]
        d_row = direction[0]
        d_col = direction[1]
        border_h = borders[0]
        border_v = borders[1]
        if adjx in range(border_h[0], border_h[1]) and adjy in range(border_v[0], border_v[1]):
            return True
        return False

    def recursive_generation(self, pos, maze, borders):
        maze[pos[1]][pos[0]] = '!'

        d_row = [-1, 0, 1, 0, -1, 1, -1, 1]
        d_col = [0, 1, 0, -1, -1, 1, 1, -1]   

        for i in range(8):
            adjx = pos[0] + d_row[i]
            adjy = pos[1] + d_col[i]
            if maze[adjy][adjx] == '.':
                maze[adjy][adjx] = '#'   

        directions = []
        for i in range(4):
            adjx = pos[0] + d_row[i]
            adjy = pos[1] + d_col[i]
            if maze[adjy][adjx] == '.' or (maze[adjy][adjx] == '#' and self.if_pos_in_range((adjx, adjy), (d_row[i], d_col[i]), borders) and maze[adjy + d_row[i]][adjx + d_col[i]] == '#' and maze[adjy - d_row[i]][adjx - d_col[i]] == '#'):
                directions.append((adjx, adjy))
        if len(directions) == 0:
            return 
        directions_number = random.randint(1, len(directions))
        new_positions = []
        for i in range(directions_number):
            index = random.randint(0, len(directions) - 1)
            maze[directions[index][1]][directions[index][0]] = '!'
            new_positions.append(directions[index])
            del directions[index]
        for new_position in new_positions:
            self.recursive_generation(new_position, maze, borders)

    def place_items_randomized(self, maze, rand_list, item_symbol, items_num):
        for i in range(items_num):
            rand_ind = random.randint(0, len(rand_list) - 1)
            pos = rand_list[rand_ind]
            del rand_list[rand_ind]
            maze[pos[1]][pos[0]] = item_symbol
    
    def generate_new_level(self, filename, smart_bots, random_bots):
        generated_level = [['.' for j in range(TOTAL_SPRITES_H)] for i in range(TOTAL_SPRITES_V)]
        length = max(TOTAL_SPRITES_H, TOTAL_SPRITES_H)
        for i in range(2, TOTAL_SPRITES_V - 2):
            generated_level[i][2] = '#'
            generated_level[i][TOTAL_SPRITES_H - 3] = '#'
        for j in range(2, TOTAL_SPRITES_H - 2):
            generated_level[2][j] = '#'
            generated_level[TOTAL_SPRITES_V - 3][j] = '#'

        self.recursive_generation((7, 3), generated_level, ((3, TOTAL_SPRITES_H - 3), (3, TOTAL_SPRITES_V - 3)))
        # Broken
        #self.fix_generated_level(generated_level, ((3, TOTAL_SPRITES_H - 3), (3, TOTAL_SPRITES_V - 3)))

        available_pos = []
        for i in range(len(generated_level)):
                for j in range(len(generated_level[i])):
                    if generated_level[i][j] == '!':
                        available_pos.append((j, i))

        self.place_items_randomized(generated_level, available_pos, 'p', 1)
        #self.place_items_randomized(generated_level, available_pos, 'b', 4)
        self.place_items_randomized(generated_level, available_pos, 'l', smart_bots)
        self.place_items_randomized(generated_level, available_pos, 'r', random_bots)
        self.place_items_randomized(generated_level, available_pos, 'k', 4)
        self.place_items_randomized(generated_level, available_pos, 's', 2)
        self.place_items_randomized(generated_level, available_pos, 'v', 2)
        self.place_items_randomized(generated_level, available_pos, 'c', len(available_pos))
        
        with open('levels/' + str(filename) + '.txt', 'w') as file:
            for row in generated_level:
                for char in row:
                    file.write(char)
                file.write('\n')

    def get_free_random_cell(self):
        free_cells = []
        for i in range(len(self.level)):
            for j in range(len(self.level[i])):
                if self.level[i][j] != '#':
                    free_cells.append((j, i))
        rand_ind = random.randint(0, len(free_cells) - 1)
        return free_cells[rand_ind]


    def init_entities(self):
        i = 0
        ghosts = []
        coins = []
        boosters = []
        sprite_index = 0
        for line in self.level:
            j = 0
            for block in line:
                if block == 'p':
                    pacman = Pacman(pacman_sprite1, j * SPRITE_SIZE, i * SPRITE_SIZE)
                if block == 'l':
                    ghosts.append(Ghost(ghost_sprites[sprite_index % len(ghost_sprites)], j * SPRITE_SIZE, i * SPRITE_SIZE, False))
                    sprite_index += 1
                if block == 'r':
                    ghosts.append(Ghost(ghost_sprites[sprite_index % len(ghost_sprites)], j * SPRITE_SIZE, i * SPRITE_SIZE, True))
                    sprite_index += 1
                if block == 'c':
                    coins.append(Coin(coin_sprite, j * SPRITE_SIZE + SPRITE_SIZE / 3, i * SPRITE_SIZE + SPRITE_SIZE / 3, COIN_VALUE))
                if block == 'v':
                    coins.append(Coin(cherry_sprite, j * SPRITE_SIZE, i * SPRITE_SIZE, COIN_VALUE * 5))
                if block == 's':
                    coins.append(Coin(strawberry_sprite, j * SPRITE_SIZE, i * SPRITE_SIZE, COIN_VALUE * 5))
                if block == 'k':
                    boosters.append(Booster(booster_sprite, j * SPRITE_SIZE, i * SPRITE_SIZE))
                j += 1
            i += 1
        return pacman, ghosts, coins, boosters

    def check_block(self, block_x, block_y):
        return self.level[int(block_y)][int(block_x)]