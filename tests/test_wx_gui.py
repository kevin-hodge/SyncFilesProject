"""Tests wx_gui

Author: Kevin Hodge
"""

import unittest
from syncfiles.wx_gui import WxGUI


class WxGUITestCase(unittest.TestCase):
    def test_init(self) -> None:
        WxGUI()
