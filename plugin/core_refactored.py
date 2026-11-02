"""Refactored RUBEM Hydrological plugin core module.

This module contains the main plugin class with modern Python practices:
- Type hints for all methods and attributes
- Comprehensive docstrings
- Better resource management
- Integration with logging system
- Proper error handling
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

try:
    from qgis.PyQt.QtCore import QCoreApplication, QSettings, QTranslator
    from qgis.PyQt.QtGui import QIcon
    from qgis.PyQt.QtWidgets import QAction
    from qgis.core import QgsApplication
except ImportError:
    from PyQt5.QtCore import QCoreApplication, QSettings, QTranslator
    from PyQt5.QtGui import QIcon
    from PyQt5.QtWidgets import QAction
    # QgsApplication won't be available outside QGIS

from plugin.logging import get_logger, PluginLogger
from plugin.exceptions import PluginInitializationError
from plugin.__version__ import __version__, __qgis_minimum_version__

if TYPE_CHECKING:
    from qgis.gui import QgisInterface

logger = get_logger(__name__)


class RUBEMHydrological:
    """QGIS Plugin Implementation for RUBEM Hydrological Model.

    This plugin provides a graphical interface for configuring and running
    the RUBEM (Rainfall rUnoff Balance Enhanced Model) distributed hydrological
    model within QGIS.

    The plugin follows QGIS plugin best practices and supports:
    - Configuration management with multiple formats
    - Asynchronous model execution
    - Result visualization and analysis
    - Internationalization (i18n)

    Attributes:
        iface: Reference to the QGIS interface.
        plugin_dir: Plugin installation directory.
        translator: Qt translator for internationalization.
        actions: List of registered plugin actions.
        menu: Plugin menu name.
        first_start: Flag indicating if plugin is starting for the first time.
        dlg: Main plugin dialog window (created on first use).
    """

    def __init__(self, iface: QgisInterface) -> None:
        """Initialize the RUBEM Hydrological plugin.

        Args:
            iface: Reference to the QGIS interface instance.

        Raises:
            PluginInitializationError: If plugin initialization fails.
        """
        logger.info(f"Initializing RUBEM Hydrological plugin v{__version__}")

        try:
            # Store reference to QGIS interface
            self.iface = iface

            # Initialize plugin directory
            self.plugin_dir = Path(__file__).parent
            logger.debug(f"Plugin directory: {self.plugin_dir}")

            # Setup logging to file
            log_dir = self._get_log_directory()
            PluginLogger.setup(log_dir=log_dir, level="INFO")
            logger.info(f"Logging configured in: {log_dir}")

            # Initialize locale and translator
            self.translator: QTranslator | None = None
            self._setup_translator()

            # Initialize instance attributes
            self.actions: list[QAction] = []
            self.menu = self.tr("&RUBEM Hydrological")
            self.first_start: bool | None = None
            self.dlg: Any = None  # Type will be RUBEMHydrologicalDialog

            logger.info("Plugin initialization completed successfully")

        except Exception as e:
            logger.exception("Failed to initialize plugin")
            raise PluginInitializationError(
                "Plugin initialization failed", details={"error": str(e)}
            ) from e

    def _get_log_directory(self) -> Path:
        """Get or create the plugin log directory.

        Returns:
            Path to the log directory.
        """
        # Use QGIS profile directory if available
        try:
            profile_path = QgsApplication.qgisSettingsDirPath()
            log_dir = Path(profile_path) / "logs" / "rubem_hydrological"
        except Exception:
            # Fallback to plugin directory
            log_dir = self.plugin_dir / "logs"

        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir

    def _setup_translator(self) -> None:
        """Setup Qt translator for internationalization.

        Loads the appropriate translation file based on user's locale settings.
        """
        locale_value = QSettings().value("locale/userLocale")
        if not locale_value:
            logger.warning("No locale setting found, using default")
            return

        locale = locale_value[:2]  # Get language code (e.g., 'pt' from 'pt_BR')
        logger.debug(f"Loading translations for locale: {locale}")

        locale_path = self.plugin_dir / "i18n" / f"RUBEMHydrological_{locale}.qm"

        if locale_path.exists():
            self.translator = QTranslator()
            if self.translator.load(str(locale_path)):
                QCoreApplication.installTranslator(self.translator)
                logger.info(f"Loaded translations from: {locale_path}")
            else:
                logger.warning(f"Failed to load translations from: {locale_path}")
        else:
            logger.debug(f"No translation file found for locale: {locale}")

    def tr(self, message: str) -> str:
        """Translate a string using Qt translation API.

        Args:
            message: String to be translated.

        Returns:
            Translated version of the message.
        """
        return QCoreApplication.translate("RUBEMHydrological", message)

    def add_action(
        self,
        icon_path: str,
        text: str,
        callback: Any,
        enabled_flag: bool = True,
        add_to_menu: bool = True,
        add_to_toolbar: bool = True,
        status_tip: str | None = None,
        whats_this: str | None = None,
        parent: Any = None,
    ) -> QAction:
        """Add a toolbar icon and menu item to the QGIS interface.

        Args:
            icon_path: Path to the icon for this action.
            text: Text for menu items and tooltips.
            callback: Function to be called when action is triggered.
            enabled_flag: Whether the action should be enabled by default.
            add_to_menu: Whether to add action to the menu.
            add_to_toolbar: Whether to add action to the toolbar.
            status_tip: Optional status bar tip text.
            whats_this: Optional "What's This" help text.
            parent: Parent widget for the action.

        Returns:
            The created QAction instance.
        """
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip:
            action.setStatusTip(status_tip)

        if whats_this:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)
            logger.debug(f"Added toolbar icon: {text}")

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)
            logger.debug(f"Added menu item: {text}")

        self.actions.append(action)
        return action

    def initGui(self) -> None:
        """Create the menu entries and toolbar icons inside the QGIS GUI.

        This method is called by QGIS when the plugin is loaded.
        """
        logger.info("Initializing GUI")

        icon_path = ":/imgBase/images/icon.png"
        self.add_action(
            icon_path,
            text=self.tr("RUBEM Hydrological"),
            callback=self.run,
            parent=self.iface.mainWindow(),
            status_tip=self.tr("Open RUBEM Hydrological Model Configuration"),
            whats_this=self.tr(
                "Configure and run the RUBEM distributed hydrological model"
            ),
        )

        self.first_start = True
        logger.info("GUI initialization completed")

    def unload(self) -> None:
        """Remove the plugin menu items and icons from QGIS GUI.

        This method is called by QGIS when the plugin is unloaded.
        """
        logger.info("Unloading plugin")

        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)

        # Clean up dialog if it exists
        if self.dlg is not None:
            self.dlg.close()
            self.dlg.deleteLater()
            self.dlg = None

        # Remove translator
        if self.translator:
            QCoreApplication.removeTranslator(self.translator)

        logger.info("Plugin unloaded successfully")

    def run(self) -> None:
        """Run method that opens the plugin dialog.

        This method is called when the plugin action is triggered.
        It creates the dialog on first run and then shows it.
        """
        logger.info("Running plugin")

        try:
            # Create dialog only once (lazy loading)
            if self.first_start:
                logger.debug("Creating plugin dialog for the first time")
                self.first_start = False

                # Import here to avoid circular imports and speed up plugin loading
                try:
                    from plugin.dialog import RUBEMHydrologicalDialog
                except ImportError:
                    from dialog import RUBEMHydrologicalDialog

                self.dlg = RUBEMHydrologicalDialog(self.iface)
                logger.info("Dialog created successfully")

            # Show the dialog
            logger.debug("Showing dialog")
            self.dlg.show()
            self.dlg.raise_()
            self.dlg.activateWindow()

            # Run the dialog event loop
            result = self.dlg.exec_()

            if result:
                logger.info("Dialog closed with OK")
            else:
                logger.info("Dialog closed with Cancel")

        except Exception as e:
            logger.exception("Error running plugin dialog")
            # Show error to user
            from qgis.PyQt.QtWidgets import QMessageBox

            QMessageBox.critical(
                self.iface.mainWindow(),
                self.tr("RUBEM Hydrological Error"),
                self.tr(
                    "An error occurred while opening the plugin:\n\n{}"
                ).format(str(e)),
            )


def classFactory(iface: QgisInterface) -> RUBEMHydrological:
    """Factory function required by QGIS to create the plugin instance.

    Args:
        iface: Reference to the QGIS interface.

    Returns:
        Instance of the RUBEMHydrological plugin.
    """
    return RUBEMHydrological(iface)
