"""
Module for testing swift package.
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
import importlib
from collections.abc import Iterable

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication

from swift.app import BaseApp
from swift.swift import Swift, AppInfo, BusInfo, _read_setup_file

class AppTest(unittest.TestCase):
    """Unit test for app.py."""

    def setUp(self):
        """Create an app every time."""
        self.app = BaseApp("name")

    def test_init(self):
        """Test if fields are initialized as constructor arguments."""
        self.assertEqual(self.app.name, "name")

    def test_set_parent(self):
        """Test if a parent constructor argument can be set as a QObject."""
        BaseApp("name", QObject())

    def test_frames(self):
        """Test BaseApp.frames()."""
        self.assertIsInstance(self.app.frames(), Iterable)


class SwiftTest(unittest.TestCase):
    """Unit test for swift.py"""

    appInfos = {
        "app1": AppInfo(
            module="module1",
            cls="cls1",
            path="path1",
            show=False,
            pos="left",
            bus=["bus1", "bus2"],
            args={"arg1": "value1"}
        ),
        "app2": AppInfo(
            module="module2",
            cls="cls2"
        )
    }

    appDicts = {
        "app1": {
            "module": "module1",
            "cls": "cls1",
            "path": "path1",
            "show": False,
            "pos": "left",
            "bus": ["bus1", "bus2"],
            "args": {"arg1": "value1"}
        },
        "app2": {
            "module": "module2",
            "cls": "cls2"
        }
    }

    busInfos = {
        "bus1": BusInfo(
            timeout=5.0
        ),
        "bus2": BusInfo()
    }

    busDicts = {
        "bus1": {
            "timeout": 5.0
        },
        "bus2": {}
    }

    def setUp(self):
        """Create a QApplication and a Swift object every time."""
        importlib.import_module = MagicMock()
        for name, appInfo in SwiftTest.appInfos.items():
            importlib.import_module.return_value.setattr(appInfo.cls, BaseApp(name))
        # start GUI
        self.qapp = QApplication(sys.argv)
        self.swift = Swift(SwiftTest.appInfos, SwiftTest.busInfos)

    def test_init(self):
        pass

    @patch("builtins.open")
    @patch("json.load", return_value={"app": appDicts, "bus": busDicts})
    def test_read_setup_file(self, mock_open, mock_load):
        """Test _read_setup_file()."""
        self.assertEqual(_read_setup_file(""), (SwiftTest.appInfos, SwiftTest.busInfos))
        mock_open.assert_called_once()
        mock_load.assert_called_once()


if __name__ == "__main__":
    unittest.main()
