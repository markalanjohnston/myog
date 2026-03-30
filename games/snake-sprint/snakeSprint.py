# ============================================================
#   ____              _        ____             _       _   
#  / ___| _ __   __ _| | _____/ ___| _ __  _ __(_)_ __ | |_ 
#  \___ \| '_ \ / _` | |/ / _ \___ \| '_ \| '__| | '_ \| __|
#   ___) | | | | (_| |   <  __/___) | |_) | |  | | | | | |_ 
#  |____/|_| |_|\__,_|_|\_\___|____/| .__/|_|  |_|_| |_|\__|
#                                   |_|                    
#
#                      Snake Sprint Game
# ============================================================
#
# Author: Mark Johnston (see disclaimer at end)
# Version: 1.0 (03/26/2026)
#
# ------------------------------------------------------------
# Description:
# A real-time snake game built with CMU Graphics where players
# control a growing snake to collect food while avoiding walls
# and self-collision. Special poison items introduce a temporary
# reversed-control mechanic, increased difficulty, and visual
# feedback to challenge player adaptability.
#
# ------------------------------------------------------------
# Instructions:
# 1. Press SPACE to start the game.
#
# 2. Use Arrow Keys or WASD to control the snake:
#       Up / W    = Move Up
#       Down / S  = Move Down
#       Left / A  = Move Left
#       Right / D = Move Right
#
# 3. Eat normal food to:
#       - Grow the snake
#       - Increase your score (+10)
#       - Clear poison effects if active
#
# 4. Avoid poison bugs:
#       - Reduces score (-5, minimum 0)
#       - Activates "poisoned" state:
#           • Controls are reversed
#           • Snake moves more slowly
#           • Snake flashes red
#       - Effect lasts until normal food is eaten
#
# 5. Game Over occurs if:
#       - The snake hits a wall
#       - The snake collides with itself
#
# 6. Press 'R' to reset the game at any time.
#
# ------------------------------------------------------------
# License:
# Creative Commons Attribution 4.0 International (CC BY 4.0)
#
# This work is licensed under the Creative Commons Attribution 4.0
# International License.
#
# You are free to:
# - Share: copy and redistribute the material in any medium or format
# - Adapt: remix, transform, and build upon the material for any purpose
#
# Under the following terms:
# - Attribution: You must give appropriate credit to the original author
#   (Mark Johnston), provide a link to the license, and indicate if
#   changes were made.
#
# This license does not impose restrictions on commercial use but
# requires visible attribution in any derivative work or redistribution.
#
# Full license text:
# https://creativecommons.org/licenses/by/4.0/
# ------------------------------------------------------------
#
# Disclaimer/Attribution:
#
# This project was developed through a collaborative process between the
# author and an AI assistant. The human contributor provided the core
# design, requirements, and iterative refinements, including detailed
# prompts, testing, and error correction. The AI was used as a productivity
# tool to accelerate implementation, generate code drafts, and assist with
# refactoring and optimization.
#
# The author possesses the technical knowledge and ability to build this
# application independently. However, AI assistance was intentionally
# leveraged to reduce development time, streamline repetitive tasks, and
# support rapid iteration. All final decisions, adjustments, and
# validations were made by the human author.
#
# This work reflects a guided, human-directed development process in which
# AI functioned as an assistive tool rather than an autonomous creator.
# ============================================================

from cmu_graphics import *

app.background = gradient('darkOliveGreen', 'black', start='top')
app.stepsPerSecond = 12

# -----------------------------
# Board / game settings
# -----------------------------
app.cellSize = 20
app.leftBoard = 20
app.topBoard = 40
app.widthBoard = 360
app.heightBoard = 340
app.cols = app.widthBoard // app.cellSize
app.rows = app.heightBoard // app.cellSize

app.normalSpeed = 7
app.poisonSpeed = 3

# -----------------------------
# Game state
# -----------------------------
app.started = False
app.gameOver = False
app.score = 0

app.direction = 'right'
app.nextDirection = 'right'
app.snake = [[8, 8], [7, 8], [6, 8]]

app.food = None
app.poison = None
app.poisoned = False

