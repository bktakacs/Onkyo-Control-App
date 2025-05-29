from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt
from onkyo_controller import build_iscp_message, send_command, query_onkyo, db_to_hex, receiver_ip, receiver_port

# Only needed for access to command line arguments
import sys

# You need one (and only one) QApplication instance per application.
# Pass in sys.argv to allow command line arguments for your app.
# If you know you won't use command line arguments QApplication([]) works too.

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Onkyo Controller App!!!')
        self.setGeometry(1000, 500, 400, 300)
        self.setWindowIcon(QIcon('on.jpg'))
    

# Start the event loop.
app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()


# Your application won't reach here until you exit and the event
# loop has stopped.
