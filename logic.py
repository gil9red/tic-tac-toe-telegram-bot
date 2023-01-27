#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import random
from math import inf


HUMAN = -1
COMP = 1
EMPTY = 0


def get_empty_board() -> list[list[int]]:
    return [
        [EMPTY, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY],
    ]


def empty_cells(state: list[list[int]]) -> list[tuple[int, int]]:
    """
    Each empty cell will be added into cells' list
    :param state: the state of the current board
    :return: a list of empty cells
    """
    cells = []

    for x, row in enumerate(state):
        for y, cell in enumerate(row):
            if cell == EMPTY:
                cells.append((x, y))

    return cells


def wins(state: list[list[int]], player: int) -> bool:
    """
    This function tests if a specific player wins. Possibilities:
    * Three rows    [X X X] or [O O O]
    * Three cols    [X X X] or [O O O]
    * Two diagonals [X X X] or [O O O]
    :param state: the state of the current board
    :param player: a human or a computer
    :return: True if the player wins
    """
    win_state = [
        [state[0][0], state[0][1], state[0][2]],
        [state[1][0], state[1][1], state[1][2]],
        [state[2][0], state[2][1], state[2][2]],
        [state[0][0], state[1][0], state[2][0]],
        [state[0][1], state[1][1], state[2][1]],
        [state[0][2], state[1][2], state[2][2]],
        [state[0][0], state[1][1], state[2][2]],
        [state[2][0], state[1][1], state[0][2]],
    ]
    return [player, player, player] in win_state


def game_over(state: list[list[int]]) -> bool:
    """
    This function test if the human or computer wins
    :param state: the state of the current board
    :return: True if the human or computer wins
    """
    return wins(state, HUMAN) or wins(state, COMP)


def evaluate(state: list[list[int]]) -> int:
    """
    Function to heuristic evaluation of state.
    :param state: the state of the current board
    :return: +1 if the computer wins; -1 if the human wins; 0 draw
    """
    if wins(state, COMP):
        score = 1
    elif wins(state, HUMAN):
        score = -1
    else:
        score = 0

    return score


def minimax(state: list[list[int]], depth: int, player: int) -> list[int, int, int]:
    """
    AI function that choice the best move
    :param state: current state of the board
    :param depth: node index in the tree (0 <= depth <= 9),
    but never nine in this case (see ai_turn() function)
    :param player: a human or a computer
    :return: a list with [the best row, the best col, best score]
    """
    if player == COMP:
        best = [-1, -1, -inf]
    else:
        best = [-1, -1, +inf]

    if depth == 0 or game_over(state):
        score = evaluate(state)
        return [-1, -1, score]

    for cell in empty_cells(state):
        x, y = cell
        state[x][y] = player
        score = minimax(state, depth - 1, -player)
        state[x][y] = 0
        score[0], score[1] = x, y

        if player == COMP:
            if score[2] > best[2]:
                best = score  # max value
        else:
            if score[2] < best[2]:
                best = score  # min value

    return best


def ai_choice(board: list[list[int]]) -> tuple[int, int]:
    depth = len(empty_cells(board))
    if depth == 0 or game_over(board):
        return -1, -1

    if depth == 9:
        x = random.choice([0, 1, 2])
        y = random.choice([0, 1, 2])
    else:
        x, y, _ = minimax(board, depth, COMP)

    return x, y


if __name__ == '__main__':
    board = get_empty_board()
    while not game_over(board):
        x, y = ai_choice(board)
        print(f'AI choice: {x}x{y}')

        board[x][y] = COMP

    print('\n'.join(
        ' | '.join('X' if cell == COMP else 'O' for cell in row)
        for row in board
    ))