# -----------------------------
# UI
# -----------------------------
Label('Snake Sprint', 200, 10, size=18, bold=True, fill='white')
scoreLabel = Label('Score: 0', 70, 390, size=16, fill='white')
statusLabel = Label('Press space to start', 210, 390, size=16, fill='white')
Label('Arrows/WASD to move | R reset', 200, 25, size=10, fill='lightGray')

Rect(app.leftBoard, app.topBoard, app.widthBoard, app.heightBoard,
     fill=gradient('darkSeaGreen', 'forestGreen', start='top'),
     border='white', borderWidth=2)

for x in range(app.leftBoard, app.leftBoard + app.widthBoard + 1, app.cellSize):
    Line(x, app.topBoard, x, app.topBoard + app.heightBoard, fill='white', opacity=10)
for y in range(app.topBoard, app.topBoard + app.heightBoard + 1, app.cellSize):
    Line(app.leftBoard, y, app.leftBoard + app.widthBoard, y, fill='white', opacity=10)

snakeGroup = Group()
foodGroup = Group()
poisonGroup = Group()

overlay = Rect(55, 135, 290, 110, fill='black', opacity=70, visible=False,
               border='white', borderWidth=2)
overlayTitle = Label('', 200, 170, size=22, bold=True, fill='white', visible=False)
overlayText = Label('', 200, 205, size=14, fill='white', visible=False)

# -----------------------------
# Helpers
# -----------------------------
def showOverlay(title, text):
    overlay.visible = True
    overlayTitle.visible = True
    overlayText.visible = True
    overlayTitle.value = title
    overlayText.value = text

def hideOverlay():
    overlay.visible = False
    overlayTitle.visible = False
    overlayText.visible = False

def cellToPixel(col, row):
    return (
        app.leftBoard + col * app.cellSize + app.cellSize / 2,
        app.topBoard + row * app.cellSize + app.cellSize / 2
    )

def inSnake(col, row):
    for part in app.snake:
        if part[0] == col and part[1] == row:
            return True
    return False

def sameCell(a, b):
    return a != None and b != None and a[0] == b[0] and a[1] == b[1]

def onBoard(col, row):
    return 0 <= col < app.cols and 0 <= row < app.rows

def updateLabels():
    scoreLabel.value = 'Score: ' + str(app.score)

    if app.gameOver:
        statusLabel.value = 'Game over'
    elif app.poisoned:
        statusLabel.value = 'Poisoned! Reverse controls'
    elif app.started:
        statusLabel.value = 'Eat the food'
    else:
        statusLabel.value = 'Press space to start'

def drawFood(x, y, poison=False):
    if poison == False:
        return Group(
            Oval(x, y, 8, 25, fill='green'),
            Oval(x - 5, y, 10, 20, fill='green', rotateAngle=30),
            Oval(x + 5, y, 10, 20, fill='green', rotateAngle=-30),
            Circle(x, y - 10, 5, fill='red')
        )
    else:
        return Group(
            Oval(x, y + 5, 18, 22, fill='maroon', border='black'),
            Circle(x, y - 10, 7, fill='darkRed', border='black'),
            Line(x - 12, y + 2, x - 4, y + 8, fill='black'),
            Line(x + 12, y + 2, x + 4, y + 8, fill='black'),
            Line(x - 12, y + 12, x - 4, y + 8, fill='black'),
            Line(x + 12, y + 12, x + 4, y + 8, fill='black'),
            Circle(x - 3, y - 12, 1.5, fill='white'),
            Circle(x + 3, y - 12, 1.5, fill='white')
        )

def drawSnake():
    snakeGroup.clear()

    flashingRed = app.poisoned and app.steps % 6 < 3

    for i in range(len(app.snake) - 1, -1, -1):
        col, row = app.snake[i]
        x, y = cellToPixel(col, row)

        if i == 0:
            headColor = 'darkRed' if flashingRed else 'darkGreen'
            tongueColor = 'orangeRed' if flashingRed else 'red'
            head = Circle(x, y, 10, fill=headColor, border='black')
            eye1 = Circle(x + 3, y - 3, 1.8, fill='white')
            eye2 = Circle(x + 3, y + 3, 1.8, fill='white')
            tongue = Polygon(x + 10, y, x + 16, y - 2, x + 16, y + 2, fill=tongueColor)
            snakeGroup.add(Group(head, eye1, eye2, tongue))
        else:
            if flashingRed:
                bodyColor = 'red' if i % 2 == 0 else 'tomato'
                borderColor = 'darkRed'
            else:
                bodyColor = 'limeGreen' if i % 2 == 0 else 'green'
                borderColor = 'darkGreen'
            snakeGroup.add(Circle(x, y, 9, fill=bodyColor, border=borderColor))

