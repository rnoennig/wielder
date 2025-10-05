import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui
import oracle_to_postgres
import importlib

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Wielder")

        self.oracle = QtWidgets.QTextEdit("alter table blabla add column b INTEGER;")
        self.oracle.setPlaceholderText("Enter Oracle SQL here...")
        self.postgres = QtWidgets.QTextEdit()
        self.postgres.setPlaceholderText("Postgres SQL will appear here")
        self.button = QtWidgets.QPushButton("Convert")

        self.sidebyside = QtWidgets.QHBoxLayout()
        self.sidebyside.addWidget(self.oracle)
        self.sidebyside.addWidget(self.postgres)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addLayout(self.sidebyside)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.on_convert)

    @QtCore.Slot()
    def on_convert(self):
        try:
            importlib.reload(oracle_to_postgres)
            converted_text = oracle_to_postgres.OracleToPostgresConverter().convert(self.oracle.toPlainText())
            self.postgres.setText(converted_text)
        except Exception as e:
            self.postgres.setText("An error occured: " + str(e))
                

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())
