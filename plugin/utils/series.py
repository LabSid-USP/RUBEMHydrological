import os
from glob import glob


def splitDirFilePrefix(filePath):
    """Split directory path and file prefix from file path.

    Adds trailing separator to directory path (OS-agnostic).

    :param filePath: File path.
    :filePath type: String

    :returns: Directory path with trailing separator and file prefix
    :rtype: str, str
    """
    # Split directory path from file name with extension
    directoryPath, fileName = os.path.split(filePath)
    # Split extension from file name
    filePrefix, _ = os.path.splitext(fileName)
    return f"{directoryPath}/", "".join(filter(str.isalpha, filePrefix))


def getFirstFileNameMapSeries(path):
    """Return the first PCRaster map-series file under ``path``.

    ``path`` may omit a trailing separator. Joining with the ``*.0*``
    pattern avoids treating ``data/landuse`` as the file prefix
    ``data/landuse*.0*``.
    """
    if not path:
        return ""
    file_list = sorted(glob(os.path.join(path, "*.0*")))
    if file_list:
        return os.path.normpath(file_list[0])
    return ""
