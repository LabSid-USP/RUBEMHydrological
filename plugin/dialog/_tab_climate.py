try:
    from ..utils.series import splitDirFilePrefix
except ImportError:
    from utils.series import splitDirFilePrefix

# Climate tab
def setPrecipitationSeriesFilePath(self):
    """Define the project's Precipitation folder file.

    Alsochange the lineEdt_Precipitation field with the selected file
    path and define the prec file prefix.

    :Slot signal: clicked
    :Signal sender: btn_Precipitation
    """
    filePath = self.getFilePath(
        caption="Select Rainfall Series File", filter="(*.001);;All Files(*)"
    )
    if filePath:
        tmpDir, tmpPrefix = splitDirFilePrefix(filePath)
        self.config.set("DIRECTORIES", "prec", tmpDir)
        self.config.set("FILENAME_PREFIXES", "prec_prefix", tmpPrefix)
        self.lineEdt_Precipitation.setText(filePath)


def setEvapotranspirationSeriesFilePath(self):
    """Define the project's Evapotranspiration folder file.

    Also updates the lineEdt_EvapoTranspiration field with the selected
    file path and define the etp file prefix.

    :Slot signal: clicked
    :Signal sender: btn_EvapoTranspiration
    """
    filePath = self.getFilePath(
        caption="Select Potential Evapotranspiration Series File",
        filter="(*.001);;All Files(*)",
    )
    if filePath:
        tmpDir, tmpPrefix = splitDirFilePrefix(filePath)
        self.config.set("DIRECTORIES", "etp", tmpDir)
        self.config.set("FILENAME_PREFIXES", "etp_prefix", tmpPrefix)
        self.lineEdt_EvapoTranspiration.setText(filePath)


def setKpSeriesFilePath(self):
    """Define the project's Class A Pan Coefficient (Kp) folder file.

    Also updates the lineEdt_PanCoefficientKp field with the selected file
    path and define the Kp file prefix.

    :Slot signal: clicked
    :Signal sender: btn_PanCoefficientKp
    """
    filePath = self.getFilePath(
        caption="Select Class A Pan Coefficient (Kp) Series File",
        filter="(*.001);;All Files(*)",
    )
    if filePath:
        tmpDir, tmpPrefix = splitDirFilePrefix(filePath)
        self.config.set("DIRECTORIES", "kp", tmpDir)
        self.config.set("FILENAME_PREFIXES", "kp_prefix", tmpPrefix)
        self.lineEdt_PanCoefficientKp.setText(filePath)


def setRainyDaysSeriesFilePath(self):
    """Define the project's Rainy Days file.

    Also updates the lineEdt_RainyDays field with the selected file path.

    :Slot signal: clicked
    :Signal sender: btn_RainyDays
    """
    filePath = self.getFilePath(
        caption="Select Rainy Days Series File",
        filter="CSV files (*.csv);;Text files (*.txt)",
        selectedFilter="Text files (*.txt)",
    )
    if filePath:
        self.config.set("TABLES", "rainydays", filePath)
        self.lineEdt_RainyDays.setText(filePath)
