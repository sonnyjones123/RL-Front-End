import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget, QFileDialog

class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Text Editor')

        self.text_edit = QTextEdit(self)

        save_button = QPushButton('Save', self)
        save_button.clicked.connect(self.save_text)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(save_button)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

    def save_text(self):
        # Get the text from the QTextEdit widget
        text_to_save = self.text_edit.toPlainText()

        # Open a file dialog to choose the file to save
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_path, _ = file_dialog.getSaveFileName(self, 'Save Text', '', 'Text Files (*.txt);;All Files (*)')

        if file_path:
            # Save text to the chosen file
            with open(file_path, 'w') as file:
                file.write(text_to_save)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = TextEditor()
    editor.show()
    sys.exit(app.exec_())
