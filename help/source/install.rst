Installing RUBEM Hydrological Plugin
====================================

From the QGIS Plugin Manager
----------------------------

To install the plugin, you use **QGIS Plugin Manager**.

1. Go to the ``Plugin`` menu and choose
   ``Manage and Install Plugins...``
2. Search for ``RUBEM Hydrological`` in the search box of the dialog
   in the ``All`` tab
3. Select the ``RUBEM Hydrological`` plugin and click ``Install``

--------------

From the repository
-------------------

If you are adventurous and would like to get the latest code of the
plugin, you can install it directly from the repository. The repository
is on `Github <https://github.com/LabSid-USP/RUBEMHydrological>`__.
There are 3 ways to get the plugin:

1. Download the latest release zip file from `GitHub Releases
   <https://github.com/LabSid-USP/RUBEMHydrological/releases>`__. Open QGIS and go to the ``Plugin`` menu and choose
   ``Manage and Install Plugins...``. Choose ``Install from ZIP`` and then choose the zip file of the latest release.

or

2. Download the main branch as zip file on `GitHub main zip
   <https://github.com/LabSid-USP/RUBEMHydrological/archive/refs/heads/main.zip>`__. Extract the zip, and copy the extracted root directory into your
   local QGIS plugin directory:

   -  on Linux:
      ``~/.local/share/QGIS/QGIS3/profiles/default/python/plugins``,
   -  on Windows:
      ``C:\Users\{username}\AppData\Roaming\QGIS\QGIS3\profiles\default\\python\plugins``

or

3. Use git to clone the repository in your plugin directory, or clone it
   somewhere else and add a symbolic link to it in your plugin
   directory.

--------------

Locating and starting the plugin in the QGIS GUI
------------------------------------------------

The plugin can be started from the submenu
of the *Plugins* menu (*Plugins-> RUBEM Hydrological -> RUBEM Hydrological*).
