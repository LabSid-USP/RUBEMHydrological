# Soil tab
# Soil Parameters
def setSoilMapFilePath(self):
    """Define the project's Soil Map file.

    Also updates the lineEdt_SoilMap field with the selected file path.

    :Slot signal: clicked
    :Signal sender: btn_SoilMap
    """
    filePath = self.getFilePath(caption="Select Soil Map File", filter="*.map")
    if filePath:
        self.config.set("RASTERS", "soil", filePath)
        self.lineEdt_SoilMap.setText(filePath)


def setDensityFilePath(self):
    """Define the project's Density file.

    Also updates the lineEdt_DensityDg field with the selected file path.

    :Slot signal: clicked
    :Signal sender: btn_DensityDg
    """
    filePath = self.getFilePath(
        caption="Select Soil Bulk Density File",
        filter="CSV files (*.csv);;Text files (*.txt)",
        selectedFilter="Text files (*.txt)",
    )
    if filePath:
        self.config.set("TABLES", "bulk_density", filePath)
        self.lineEdt_DensityDg.setText(filePath)


def setHydraulicConductivityFilePath(self):
    """Define the project's HydraulicConductivity file.

    Also updates the lineEdt_HydraulicConductivityKr field with the\n
        selected file path.

    :Slot signal: clicked
    :Signal sender: btn_HydraulicConductivityKr
    """
    filePath = self.getFilePath(
        caption="Select Soil Saturated Hydraulic Conductivity File",
        filter="CSV files (*.csv);;Text files (*.txt)",
        selectedFilter="Text files (*.txt)",
    )
    if filePath:
        self.config.set("TABLES", "K_sat", filePath)
        self.lineEdt_HydraulicConductivityKr.setText(filePath)


def setFieldCapacityFilePath(self):
    """Define the project's Field Capacity file.

    Also updates the lineEdt_FieldCapacityCC field with the selected\n
        file path.

    :Slot signal: clicked
    :Signal sender: btn_FieldCapacityCC
    """
    filePath = self.getFilePath(
        caption="Select Soil Field Capacity File",
        filter="CSV files (*.csv);;Text files (*.txt)",
        selectedFilter="Text files (*.txt)",
    )
    if filePath:
        self.config.set("TABLES", "T_fcap", filePath)
        self.lineEdt_FieldCapacityCC.setText(filePath)


def setWiltingPointFilePath(self):
    """Define the project's Wilting Point file.

    Also updates the lineEdt_WiltingPointWP field with the selected\n
        file path.

    :Slot signal: clicked
    :Signal sender: btn_WiltingPointWP
    """
    filePath = self.getFilePath(
        caption="Select Soil Wilting Point File",
        filter="CSV files (*.csv);;Text files (*.txt)",
        selectedFilter="Text files (*.txt)",
    )
    if filePath:
        self.config.set("TABLES", "T_wp", filePath)
        self.lineEdt_WiltingPointWP.setText(filePath)


def setSaturationFilePath(self):
    """Define the project's Saturation file.

    Also updates the lineEdt_Saturation field with the selected file path.

    :Slot signal: clicked
    :Signal sender: btn_Saturation
    """
    filePath = self.getFilePath(
        caption="Select Soil Saturation File",
        filter="CSV files (*.csv);;Text files (*.txt)",
        selectedFilter="Text files (*.txt)",
    )
    if filePath:
        self.config.set("TABLES", "T_sat", filePath)
        self.lineEdt_Saturation.setText(filePath)


def setRootZoneThicknessFilePath(self):
    """Define the project's Root Zone Thickness file.

    Also updates the lineEdt_RootZoneThicknessZr field with the selected\n
        file path.

    :Slot signal: clicked
    :Signal sender: btn_RootZoneThicknessZr
    """
    filePath = self.getFilePath(
        caption="Select Soil Rootzone Depth File",
        filter="CSV files (*.csv);;Text files (*.txt)",
        selectedFilter="Text files (*.txt)",
    )
    if filePath:
        self.config.set("TABLES", "rootzone_depth", filePath)
        self.lineEdt_RootZoneThicknessZr.setText(filePath)


# Initial Soil Conditions
def setInitialSoilMoisture(self):
    """Define the project's Initial soil moisture value in millimeters.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_InitialSoilMoisture
    """
    self.config.set(
        "INITIAL_SOIL_CONDITIONS",
        "T_ini",
        str(self.doubleSpinBox_InitialSoilMoisture.value()),
    )


def setInitialBaseFlow(self):
    """Define the project's Initial Base Flow value in millimeters.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_BaseFlowInitial
    """
    self.config.set(
        "INITIAL_SOIL_CONDITIONS",
        "bfw_ini",
        str(self.doubleSpinBox_BaseFlowInitial.value()),
    )


def setBaseFlowLimit(self):
    """Define the project's Base Flow Limit value in millimeters.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_BaseFlowLimit
    """
    self.config.set(
        "INITIAL_SOIL_CONDITIONS",
        "bfw_lim",
        str(self.doubleSpinBox_BaseFlowLimit.value()),
    )


def setInitialTus(self):
    """Define the project's Initial Tus value in millimeters.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_TusInitial
    """
    self.config.set(
        "INITIAL_SOIL_CONDITIONS",
        "S_sat_ini",
        str(self.doubleSpinBox_TusInitial.value()),
    )
