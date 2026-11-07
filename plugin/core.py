# RUBEM Hydrological is a QGIS plugin that assists in setup the RUBEM model:
# Copyright (C) 2021-2024 LabSid PHA EPUSP

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Contact: rubem.hydrological@labsid.eng.br

"""RUBEM Hydrological plugin main working code.

Contains all the information about the actions of the plugin and the main code.
"""

import os

from qgis.PyQt.QtCore import QCoreApplication, QResource, QSettings, Qt, QTranslator
from qgis.PyQt.QtGui import QAction, QIcon

try:
    from .dialog import RUBEMHydrologicalDialog
except ImportError as _exc:
    # Only fall back to the bare name when the relative import itself is
    # unavailable. A failure inside the dialog (e.g. a missing third-party
    # module), including ImportError with name is None, must keep its own
    # message instead of surfacing as a missing dialog module.
    if _exc.name is None or not (
        _exc.name == "dialog" or _exc.name.endswith(".dialog")
    ):
        raise
    from dialog import RUBEMHydrologicalDialog


class RUBEMHydrological:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Initialize plugin setup.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # Root-level catalogs: full QGIS locale, then the two-letter fallback.
        locale_value = QSettings().value("locale/userLocale") or ""
        locale_full = str(locale_value).replace("-", "_").split(".")[0]
        i18n_dir = os.path.join(os.path.dirname(self.plugin_dir), "i18n")
        locale_candidates = []
        if locale_full:
            locale_candidates.append(locale_full)
            language = locale_full.split("_", 1)[0]
            if language and language != locale_full:
                locale_candidates.append(language)
        self.translator = None
        for locale in locale_candidates:
            locale_path = os.path.join(i18n_dir, f"RUBEMHydrological_{locale}.qm")
            if not os.path.exists(locale_path):
                continue
            translator = QTranslator()
            if translator.load(locale_path):
                self.translator = translator
                QCoreApplication.installTranslator(self.translator)
                break

        # Declare instance attributes
        self.actions = []
        self._resources_registered = False
        self._resources_path = os.path.join(
            self.plugin_dir, "gui", "generated", "resources.rcc"
        )
        self.menu = self.tr("&RUBEM Hydrological")

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate("RUBEMHydrological", message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
    ):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            # metadata.txt category=Raster — match the Raster menu for
            # plugins.qgis.org placement recommendations.
            self.iface.addPluginToRasterMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        # Register Qt resources before any QIcon is created from a
        # ":/..." path. Track how many successful registers this plugin
        # made so unload can drain the Qt refcount (the dialog may also
        # register once if the icon path is still missing).
        resource_path = getattr(self, "_resources_path", None) or os.path.join(
            self.plugin_dir, "gui", "generated", "resources.rcc"
        )
        self._resources_path = resource_path
        self._resources_register_count = getattr(self, "_resources_register_count", 0)
        if QResource.registerResource(resource_path):
            self._resources_register_count += 1
        icon_path = ":/imgBase/images/icon.png"
        self.add_action(
            icon_path,
            text=self.tr("RUBEM Hydrological"),
            callback=self.run,
            parent=self.iface.mainWindow(),
        )

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Remove the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginRasterMenu(self.tr("&RUBEM Hydrological"), action)
            self.iface.removeToolBarIcon(action)
        resource_path = getattr(self, "_resources_path", None) or os.path.join(
            self.plugin_dir, "gui", "generated", "resources.rcc"
        )
        # Drain every register this process still holds for our .rcc.
        remaining = getattr(self, "_resources_register_count", 0)
        while remaining > 0 and QResource.unregisterResource(resource_path):
            remaining -= 1
        # Also clear a leftover dialog registration, if any.
        while QResource.unregisterResource(resource_path):
            pass
        self._resources_register_count = 0

    def run(self):
        """Run method that performs all the real work."""
        # Create the dialog with elements (after translation) and keep ref
        # Only create GUI ONCE in callback, so that it will only load when the
        # plugin is started
        if self.first_start:
            self.first_start = False
            self.dlg = RUBEMHydrologicalDialog(self.iface)

        # configure top window tile
        self.dlg.setWindowFlags(
            Qt.WindowType.WindowSystemMenuHint
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowContextHelpButtonHint
            | Qt.WindowType.WindowCloseButtonHint
        )

        # show the dialog
        self.dlg.show()
        self.dlg.adjustSize()
        # Run the dialog event loop
        result = self.dlg.exec()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
