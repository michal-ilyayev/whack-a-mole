##########################################################
# Programmer: Michal Ilyayev
# Date: 18/06/2024
# File Name: final.py
# Description: This is the final version of the game
##########################################################

import pathlib
import pygame
import random


pygame.init()

# ---------------------------------------#
#         game properties                #
# ---------------------------------------#
WIDTH = 600
HEIGHT = 700
GRIDSIZE = 180
XOffset = 120
YOffset = 220
HolesGrid = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
FPS = 60

Screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Whack a Mole")
Clock = pygame.time.Clock()

# ---------------------------------------#
#         picture properties             #
# ---------------------------------------#

CWD = pathlib.Path(__file__).parent

# Load background images
BackgroundFileName = pygame.image.load(CWD / "images/background.png")
Background = pygame.transform.scale(BackgroundFileName, (WIDTH, HEIGHT))

# Load hole image
HoleImageFileName = pygame.image.load(CWD / "images/hole.png")
HoleImage = pygame.transform.scale(HoleImageFileName, (120, 120))

# Load and resize mole images
MoleImageFileName = pygame.image.load(CWD / "images/mole.png")
MoleImage = pygame.transform.scale(MoleImageFileName, (100, 100))

# Load and scale bomb image
BombImageFileName = pygame.image.load(CWD / "images/bomb.png")
BombImage = pygame.transform.scale(BombImageFileName, (100, 100))


# ---------------------------------------#
#           game components              #
# ---------------------------------------#

class Hole:
    def __init__(self, num, col, row):
        self.num = num
        self.col = col
        self.row = row

    def draw(self):
        Screen.blit(HoleImage, (XOffset + self.col * GRIDSIZE - 60, YOffset + self.row * GRIDSIZE - 60))


class Mole:
    def __init__(self, MoleType):
        self.MoleType = MoleType
        self.MoleX = 0
        self.MoleY = 0
        self.Speed = 3
        self.HoleNum = 0
        self.HoleRow = 0
        self.Move = False
        self.Counter = 0

    def selectHole(self, takenHoles):
        # Select a hole that is not taken
        self.HoleNum = random.randint(0, 8)
        while self.HoleNum in takenHoles:
            self.HoleNum = random.randint(0, 8)

        col = self.HoleNum % 3
        row = self.HoleNum // 3
        self.HoleRow = YOffset + row * GRIDSIZE
        self.MoleX = XOffset + GRIDSIZE * col
        self.MoleY = self.HoleRow - 55
        self.Move = True
        self.Counter = 0

    def draw(self):
        if self.Move:
            if self.MoleType == "mole":
                Screen.blit(MoleImage, (self.MoleX - 50, self.MoleY))
            elif self.MoleType == "bomb":
                Screen.blit(BombImage, (self.MoleX - 50, self.MoleY))

    def show(self):
        if self.Move:
            self.Counter += 1

            # Mole is visible for 2 seconds
            if self.Counter < 120:
                if self.MoleY > self.HoleRow - 80:
                    self.MoleY -= self.Speed

            # Adjusted the y-coordinate
            elif self.MoleY < self.HoleRow - 80:
                self.MoleY += self.Speed * 3

            else:
                self.Move = False
                self.Counter = 0

    def isClicked(self, mousePos):
        # Check if the mole is clicked by the mouse
        if self.Move:
            if self.MoleX - 50 < mousePos[0] < self.MoleX + 50 and self.MoleY < mousePos[1] < self.MoleY + 100:
                return True
        return False


# ---------------------------------------#
#           game class                   #
# ---------------------------------------#

class Game:
    def __init__(self):
        self.Holes = []
        self.Moles = []
        self.Score = 0
        self.Lives = 3
        self.GameOver = False
        self.GameOverCounter = 0
        self.GameOverText = pygame.font.SysFont("comicsans", 100)
        self.ScoreText = pygame.font.SysFont("comicsans", 50)
        self.LivesText = pygame.font.SysFont("comicsans", 50)

        for row in range(3):
            for col in range(3):
                self.Holes.append(Hole(row * 3 + col, col, row))

        for mole in range(3):
            self.Moles.append(Mole("mole"))

        self.Bomb = Mole("bomb")

    def draw(self):
        Screen.blit(Background, (0, 0))

        for mole in self.Moles:
            mole.draw()

        self.Bomb.draw()

        for hole in self.Holes:
            hole.draw()

        score = self.ScoreText.render(f"Score: {self.Score}", 1, (255, 255, 255))
        Screen.blit(score, (10, 10))

        lives = self.LivesText.render(f"Lives: {self.Lives}", 1, (255, 255, 255))
        Screen.blit(lives, (WIDTH - lives.get_width() - 10, 10))

        if self.GameOver:
            text = self.GameOverText.render("GAME OVER", 1, (255, 255, 255))
            Screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))


# ---------------------------------------#
#           main function                #
# ---------------------------------------#

def main():
    game = Game()
    inPlay = True
    showUpTimer = 0
    showUpEnd = 100

    while inPlay:
        Screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                inPlay = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mousePos = pygame.mouse.get_pos()
                for mole in game.Moles:
                    if mole.isClicked(mousePos):
                        game.Score += 1
                        mole.Move = False
                        mole.Counter = 0

                if game.Bomb.isClicked(mousePos):
                    game.Lives -= 1
                    game.Bomb.Move = False
                    game.Bomb.Counter = 0

        if game.Lives <= 0:
            game.GameOver = True

            # turn off the game after 3 seconds
            game.GameOverCounter += 1
            if game.GameOverCounter >= 180:
                inPlay = False

        if not game.GameOver:
            showUpTimer += 1
            if showUpTimer >= showUpEnd:

                # holes that are already taken
                takenHoles = [mole.HoleNum for mole in game.Moles] + [game.Bomb.HoleNum]

                # select a new hole for each mole
                for mole in game.Moles:
                    if not mole.Move:
                        mole.selectHole(takenHoles)
                        takenHoles.append(mole.HoleNum)
                        break

                # select a new hole for the bomb
                if not game.Bomb.Move:
                    game.Bomb.selectHole(takenHoles)

                showUpTimer = 0

            for mole in game.Moles:
                mole.show()
            game.Bomb.show()

        game.draw()
        pygame.display.update()

        Clock.tick(FPS)

    pygame.quit()


# if __name__ == "__main__":
main()
