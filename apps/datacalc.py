"""
App module for showing the sum of two values from selected databases.
"""

import json

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QPushButton, QLabel

from swift.app import BaseApp
from apps.backend import read

class ViewerFrame(QWidget):
    """Frame of for selecting databases and showing the calculated number.
    
    Attributes:
        dbBoxes: A dictionary containing two comboboxes for selecting the database 
          from which the value of A and B is fetched.
        calculateButton: A button for calculating the sum of recently fetched 'A' and 'B'.
        numberLabel: A label showing the sum, or an error message if something goes wrong.
    """
    def __init__(self, parent=None):
        """
        Args:
            parent: A parent widget.
        """
        super().__init__(parent=parent)
        # widgets
        self.dbBoxes = {
            "A": QComboBox(self),
            "B": QComboBox(self),
        }
        self.calculateButton = QPushButton("sum", self)
        self.numberLabel = QLabel("not calculated", self)
        # layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.dbBoxes["A"])
        layout.addWidget(self.dbBoxes["B"])
        layout.addWidget(self.calculateButton)
        layout.addWidget(self.numberLabel)


class DataCalcApp(BaseApp):
    def __init__(self, name: str, tables: list=["A", "B"]):
        super().__init__(name)
        self.tables = tables
        self.dbs = {"": ""}
        self.dbNames = {"A": "", "B": ""}
        self.viewerFrame = ViewerFrame()
        # connect signals to slots
        self.received.connect(self.updateDB)
        for dbBox in self.viewerFrame.dbBoxes.values():
            dbBox.currentIndexChanged.connect(self.setDB)
        self.viewerFrame.calculateButton.clicked.connect(self.calculateSum)

    def frames(self):
        """Gets frames for which are managed by the app.

        Returns:
            A tuple containing frames for showing.
        """
        return (self.viewerFrame,)
    
    @pyqtSlot(str, str)
    def updateDB(self, busName: str, msg: str):
        """Updates the database list using the transferred message.

        This is a slot for received signal.

        Args:
            busName: A name of the bus that transfered the signal.
            msg: An input message to be transferred through the bus.
              The structure follows the message protocol of DBMgrApp.
        """
        if busName == "dbbus":
            try:
                msg = json.loads(msg)
            except json.JSONDecodeError as e:
                print(f"apps.datacalc.updateDB(): {e!r}")
            else:
                orgDbNames = self.dbNames.copy()
                self.dbs = {"": ""}
                for dbBox in self.viewerFrame.dbBoxes.values():
                    dbBox.clear()
                    dbBox.addItem("")
                for db in msg.get("db", ()):
                    if all(key in db for key in ("name", "path")):
                        name, path = db["name"], db["path"]
                        self.dbs[name] = path
                        for dbBox in self.viewerFrame.dbBoxes.values():
                            dbBox.addItem(name)
                    else:
                        print(f"The message was ignored because "
                              f"the database {db} has no such key; name or path.")
                for name, orgDbName in orgDbNames.items():
                    if orgDbName in self.dbs:
                        self.viewerFrame.dbBoxes[name].setCurrentText(orgDbName)
        else:
            print(f"The message was ignored because "
                  f"the treatment for the bus {busName} is not implemented.")

    @pyqtSlot()
    def setDB(self):
        """Sets the databases to fetch the numbers."""
        for name, dbBox in self.viewerFrame.dbBoxes.items():
            self.dbNames[name] = dbBox.currentText()

    @pyqtSlot()
    def calculateSum(self):
        """Calculates and shows the sum of two values when the button is clicked."""
