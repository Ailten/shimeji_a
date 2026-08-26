
import sys

from PySide6.QtWidgets import QApplication

from classes.character import Character

app = QApplication(sys.argv)

shimeji = Character()
shimeji.loadSprites([
    "sprites/default.png"
])
shimeji.snapToCenter()
shimeji.snapToGround()
shimeji.show()

sys.exit(app.exec())  # block programme, (try with asyncio ?)
