"""QGIS HIG dialog chrome: scroll pages, footer button box, size policies."""

from qgis.PyQt.QtCore import QCoreApplication, Qt
from qgis.PyQt.QtWidgets import (
    QDialogButtonBox,
    QFrame,
    QScrollArea,
    QSizePolicy,
    QWidget,
)


def _wrap_tab_in_scroll(tab: QWidget) -> None:
    """Wrap a tab page's existing layout in a resizable ``QScrollArea``.

    Settings / Soil / Land Use already ship with a scroll area in the ``.ui``.
    """
    layout = tab.layout()
    if layout is None:
        return
    if layout.count() == 1:
        only = layout.itemAt(0).widget()
        if isinstance(only, QScrollArea):
            return

    scroll = QScrollArea(tab)
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    inner = QWidget()
    inner_layout = type(layout)(inner)
    inner_layout.setContentsMargins(0, 0, 0, 0)
    while layout.count():
        item = layout.takeAt(0)
        if item.widget() is not None:
            inner_layout.addWidget(item.widget())
        elif item.layout() is not None:
            inner_layout.addLayout(item.layout())
        elif item.spacerItem() is not None:
            inner_layout.addItem(item)
    scroll.setWidget(inner)
    layout.addWidget(scroll)


def _reparent_progress_into_footer(dialog) -> None:
    """Move ``progressBar`` out of the Run tab into the dialog footer row."""
    progress = dialog.progressBar
    parent_layout = (
        progress.parentWidget().layout() if progress.parentWidget() else None
    )
    if parent_layout is not None:
        parent_layout.removeWidget(progress)

    footer = dialog.horizontalLayout_dialogButtons
    # Insert progress before the button box (index 0).
    footer.insertWidget(0, progress, stretch=1)


def setup_hig_chrome(dialog) -> None:
    """Apply HIG chrome after ``setupUi``: scrolls, Run button, size policies."""
    dialog.setMaximumHeight(580)
    dialog.tabWidget.setSizePolicy(
        QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
    )

    for name in (
        "tab_Climate",
        "tab_ModelParam",
        "tab_Run",
        "tab_Results",
    ):
        tab = getattr(dialog, name, None)
        if tab is not None:
            _wrap_tab_in_scroll(tab)

    for name in (
        "textBrowser_log",
        "treeView_MapSeriesData",
        "treeView_TimeSeriesData",
    ):
        widget = getattr(dialog, name, None)
        if widget is not None:
            widget.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
            widget.setMinimumHeight(0)

    _reparent_progress_into_footer(dialog)

    # Inline translate so pylupdate6 keeps the RUBEMHydrological context.
    dialog.btn_Run = dialog.button_box.addButton(
        QCoreApplication.translate("RUBEMHydrological", "&Run"),
        QDialogButtonBox.ButtonRole.ActionRole,
    )
    dialog.btn_Run.setToolTip(
        QCoreApplication.translate(
            "RUBEMHydrological", "Run the model with defined configuration"
        )
    )
    dialog.btn_Run.setAutoDefault(False)
    dialog.btn_Run.setDefault(False)
    dialog.btn_Run.clicked.connect(dialog.setRunState)

    dialog.btn_Close = dialog.button_box.button(QDialogButtonBox.StandardButton.Close)
    dialog.btn_Cancel = dialog.btn_Close  # legacy alias used by unit fakes
    dialog.button_box.rejected.connect(dialog.reject)

    help_btn = dialog.button_box.button(QDialogButtonBox.StandardButton.Help)
    if help_btn is not None:
        help_btn.clicked.connect(dialog.helpHandler)

    for name in (
        "pushButton_NewProject",
        "pushButton_OpenProject",
        "pushButton_SaveProject",
        "pushButton_SaveAsProject",
        "toolButton_Help",
        "toolButton_About",
    ):
        button = getattr(dialog, name, None)
        if button is not None and hasattr(button, "setAutoDefault"):
            button.setAutoDefault(False)
            if hasattr(button, "setDefault"):
                button.setDefault(False)
