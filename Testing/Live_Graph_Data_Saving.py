import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QWidget
import tkinter as tk
from tkinter import messagebox

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt6 Widget")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        label = QLabel("This is a PyQt6 Widget")
        layout.addWidget(label)

        button = QPushButton("Open Tkinter Dialog")
        button.clicked.connect(self.open_dialog)
        layout.addWidget(button)

    def get_widget_position(self):
        # Get the global position of the PyQt6 window
        widget_pos = self.mapToGlobal(self.rect().center())
        return widget_pos.x(), widget_pos.y()

    def open_dialog(self):
        # Create a Tkinter window
        root = tk.Tk()
        root.withdraw()  # Hide the root window

        # Get the position of the PyQt6 widget
        widget_x, widget_y = self.get_widget_position()

        # Calculate the position for the Tkinter dialog to be centered around the PyQt6 widget
        dialog_x = widget_x - 150  # Width of the Tkinter dialog box divided by 2
        dialog_y = widget_y - 100  # Height of the Tkinter dialog box divided by 2

        # Show the Tkinter dialog box centered around the PyQt6 widget
        root.geometry(f"+{dialog_x}+{dialog_y}")
        messagebox.showinfo("Tkinter Dialog", "This is a Tkinter dialog centered around the PyQt6 widget")

        root.mainloop()

def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_app()