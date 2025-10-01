import sys
import random
from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMenu
from PySide6.QtGui import QPainter, QPen, QBrush, QFont
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtMultimedia import QSoundEffect

CELL_SIZE = 20
GRID_WIDTH = 20
GRID_HEIGHT = 15

class SnakeGame(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.Antialiasing)
        self.setSceneRect(0, 0, CELL_SIZE * GRID_WIDTH, CELL_SIZE * GRID_HEIGHT)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)

        # Äänet
        self.eat_sound = QSoundEffect()
        self.eat_sound.setSource(QUrl.fromLocalFile("eat.wav"))
        self.eat_sound.setVolume(0.5)

        self.gameover_sound = QSoundEffect()
        self.gameover_sound.setSource(QUrl.fromLocalFile("gameover.wav"))
        self.gameover_sound.setVolume(0.5)

        self.game_started = False
        self.init_screen()

    def init_screen(self):
        start_text = self.scene().addText("Press any key to start", QFont("Arial", 18))
        text_width = start_text.boundingRect().width()
        text_x = (self.width() - text_width) / 5
        start_text.setPos(text_x, GRID_HEIGHT * CELL_SIZE / 2)

    def keyPressEvent(self, event):
        key = event.key()
        if not self.game_started:
            self.game_started = True
            self.scene().clear()
            self.start_game()
            return

        if key in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
            if key == Qt.Key_Left and self.direction != Qt.Key_Right:
                self.direction = key
            elif key == Qt.Key_Right and self.direction != Qt.Key_Left:
                self.direction = key
            elif key == Qt.Key_Up and self.direction != Qt.Key_Down:
                self.direction = key
            elif key == Qt.Key_Down and self.direction != Qt.Key_Up:
                self.direction = key

    def update_game(self):
        head_x, head_y = self.snake[0]

        if self.direction == Qt.Key_Left:
            new_head = (head_x - 1, head_y)
        elif self.direction == Qt.Key_Right:
            new_head = (head_x + 1, head_y)
        elif self.direction == Qt.Key_Up:
            new_head = (head_x, head_y - 1)
        elif self.direction == Qt.Key_Down:
            new_head = (head_x, head_y + 1)

        # board limits
        if new_head in self.snake or not (0 <= new_head[0] < GRID_WIDTH) or not (0 <= new_head[1] < GRID_HEIGHT):
            self.timer.stop()
            self.gameover_sound.play()  # Game Over ääni
            self.game_over()
            return

        # syöminen
        if new_head == self.food:
            self.snake.insert(0, new_head)
            self.eat_sound.play()  # Syömisääni
            self.food = self.spawn_food()
        else:
            self.snake.insert(0, new_head)
            self.snake.pop()

        self.print_game()

    def game_over(self):
        game_over_text = self.scene().addText("Game Over", QFont("Arial", 24))
        text_width = game_over_text.boundingRect().width()
        text_x = (self.width() - text_width) / 2
        game_over_text.setPos(text_x, GRID_HEIGHT * CELL_SIZE / 2)

    def print_game(self):
        self.scene().clear()
        for segment in self.snake:
            x, y = segment
            self.scene().addRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE, QPen(Qt.black), QBrush(Qt.black))
        fx, fy = self.food
        self.scene().addRect(fx * CELL_SIZE, fy * CELL_SIZE, CELL_SIZE, CELL_SIZE, QPen(Qt.black), QBrush(Qt.black))

    def spawn_food(self):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake:
                return x, y
            self.scene().addRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE,
                                 QPen(Qt.black), QBrush(Qt.black))
        
    def start_game(self):
        self.direction = Qt.Key_Right
        self.snake = [(5, 5), (5, 6), (5, 7)]
        self.timer.start(300)
        self.food = self.spawn_food()

def main():
    app = QApplication(sys.argv)
    game = SnakeGame()
    game.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()