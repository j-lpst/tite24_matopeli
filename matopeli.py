import sys
import random
from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsOpacityEffect
from PySide6.QtGui import QPainter, QPen, QBrush, QFont, QColor
from PySide6.QtCore import Qt, QTimer, QUrl, QPropertyAnimation, QEasingCurve
from PySide6.QtMultimedia import QSoundEffect

CELL_SIZE = 20
GRID_WIDTH = 20
GRID_HEIGHT = 15


class SnakeGame(QGraphicsView):
    def __init__(self):
        super().__init__()

        scene = QGraphicsScene(self)
        scene.setBackgroundBrush(QBrush(Qt.white))  # Valkoinen background
        self.setScene(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setSceneRect(0, 0, CELL_SIZE * GRID_WIDTH, CELL_SIZE * GRID_HEIGHT)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.timer_delay = 300

        # Äänet
        self.eat_sound = QSoundEffect()
        self.eat_sound.setSource(QUrl.fromLocalFile("eat.wav"))
        self.eat_sound.setVolume(0.5)

        self.gameover_sound = QSoundEffect()
        self.gameover_sound.setSource(QUrl.fromLocalFile("gameover.wav"))
        self.gameover_sound.setVolume(0.5)

        self.game_started = False
        self.is_game_over = False
        self.animations = []

        self.init_screen()

        # Masennus :(
        self.quotes = [
            ("Life is a tale told by an idiot, full of sound and fury, signifying nothing.", "William Shakespeare"),
            ("We are born crying, live complaining, and die disappointed.", "Thomas Fuller"),
            ("There is but one truly serious philosophical problem, and that is suicide.", "Albert Camus"),
            ("Man is condemned to be free.", "Jean-Paul Sartre"),
            ("All that we see or seem is but a dream within a dream.", "Edgar Allan Poe"),
            ("To live is to suffer, to survive is to find some meaning in the suffering.", "Friedrich Nietzsche"),
            ("The only thing we learn from history is that we learn nothing from history.", "Georg Hegel"),
            ("Life has no meaning the moment you lose the illusion of being eternal.", "Jean-Paul Sartre"),
            ("Everything is meaningless, except the meaning we give it.", "Jean-Paul Sartre"),
            ("We are prisoners of our own minds.", "Blaise Pascal"),
            ("Man suffers only because he takes seriously what the gods made for fun.", "Alan Watts"),
            ("The universe is indifferent to our suffering.", "Carl Sagan"),
            ("The meaning of life is that it stops.", "Fran Lebowitz"),
            ("We are born to die, but we spend a lifetime forgetting.", "Unknown"),
            ("Hope is the worst of evils, for it prolongs the torment of man.", "Friedrich Nietzsche"),
            ("Everything is ephemeral, even despair.", "Unknown"),
            ("No one can confidently say that he will still be alive tomorrow.", "Euripides"),
            ("Everything is fleeting; hold nothing too tightly.", "Buddha"),
            ("Life is a series of meaningless gestures.", "Jean-Paul Sartre"),
            ("We live as we dream — alone.", "Joseph Conrad"),
            ("Life is but a fleeting shadow of a shadow.", "Horace"),
            ("Life is an error, and death is correction.", "Unknown"),
            ("To die will be an awfully big adventure.", "J.M. Barrie"),
            ("The fear of death follows from the fear of life.", "Mark Twain"),
            ("Man is born free, and everywhere he is in chains.", "Jean-Jacques Rousseau"),
            ("We are always getting ready to live but never living.", "Ralph Waldo Emerson")

        ]

    def init_screen(self):
        start_text = self.scene().addText("Press any key to start", QFont("Arial", 18))
        text_width = start_text.boundingRect().width()
        text_x = (self.width() - text_width) / 5
        start_text.setPos(text_x, GRID_HEIGHT * CELL_SIZE / 2)

    def keyPressEvent(self, event):
        key = event.key()
        if hasattr(self, 'awaiting_restart') and self.awaiting_restart:
            if key not in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
                self.awaiting_restart = False
                self.game_started = True
                self.is_game_over = False
                self.gameover_sound.stop()
                self.scene().clear()
                self.start_game()
            return

        if not self.game_started:
            self.game_started = True
            self.scene().clear()
            self.start_game()
            self.score = 0
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

        if new_head in self.snake or not (0 <= new_head[0] < GRID_WIDTH) or not (0 <= new_head[1] < GRID_HEIGHT):
            self.timer.stop()
            self.is_game_over = True
            self.gameover_sound.play()
            self.game_over()
            return

        if new_head == self.food:
            self.snake.insert(0, new_head)
            self.eat_sound.play()
            self.food = self.spawn_food()
            self.score += 1
            self.timer_delay = max(60, int(self.timer_delay * 0.93))
            self.timer.start(self.timer_delay)
        else:
            self.snake.insert(0, new_head)
            self.snake.pop()

        self.print_game()

    def game_over(self):
        self.print_game()

        # Pimeä filteri tekstin ja madon välissä
        overlay = QGraphicsRectItem(0, 0, CELL_SIZE * GRID_WIDTH, CELL_SIZE * GRID_HEIGHT)
        overlay.setBrush(QBrush(QColor(0, 0, 0, 0)))  # start transparent
        overlay.setPen(Qt.NoPen)
        overlay.setZValue(5)  # Madon (0) ja tekstin (10) välissä
        self.scene().addItem(overlay)

        def update_overlay(value):
            overlay.setBrush(QBrush(QColor(0, 0, 0, int(value))))

        dark_anim = QPropertyAnimation(self, b"dummy")
        dark_anim.valueChanged.connect(update_overlay)
        dark_anim.setDuration(10000)
        dark_anim.setStartValue(0)
        dark_anim.setEndValue(200)  # Läpinäkyvyys
        dark_anim.setEasingCurve(QEasingCurve.InOutQuad)
        dark_anim.start()
        self.animations.append(dark_anim)

        # Game Over
        game_over_text = self.scene().addText("Game Over", QFont("Old English Text MT", 30))
        game_over_text.setDefaultTextColor(Qt.white)
        game_over_text.setZValue(10)
        text_width = game_over_text.boundingRect().width()
        text_x = (self.width() - text_width) / 2
        text_y = GRID_HEIGHT * CELL_SIZE / 2
        game_over_text.setPos(text_x, text_y)

        # Quote and author separately
        quote, author = random.choice(self.quotes)

        # Quote text
        quote_text = self.scene().addText(f"\"{quote}\"", QFont("Times New Roman", 10))
        quote_text.setDefaultTextColor(Qt.white)
        quote_text.setZValue(10)
        quote_width = quote_text.boundingRect().width()
        quote_x = (self.width() - quote_width) / 2
        quote_y = text_y + game_over_text.boundingRect().height() + 8
        quote_text.setPos(quote_x, quote_y)

        # Author text (below quote)
        author_text = self.scene().addText(f"— {author}", QFont("Times New Roman", 10))
        author_text.setDefaultTextColor(Qt.white)
        author_text.setZValue(10)
        author_width = author_text.boundingRect().width()
        author_x = (self.width() - quote_width) / 2
        author_y = quote_y + quote_text.boundingRect().height() - 8
        author_text.setPos(author_x, author_y)

        # Restart
        restart_text = self.scene().addText("Press any key to start anew", QFont("Times New Roman", 12))
        restart_text.setDefaultTextColor(Qt.white)
        restart_text.setZValue(10)
        restart_width = restart_text.boundingRect().width()
        restart_x = (self.width() - restart_width) / 2
        restart_y = author_y + author_text.boundingRect().height() + 12
        restart_text.setPos(restart_x, restart_y)

        # Fade-in animations
        # Game over fades in normally
        go_opacity = QGraphicsOpacityEffect()
        game_over_text.setGraphicsEffect(go_opacity)
        go_anim = QPropertyAnimation(go_opacity, b"opacity")
        go_anim.setDuration(10000)
        go_anim.setStartValue(0)
        go_anim.setEndValue(1)
        go_anim.start()
        self.animations.append(go_anim)

        # Quote fades in
        quote_opacity = QGraphicsOpacityEffect()
        quote_text.setGraphicsEffect(quote_opacity)
        quote_anim = QPropertyAnimation(quote_opacity, b"opacity")
        quote_anim.setDuration(10000)
        quote_anim.setStartValue(0)
        quote_anim.setEndValue(1)
        quote_anim.start()
        self.animations.append(quote_anim)

        # Author fades in later using QTimer single-shot delay
        author_opacity = QGraphicsOpacityEffect()
        author_text.setGraphicsEffect(author_opacity)
        author_opacity.setOpacity(0)  # start invisible
        author_anim = QPropertyAnimation(author_opacity, b"opacity")
        author_anim.setDuration(2000)
        author_anim.setStartValue(0)
        author_anim.setEndValue(1)
        author_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.animations.append(author_anim)

        QTimer.singleShot(12000, author_anim.start)  # 12 s

        # Restart fades in normally
        restart_opacity = QGraphicsOpacityEffect()
        restart_text.setGraphicsEffect(restart_opacity)
        restart_opacity.setOpacity(0)  # start invisible
        restart_anim = QPropertyAnimation(restart_opacity, b"opacity")
        restart_anim.setDuration(3000)
        restart_anim.setStartValue(0)
        restart_anim.setEndValue(1)
        restart_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.animations.append(restart_anim)

        QTimer.singleShot(14000, restart_anim.start)  # 12 s

        self.awaiting_restart = True


    def print_game(self):
        self.scene().clear()
        for segment in self.snake:
            x, y = segment
            color = Qt.gray if self.is_game_over else Qt.green
            self.scene().addRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE,
                                 QPen(Qt.black), QBrush(color))
        fx, fy = self.food
        food_color = Qt.black if self.is_game_over else Qt.red
        self.scene().addRect(fx * CELL_SIZE, fy * CELL_SIZE, CELL_SIZE, CELL_SIZE,
                             QPen(Qt.black), QBrush(food_color))
        self.scene().addText(f"Score: {self.score}", QFont("Arial", 12))

    def spawn_food(self):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake:
                return x, y

    def start_game(self):
        self.is_game_over = False
        self.animations.clear()
        self.direction = Qt.Key_Right
        self.snake = [(5, 5), (5, 6), (5, 7)]
        self.food = self.spawn_food()
        self.score = 0
        self.level_limit = 5
        self.timer_delay = 300
        self.timer.start(self.timer_delay)


def main():
    app = QApplication(sys.argv)
    game = SnakeGame()
    game.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
