try:
    from qgis.PyQt.QtWidgets import QFileDialog
except ImportError:
    from PyQt5.QtWidgets import QFileDialog


def getDirectoryPath(self, caption):
    """Get the path of an existing directory using QFileDialog\n
    and returns it.

    :param caption: This is the title of the file selection window.
    :type caption: String

    :returns: Directory path selected by the user.
    :rtype: String
    """
    directoryPath = QFileDialog.getExistingDirectory(
        self, caption=caption, directory=self.lastOpenedDirectory
    )
    if directoryPath:
        return f"{directoryPath}/"


def getFilePath(self, caption, filter, selectedFilter=""):
    """Get the path of an existing file using QFileDialog and returns it.

    :param caption: This is the title of the file selection window.
    :type caption: String

    :param filter: Only files that match the given filter are shown.
    :type filter: String

    :returns: File path selected by the user.
    :rtype: String
    """
    filePath, _ = QFileDialog.getOpenFileName(
        self,
        caption=caption,
        directory=self.lastOpenedDirectory,
        filter=filter,
        initialFilter=selectedFilter,
    )
    if filePath:
        return filePath
