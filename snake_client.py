# Filip Maletic (250866829)
# CS 3357A Assignment 3: Server-driven snake game.
# November 9, 2023

import socket
import sys
import pygame
import time

# Server
PORT = 5555
SERVER_IP = "localhost"
ADDR = (SERVER_IP, PORT)
# Game dimensions
WIDTH = 500
HEIGHT = 500
SQUARE_SIZE = 25
# Colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

pygame.init()   # Initializes pygame

# Creates a client socket and connects it to the game server.
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((ADDR))
clientSocket.settimeout(0.1)  # Sets a timeout of 0.1 seconds

# Initializes game window with default dimensions.
gameWindow = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")

# Sends get to the server so the server can send back the starting game state to the receiving client.
clientSocket.send("get".encode())

# Initializes time of latest key press.
latest_key_press = 0    

# Main loop that handles all possible user inputs and updates game window with the current game state.
while True:
    currTime = time.time()
    for event in pygame.event.get():
        # Closes the game window if quit is inputted.
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    timePassed = currTime - latest_key_press    # Time passed since the previous key press

    # Handles all possible user key presses and sends the corresponding command back to the server.
    if timePassed >= 0.1:      # Checks if a minimum of 0.1 seconds have passed since the last key press input. Creates a delay so the server doesn't get overwhelmed.
        keys = pygame.key.get_pressed()
        # up key input
        if keys[pygame.K_UP]:
            clientSocket.send("up".encode())
        # down key input
        elif keys[pygame.K_DOWN]:
            clientSocket.send("down".encode())
        # left key input
        elif keys[pygame.K_LEFT]:
            clientSocket.send("left".encode())
        # right key input
        elif keys[pygame.K_RIGHT]:
            clientSocket.send("right".encode())
        # reset key input
        elif keys[pygame.K_r]:
            clientSocket.send("reset".encode())
        # quit key input
        elif keys[pygame.K_q]:
            clientSocket.send("quit".encode())
        # Defaults to get command if no key is being pressed, so the snake is always displayed as moving to the player.
        else:
            clientSocket.send("get".encode())
        latest_key_press = currTime
    # Tries to receive game state from server.
    try:
        gameState = clientSocket.recv(1024).decode()
    # Excepts socket timeout if no data is recieved within the timeout (so the game can continue without crashing)
    except socket.timeout:
        pass  # Keeps the loop going and the game running

    # Initiliazes snake and snack coordinate lists that will store the square positions for each game state.
    snake_coordinates = []
    snack_coordinates = []
    # Splits the game state string into the snake and snack string parts
    snake_string, snack_string = gameState.split("|")

    # Parses snake coordinates and adds them to the corresponding list
    snake_squares = snake_string.split("*")
    for square in snake_squares:
        coordinate = tuple(map(int, square.strip("()").split(",")))
        snake_coordinates.append(coordinate)

    # Parses snack coordinates and adds them to the corresponding list
    snack_squares = snack_string.split("**")
    for square in snack_squares:
        coordinate = tuple(map(int, square.strip("()").split(",")))
        snack_coordinates.append(coordinate)

    # Resets the game window to a black screen so the new game state can be drawn.
    gameWindow.fill(BLACK)

    # Draws the snake positions for the current game state.
    for coordinate in snake_coordinates:
        pygame.draw.rect(gameWindow, RED, (coordinate[0] * SQUARE_SIZE, coordinate[1] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    # Drawing the eyes on the head of the snake.
    leftEye = (snake_coordinates[0][0] * SQUARE_SIZE + 6, snake_coordinates[0][1] * SQUARE_SIZE + 5)
    rightEye = (snake_coordinates[0][0] * SQUARE_SIZE + 16, snake_coordinates[0][1] * SQUARE_SIZE + 5)
    pygame.draw.rect(gameWindow, BLACK, (leftEye[0], leftEye[1], 5, 5))
    pygame.draw.rect(gameWindow, BLACK, (rightEye[0], rightEye[1], 5, 5))

    # Draws the snack positions for the current game state.
    for coordinate in snack_coordinates:
        pygame.draw.rect(gameWindow, GREEN, (coordinate[0] * SQUARE_SIZE, coordinate[1] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    # Draws white grid lines.
    for x in range(0, WIDTH, SQUARE_SIZE):
        pygame.draw.line(gameWindow, WHITE, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, SQUARE_SIZE):
        pygame.draw.line(gameWindow, WHITE, (0, y), (WIDTH, y))

    pygame.display.update()  # Updates the game window with the current game state.
    