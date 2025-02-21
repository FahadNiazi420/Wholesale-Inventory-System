import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon
from main_screen_logic import MasterScreen
import resources_rc

def show_critical_error(message):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle("Critical Error")
    msg_box.setText(message)
    msg_box.exec_()

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)


        login_screen = MasterScreen()
        login_screen.show()
        sys.exit(app.exec_())
    except Exception as e:
        show_critical_error(f"Application failed to start: {str(e)}")
