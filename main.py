from algorithms import Algoritms
import pygame
import random
import time

pygame.init()

from maze import Maze
from global_def import *
from plotter import plot

pygame.display.set_caption('Pacman')
pygame.display.set_icon(icon)

#random.seed(7)
maze = Maze(levels[1])
#smart_bots = int(input("Enter amount of smart bots: "))
#random_bots = int(input("Enter amount of random bots: "))
#chosen_alg = input("Enter algorihtm(minimax(m)/expectimax(e)): ")
smart_bots = 4
random_bots = 0
chosen_alg = 'm'
graphics_mode_enabled = True
maze.generate_new_level(random_level_name, smart_bots, random_bots)
algorithms = Algoritms()
func_helper = [('BFS', algorithms.get_bfs_function()), ('UCS', algorithms.get_ucs_function())]
func_index = 0

running = True
clock = pygame.time.Clock()
reset = True
is_minimax = True
if (chosen_alg == 'e'):
    is_minimax = False
lives = 3
score = 0
record_score = 0
plot_scores = []
plot_mean_scores = []
total_score = 0

while running:
    if reset:
        maze.load()
        pacman, ghosts, coins, boosters = maze.init_entities()
        sprite_order = 1
        sprite_interval = SPRITE_CHANGE_INTERVAL
        bot_interval = BOT_CHANGE_DIRECTION_INTERVAL
        pacman_interval = PACMAN_CHANGE_DIRECTION_INTERVAL
        killer_timer = KILLER_MODE_DURATION
        blinking_interval = BLINKING_BASE_INTERVAL
        anim_interval = ANIM_FRAME_DURATION
        game_start_time = time.time()
        anim_ind = 0
        rand_helper = [-1, 1]
        is_killer_mode_active = False
        has_blinked = False
        is_anim_being_played = False
        has_player_lost = False
        are_all_coins_collected = False
        reset = False

    while running and not(has_player_lost) and not(are_all_coins_collected):
        if (graphics_mode_enabled):
            clock.tick(FPS)
        #start_time = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    func_index = (func_index + 1) % TRAVERSAL_FUNCTIONS_AMOUNT
                if event.key == pygame.K_LEFT:
                    pass
                    #pacman.set_velocity(-3, 0)
                if event.key == pygame.K_RIGHT:
                    pass
                    #pacman.set_velocity(3, 0)
                if event.key == pygame.K_UP:
                    pass
                    #pacman.set_velocity(0, -3)
                if event.key == pygame.K_DOWN:
                    pass
                    #pacman.set_velocity(0, 3)

        state_old = get_state(maze, ghosts, pacman, coins, boosters)
        final_move = get_action(state_old)
        cur_score = score
        cur_lives = lives

        if is_killer_mode_active:
            killer_timer -= 1
            if killer_timer < BLINKING_WARNING_THRESHOLD:
                blinking_interval -= 1
                if blinking_interval == 0:
                    blinking_interval = BLINKING_BASE_INTERVAL - (BLINKING_WARNING_THRESHOLD - killer_timer) // BLINKING_BASE_INTERVAL * 2
                    if blinking_interval < BLINKING_BASE_INTERVAL // 5:
                        blinking_interval = BLINKING_BASE_INTERVAL // 5
                    if has_blinked:
                        apply_ghost_sprites(ghosts, [ghost_killer_mode_sprite])
                    else:
                        apply_ghost_sprites(ghosts, [blank_sprite])
                    has_blinked = not(has_blinked)
            if killer_timer == 0:
                is_killer_mode_active = False
                apply_ghost_sprites(ghosts, ghost_sprites)

        sprite_interval -= 1
        if (sprite_interval == 0):
            sprite_interval = SPRITE_CHANGE_INTERVAL
            sprite_order = sprite_order % 2 + 1
            if (sprite_order == 1):
                pacman.set_sprite(pacman_sprite1)
            else:
                pacman.set_sprite(pacman_sprite2)

        screen.fill((0, 0, 0))

        min_steps = 999999
        pacman_ppos = pacman.get_pos()
        pacman_coordinates = maze.coord_to_floored_block_position(pacman_ppos)
        coin_coordinates = []
        are_all_coins_collected = True
        for coin in coins:
            if (coin.get_visibility_state()):
                if pacman.check_entity_collision(coin) and not(is_anim_being_played):
                    score += coin.get_value()
                    coin.change_visibility_state()
                else:
                    coin_coordinates.append(maze.coord_to_floored_block_position(coin.get_pos()))
                    # Undone prior to lab4 
                    #steps, path = algorithms.find_path(algorithms.get_astar_function(), maze.get_level(), maze.coord_to_floored_block_position(pacman_ppos), maze.coord_to_floored_block_position(coin.get_pos()))
                    #if steps < min_steps:
                    #    min_steps = steps
                    #    min_path = path
                    are_all_coins_collected = False
                    if (graphics_mode_enabled):
                        screen.blit(coin.get_sprite(), coin.get_pos())

        if are_all_coins_collected:
            row_contents = [1, str(time.time() - game_start_time)[ : 6], score, 1 if (is_minimax) else 0]
            append_row_to_csv(results_filename, row_contents)
            level_idx += 1
            if (len(levels) > level_idx):
                # maze.set_level(levels[level_idx])
                maze.set_level(levels[1])

        #UNDONE
        #next_cell = find_next_cell(min_path)
        #target_ppos = (next_cell[0] * SPRITE_SIZE, next_cell[1] * SPRITE_SIZE)
        #pacman.set_velocity(get_direction(target_ppos[0], pacman_ppos[0]) * 3, get_direction(target_ppos[1], pacman_ppos[1]) * 3)

        for booster in boosters:
            if (booster.get_visibility_state()):
                if pacman.check_entity_collision(booster) and not(is_anim_being_played):
                    is_killer_mode_active = True
                    killer_timer = KILLER_MODE_DURATION
                    blinking_interval = BLINKING_BASE_INTERVAL
                    has_blinked = False
                    apply_ghost_sprites(ghosts, [ghost_killer_mode_sprite])
                    booster.change_visibility_state()
                else:
                    if (graphics_mode_enabled):
                        screen.blit(booster.get_sprite(), booster.get_pos())

        bot_interval -= 1
        pacman_interval -= 1
        time_total = 0
        color_alg_visual_ind = 0
        rect_offset_ind = 2
        ghost_coordinates = []

        # Try to solve the problem in one piece w/o second loop(overlapping path over ghosts)
        for ghost in ghosts:
            ghost_coordinates.append(maze.coord_to_floored_block_position(ghost.get_pos()))
            if ghost.get_visibility_state():
                ghost_ppos = ghost.get_pos()
                target_ppos = ghost_ppos
                if not(ghost.is_randomized()):
                    #start_time = time.time()
                    steps, path = algorithms.find_path(func_helper[func_index][1], maze.get_level(), maze.coord_to_floored_block_position(ghost_ppos), maze.coord_to_floored_block_position(pacman_ppos))
                    #time_total += time.time() - start_time
                    next_cell = find_next_cell(path)
                    target_ppos = (next_cell[0] * SPRITE_SIZE, next_cell[1] * SPRITE_SIZE)
                    if next_cell == maze.coord_to_floored_block_position(pacman_ppos):
                        target_ppos = (pacman_ppos[0], pacman_ppos[1])
                    ghost.set_velocity(get_direction(target_ppos[0], ghost_ppos[0]) * 12, get_direction(target_ppos[1], ghost_ppos[1]) * 12)

                    # for i in range(len(path)):
                    #     for j in range(len(path[i])):
                    #         if path[i][j] != 0:
                    #             pygame.draw.rect(screen, colors[color_alg_visual_ind], pygame.Rect(j * SPRITE_SIZE + rect_offset_ind, i * SPRITE_SIZE + rect_offset_ind, SPRITE_SIZE - 2 * rect_offset_ind, SPRITE_SIZE - 2 * rect_offset_ind),  2)
                    # rect_offset_ind += 2
                    # color_alg_visual_ind = (color_alg_visual_ind + 1) % len(colors)
                elif bot_interval == 0:
                    # Choose the option
                    new_velocity_x = (random.randint(0, 2) - 1) * 3
                    if new_velocity_x == 0:
                        new_velocity_y = rand_helper[random.randint(0, 1)] * 3
                    else:
                        new_velocity_y = 0
                    ghost.set_velocity(new_velocity_x, new_velocity_y)
                    #next_cell = maze.get_free_random_cell()
                    #target_ppos = (next_cell[0] * SPRITE_SIZE, next_cell[1] * SPRITE_SIZE)
                    #ghost.set_velocity(get_direction(target_ppos[0], ghost_ppos[0]) * 3, get_direction(target_ppos[1], ghost_ppos[1]) * 3)

                
        
        if (bot_interval == 0):
            bot_interval = BOT_CHANGE_DIRECTION_INTERVAL
        pacman_velocity = (0, 0)
        if final_move[1] == 1:
            pacman_velocity = (0, -16)
        if final_move[2] == 1:
            pacman_velocity = (16, 0)
        if final_move[3] == 1:
            pacman_velocity = (0, 16)
        if final_move[4] == 1:
            pacman_velocity = (-16, 0)
        pacman.set_velocity(pacman_velocity[0], pacman_velocity[1])
        # Make it change direction every 12 ticks COMMENTED TEMPORARILY
        # if (pacman_interval == 0):
        #     pacman_interval = PACMAN_CHANGE_DIRECTION_INTERVAL
        #     if is_minimax:
        #         minimax_value, target = algorithms.minimax(maze.get_level(), pacman_coordinates, ghost_coordinates, coin_coordinates, 1, -99999999, 99999999, 0)
        #     else:
        #         minimax_value, target = algorithms.expectimax(maze.get_level(), pacman_coordinates, ghost_coordinates, coin_coordinates, 1, 0)
        #     #print(minimax_value, ' ###### ', target, ' ### ', pacman_coordinates)
        #     if not(target is None):
        #         target_ppos = (target[0] * SPRITE_SIZE, target[1] * SPRITE_SIZE)
        #         pacman.set_velocity(get_direction(target_ppos[0], pacman_ppos[0]) * 4, get_direction(target_ppos[1], pacman_ppos[1]) * 4)

        if not(is_anim_being_played):
            pacman.move(maze)

        for ghost in ghosts:
            if not(ghost.get_visibility_state()):
                ghost.set_invisibility_timer(ghost.get_invisibility_timer() - 1)
                if ghost.get_invisibility_timer() == 0:
                    ghost.change_visibility_state()
                    ghost.reset_pos()
            else:
                #if bot_interval == 0:
                #    new_velocity_x = (random.randint(0, 2) - 1) * 3
                #    if new_velocity_x == 0:
                #        new_velocity_y = rand_helper[random.randint(0, 1)] * 3
                #    else:
                #        new_velocity_y = 0
                #    ghost.set_velocity(new_velocity_x, new_velocity_y)
                if pacman.check_entity_collision(ghost) and not(is_anim_being_played):
                    if is_killer_mode_active:
                       ghost.set_invisibility_timer(RESPAWN_TIME)
                       ghost.change_visibility_state()
                       score += EATEN_ENEMY_REWARD
                    else: 
                        anim_interval = 1
                        #anim_interval = ANIM_FRAME_DURATION
                        is_anim_being_played = True
                        anim_ind = 0
                if not(is_anim_being_played):
                    ghost.move(maze)
                if (graphics_mode_enabled):
                    screen.blit(ghost.get_sprite(), ghost.get_pos())
        
        reward = 0
        if cur_score < score:
            reward = 1
        if cur_lives > lives:
            reward = -1

        if not(is_anim_being_played):
            if (graphics_mode_enabled):
                screen.blit(pacman.get_directed_sprite(), pacman.get_pos())

        if (is_anim_being_played):
            is_anim_being_played = False
            lives -= 1
            if lives == 0:
                has_player_lost = True
                row_contents = [0, str(time.time() - game_start_time)[ : 6], score, 1 if (is_minimax) else 0]
                append_row_to_csv(results_filename, row_contents)
            else:
                pacman.reset_pos()
            #anim_interval -= 1
            #if anim_interval == 0:
            #    if anim_ind >= len(pacman_death_anim):
            #        is_anim_being_played = False
            #        lives -= 1
            #        if lives == 0:
            #            has_player_lost = True
            #            row_contents = [0, str(time.time() - game_start_time)[ : 6], score, 1 if (is_minimax) else 0]
            #            append_row_to_csv(results_filename, row_contents)
            #        else:
            #            pacman.reset_pos()
            #    else:
            #        anim_ind += 1
            #        anim_interval = ANIM_FRAME_DURATION
            #if anim_ind < len(pacman_death_anim):
            #    if (graphics_mode_enabled):
            #        screen.blit(pacman_death_anim[anim_ind], pacman.get_pos())
        if (graphics_mode_enabled):
            maze.draw_level()

        # score_ins = hud_font.render('Score: ' + str(score), True, (255, 255, 255))
        # lives_ins = hud_font.render('Lives: ' + str(lives), True, (255, 255, 255))
        # level_ins = hud_font.render('Level: ' + str(level_idx + 1) + '/' + str(len(levels)), True, (255, 255, 255))
        # current_alg_ins = hud_font.render('Current algorithm: ' + func_helper[func_index][0], True, (255, 255, 255))
        # #alg_exec_time_ins = hud_font.render('Algorithm execution time: ' + str(time_total * 1000)[:6] + 'ms', True, (255, 255, 255))
        # screen.blit(score_ins, (0, 0))
        # screen.blit(lives_ins, (0, 30))
        # screen.blit(level_ins, (0, 60))
        # screen.blit(current_alg_ins, (0, 90))
        #screen.blit(alg_exec_time_ins, (0, 120))

        pygame.display.update()
        state_new = get_state(maze, ghosts, pacman, coins, boosters)
        game_over = has_player_lost or are_all_coins_collected
        train_short_memory(state_old, final_move, reward, state_new, game_over)
        remember(state_old, final_move, reward, state_new, game_over)
        #print(time.time() - start_time)

    n_games += 1
    train_long_memory()
    if score > record_score:
        record_score = score
        model.save()
    print("Game #" + str(n_games), 'ended with score', score, 'with overall record', record_score)
    plot_scores.append(score)
    total_score += score
    mean_score = total_score / n_games
    plot_mean_scores.append(mean_score)
    plot(plot_scores, plot_mean_scores)

    reset = True
    if has_player_lost:
        maze.set_level(levels[1])
        level_idx = 1
        lives = 3
        score = 0
    if are_all_coins_collected and len(levels) <= level_idx:
        running = False

    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_SPACE:
            #         reset = True
            #         if has_player_lost:
            #             maze.set_level(levels[0])
            #             level_idx = 0
            #             lives = 3
            #             score = 0
            #         if are_all_coins_collected and len(levels) <= level_idx:
            #             running = False

    # if running and has_player_lost:
    #     screen.fill((0, 0, 0))
    #     gameover_ins = transition_font.render('Game over!', True, (255, 255, 255))
    #     end_score_ins = transition_font.render('Score: ' + str(score), True, (255, 255, 255))
    #     press_key_ins = transition_font.render('Press SPACEBAR to restart the game', True, (255, 255, 255))
    #     screen.blit(gameover_ins, gameover_ins.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40)))
    #     screen.blit(end_score_ins, end_score_ins.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)))
    #     screen.blit(press_key_ins, press_key_ins.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40)))
    #     pygame.display.update()
# 
    # if running and are_all_coins_collected:
    #     screen.fill((0, 0, 0))
    #     level_completed_ins = transition_font.render('You have completed the level!', True, (255, 255, 255))
    #     end_score_ins = transition_font.render('Score: ' + str(score), True, (255, 255, 255))
    #     if (len(levels) > level_idx):
    #         press_key_ins = transition_font.render('Press SPACEBAR to procceed to the next level', True, (255, 255, 255))
    #     else:
    #         press_key_ins = transition_font.render('Press SPACEBAR to close the game', True, (255, 255, 255))
    #     screen.blit(level_completed_ins, level_completed_ins.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40)))
    #     screen.blit(end_score_ins, end_score_ins.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)))
    #     screen.blit(press_key_ins, press_key_ins.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40)))
    #     pygame.display.update()