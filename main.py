import pygame as pg
from settings import *

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(RESOLUTION)
        self.nane = pg.display.set_caption("The problem of the horse's gait")
        self.clock = pg.time.Clock()
        self.done = False
        self.chessboard = Chessboard(screen=self.screen)

    def run(self):
        while not self.done:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.done = True

            self.screen.fill(COLORS['black'])

            self.chessboard.draw_chessboard()
            pg.display.flip()
            self.clock.tick(FPS)


class Chessboard:
    def __init__(self, n=8, m=8, screen=None):
        self.board = [[0 for _ in range(n)] for _ in range(m)]
        self.board[0][0] = 1
        
        if screen is None:
            raise ValueError("You must provide a screen")
        else:
            self.screen = screen

    def draw_chessboard(self):
        tile_size = DESK_RESOLUTION [0] // 8
        colors = [COLORS['cream'], COLORS['dark_brown']]
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                pg.draw.rect(self.screen, color, (col * tile_size, row * tile_size, tile_size, tile_size))


if __name__ == '__main__':
    game = Game()
    game.run()
    pg.quit()
    quit()