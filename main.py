from copy import deepcopy
from Tree import TreeNode
from strats import euclidean_dist, manhattan_dist, chebyshev_dist
from visualise import HalmaBoardGUI
import time
import os

MAX, MIN = float('inf'),  float('-inf')
max_player_pawn, min_player_pawn, empty_square = 1, 2, 0
board_size = (16, 16)
max_goal, min_goal = (board_size[0] - 1, board_size[1] - 1), (0, 0)
max_winning_setup = [(15, 15), (15, 14), (15, 13), (15, 12), (15, 11),
                     (14, 15), (14, 14), (14, 13), (14, 12), (14, 11),
                     (13, 15), (13, 14), (13, 13), (13, 12),
                     (12, 15), (12, 14), (12, 13),
                     (11, 15), (11, 14)]
min_winning_setup = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
                     (1, 0), (1, 1), (1, 2), (1, 3), (1, 4),
                     (2, 0), (2, 1), (2, 2), (2, 3),
                     (3, 0), (3, 1), (3, 2),
                     (4, 0), (4, 1)]


def move_pawn(current_board_state, current_pos, next_pos, player):
    if not 0 <= current_pos[0] < board_size[0] or not 0 <= current_pos[1] < board_size[1] or not 0 <= next_pos[0] < board_size[0] or not 0 <= next_pos[1] < board_size[1]:
        return
    if current_board_state[next_pos[0]][next_pos[1]] != empty_square:
        return
    if current_board_state[current_pos[0]][current_pos[1]] != player:
        return
    new_board_state = deepcopy(current_board_state)
    new_board_state[current_pos[0]][current_pos[1]] = empty_square
    new_board_state[next_pos[0]][next_pos[1]] = player
    return new_board_state


def evaluate(board_state, eval_strat):
    evaluation = 0
    for i, row in enumerate(board_state):
        for j, sq in enumerate(row):
            if sq != empty_square:
                goal = max_goal if sq == max_player_pawn else min_goal
                multiplier = 1 if sq == max_player_pawn else -1
                if eval_strat == 1:
                  evaluation += multiplier * (euclidean_dist((i,j), goal))
                elif eval_strat == 2:
                    evaluation += multiplier * (manhattan_dist((i,j), goal))
                elif eval_strat == 3:
                    evaluation += multiplier * (chebyshev_dist((i,j), goal))
                else:
                    evaluation += 0
    return evaluation

def get_possible_moves(pawn, board_state):
    possible_moves = []
    for i, row in enumerate(board_state):
        for j, sq in enumerate(row):
            if sq == pawn:
                for ii in range(-1, 2):
                    for jj in range(-1, 2):
                        if 0 <= (i + ii) < board_size[0] and 0 <= (j + jj) < board_size[1] and board_state[i + ii][j + jj] == empty_square:
                            possible_moves.append(((i, j), (i + ii, j + jj)))
                        elif 0 <= (i + ii) < board_size[0] and 0 <= (j + jj) < board_size[1] and board_state[i + ii][j + jj] != empty_square:
                            possible_moves.extend(make_jumps((i, j), (i, j), (ii, jj), board_state, []))
    return possible_moves

def make_jumps(original_pos, start_pos, direction, board_state, result):
    landing_pos = (start_pos[0] + direction[0] * 2, start_pos[1] + direction[1] * 2)
    if \
            not 0 <= landing_pos[0] < board_size[0] \
            or not 0 <= landing_pos[1] < board_size[1] \
            or board_state[landing_pos[0]][landing_pos[1]] != empty_square \
            or board_state[start_pos[0] + direction[0]][start_pos[1] + direction[1]] == empty_square:
        return result

    result.append((original_pos, landing_pos))
    return make_jumps(original_pos, landing_pos, direction, board_state, result)

def next_player(player):
    if player == max_player_pawn:
        return min_player_pawn
    else:
        return max_player_pawn

def minimax(depth, maxDepth, player, node: TreeNode, alpha, beta, eval_strat, pruning):
    nodes_visited = 0
    if depth == maxDepth:
        evaluation = evaluate(node.game_state, eval_strat)
        node.value = evaluation
        return evaluation, nodes_visited
    if player == max_player_pawn:
        best = MIN
        for child in node.children:
            val, child_nodes_visited = minimax(depth + 1, maxDepth, min_player_pawn, child, alpha, beta, eval_strat, pruning)
            nodes_visited += child_nodes_visited + 1
            best = max(best, val)
            alpha = max(alpha, best)

            if pruning and beta <= alpha:
                break
        node.value = best
        return best, nodes_visited
    else:
        best = MAX
        for child in node.children:
            val, child_nodes_visited = minimax(depth + 1, maxDepth, max_player_pawn, child, alpha, beta, eval_strat, pruning)
            nodes_visited += child_nodes_visited + 1
            best = min(best, val)
            beta = min(beta, best)

            if pruning and beta <= alpha:
                break
        node.value = best
        return best, nodes_visited

def game_over(board_state):
    max_flag, min_flag = True, True
    for pos in max_winning_setup:
        if board_state[pos[0]][pos[1]] != 1:
            max_flag = False
            break
    for pos in min_winning_setup:
        if board_state[pos[0]][pos[1]] != 2:
            min_flag = False
            break
    if max_flag:
        print('1 WON')
        return True
    if min_flag:
        print('2 WON')
        return True
    return False

