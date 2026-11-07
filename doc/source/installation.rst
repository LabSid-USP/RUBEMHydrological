Installation
============

The plugin requires the user to have QGIS 4 installed (we recommend the latest QGIS 4.2 release). Model runs also need **PCRaster** and **GDAL** (``osgeo``) from the QGIS/OSGeo environment (conda, OSGeo4W, or system packages — not pip). Saving or opening a project needs ``pydantic`` (>=2.11), ``humanize`` (>=4) and ``python-dateutil`` (>=2); when those pure-Python packages are missing the plugin prompts before installing them into an isolated environment.

The user can download the latest version of RUBEM Hydrological from `GitHub <https://github.com/LabSid-USP/RUBEMHydrological/releases>`__ or directly from the Official QGIS Plugin repository.

.. caution::
   
   The submission of the RUBEM Hydrological plugin to the QGIS Official Plugins repository is still under evaluation by the team.

From the repository
-------------------

If you would like to get the latest code of the plugin, you can download it directly from the `repository <https://github.com/LabSid-USP/RUBEMHydrological>`__. 

1. Download the latest release zip file from the `releases page <https://github.com/LabSid-USP/RUBEMHydrological/releases>`__;
2. Open QGIS and go to the ``Plugin`` menu;
3. Choose Manage and ``Install Plugins...``;
4. Choose ``Install from ZIP``;
5. Choose the downloaded zip file;
6. Click ``Install Plugin``;
7. The successful message will show if the RUBEM Hydrological is installed.

..  youtube:: F8zx9So2nrI
    :width: 100%

---------

From the QGIS Plugin Manager
----------------------------

To install the plugin, you use **QGIS Plugin Manager**.

1. Go to the ``Plugin`` menu and choose ``Manage and Install Plugins...``;
2. Search for ``RUBEM Hydrological`` in the search box of the dialog in the ``All`` tab;
3. Select the ``RUBEM Hydrological`` plugin and click ``Install``.

--------------

Locating and starting the plugin in the QGIS GUI
------------------------------------------------

The plugin can be started from the *Raster* menu
(``Raster -> RUBEM Hydrological -> RUBEM Hydrological``), matching ``category=Raster`` in ``metadata.txt``.
