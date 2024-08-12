import pathlib
import pygame
import random


pygame.init()

# ---------------------------------------
# game properties
# ---------------------------------------

WIDTH = 600
HEIGHT = 700
GRID_SIZE = 180
X_OFFSET = 120
Y_OFFSET = 220
HOLES_GRID = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Whack a Mole')
clock = pygame.time.Clock()

# ---------------------------------------
# picture properties
# ---------------------------------------

CWD = pathlib.Path(__file__).parent

# Load background images
background_file_name = pygame.image.load(CWD / 'images/background.png')
background = pygame.transform.scale(background_file_name, (WIDTH, HEIGHT))

# Load hole image
hole_image_file_name = pygame.image.load(CWD / 'images/hole.png')
hole_image = pygame.transform.scale(hole_image_file_name, (120, 120))

# Load and resize mole images
mole_image_file_name = pygame.image.load(CWD / 'images/mole.png')
mole_image = pygame.transform.scale(mole_image_file_name, (100, 100))

# Load and scale bomb image
bomb_image_file_name = pygame.image.load(CWD / 'images/bomb.png')
bomb_image = pygame.transform.scale(bomb_image_file_name, (100, 100))


# ---------------------------------------
# game components
# ---------------------------------------


class Hole:
    def __init__(self, num, col, row):
        self.num = num
        self.col = col
        self.row = row

    def draw(self):
        screen.blit(hole_image, (X_OFFSET + self.col * GRID_SIZE - 60, Y_OFFSET + self.row * GRID_SIZE - 60))


class Mole:
    def __init__(self, mole_type):
        self.mole_type = mole_type
        self.mole_x = 0
        self.mole_y = 0
        self.speed = 3
        self.hole_num = 0
        self.hole_row = 0
        self.move = False
        self.counter = 0

    def select_hole(self, taken_holes):
        # Select a hole that is not taken
        self.hole_num = random.randint(0, 8)
        while self.hole_num in taken_holes:
            self.hole_num = random.randint(0, 8)

        col = self.hole_num % 3
        row = self.hole_num // 3
        self.hole_row = Y_OFFSET + row * GRID_SIZE
        self.mole_x = X_OFFSET + GRID_SIZE * col
        self.mole_y = self.hole_row - 55
        self.move = True
        self.counter = 0

    def draw(self):
        if self.move:
            if self.mole_type == 'mole':
                screen.blit(mole_image, (self.mole_x - 50, self.mole_y))
            elif self.mole_type == 'bomb':
                screen.blit(bomb_image, (self.mole_x - 50, self.mole_y))

    def show(self):
        if self.move:
            self.counter += 1

            # Mole is visible for 2 seconds
            if self.counter < 120:
                if self.mole_y > self.hole_row - 80:
                    self.mole_y -= self.speed

            # Adjusted the y-coordinate
            elif self.mole_y < self.hole_row - 80:
                self.mole_y += self.speed * 3

            else:
                self.move = False
                self.counter = 0

    def is_clicked(self, mouse_pos):
        # Check if the mole is clicked by the mouse
        if self.move:
            if self.mole_x - 50 < mouse_pos[0] < self.mole_x + 50 and self.mole_y < mouse_pos[1] < self.mole_y + 100:
                return True
        return False


# ---------------------------------------
# Game class
# ---------------------------------------


class Game:
    def __init__(self):
        self.holes = []
        self.moles = []
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.game_over_counter = 0
        self.game_over_text = pygame.font.SysFont('comicsans', 100)
        self.score_text = pygame.font.SysFont('comicsans', 50)
        self.lives_text = pygame.font.SysFont('comicsans', 50)

        for row in range(3):
            for col in range(3):
                self.holes.append(Hole(row * 3 + col, col, row))

        for mole in range(3):
            self.moles.append(Mole('mole'))

        self.bomb = Mole('bomb')

    def draw(self):
        screen.blit(background, (0, 0))

        for mole in self.moles:
            mole.draw()

        self.bomb.draw()

        for hole in self.holes:
            hole.draw()

        score = self.score_text.render(f'Score: {self.score}', 1, (255, 255, 255))
        screen.blit(score, (10, 10))

        lives = self.lives_text.render(f'Lives: {self.lives}', 1, (255, 255, 255))
        screen.blit(lives, (WIDTH - lives.get_width() - 10, 10))

        if self.game_over:
            text = self.game_over_text.render('GAME OVER', 1, (255, 255, 255))
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))


# ---------------------------------------
# main function
# ---------------------------------------


def main():
    game = Game()
    in_play = True
    show_up_timer = 0
    show_up_end = 100

    while in_play:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                in_play = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mousePos = pygame.mouse.get_pos()
                for mole in game.moles:
                    if mole.is_clicked(mousePos):
                        game.score += 1
                        mole.move = False
                        mole.counter = 0

                if game.bomb.is_clicked(mousePos):
                    game.lives -= 1
                    game.bomb.move = False
                    game.bomb.counter = 0

        if game.lives <= 0:
            game.game_over = True

            # turn off the game after 3 seconds
            game.game_over_counter += 1
            if game.game_over_counter >= 180:
                in_play = False

        if not game.game_over:
            show_up_timer += 1
            if show_up_timer >= show_up_end:
                # holes that are already taken
                taken_holes = [mole.hole_num for mole in game.moles] + [game.bomb.hole_num]

                # select a new hole for each mole
                for mole in game.moles:
                    if not mole.move:
                        mole.select_hole(taken_holes)
                        taken_holes.append(mole.hole_num)
                        break

                # select a new hole for the bomb
                if not game.bomb.move:
                    game.bomb.select_hole(taken_holes)

                show_up_timer = 0

            for mole in game.moles:
                mole.show()
            game.bomb.show()

        game.draw()
        pygame.display.update()

        clock.tick(FPS)

    pygame.quit()


# if __name__ == "__main__":
main()
