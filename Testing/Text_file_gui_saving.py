from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class SeparateWindow(QDialog):
    def __init__(self, parent=None):
        # Creating Label for Note taking Components
        super(SeparateWindow, self).__init__(parent)
        #noteTakerPanel = QWidget()
        noteTakerLayout = QVBoxLayout()
        noteTakerLayout.setAlignment(Qt.AlignLeft)
        
        # Note taking label
        self.noteTakingLabel = QLabel("<b>Note Taking</b>", alignment = Qt.AlignLeft)
        self.noteTakingLabel.setStyleSheet('QLabel {color: black; font-size: 24px;}')
        noteTakerLayout.addWidget(self.noteTakingLabel)

        # Note taking screen
        self.text_edit = QTextEdit(self)
        noteTakerLayout.addWidget(self.text_edit)
                

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Create a central widget, e.g., QStackedWidget
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Add your initial widgets to the stacked widget
        widget1 = QWidget()
        widget2 = QWidget()
        self.stacked_widget.addWidget(widget1)
        self.stacked_widget.addWidget(widget2)

        # Add a button to switch to the next widget
        switch_button = QPushButton("Switch Widget")
        switch_button.clicked.connect(self.switch_widget)
        layout.addWidget(switch_button)

    def switch_widget(self):
        # Switch to the next widget in the stacked widget
        current_index = self.stacked_widget.currentIndex()
        next_index = (current_index + 1) % self.stacked_widget.count()
        self.stacked_widget.setCurrentIndex(next_index)

        # Open the separate window without blocking the main widget
        separate_window = SeparateWindow(self)
        separate_window.setModal(False)  # Set to False for non-blocking behavior
        separate_window.show()

if __name__ == "__main__":
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec_()
