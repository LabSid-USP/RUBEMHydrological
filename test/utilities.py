"""Legacy helpers kept for documentation links.

Integration tests now use pytest-qgis fixtures (``qgis_app``, ``qgis_iface``)
and pytest-qt (``qtbot``). Prefer those over this module.
"""

from __future__ import annotations

import warnings


def get_qgis_app():
    """Deprecated: use pytest-qgis fixtures instead of this bootstrap.

    Historically returned ``(QgsApplication, canvas, iface, parent)``. The old
    interface stub imported ``QgsMapLayerRegistry`` / ``QgsMapCanvasLayer`` and
    is incompatible with QGIS 4.
    """
    warnings.warn(
        "test.utilities.get_qgis_app is deprecated; use pytest-qgis fixtures "
        "(qgis_app, qgis_iface) and pytest-qt (qtbot).",
        DeprecationWarning,
        stacklevel=2,
    )
    return None, None, None, None
