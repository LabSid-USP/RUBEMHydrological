# coding=utf-8
"""Dialog test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = "rubem.hydrological@labsid.eng.br"
__date__ = "2021-05-19"
__copyright__ = "Copyright 2021, LabSid"

import unittest
from test.utilities import get_qgis_app

from qgis.PyQt.QtWidgets import QApplication, QDialog, QDialogButtonBox

from plugin.dialog import RUBEMHydrologicalDialog


QGIS_APP = get_qgis_app()


class RUBEMHydrologicalDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        self.app = QApplication.instance() or QApplication([])
        self.dialog = RUBEMHydrologicalDialog(None)

    def tearDown(self):
        """Runs after each test."""
        self.dialog = None

    def test_dialog_has_button_box_with_close(self):
        """HIG footer exposes Close (RejectRole), not Ok."""
        close = self.dialog.button_box.button(QDialogButtonBox.StandardButton.Close)
        self.assertIsNotNone(close)
        ok = self.dialog.button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.assertIsNone(ok)
        self.assertFalse(self.dialog.btn_Run.isEnabled())

    def test_dialog_close_rejects_when_idle(self):
        """Close routes through reject when no project/run is active."""
        button = self.dialog.button_box.button(QDialogButtonBox.StandardButton.Close)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.DialogCode.Rejected)


if __name__ == "__main__":
    suite = unittest.makeSuite(RUBEMHydrologicalDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
