import pygame
from game import Game
import numpy as np
import pdb

pygame.init()

RADIUS = 20
POINT_RAD = 2
STONE_RAD = RADIUS
DISP_IN_TERMINAL = False
BOARD_COLOR = (244, 209, 128) # My color for a board
env = Game(shape=(9, 9))
WINDOW_SHAPE = (env.actual_shape[1] * 2 * RADIUS, env.actual_shape[0] * 2 * RADIUS)

black_img = pygame.image.load('theme/black1.png')
black_img = pygame.transform.scale(black_img, (2 * STONE_RAD, 2 * STONE_RAD))
white_img = pygame.image.load('theme/white1.png')
white_img = pygame.transform.scale(white_img, (2 * STONE_RAD, 2 * STONE_RAD))
gameDisplay = pygame.display.set_mode(WINDOW_SHAPE)
# gameDisplay.fill((244, 209, 128)) 
pygame.display.set_caption('NewGo')

# translate board coordinate to game coordinate
def btog(x, y):
    xx = y * 2 * RADIUS + RADIUS# Because the coordinate system are not exactly the same
    yy = x * 2 * RADIUS + RADIUS
    return xx, yy

# translate game coordinate to board coordinate
def gtob(x, y):
    xx = round((y - RADIUS) / (2 * RADIUS)) 
    yy = round((x - RADIUS) / (2 * RADIUS))
    return xx, yy

# draw lines on the board
def draw_lines(gameDisplay, env: Game, thickness = 2):
    # draw horizontal lines:
    for i in range(env.actual_shape[0]):
        # left and right end points
        if i % 2 == 1:
            continue
        start = btog(i, 0)
        end = btog(i, env.actual_shape[1] - 1)
        pygame.draw.line(gameDisplay, (0, 0, 0), start, end, width=thickness)

    # draw vertical lines:
    for i in range(env.actual_shape[1]):
        # left and right end points
        if i % 2 == 1:
            continue
        start = btog(0, i)
        end = btog(env.actual_shape[0] - 1, i)
        pygame.draw.line(gameDisplay, (0, 0, 0), start, end, width=thickness)

    # draw inclined lines
    for i in range(0, env.actual_shape[0] - 2, 2):
        for j in range(0, env.actual_shape[1] - 2, 2):
            
            upper_left = btog(i, j)
            bottom_right = btog(i+2, j+2)

            upper_right = btog(i, j+2)
            bottom_left = btog(i+2, j)
            pygame.draw.line(gameDisplay, (0, 0, 0), upper_left, bottom_right, width=thickness)
            pygame.draw.line(gameDisplay, (0, 0, 0), upper_right, bottom_left, width=thickness)

# draw a stone image
def draw_stone(gameDisplay, x, y, img):
    xx, yy = btog(x, y)
    gameDisplay.blit(img, (xx - RADIUS, yy - RADIUS))

# draw board based on the env
def draw_board(gameDisplay, env: Game, point_radius, stone_radius):
    gameDisplay.fill(BOARD_COLOR)
    draw_lines(gameDisplay, env)
    board = env.current_board
    for i in range(len(board)):
        for j in range(len(board[i])):
            match board[i][j]:
                case 0:
                    continue
                case 1:
                    if env.actual_shape[0] == 1 or env.actual_shape[1] == 1:
                        pygame.draw.circle(gameDisplay, (0, 0, 0), btog(i, j), radius=point_radius)
                case env.black:
                    draw_stone(gameDisplay, i, j, black_img)
                    # pygame.draw.circle(gameDisplay, (0, 0, 0), btog(i, j), radius=stone_radius)
                case env.white:
                    draw_stone(gameDisplay, i, j, white_img)
                    # pygame.draw.circle(gameDisplay, (255, 255, 255), btog(i, j), radius=stone_radius)

# draw points that help debug, pts are board coordinates!!!
def draw_points(gameDisplay, pts, color = (0, 255, 0), radius = 10):
    for x, y in pts:
        pygame.draw.circle(gameDisplay, color, btog(x, y), radius= radius)

# 
def draw_count(gameDisplay, board_count):
    black_count = 0
    white_count = 0
    for i in range(len(board_count)):
        for j in range(len(board_count[i])):
            if board_count[i][j] == 0:
                continue
            elif board_count[i][j] == env.black:
                draw_points(gameDisplay, [[i, j]], color = (0, 0, 0))
                black_count += 1
            elif board_count[i][j] == env.white:
                draw_points(gameDisplay, [[i, j]], color = (255, 255, 255))
                white_count += 1
            elif board_count[i][j] == 4: 
                draw_points(gameDisplay, [[i, j]], color = [128, 128, 128])
                black_count += 1/2
                white_count += 1/2
            else:
                draw_points(gameDisplay, [[i, j]], color = [255, 0, 0])
    return black_count, white_count

crashed = False
count_requested = False
est_requested = False
last_move = None
board_count = None
est_count = None

while not crashed:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = True
        
        if event.type == pygame.MOUSEBUTTONUP:
            x, y = pygame.mouse.get_pos()
            xx, yy = gtob(x, y) 
            if env.step(xx, yy) == 0:
                last_move = (xx, yy)
                board_count = env.count()
                est_count = env.est()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_p:
                env.pass_move()
                if env.game_end:
                    print('game has ended')
                else:
                    print('passed, now it\'s {}\'s turn'.format(env.get_str_turn()))

            
            elif event.key == pygame.K_c:
                if count_requested == False:
                    count_requested = True
                    board_count = env.count()
                    black_count, white_count = draw_count(gameDisplay, board_count)
                    print('count requested, black count: {}, white count: {}'.format(black_count, white_count))
                    est_requested = False
                else:
                    count_requested = False
            
            elif event.key == pygame.K_e:
                if est_requested == False:
                    est_requested = True
                    est_count = env.est()
                    black_count, white_count = draw_count(gameDisplay, est_count)
                    print('estimation requested, black count: {}, white count: {}'.format(black_count, white_count))
                    count_requested = False
                else:
                    est_requested = False
            
            elif event.key == pygame.K_u:
                if env.undo() == 0:
                    print('undo proceeded, now it is {}\'s turn'.format(env.get_str_turn()))
                    board_count = env.count()
                    est_count = env.est()
                    last_move = None 

    draw_board(gameDisplay, env, POINT_RAD, STONE_RAD)
    if last_move is not None:
        draw_points(gameDisplay, [last_move])

    if count_requested:
        draw_count(gameDisplay, board_count)

    if est_requested:
        draw_count(gameDisplay, est_count)

    pygame.display.update()

pygame.quit()