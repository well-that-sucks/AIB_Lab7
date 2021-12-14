from collections import deque as queue

class Algoritms:
    MINIMAX_MAX_DEPTH = 4
    EXPECTIMAX_MAX_DEPTH = 3
    MINIMAX_WIN_VALUE = 1000000

    def return_min(self, res1, res2):
        if (res1[0] <= res2[0]):
            return res1
        return res2

    def retrieve_shortest_path(self, maze, pos, target, path_matrix):
        d_row = [-1, 0, 1, 0]
        d_col = [0, 1, 0, -1]
        t_matrix = [[0 for element in row] for row in maze]
        t_matrix[target[1]][target[0]] = path_matrix[target[1]][target[0]]
        position = target

        while position != pos:
            for i in range(4):
                adjx = position[0] + d_row[i]
                adjy = position[1] + d_col[i]
                if path_matrix[position[1]][position[0]] == path_matrix[adjy][adjx] + 1:
                    t_matrix[adjy][adjx] = t_matrix[position[1]][position[0]] - 1
                    position = (adjx, adjy)
                    break
        return t_matrix

    def find_path_dfs(self, maze, pos, target, step, path_matrix, visited):
        if not(pos[1] in range(len(maze)) and pos[0] in range(len(maze[0]))) or visited[pos[1]][pos[0]]:
            return (999999, path_matrix)
        path_matrix[pos[1]][pos[0]] = step
        if pos == target:
            return (step, path_matrix)
        if maze[pos[1]][pos[0]] != '#':
            visited[pos[1]][pos[0]] = True
            res = self.find_path_dfs(maze, (pos[0] + 1, pos[1]), target, step + 1, [x[:] for x in path_matrix], visited)
            if res[0] != 999999:
                return res
            res = self.find_path_dfs(maze, (pos[0] - 1, pos[1]), target, step + 1, [x[:] for x in path_matrix], visited)
            if res[0] != 999999:
                return res
            res = self.find_path_dfs(maze, (pos[0], pos[1] + 1), target, step + 1, [x[:] for x in path_matrix], visited)
            if res[0] != 999999:
                return res
            res = self.find_path_dfs(maze, (pos[0], pos[1] - 1), target, step + 1, [x[:] for x in path_matrix], visited)
            if res[0] != 999999:
                return res
            #res = self.find_path_dfs(maze, (pos[0] + 1, pos[1]), target, step + 1, [x[:] for x in path_matrix], visited)
            #res = self.return_min(res, self.find_path_dfs(maze, (pos[0] - 1, pos[1]), target, step + 1, [x[:] for x in path_matrix], visited))
            #res = self.return_min(res, self.find_path_dfs(maze, (pos[0], pos[1] + 1), target, step + 1, [x[:] for x in path_matrix], visited))
            #res = self.return_min(res, self.find_path_dfs(maze, (pos[0], pos[1] - 1), target, step + 1, [x[:] for x in path_matrix], visited))
            #visited[pos[1]][pos[0]] = False
            return res
        return (999999, path_matrix)

    def find_path_bfs(self, maze, pos, target, step, path_matrix, visited):
        d_row = [-1, 0, 1, 0]
        d_col = [0, 1, 0, -1]
        q = queue()
        q.append((step, pos[0], pos[1]))

        while (len(q) > 0):
            cell = q.popleft()
            visited[cell[2]][cell[1]] = True
            if path_matrix[cell[2]][cell[1]] > cell[0] or path_matrix[cell[2]][cell[1]] == 0:
                path_matrix[cell[2]][cell[1]] = cell[0]
            if (cell[1], cell[2]) == target:
                return cell[0], self.retrieve_shortest_path(maze, pos, target, path_matrix)
            else:
                for i in range(4):
                    adjx = cell[1] + d_row[i]
                    adjy = cell[2] + d_col[i]
                    if adjy in range(len(maze)) and adjx in range(len(maze[0])) and not(visited[adjy][adjx]) and maze[adjy][adjx] != '#':
                        q.append((cell[0] + 1, adjx, adjy))

        return path_matrix[target[1]][target[0]], self.retrieve_shortest_path(maze, pos, target, path_matrix)

    def find_path_ucs(self, maze, pos, target, step, path_matrix, visited):
        d_row = [-1, 0, 1, 0]
        d_col = [0, 1, 0, -1]

        queue = []
        queue.append((step, pos[0], pos[1]))

        while (len(queue) > 0):
            queue = sorted(queue)
            cell = queue[0]
            del queue[0]
            if not(visited[cell[2]][cell[1]]):
                visited[cell[2]][cell[1]] = True
                if path_matrix[cell[2]][cell[1]] > cell[0] or path_matrix[cell[2]][cell[1]] == 0:
                    path_matrix[cell[2]][cell[1]] = cell[0]
                if (cell[1], cell[2]) == target:
                    return cell[0], self.retrieve_shortest_path(maze, pos, target, path_matrix)
                else:
                    for i in range(4):
                        adjx = cell[1] + d_row[i]
                        adjy = cell[2] + d_col[i]
                        if adjy in range(len(maze)) and adjx in range(len(maze[0])) and not(visited[adjy][adjx]) and maze[adjy][adjx] != '#':
                            queue.append((cell[0] + 1, adjx, adjy))
    
        return path_matrix[target[1]][target[0]], self.retrieve_shortest_path(maze, pos, target, path_matrix)

    def find_path_astar(self, maze, pos, target, step, path_matrix, visited):
        d_row = [-1, 0, 1, 0]
        d_col = [0, 1, 0, -1]

        queue = []
        queue.append((1, 1, 0, pos[0], pos[1]))

        while (len(queue) > 0):
            queue = sorted(queue)
            cell = queue[0]
            del queue[0]
            if not(visited[cell[4]][cell[3]]):
                visited[cell[4]][cell[3]] = True
                if path_matrix[cell[4]][cell[3]] > cell[1] or path_matrix[cell[4]][cell[3]] == 0:
                    path_matrix[cell[4]][cell[3]] = cell[1]
                if (cell[3], cell[4]) == target:
                    return cell[1], self.retrieve_shortest_path(maze, pos, target, path_matrix)
                else:
                    for i in range(4):
                        adjx = cell[3] + d_row[i]
                        adjy = cell[4] + d_col[i]
                        if adjy in range(len(maze)) and adjx in range(len(maze[0])) and not(visited[adjy][adjx]) and maze[adjy][adjx] != '#':
                            cell_g = cell[1] + 1
                            cell_h = abs(adjx - target[0]) + abs(adjy - target[1])
                            queue.append((cell_g + cell_h, cell_g, cell_h, adjx, adjy))
        return path_matrix[target[1]][target[0]], self.retrieve_shortest_path(maze, pos, target, path_matrix)

    def find_path(self, search_function, maze, starting_pos, ending_pos):
        res = search_function(maze, starting_pos, ending_pos, 1, [[0 for element in row] for row in maze], [[False for element in row] for row in maze])
        return res[0], res[1]

    def get_dfs_function(self):
        return self.find_path_dfs
    
    def get_bfs_function(self):
        return self.find_path_bfs

    def get_ucs_function(self):
        return self.find_path_ucs
    
    def get_astar_function(self):
        return self.find_path_astar

    def estimating_function(self, p_coord, b_coord, c_coord, coins_collected):
        distance = 0
        for b in b_coord:
            distance += abs(p_coord[0] - b[0]) + abs(p_coord[1] - b[1])
        avg_dist = distance / len(b_coord)
        min_dist = 999999
        for c in c_coord:
            distance = abs(p_coord[0] - c[0]) + abs(p_coord[1] - c[1])
            if (distance < min_dist):
                min_dist = distance
        fx = -5000
        if len(c_coord) == 0:
            c_coord.append((1, 1))
        if (avg_dist != 0):
            fx = coins_collected * 50 + (1000 - min_dist) * (1 / len(c_coord)) * 10 - (1 / avg_dist) * 750 # Maybe 1000?
        #if (fx > self.MINIMAX_WIN_VALUE):
        #    fx = self.MINIMAX_WIN_VALUE - 999
        #if (fx < -self.MINIMAX_WIN_VALUE):
        #    fx = -self.MINIMAX_WIN_VALUE + 999
        return fx

    def get_winner(self, p_coord, b_coord, c_coord):
        if len(c_coord) == 0:
            return 1
        for c in c_coord:
            if p_coord == c and len(c_coord) <= 1:
                return 1
        for b in b_coord:
            if p_coord == b:
                return -1
        return 0

    def minimax(self, maze, p_coord, b_coord, c_coord, step, alpha, beta, coins_collected):
        winner = self.get_winner(p_coord, b_coord, c_coord)
        if (winner != 0):
            return winner * (self.MINIMAX_WIN_VALUE - step), None
        if (step > self.MINIMAX_MAX_DEPTH):
            return self.estimating_function(p_coord, b_coord, c_coord, coins_collected), None
        d_row = [-1, 0, 1, 0]
        d_col = [0, 1, 0, -1]
        if (step % 2 == 1):
            v = -9999999
            best_move = None
            for i in range(4):
                adjx = p_coord[0] + d_row[i]
                adjy = p_coord[1] + d_col[i]
                if adjy in range(len(maze)) and adjx in range(len(maze[0])) and maze[adjy][adjx] != '#':
                    is_coin_collision = False
                    i = 0
                    while not(is_coin_collision) and i in range(len(c_coord)):
                        if not(is_coin_collision) and c_coord[i] == (adjx, adjy):
                            t = c_coord[i]
                            del c_coord[i]
                            res = self.minimax(maze, (adjx, adjy), b_coord, c_coord, step + 1, alpha, beta, coins_collected + 1)[0]
                            c_coord.append(t)
                            is_coin_collision = True
                        i += 1

                    if not(is_coin_collision):
                        res = self.minimax(maze, (adjx, adjy), b_coord, c_coord, step + 1, alpha, beta, coins_collected)[0]
                    if (res > v):
                        v = res
                        if (step == 1):
                            best_move = (adjx, adjy)
                    if v >= beta:
                        return v, best_move
                    alpha = max(v, alpha)
            return v, best_move
        else:
            v = 9999999
            t_arr = []
            for i in range(len(b_coord)):
                t_arr.append(0)
            if len(t_arr) == 0:
                t_arr.append(4)
            while t_arr[0] < 4:
                t_arr[len(t_arr) - 1] += 1
                for i in reversed(range(1, len(t_arr))):
                    if t_arr[i] == 4:
                        t_arr[i] = 0
                        t_arr[i - 1] += 1
                if t_arr[0] < 4:
                    b_coord_new = []
                    for i in range(len(b_coord)):
                        adjx = b_coord[i][0] + d_row[t_arr[i]]
                        adjy = b_coord[i][1] + d_col[t_arr[i]]
                        if adjy in range(len(maze)) and adjx in range(len(maze[0])) and maze[adjy][adjx] != '#':
                            b_coord_new.append((adjx, adjy))
                    if len(b_coord_new) == len(b_coord):
                        v = min(v, self.minimax(maze, p_coord, b_coord_new, c_coord, step + 1, alpha, beta, coins_collected)[0])
                        if v <= alpha:
                            return v, None
                        beta = min(v, beta)
            return v, None

    def expectimax(self, maze, p_coord, b_coord, c_coord, step, coins_collected):
        if (step > self.EXPECTIMAX_MAX_DEPTH):
            return self.estimating_function(p_coord, b_coord, c_coord, coins_collected), None
        winner = self.get_winner(p_coord, b_coord, c_coord)
        if (winner != 0):
            return winner * (self.MINIMAX_WIN_VALUE - step), None
        d_row = [-1, 0, 1, 0]
        d_col = [0, 1, 0, -1]
        if (step % 2 == 1):
            v = -9999999
            best_move = None
            for i in range(4):
                adjx = p_coord[0] + d_row[i]
                adjy = p_coord[1] + d_col[i]
                if adjy in range(len(maze)) and adjx in range(len(maze[0])) and maze[adjy][adjx] != '#':
                    is_coin_collision = False
                    i = 0
                    while not(is_coin_collision) and i in range(len(c_coord)):
                        if not(is_coin_collision) and c_coord[i] == (adjx, adjy):
                            # Maybe solve the problem w/o deleting coin? For example, substract from length of coin list amount of coins collected in f(x)
                            t = c_coord[i]
                            del c_coord[i]
                            res = self.expectimax(maze, (adjx, adjy), b_coord, c_coord, step + 1, coins_collected + 1)[0]
                            c_coord.append(t)
                            is_coin_collision = True
                        i += 1

                    if not(is_coin_collision):
                        res = self.expectimax(maze, (adjx, adjy), b_coord, c_coord, step + 1, coins_collected)[0]
                    if (res > v):
                        v = res
                        if (step == 1):
                            best_move = (adjx, adjy)
            return v, best_move
        else:
            v = 0
            branches = 0
            t_arr = []
            for i in range(len(b_coord)):
                t_arr.append(0)
            if len(t_arr) == 0:
                t_arr.append(4)
            while t_arr[0] < 4:
                t_arr[len(t_arr) - 1] += 1
                for i in reversed(range(1, len(t_arr))):
                    if t_arr[i] == 4:
                        t_arr[i] = 0
                        t_arr[i - 1] += 1
                if t_arr[0] < 4:
                    b_coord_new = []
                    for i in range(len(b_coord)):
                        adjx = b_coord[i][0] + d_row[t_arr[i]]
                        adjy = b_coord[i][1] + d_col[t_arr[i]]
                        if adjy in range(len(maze)) and adjx in range(len(maze[0])) and maze[adjy][adjx] != '#':
                            b_coord_new.append((adjx, adjy))
                    if len(b_coord_new) == len(b_coord):
                        v += self.expectimax(maze, p_coord, b_coord_new, c_coord, step + 1, coins_collected)[0]
                        branches += 1

            return v / branches, None