import pygame
import copy
import random
import math
import time
import random
from collections import namedtuple

pygame.init()
font = "fonts/DragonHunter-9Ynxj.otf"
inf = math.inf
GameState = namedtuple('GameState', 'to_move, utility, board, moves') # state var during the whole code will include tuples: to_move(X or O); ultility; board; moves(x, y)
screen = pygame.display.set_mode((1000, 750))
pygame.display.set_caption('Tic-Tac-Toe')
icon = pygame.image.load('sprites/icon.png')
pygame.display.set_icon(icon)
pygame.display.update
run = True

# _______________________________________________________________
# MINIMAX
def minmax_search(state, game):
    player = game.to_move(state)

    def max_value(state):
        if game.terminal_test(state):
            return game.utility(state, player)
        v = -inf
        for a in game.actions(state):
            v = max(v, min_value(game.result(state, a)))
        return v

    def min_value(state):
        if game.terminal_test(state):
            return game.utility(state, player)
        v = inf
        for a in game.actions(state):
            v = min(v, max_value(game.result(state, a)))
        return v

    return max(game.actions(state), key=lambda a: min_value(game.result(state, a)))

# _______________________________________________________________
# Alpha-Beta Prunning with Depth-Limited 
# Depth search is limited to 3 in order to avoid too slow searching for best_action
def alpha_beta_cutoff_search(state, game, d=3, cutoff_test=None, eval_fn=None): 
    player = game.to_move(state)

    # Functions used by alpha_beta
    def max_value(state, alpha, beta, depth):
        if cutoff_test(state, depth):
            return eval_fn(state, game)
        v = -inf
        for a in game.actions(state):
            v = max(v, min_value(game.result(state, a), alpha, beta, depth + 1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(state, alpha, beta, depth):
        if cutoff_test(state, depth):
            return eval_fn(state, game)
        v = inf
        for a in game.actions(state):
            v = min(v, max_value(game.result(state, a), alpha, beta, depth + 1))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    cutoff_test = (cutoff_test or (lambda state, depth: depth > d or game.terminal_test(state)))
    eval_fn = eval_fn or (lambda state: game.utility(state, player))
    best_score = -inf
    beta = inf
    best_action = None

    # Randomize the choice of action
    #suffle_actions = game.actions(state)
    #random.shuffle(suffle_actions)

    for a in game.actions(state):
        if player == 'O':
            v = min_value(game.result(state, a), best_score, beta, 1)
        else:
            v = max_value(game.result(state, a), best_score, beta, 1)
        if player == 'O':
            v = -v
            if v > best_score:
                best_score = v
                best_action = a
        else:
            if v > best_score:
                best_score = v
                best_action = a
    return best_action


def evaluate(state, game):
    board = state.board
    player = state.to_move
    size = game.k

    player = 'X'
    enemy = 'O'

    # Calculate the current value of board after taking the action
    def calc(li, eval):
        s = game.k
        while s:
            # Evaluate the value of board at each different state(action)
            # Player 'X' for max value, player 'O' for min value
            if li.count(player) == s:
                eval += (10**(s))
            elif li.count(enemy) == s:
                eval -= (10**(s))
            s-=1
        return eval
    eval = 0
    # Row
    for i in range(size):
        li = []
        for j in range(size):
            li.append(board.get((i+1, j+1), '.'))
        eval = calc(li, eval)
    # Column
    for j in range(size):
        li = []
        for i in range(size):
            li.append(board.get((i+1, j+1), '.'))
        eval = calc(li, eval)

    li = []
    # Diagonal (top left to bottom right)
    for i in range(size):
        li.append(board.get((i+1, i+1), '.'))
    eval = calc(li, eval)

    li = []
    # Diagonal (bottom left to top right)
    for i in range(size):
        for j in range(size):
            if i+j+2 == size+1:
                li.append(board.get((i+1, j+1), '.'))
    eval = calc(li, eval)

    return eval

# ______________________________________________________________________________
# Players

def minimax_player(game, state):
    return minmax_search(state, game)

def alpha_beta_dl_player(game, state):
    return alpha_beta_cutoff_search(state, game, eval_fn=evaluate)

# ______________________________________________________________________________
# Some Sample Games

class Game:
    def actions(self, state):
        raise NotImplementedError

    def result(self, state, move):
        raise NotImplementedError

    def utility(self, state, player):
        raise NotImplementedError

    def terminal_test(self, state):
        return not self.actions(state)

    def to_move(self, state):
        return state.to_move

    def display(self, state):
        print(state)

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

    def play_game(self, *players):
        # Initialize the state of the game that includes the GameTuple: {to_move, utility, board, moves}
        state = self.initial
        run = True
        game_completed = False
            # for event in pygame.event.get():
            #         if event.type == pygame.QUIT:
            #             run = False
        while run:            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    return self.utility(state, self.to_move(self.initial))
                if event.type == pygame.MOUSEBUTTONUP:
                    pass
            #pygame.display.update()
            # Check if the game is completed(all the cells are filled with 'X' and 'O')
            if not game_completed:
                for player in players:
                    time.sleep(0.1)
                #run2 = True

                    move = player(self, state) # The current player's turn, this will call the function alpha_beta_dl_player(game, state) above to calculate and return the best move for this current player
                    i = move[0]-1
                    j = move[1]-1
                    coord = ((j*res + (1/6)*res), (i*res + (1/6)*res))
                    if state.to_move == 'X':
                        screen.blit(cross,coord)
                    else:
                        screen.blit(circle,coord)
                    state = self.result(state, move)
                    self.display(state)
                    print('\n')
                    pygame.display.update()
                    if self.terminal_test(state):
                        game_completed = True
                        time.sleep(3)
                        break

            pygame.display.update()


# Subclass that Inherits from Game class
class TicTac(Game):
    def __init__(self, h=3, v=3, k=3):
        self.h = h
        self.v = v
        self.k = k
        moves = [(x, y) for x in range(1, h + 1)
                 for y in range(1, v + 1)]
        self.initial = GameState(to_move='X', utility=0, board={}, moves=moves)

    def actions(self, state):
        return state.moves

    def result(self, state, move):
        if move not in state.moves:
            return state  # Illegal move has no effect
        # Copy the main board into another board, so it will not affect directly to the main board after each prediction of search algorithms
        board = state.board.copy()
        board[move] = state.to_move
        moves = list(state.moves)
        moves.remove(move)
        return GameState(to_move=('O' if state.to_move == 'X' else 'X'),
                         utility=self.compute_utility(board, move, state.to_move),
                         board=board, moves=moves)

    def utility(self, state, player):
        return state.utility if player == 'X' else -state.utility

    def terminal_test(self, state):
        return state.utility != 0 or len(state.moves) == 0

    def display(self, state):
        board = state.board
        for x in range(1, self.h + 1):
            for y in range(1, self.v + 1):
                print(board.get((x, y), '.'), end=' ')
            print()

    def compute_utility(self, board, move, player):
        if (self.k_in_row(board, move, player, (0, 1)) or
                self.k_in_row(board, move, player, (1, 0)) or
                self.k_in_row(board, move, player, (1, -1)) or
                self.k_in_row(board, move, player, (1, 1))):
            return +1 if player == 'X' else -1
        else:
            return 0

    def k_in_row(self, board, move, player, delta_x_y):
        (delta_x, delta_y) = delta_x_y
        x, y = move
        n = 0  # n is number of moves in row
        while board.get((x, y)) == player:
            n += 1
            x, y = x + delta_x, y + delta_y
        x, y = move
        while board.get((x, y)) == player:
            n += 1
            x, y = x - delta_x, y - delta_y
        n -= 1  # Because we counted move itself twice
        return n >= self.k

# Format the text
def text_format(message, textFont, textSize, textColor):
    newFont=pygame.font.Font(textFont, textSize)
    newText=newFont.render(message, 0, textColor)
    return newText


# Let's draw and blit the game !!!
player1 = None
player2 = None
click = False
menu = True

# Choose the algorithm for AI players (Here we choose the depth-limited al-beta prunning for both)
player1= alpha_beta_dl_player
player2= alpha_beta_dl_player

grid_size = None
menu = True
while menu:
    screen.fill((0,0,0))
    icon = pygame.transform.scale(icon,(96,96))
    # screen.blit(icon, (50,15))
    title=text_format(" Game Size", font, 90, (255,255,255)) 
    screen.blit(title, (150, 15))
    mx, my = pygame.mouse.get_pos()
 
    button_1 = pygame.Rect(50, 125, 600, 50)
    user=text_format(" 3X3", font, 50, (255,255,255)) 

    button_2 = pygame.Rect(50, 200, 600, 50)
    mm=text_format(" 4X4 (Use only for DepthLimited)", font, 50, (255,255,255)) 

    button_3 = pygame.Rect(50, 275, 600, 50)
    dlmm=text_format(" 5X5 (Use only for DepthLimited)", font, 50, (255,255,255)) 
    
    button_4 = pygame.Rect(50, 350, 600, 50)
    ab=text_format(" 6X6 (Use only for DepthLimited)", font, 50, (255,255,255))

    button_5 = pygame.Rect(50, 425, 600, 50)
    dlab=text_format(" 7X7 (Use only for DepthLimited)", font, 50, (255,255,255))
    
    button_6 = pygame.Rect(50, 500, 600, 50)
    ran=text_format(" 10X10 (Use only for DepthLimited)", font, 50, (255,255,255))

    if button_1.collidepoint((mx, my)):
        if click:
            grid_size = 3
            menu = False
    if button_2.collidepoint((mx, my)):
        if click:
            grid_size = 4
            menu = False
    if button_3.collidepoint((mx, my)):
        if click:
            grid_size = 5
            menu = False
    if button_4.collidepoint((mx,my)):
        if click:
            grid_size = 6
            menu = False
    if button_5.collidepoint((mx,my)):
        if click:
            grid_size= 7
            menu = False
    if button_6.collidepoint((mx,my)):
        if click:
            grid_size = 10
            menu = False
    
    pygame.draw.rect(screen, (0, 97, 230), button_1)
    screen.blit(user, (60, 125))

    pygame.draw.rect(screen, (73, 97, 230), button_2)
    screen.blit(mm, (60, 200))
    
    pygame.draw.rect(screen, (73, 97, 230), button_3)
    screen.blit(dlmm, (60, 275))

    pygame.draw.rect(screen, (73, 97, 230), button_4)
    screen.blit(ab, (60, 350))

    pygame.draw.rect(screen, (73, 97, 230), button_5)
    screen.blit(dlab, (60, 425))

    pygame.draw.rect(screen, (73, 97, 230), button_6)
    screen.blit(ran, (60, 500))

    click = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            menu = False
            pygame.quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                click = True
 
        pygame.display.update()

res = 96
if grid_size >= 8:
    res = 72
a = grid_size
menu = True

screen = pygame.display.set_mode((a*res, a*res))
pygame.display.set_caption('Tic-Tac-Toe')
square = pygame.image.load('sprites/square.png')
square = pygame.transform.scale(square,(res,res))
cross = pygame.image.load('sprites/x.png')
cross = pygame.transform.scale(cross,(int((2/3)*res),int((2/3)*res)))
circle = pygame.image.load('sprites/o.png')
circle = pygame.transform.scale(circle,(int((2/3)*res),int((2/3)*res)))
for i in range(grid_size):
        for j in range(grid_size):
            screen.blit(square,(i*res,j*res))
pygame.display.update()

# Win when the first has 5 respectively
TicTac(grid_size,grid_size,5).play_game(player1, player2)
