import pygame as pg
from settings import *
import os


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(RESOLUTION)
        self.name = pg.display.set_caption("The problem of the horse's gait")
        self.clock = pg.time.Clock()
        self.done = False
        self.chessboard = Chessboard(screen=self.screen)
        self.horse = Horse(0, 0, screen=self.screen)
        self.font = pg.font.Font(None, 36)

        self.input_x = InputBox(620, 50, 50, 36, '0')
        self.input_y = InputBox(680, 50, 50, 36, '0')
        self.start_button = Button(620, 100, 150, 40, "Start")
        self.stop_button = Button(620, 150, 150, 40, "Stop")
        self.undo_button = Button(620, 200, 150, 40, "Undo")
        self.hide_button = Button(620, 250, 150, 40, "Hide/Show")
        self.save_button = Button(620, 300, 150, 40, "Save Image")
        self.ui_elements = [self.input_x, self.input_y, self.start_button, self.stop_button, self.undo_button, self.hide_button, self.save_button]

        # Логіка
        self.show_moves = False
        self.valid_moves = []
        self.is_running = False  
        self.step_counter = 0 
        self.visited_cells = {} 
        self.history = []
        self.is_visible = True 

    def run(self):
        while not self.done:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.done = True

                for element in self.ui_elements:
                    if element.handle_event(event):
                        if element == self.start_button:
                            self.start_game()
                        elif element == self.stop_button:
                            self.stop_game()
                        elif element == self.undo_button:
                            self.undo_move()
                        elif element == self.hide_button: 
                            self.toggle_visibility()
                        elif element == self.save_button:
                            self.save_board_image()

                if self.is_running:
                    if event.type == pg.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            x, y = event.pos
                            self.handle_move(x, y)

            self.screen.fill(COLORS['black'])
            self.chessboard.draw_chessboard()

            self.highlight_moves()

            if self.is_visible:
                self.horse.draw_horse()
                self.draw_steps()

            if not self.is_visible:
                self.draw_path()

            self.draw_steps()

            for element in self.ui_elements:
                element.draw(self.screen)

            pg.display.flip()
            self.clock.tick(FPS)

    def save_board_image(self):
        board_x = 0
        board_y = 0
        board_width = DESK_RESOLUTION[0] 
        board_height = DESK_RESOLUTION[1]  

        board_surface = self.screen.subsurface((board_x, board_y, board_width, board_height))
        
        img_name = f"saves/chessboard_image{self.chech_last_save_img_name()}.png"
        pg.image.save(board_surface, img_name)

    @staticmethod
    def chech_last_save_img_name():
        files = os.listdir("saves")
        max_number = 0
        for file in files:
            if file.startswith("chessboard_image") and file.endswith(".png"):
                try:
                    number = int(file[len("chessboard_image"):-4])
                    if number > max_number:
                        max_number = number
                except ValueError:
                    continue
        return max_number + 1

    def handle_move(self, x, y):
        tile_size = DESK_RESOLUTION[0] // 8
        x_index = x // tile_size
        y_index = y // tile_size

        if (x_index, y_index) in self.visited_cells:
            print(f"Клітинка ({x_index}, {y_index}) вже відвідана, не можна туди рухатись.")
            return 

        if (x_index, y_index) in self.valid_moves:
            self.horse.set_position(x_index, y_index)
            self.step_counter += 1
            self.visited_cells[(x_index, y_index)] = self.step_counter
            self.history.append((self.horse.x, self.horse.y))  
            self.valid_moves = self.horse.possible_moves() 

    def draw_path(self):
        tile_size = DESK_RESOLUTION[0] // 8
        for i in range(1, len(self.history)):
            start_x, start_y = self.history[i - 1]
            end_x, end_y = self.history[i]
            pg.draw.line(self.screen, COLORS['red'], 
                         (start_x * tile_size + tile_size // 2, start_y * tile_size + tile_size // 2),
                         (end_x * tile_size + tile_size // 2, end_y * tile_size + tile_size // 2),
                         4)

    def start_game(self):
        try:
            x = int(self.input_x.text)
            y = int(self.input_y.text)
            if 0 <= x < 8 and 0 <= y < 8:
                self.horse.set_position(x, y)
                self.step_counter = 1 
                self.visited_cells = {(x, y): self.step_counter} 
                self.history = [(x, y)]
                self.is_running = True 
                self.show_moves = True
                self.valid_moves = self.horse.possible_moves() 
            else:
                print("Координати поза межами дошки!")
        except ValueError:
            print("Некоректні координати!")

    def stop_game(self):
        self.is_running = False

    def undo_move(self):
        if len(self.history) > 1:
            self.history.pop()
            
            prev_x, prev_y = self.history[-1]
            
            self.horse.set_position(prev_x, prev_y)
            
            self.step_counter -= 1
            
            last_move = list(self.visited_cells.keys())[-1]
            self.visited_cells.pop(last_move)
            
            self.valid_moves = self.horse.possible_moves()
        else:
            print("Немає попереднього кроку для відкату!")

    def highlight_moves(self):
        if not self.is_visible:
            return
        tile_size = DESK_RESOLUTION[0] // 8
        for move in self.valid_moves:
            color = COLORS['green']
            pg.draw.rect(self.screen, color, (move[0] * tile_size, move[1] * tile_size, tile_size, tile_size), 5)

    def draw_steps(self):
        if not self.is_visible:
            return
        tile_size = DESK_RESOLUTION[0] // 8
        for (x, y), step in self.visited_cells.items():
            text = self.font.render(str(step), True, COLORS['white'])
            self.screen.blit(text, (x * tile_size + tile_size // 4, y * tile_size + tile_size // 4))

    def toggle_visibility(self):
        self.is_visible = not self.is_visible


class Chessboard:
    def __init__(self, n=8, m=8, screen=None):
        self.board = [[0 for _ in range(n)] for _ in range(m)]
        self.board[0][0] = 1
        
        if screen is None:
            raise ValueError("You must provide a screen")
        else:
            self.screen = screen

    def draw_chessboard(self):
        tile_size = DESK_RESOLUTION[0] // 8
        colors = [COLORS['cream'], COLORS['dark_brown']]
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                pg.draw.rect(self.screen, color, (col * tile_size, row * tile_size, tile_size, tile_size))


class Horse:
    def __init__(self, x, y, screen=None):
        self.x = x
        self.y = y
        self.screen = screen
        self.size = DESK_RESOLUTION[0] // 8 - 5
        self.img = pg.image.load('img/horse.png', 'horse')
        self.img = pg.transform.scale(self.img, (self.size, self.size))

    def calculate_position(self, a):
        return a * (DESK_RESOLUTION[0] // 8)

    def draw_horse(self):
        pos_x = self.calculate_position(self.x)
        pos_y = self.calculate_position(self.y) + 2.5
        self.screen.blit(self.img, (pos_x, pos_y))

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def possible_moves(self):
        moves = []
        directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for dx, dy in directions:
            new_x, new_y = self.x + dx, self.y + dy
            if 0 <= new_x < 8 and 0 <= new_y < 8:
                moves.append((new_x, new_y))
        return moves


class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLORS['white']
        self.text = text
        self.txt_surface = pg.font.Font(None, 36).render(text, True, COLORS['white'])
        self.active = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = COLORS['blue'] if self.active else COLORS['white']
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    self.active = False
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = pg.font.Font(None, 36).render(self.text, True, COLORS['white'])

    def draw(self, screen):
        pg.draw.rect(screen, self.color, self.rect, 2)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))


class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLORS['cream']
        self.text = text
        self.txt_surface = pg.font.Font(None, 36).render(text, True, COLORS['black'])
        self.clicked_state = False 

    def draw(self, screen):
        pg.draw.rect(screen, self.color, self.rect)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.clicked_state = True  
        elif event.type == pg.MOUSEBUTTONUP:
            if self.clicked_state and self.rect.collidepoint(event.pos):
                self.clicked_state = False 
                return True  
        return False 

if __name__ == "__main__":
    game = Game()
    game.run()
