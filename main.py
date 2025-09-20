import logging
import asyncio
from colorlog import ColoredFormatter
from app.db.engine import init_db
import sys
from PyQt6.QtWidgets import QApplication
from app.ui.board import Board


handler = logging.StreamHandler()
formatter = ColoredFormatter(
    "%(log_color)s%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red"
    }
)
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)


def start_app():
    app = QApplication(sys.argv)
    board = Board()
    board.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    asyncio.run(init_db())
    # start_app()

    from app.storage import *

    doc = save_file("D:/PythonProjects/HADSA/requirements.txt")
