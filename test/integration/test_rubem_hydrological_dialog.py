"""GUI integration tests for the live RUBEM Hydrological dialog."""

from __future__ import annotations

import pytest
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox

pytestmark = pytest.mark.integration


def test_dialog_has_close_help_and_gated_run(dialog) -> None:
    """Footer exposes Close/Help; Run starts disabled until a project exists."""
    box = dialog.button_box
    assert box.button(QDialogButtonBox.StandardButton.Close) is not None
    assert box.button(QDialogButtonBox.StandardButton.Help) is not None
    assert box.button(QDialogButtonBox.StandardButton.Ok) is None
    assert dialog.btn_Run is not None
    assert not dialog.btn_Run.isEnabled()


def test_dialog_close_rejects_when_idle(dialog, qtbot) -> None:
    """Close routes through reject when no project/run is active."""
    dialog.show()
    qtbot.waitExposed(dialog)
    close = dialog.button_box.button(QDialogButtonBox.StandardButton.Close)
    with qtbot.waitSignal(dialog.finished, timeout=5000):
        close.click()
    assert dialog.result() == QDialog.DialogCode.Rejected


def test_escape_rejects_when_idle(dialog, qtbot) -> None:
    """Escape uses the same ``reject`` / ``_may_leave_dialog`` path as Close."""
    from qgis.PyQt.QtCore import Qt

    dialog.show()
    qtbot.waitExposed(dialog)
    with qtbot.waitSignal(dialog.finished, timeout=5000):
        qtbot.keyClick(dialog, Qt.Key.Key_Escape)
    assert dialog.result() == QDialog.DialogCode.Rejected


def test_footer_owns_progress_bar(dialog) -> None:
    """Progress bar is reparented next to the dialog-level button box."""
    assert dialog.progressBar.parentWidget() is dialog
    assert dialog.horizontalLayout_dialogButtons.indexOf(dialog.progressBar) == 0
