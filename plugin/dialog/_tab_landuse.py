# Land Use tab
# Land Use Series
def setLandUseSeriesFilePath(self):
    """Define the project's Land Use Series file folder.

    Also updates the lineEdt_LandUseSeries field with the selected file
    path and set land use file prefix.

    :Slot signal: clicked
    :Signal sender: btn_LandUseSeries
    """
    filePath = self.getFilePath(
        caption="Select Land Use Series File", filter="(*.001);;All Files(*)"
    )
    if filePath:
        tmpDir, tmpPrefix = self.splitDirFilePrefix(filePath)
        self.config.set("DIRECTORIES", "landuse", tmpDir)
        self.config.set("FILENAME_PREFIXES", "landuse_prefix", tmpPrefix)
        self.lineEdt_LandUseSeries.setText(filePath)


# NDVI
def setNDVISeriesFilePath(self):
    """Define the project's NDVISeries file folder.

    Also updates the lineEdt_NDVISeries field with the selected file
    path and define the ndvi file prefix.

    :Slot signal: clicked
    :Signal sender: btn_NDVISeries
    """
    filePath = self.getFilePath(
        caption="Select NDVI Series File", filter="(*.001);;All Files(*)"
    )
    if filePath:
        tmpDir, tmpPrefix = self.splitDirFilePrefix(filePath)
        self.config.set("DIRECTORIES", "ndvi", tmpDir)
        self.config.set("FILENAME_PREFIXES", "ndvi_prefix", tmpPrefix)
        self.lineEdt_NDVISeries.setText(filePath)


def setNDVIMaximumSeriesFilePath(self):
    """Define the project's NDVIMax file.

    Also updates the lineEdt_NDVIMax field with the selected file path.

    :Slot signal: clicked
    :Signal sender: btn_NDVIMax
    """
    filePath = self.getFilePath(
        caption="Select Maximum NDVI Series File", filter="(*.map)"
    )
    if filePath:
        self.config.set("RASTERS", "ndvi_max", filePath)
        self.lineEdt_NDVIMax.setText(filePath)


def setNDVIMinimumSeriesFilePath(self):
    """Define the project's NDVIMin file.

    Also updates the lineEdt_NDVIMin field with the selected file path.

    :Slot signal: clicked
    :Signal sender: btn_NDVIMin
    """
    filePath = self.getFilePath(
        caption="Select Minimum NDVI Series File", filter="(*.map)"
    )
    if filePath:
        self.config.set("RASTERS", "ndvi_min", filePath)
        self.lineEdt_NDVIMin.setText(filePath)


# a
def setAiFilePath(self):
    """Define the project's a_i file.

    Also updates the lineEdt_a_i field with the selected file path.

    :Slot signal: clicked
    :Signal sender: btn_a_i
    """
    filePath = self.getFilePath(
        caption="Select Impervious Area Fraction (ai) File",
        filter="CSV files (*.csv);;Text files (*.txt)",
        selectedFilter="Text files (*.txt)",
    )
    if filePath:
        self.config.set("TABLES", "a_i", filePath)
        self.lineEdt_a_i.setText(filePath)


def setAoFilePath(self):
    """Define the project's a_o file.

    Also updates the lineEdt_a_o field with the selected file path.

    :Slot signal: clicked
    :Signal sender: btn_a_o
    """
    filePath = self.getFilePath(
        caption="Select Open Water Area Fraction (ao) File",
        filter="CSV files (*.csv);;Text files (*.txt)",
        selectedFilter="Text files (*.txt)",
    )
    if filePath:
        self.config.set("TABLES", "a_o", filePath)
        self.lineEdt_a_o.setText(filePath)


def setAsFilePath(self):
    """Define the project's a_s file.

    Also updates the lineEdt_a_s field with the selected file path.

    :Slot signal: clicked
    :Signal sender: btn_a_s
    """
    filePath = self.getFilePath(
        caption="Select Bare Soil Area Fraction (as) File",
        filter="CSV files (*.csv);;Text files (*.txt)",
        selectedFilter="Text files (*.txt)",
    )
    if filePath:
        self.config.set("TABLES", "a_s", filePath)
        self.lineEdt_a_s.setText(filePath)


def setAvFilePath(self):
    """Define the project's a_v file.

    Also updates the lineEdt_a_v field with the selected file path.

    :Slot signal: clicked
    :Signal sender: btn_a_v
    """
    filePath = self.getFilePath(
        caption="Select Vegetated Area Fraction (av) File",
        filter="CSV files (*.csv);;Text files (*.txt)",
        selectedFilter="Text files (*.txt)",
    )
    if filePath:
        self.config.set("TABLES", "a_v", filePath)
        self.lineEdt_a_v.setText(filePath)


# Manning
def setManningFilePath(self):
    """Define the project's Manning file.

    Also updates the lineEdt_Manning field with the selected file path.

    :Slot signal: clicked
    :Signal sender: btn_Manning
    """
    filePath = self.getFilePath(
        caption="Select Manning File",
        filter="CSV files (*.csv);;Text files (*.txt)",
        selectedFilter="Text files (*.txt)",
    )
    if filePath:
        self.config.set("TABLES", "manning", filePath)
        self.lineEdt_Manning.setText(filePath)


# Kc
def setKcMaximumFilePath(self):
    """Define the project's KcMax file.

    Also updates the lineEdt_KcMax field with the selected file path.

    :Slot signal: clicked
    :Signal sender: btn_KcMax
    """
    filePath = self.getFilePath(
        caption="Select Maximum Crop Coefficient (Kc) File",
        filter="CSV files (*.csv);;Text files (*.txt)",
        selectedFilter="Text files (*.txt)",
    )
    if filePath:
        self.config.set("TABLES", "K_c_max", filePath)
        self.lineEdt_KcMax.setText(filePath)


def setKcMinimumFilePath(self):
    """Define the project's KcMin file.

    Also updates the lineEdt_KcMin field with the selected file path.

    :Slot signal: clicked
    :Signal sender: btn_KcMin
    """
    filePath = self.getFilePath(
        caption="Select Minimum Crop Coefficient (Kc) File",
        filter="CSV files (*.csv);;Text files (*.txt)",
        selectedFilter="Text files (*.txt)",
    )
    if filePath:
        self.config.set("TABLES", "K_c_min", filePath)
        self.lineEdt_KcMin.setText(filePath)


# Fpar
def setFparMaximum(self):
    """Define the project's Fpar Maximum value.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_FparMax
    """
    self.config.set("CONSTANTS", "fpar_max", str(self.doubleSpinBox_FparMax.value()))


def setFparMinimum(self):
    """Define the project's Fpar Minimum value.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_FparMin
    """
    self.config.set("CONSTANTS", "fpar_min", str(self.doubleSpinBox_FparMin.value()))


# Interception
def setInterception(self):
    """Define the project's Interception value.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_Interception
    """
    self.config.set("CONSTANTS", "i_imp", str(self.doubleSpinBox_Interception.value()))


# Leaf Area Index
def setLeafAreaIndexMaximum(self):
    """Define the project's Maximum Leaf Area Index value.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_LeafAreaIndexMax
    """
    self.config.set(
        "CONSTANTS", "lai_max", str(self.doubleSpinBox_LeafAreaIndexMax.value())
    )
