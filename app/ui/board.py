from PyQt6.QtWidgets import QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget


class Board(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("HADSA v0.0.1")
        self.setGeometry(300, 150, 1280, 720)

        # Элементы
        self.label = QLabel("Привет, PyQt6!")
        self.button = QPushButton("Нажми меня")
        self.button.clicked.connect(self.on_button_click)

        # Лэйаут
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def on_button_click(self):
        self.label.setText("Кнопка нажата!")
