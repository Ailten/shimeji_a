
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtWidgets import QApplication

from pathlib import Path
from time import sleep
import asyncio
import threading
import sys

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from PySide6.QtGui import QMouseEvent

from .characterAction import CharacterAction

class Character(QLabel):
    is_over_menu_bar: bool = True
    menu_bar_height: int = 33

    is_allow_to_duplicate: bool = False  # Need Fixe from spawn QApplication.
    instances: list["Character"] = []

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

        # params.
        self.time_from_lauch = 0
        self.action = CharacterAction.Wait
        self.time_from_last_action = 0
        self.action_package = {'wait_delay': 2}
        self.is_look_right = True
        self.pos_float = [0, 0]

        # instances static.
        Character.instances.append(self)

    # ------>

    def loadSprite(self, sprite_path: str):
        sprite_name = Path(sprite_path).stem
        pixmap = QPixmap(sprite_path)
        self.sprites[sprite_name] = pixmap

        # first sprite load (set sprite print and size).
        if len(self.sprites) == 1:
            self.setSprite(sprite_name)
            self.resize(pixmap.size())

    def setSprite(self, sprite_name: str, is_flip_left:bool|None = None):
        if is_flip_left == None:
            is_flip_left = not self.is_look_right

        pixmap = self.sprites.get(sprite_name)
        if pixmap == None:  # if sprite not found, use the 'default' one.
            pixmap = self.sprites.get('default')
        if pixmap == None:  # still not found the default, return (or throw exception).
            # TODO: log error : sprite not found.
            return
        
        if is_flip_left:
            pixmap = pixmap.transformed(QTransform().scale(-1, 1))

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

    def updatePosFromFloat(self):
        self.setPos(
            int(self.pos_float[0]),
            int(self.pos_float[1])
        )

    # ------>

    def snapToGround(self):
        self.setPosY(self.getMaxPosScreenY())
        self.pos_float = [float(self.x()), float(self.y())]

    def snapToCenter(self):
        screen_geo = self.screen().geometry()
        self.setPos(
            screen_geo.width() // 2,
            screen_geo.height() // 2,
        )
        self.pos_float = [float(self.x()), float(self.y())]

    # ------>

    def mousePressEvent(self, event: "QMouseEvent"):  # main event for mouse (from the library).

        if event.button() == Qt.RightButton:
            Character.instances.remove(self)
            self.close()  # close the tool window.
            if len(Character.instances) == 0:
                QApplication.quit()  # close the process (loop infint).

    # ------>

    async def updateLoop(self):

        sleep_time_update = 1.0 / 30  # 30 fps.
        
        while True:

            # cut the loop.
            app = QApplication.instance()
            if app is None or app.closingDown():
                return

            # do the action update.
            self.action.do(self)

            # wait fps.
            sleep(sleep_time_update)
            self.time_from_lauch += sleep_time_update

    # ------>

    def getTimeInAction(self) -> float:
        return self.time_from_lauch - self.time_from_last_action

    # ------>

    def getMaxPosScreenX(self) -> int:
        return self.screen().geometry().width() - self.size().width()

    def getMaxPosScreenY(self) -> int:
        output = self.screen().geometry().height() - self.size().height()
        if not Character.is_over_menu_bar:
            output -= Character.menu_bar_height
        return output
    
    # ------>

    def spawn(self, sprites:list[str]|None=None) -> "Character":
        new_instance = Character()

        # set sprites.
        if sprites == None:
            new_instance.sprites = self.sprites
        else:
            new_instance.loadSprites(sprites)
        
        # set pos (same as parent).
        new_instance.move(self.x(), self.y())

        new_instance.show()

        # get app instance (or create it).
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # async call for launch it.
        def appExecInstance():
            asyncio.run(sys.exit(app.exec()))  # FIXME: QApplication::exec: Must be called from the main thread
        app_exec_instance = threading.Thread(target=appExecInstance, daemon=True)
        app_exec_instance.start()

        # loop update of new instance.
        def updateLoopAsync():
            asyncio.run(new_instance.updateLoop())
        update_loop = threading.Thread(target=updateLoopAsync, daemon=True)
        update_loop.start()

        return new_instance