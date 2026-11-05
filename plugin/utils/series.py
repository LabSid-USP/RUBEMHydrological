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


def series_file_prefix(file_name: str) -> str:
    """Alphabetic map-series prefix, matching :func:`splitDirFilePrefix`."""
    file_prefix, _ = os.path.splitext(os.path.basename(file_name))
    return "".join(filter(str.isalpha, file_prefix))


def getFirstFileNameMapSeries(path, prefix: str = ""):
    """Return the first PCRaster map-series file under ``path``.

    ``path`` may omit a trailing separator. Joining with the ``*.0*``
    pattern avoids treating ``data/landuse`` as the file prefix
    ``data/landuse*.0*``. When ``prefix`` is set, only maps whose
    alphabetic prefix matches are considered, so loading the GUI cannot
    replace a stored series prefix with another map that sorts first.
    """
    if not path:
        return ""
    file_list = sorted(glob(os.path.join(path, "*.0*")))
    if prefix:
        file_list = [
            candidate
            for candidate in file_list
            if series_file_prefix(candidate) == prefix
        ]
    if file_list:
        return os.path.normpath(file_list[0])
    return ""
