from qgis.PyQt.QtWidgets import QMessageBox

# TODO: docstring
def getUserRetSaveCurProj(self):
    """[summary].

    :return: [description]
    :rtype: [type]
    """
    response = QMessageBox.warning(
        self,
        "RUBEM Hydrological",
        "Do you want to save the current project?\n\n"
        "Your changes will be lost if you don't save them.",
        QMessageBox.StandardButton.Save
        | QMessageBox.StandardButton.Discard
        | QMessageBox.StandardButton.Cancel,
        QMessageBox.StandardButton.Save,
    )
    return response


def getUserRetQGISCurProj(self):
    """[summary].

    :return: [description]
    :rtype: [type]
    """
    response = QMessageBox.warning(
        self,
        "RUBEM Hydrological",
        "Do you want to proceed without saving the current QGIS project?\n\n"
        "Your changes will be lost if you don't save them.",
        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
        QMessageBox.StandardButton.Ok,
    )
    return response


def getUserRetDirNotEmpty(self):
    """[summary].

    :return: [description]
    :rtype: [type]
    """
    response = QMessageBox.warning(
        self,
        "RUBEM Hydrological",
        "The selected output directory is not empty. Do you want to proceed using this output directory?\n\n"
        "Files in this directory may be removed and/or altered.",
        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
        QMessageBox.StandardButton.Ok,
    )
    return response
