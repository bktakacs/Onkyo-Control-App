# from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QMenu, QAction
# from PyQt5.QtGui import QIcon
# from PyQt5.QtCore import QSize, Qt

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from onkyo_controller import build_iscp_message, send_command, query_onkyo, db_to_hex, receiver_ip, receiver_port

# Only needed for access to command line arguments
import sys

# You need one (and only one) QApplication instance per application.
# Pass in sys.argv to allow command line arguments for your app.
# If you know you won't use command line arguments QApplication([]) works too.

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()

class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Onkyo Controller App!!!')
        self.setGeometry(900, 500, 500, 500)
        self.setWindowIcon(QIcon('on.jpg'))
        
        layout = QGridLayout()
        self.setLayout(layout)

        # main
        label_main = QLabel('Control your Onkyo Here')
        label_main.setAlignment(Qt.AlignRight)
        layout.addWidget(label_main, 0, 0, 2, 1)

        # power
        # label
        label_power_status = QLabel('Receiver: Standby')
        layout.addWidget(label_power_status, 1, 0)
        # button
        button_power = QPushButton('Toggle Power')
        button_power.clicked.connect(self.power_toggle)
        layout.addWidget(button_power, 1, 1)

        # volume
        # label
        label_vol = QLabel('Volume')
        layout.addWidget(label_vol, 2, 1)
        # slider

        # mute toggle
        # label
        # button

        # change input
        # label
        label_input = QLabel('Select Audio Input')
        label_input.setWordWrap(True)
        layout.addWidget(label_input, 4, 0)
        # radiobutton
        radb_input_mac = QRadioButton('Mac mini (PC)')
        radb_input_mac.setChecked(True)
        radb_input_mac


    
    # def power_toggle(self):
    #     pwr_status = query_onkyo(
    #         'PWRQSTN', expected_prefix='!1PWR', verbose=False
    #     ).split('!1PWR')[1][:2]
    #     send_command('PWR00' if pwr_status == '01' else 'PWR01')
    #     l2.configure(text='Receiver: On' if pwr_status == '00' else 'Receiver: Standby')


app = QApplication(sys.argv)
screen = Window()
screen.show()

# Start the event loop.
# app = QApplication(sys.argv)

# window = MainWindow()
# window.show()

sys.exit(app.exec_())
# app.exec()



# Your application won't reach here until you exit and the event
# loop has stopped.