def placeItem(blockedCell=None):
    while True:
        col = randrange(0, app.cols)
        row = randrange(0, app.rows)
        if not inSnake(col, row):
            if blockedCell == None or blockedCell[0] != col or blockedCell[1] != row:
                return [col, row]

def spawnFood():
    app.food = placeItem(app.poison)
    foodGroup.clear()
    x, y = cellToPixel(app.food[0], app.food[1])
    foodGroup.add(drawFood(x, y, False))

def spawnPoison():
    poisonGroup.clear()
    app.poison = None

    if randrange(0, 100) < 35:
        app.poison = placeItem(app.food)
        x, y = cellToPixel(app.poison[0], app.poison[1])
        poisonGroup.add(drawFood(x, y, True))

def resetGame():
    app.started = False
    app.gameOver = False
    app.score = 0
    app.direction = 'right'
    app.nextDirection = 'right'
    app.snake = [[8, 8], [7, 8], [6, 8]]
    app.poisoned = False
    app.steps = 0

    hideOverlay()
    spawnFood()
    spawnPoison()
    drawSnake()
    updateLabels()

def startGame():
    if app.gameOver:
        resetGame()
    app.started = True
    hideOverlay()
    updateLabels()

def setDirection(direction):
    opposites = {
        'up': 'down',
        'down': 'up',
        'left': 'right',
        'right': 'left'
    }
    if opposites[app.direction] != direction:
        app.nextDirection = direction

def handleInput(direction):
    if app.poisoned:
        if direction == 'up':
            direction = 'down'
        elif direction == 'down':
            direction = 'up'
        elif direction == 'left':
            direction = 'right'
        elif direction == 'right':
            direction = 'left'
    setDirection(direction)

def moveSnake():
    app.direction = app.nextDirection
    headCol, headRow = app.snake[0]

    if app.direction == 'up':
        headRow -= 1
    elif app.direction == 'down':
        headRow += 1
    elif app.direction == 'left':
        headCol -= 1
    else:
        headCol += 1

    newHead = [headCol, headRow]

    if not onBoard(headCol, headRow) or inSnake(headCol, headRow):
        app.gameOver = True
        app.started = False
        showOverlay('Game Over', 'Press space to play again')
        updateLabels()
        return

    app.snake.insert(0, newHead)

    if sameCell(newHead, app.food):
        app.score += 10
        if app.poisoned:
            app.poisoned = False
        spawnFood()
        spawnPoison()
    elif sameCell(newHead, app.poison):
        app.score = max(0, app.score - 5)
        app.poisoned = True
        poisonGroup.clear()
        app.poison = None
        if len(app.snake) > 3:
            app.snake.pop()
    else:
        app.snake.pop()

    drawSnake()
    updateLabels()

# -----------------------------
# Events
# -----------------------------
def onKeyPress(key):
    if key == 'space':
        startGame()
    elif key == 'r':
        resetGame()
    elif key == 'up' or key == 'w':
        handleInput('up')
    elif key == 'down' or key == 's':
        handleInput('down')
    elif key == 'left' or key == 'a':
        handleInput('left')
    elif key == 'right' or key == 'd':
        handleInput('right')

def onKeyRelease(key):
    pass

def onKeyHold(keys):
    if 'up' in keys or 'w' in keys:
        handleInput('up')
    elif 'down' in keys or 's' in keys:
        handleInput('down')
    elif 'left' in keys or 'a' in keys:
        handleInput('left')
    elif 'right' in keys or 'd' in keys:
        handleInput('right')

def onStep():
    app.steps += 1

    if app.poisoned:
        app.stepsPerSecond = app.poisonSpeed
    else:
        app.stepsPerSecond = app.normalSpeed

    drawSnake()

    if app.started and app.gameOver == False:
        moveSnake()

resetGame()