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
    """[summary].

    :param path: [description]
    :type path: [type]

    :return: [description]
    :rtype: [type]
    """
    pattern = "*.0*"
    fileList = glob(f"{path}{pattern}")
    if fileList:
        return os.path.normpath(fileList[0])
    else:
        return ""