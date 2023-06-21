import time
import pygame
import numpy as np
import random

MUTATION_RATE = 0.2
BIG_MUTATION = 0.02
AGE_LIMIT = 7

COLOR_BG = (10, 10, 10)
COLOR_GRID = (40, 40, 40)

colonyList = []

class Colony:
    def __init__(self):
        self.initalStrength = 127
        self.initialReproduction = 127
        self.color = tuple(np.random.choice(range(256), size=3))
        self.count = 0
        self.totalStrength = 0
        self.totalReproduction = 0

class Cell:
    def __init__(self, parentStrength, parentReproduction, colony):
        num = random.randint(0, 99)
        
        if num < BIG_MUTATION * 100:
            self.strength = parentStrength + 100
            self.reproduction = parentReproduction - 50

        elif num < MUTATION_RATE * 100:
            mutate = random.randint(0, 1)

            if mutate == 0:
                high = parentStrength + 10
                low = 0 if parentStrength - 10 < 0 else parentStrength - 10
                self.strength = random.randrange(low, high)
                self.reproduction = parentReproduction
            else:
                high = 255 if parentReproduction + 10 > 255 else parentReproduction + 10
                low = 0 if parentReproduction - 10 < 0 else parentReproduction - 10
                self.reproduction = random.randrange(low, high)
                self.strength = parentStrength
        else:
            self.strength = parentStrength
            self.reproduction = parentReproduction

        self.colony = colony
        self.age = 0

        if num < BIG_MUTATION * 100:
            self.ageLimit = AGE_LIMIT // 2
        else:
            self.ageLimit = AGE_LIMIT

def fight(cell1, cell2):
    if cell1.strength < cell2.strength:
        return 1
    elif cell1.strength > cell2.strength:
        return -1
    return 0

def update(screen, cells, size, with_progress=False):

    for row, col in np.ndindex(cells.shape):
        if cells[row, col]:
            color = cells[row, col].colony.color
        else:
            color = COLOR_BG

        LEFT = row, col - 1
        RIGHT = row, col + 1
        UP = row - 1, col
        DOWN = row + 1, col
        STAY = row, col

        if cells[row, col]:
            cells[row, col].colony.count += 1
            cells[row, col].colony.totalStrength += cells[row, col].strength
            cells[row, col].colony.totalReproduction += cells[row, col].reproduction

        if with_progress and cells[row, col]:

            if cells[row, col].age >= cells[row, col].ageLimit:
                cells[row, col] = None
                color = COLOR_BG
                pygame.draw.rect(screen, color, (col * size, row * size, size - 1, size - 1))
                continue

            arr = [UP, RIGHT, LEFT, DOWN, STAY]
            np.random.shuffle(arr)

            if random.randint(1, 500) < cells[row, col].reproduction:
                for x, y in arr:
                    if not (0 <= x < len(cells) and 0 <= y < len(cells[x])):
                        continue
                    if x == row and y == col:
                        cells[x, y] = Cell(parentStrength=cells[row, col].strength, parentReproduction=cells[row, col].reproduction, colony=cells[row, col].colony)
                        break
                    else:
                        if not cells[x, y]:
                            cells[x, y] = Cell(parentStrength=cells[row, col].strength, parentReproduction=cells[row, col].reproduction, colony=cells[row, col].colony)
                            break

            arr = [DOWN, RIGHT, UP, LEFT]
            np.random.shuffle(arr)
            direction = random.choice(arr)
            x, y = direction

            if not (0 <= x < len(cells) and 0 <= y < len(cells[x])):
                x, y = row, col
            elif cells[x, y]:
                if cells[x, y].colony is not cells[row, col].colony:
                    res = fight(cells[x, y], cells[row, col])
                    if res == -1:
                        cells[row, col] = cells[x, y]
                        cells[x, y] = None
                        x, y = row, col
                    elif res == 1:
                        cells[x, y] = cells[row, col]
                        cells[row, col] = None
                    else:
                        x, y = row, col
                else:
                    x, y = row, col
            else:
                cells[x, y] = cells[row, col]
                cells[row, col] = None

            cells[x, y].age += 1

        pygame.draw.rect(screen, color, (col * size, row * size, size - 1, size - 1))

    for n, c in enumerate(colonyList):
        if c.count != 0:
            print(f"Colony {n + 1}: Average Strength: {c.totalStrength // c.count}, Average Reproduction: {c.totalReproduction // c.count}")

        c.count = 0
        c.totalStrength = 0
        c.totalReproduction = 0
    print()

    return cells


#This portion of the code was heavily inspired from a YouTube video explaining how to create Game Of Life in Python
# https://www.youtube.com/watch?v=cRWg2SWuXtM
def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 800))

    cells = np.zeros((80, 100), dtype=Cell)
    screen.fill(COLOR_GRID)
    update(screen, cells, 10)

    pygame.display.flip()
    pygame.display.update()

    running = False

    pop = Colony()
    colonyList.append(pop)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    running = not running
                    update(screen, cells, 10)
                    pygame.display.update()
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                cells[pos[1] // 10, pos[0] // 10] = Cell(parentStrength=pop.initalStrength, parentReproduction=pop.initialReproduction, colony=pop)
                update(screen, cells, 10)
                pygame.display.update()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    pop = Colony()
                    colonyList.append(pop)
                    update(screen, cells, 10)
                    pygame.display.update()

            
        screen.fill(COLOR_GRID)

        if running:
            cells = update(screen, cells, 10, with_progress=True)
            pygame.display.update()

        time.sleep(0.001)

if __name__ == '__main__':
    main()