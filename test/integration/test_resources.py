"""Resource bundle smoke tests (icons referenced by the live UI)."""

from __future__ import annotations

import pytest
from qgis.PyQt.QtGui import QIcon

pytestmark = pytest.mark.integration

ICON_PATHS = (
    ":/imgBase/images/icon.png",
    ":/imgBase/images/labsid.png",
    ":/imgBase/images/epusp.png",
    ":/imgBase/images/adp.png",
    ":/iconMenu/images/qgis-default-theme/mActionFileNew.svg",
    ":/iconMenu/images/qgis-default-theme/mActionFileOpen.svg",
    ":/iconMenu/images/qgis-default-theme/mActionFileSave.svg",
    ":/iconMenu/images/qgis-default-theme/mActionFileSaveAs.svg",
    ":/iconMenu/images/qgis-default-theme/mActionHelpContents.svg",
    ":/iconMenu/images/qgis-default-theme/pluginNew.svg",
)


@pytest.mark.parametrize("path", ICON_PATHS)
def test_resource_icon_is_available(registered_resources, path: str) -> None:
    """Each packaged icon resolves after the ``.rcc`` is registered."""
    icon = QIcon(path)
    assert not icon.isNull(), path