def play(initial_board_state, depth, max_strat, min_strat, pruning):

    current_board_state = initial_board_state
    current_pawn = max_player_pawn
    round_count = 0
    nodes_visited = 0
    start_time = time.time()
    while round_count < 300:
        if game_over(current_board_state):
            return round_count, nodes_visited, (time.time() - start_time)
        round_count += 1
        root_node = TreeNode(current_board_state, current_pawn, None)
        build_tree(root_node, depth)

        evaluation, round_nodes_visited = minimax(
            depth=0, maxDepth=depth, player=current_pawn,
            node=root_node, alpha=MIN, beta=MAX,
            eval_strat=max_strat if current_pawn == max_player_pawn else min_strat,
            pruning=pruning
        )

        nodes_visited += round_nodes_visited
        for child in root_node.children:
            if child.value == evaluation:
                current_board_state = deepcopy(child.game_state)
                break

        current_pawn = next_player(current_pawn)
        app.board_state = current_board_state
        app.draw_board()
        app.after(1)
    end_time = time.time()
    return round_count, nodes_visited, (end_time - start_time)

def build_tree(node, depth):
    if depth == 0:
        return
    player_to_move = next_player(node.player_to_move)
    moves = get_possible_moves(node.player_to_move, node.game_state)

    for move in moves:
        new_board_state = move_pawn(node.game_state, move[0], move[1], node.player_to_move)
        child_node = TreeNode(new_board_state, player_to_move, parent=node)
        node.add_child(child_node)
        build_tree(child_node, depth - 1)

if __name__ == '__main__':

    board = [
        [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2],
    ]
    # print(evaluate(board_2, 2))
    # app = HalmaBoardGUI(board)
    # rounds, nodes, duration = play(board, depth=3, max_strat=2, min_strat=1, pruning=True)
    # print(rounds, nodes, duration)
    # app.mainloop()

    path = 'C:/Users/pesta/studia/sem_6/AI/lab2/positions'
    # filename = os.listdir(path)[1]
    # with open(os.path.join(path, filename), 'r') as file:
    #     lines = file.readlines()
    #     matrix = [[0]*16 for _ in range(16)]
    #     for i in range(16):
    #         numbers = map(int, lines[i].strip().split())
    #         matrix[i] = list(numbers)
    #     board = deepcopy(matrix)
    #     rounds, nodes, duration = play(board, depth=2, max_strat=1, min_strat=2, pruning=True)
    #     print(f'depth: 2, max_strat: 1, min_strat: 2, pruning: true, metrix: {rounds}, {nodes}, {duration}')
    #     print()
    app = HalmaBoardGUI(board)
    play(board, depth=2, max_strat=3, min_strat=2, pruning=True)
    # for filename in os.listdir(path):
    #     with open(os.path.join(path, filename), 'r') as file:
    #         lines = file.readlines()
    #         matrix = [[0]*16 for _ in range(16)]
    #         for i in range(16):
    #             numbers = map(int, lines[i].strip().split())
    #             matrix[i] = list(numbers)
    #         board = deepcopy(matrix)
    #
    #         rounds, nodes, duration = play(board, depth=2, max_strat=1, min_strat=2, pruning=True)
    #         print(f'depth: 2, max_strat: 1, min_strat: 2, pruning: true, metrix: {rounds}, {nodes}, {duration}')
    #         print()
    #
    # print('NO PRUNING')
    # for filename in os.listdir(path):
    #     with open(os.path.join(path, filename), 'r') as file:
    #         lines = file.readlines()
    #         matrix = [[0]*16 for _ in range(16)]
    #         for i in range(16):
    #             numbers = map(int, lines[i].strip().split())
    #             matrix[i] = list(numbers)
    #         board = deepcopy(matrix)
    #
    #         rounds, nodes, duration = play(board, depth=2, max_strat=1, min_strat=2, pruning=False)
    #         print(f'depth: 2, max_strat: 1, min_strat: 2, pruning: false, metrix: {rounds}, {nodes}, {duration}')
    #         print()
    #
    # print('STRAT 3 PRUNING')
    # print()
    # for filename in os.listdir(path):
    #     with open(os.path.join(path, filename), 'r') as file:
    #         lines = file.readlines()
    #         matrix = [[0]*16 for _ in range(16)]
    #         for i in range(16):
    #             numbers = map(int, lines[i].strip().split())
    #             matrix[i] = list(numbers)
    #         board = deepcopy(matrix)
    #
    #         rounds, nodes, duration = play(board, depth=2, max_strat=1, min_strat=3, pruning=True)
    #         print(f'depth: 2, max_strat: 1, min_strat: 3, pruning: true, metrix: {rounds}, {nodes}, {duration}')
    #         print()
    #
    # print('NO PRUNING')
    # for filename in os.listdir(path):
    #     with open(os.path.join(path, filename), 'r') as file:
    #         lines = file.readlines()
    #         matrix = [[0]*16 for _ in range(16)]
    #         for i in range(16):
    #             numbers = map(int, lines[i].strip().split())
    #             matrix[i] = list(numbers)
    #         board = deepcopy(matrix)
    #
    #         rounds, nodes, duration = play(board, depth=2, max_strat=1, min_strat=3, pruning=False)
    #         print(f'depth: 2, max_strat: 1, min_strat: 3, pruning: false, metrix: {rounds}, {nodes}, {duration}')
    #         print()

    app.mainloop()




