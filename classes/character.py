
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication

from pathlib import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from PySide6.QtGui import QMouseEvent

class Character(QLabel):

    def __init__(self):
        super().__init__()

        # define window params.
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool  # do not mark it as window in bottom menu.
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # sprites.
        self.sprites: dict[str, QPixmap] = dict()

    # ------>

    def loadSprite(self, sprite_path: str):
        sprite_name = Path(sprite_path).stem
        pixmap = QPixmap(sprite_path)
        self.sprites[sprite_name] = pixmap

        # first sprite load (set sprite print and size).
        if len(self.sprites) == 1:
            self.setPixmap(pixmap)
            self.resize(pixmap.size())

    def setSprite(self, sprite_name: str):
        pixmap = self.sprites.get(sprite_name)
        if pixmap == None:
            # TODO: log error : sprite not found.
            return
        self.setPixmap(pixmap)

    def loadSprites(self, sprites: list[str]):
        for s in sprites:
            self.loadSprite(s)

    # ------>

    def setPos(self, x: int, y: int):
        self.move(x, y)

    def increasePos(self, x: int, y: int):
        self.setPos(x=self.x() + x, y=self.y() + y)

    def setPosX(self, x: int):
        self.setPos(x=x, y=self.y())
    def setPosY(self, y: int):
        self.setPos(x=self.x(), y=y)

    def increasePosX(self, x: int):
        self.increasePos(x=x, y=0)
    def increasePosY(self, y: int):
        self.increasePos(x=0, y=y)

    # ------>

    def snapToGround(self):
        height_screen = self.screen().geometry().height()
        height = self.size().height()
        new_pos_y = height_screen - height
        self.setPosY(new_pos_y)

    def snapToCenter(self):
        screen_geo = self.screen().geometry()
        self.setPos(
            screen_geo.width() // 2,
            screen_geo.height() // 2,
        )

    # ------>

    def mousePressEvent(self, event: "QMouseEvent"):  # main event for mouse (from the library).

        if event.button() == Qt.RightButton:
            self.close()  # close the tool window.
            QApplication.quit()  # close the process (loop infint).