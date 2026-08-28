
import sys
import asyncio
import threading

from PySide6.QtWidgets import QApplication

from classes.character import Character

app = QApplication(sys.argv)

Character.is_over_menu_bar = False
shimeji = Character()
shimeji.loadSprites([
    "sprites/default.png"
])
shimeji.snapToCenter()
shimeji.snapToGround()
shimeji.show()

# async loop thread (update).
def updateLoopAsync():
    asyncio.run(shimeji.updateLoop())
update_loop = threading.Thread(target=updateLoopAsync, daemon=True)
update_loop.start()


sys.exit(app.exec())  # block programme.
