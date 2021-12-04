import os

from qgis.core import Qgis

try:
    from ..validation.validators import *
except ImportError:
    from validation.validators import *

# TODO: Add docstring information and comments
def hasFilledAllFields(self):
    """Check if all fields have been properly filled in.

    Returns:
        [type]: [description]
    """
    emptyFields = []
    for key, element in self.uiDirPathDict.items():
        lineEdit, _ = element
        if not lineEdit.text() or not os.path.exists(lineEdit.text()):
            lineEdit.setStyleSheet(INVALID_LINEEDIT_STYLESHEET)
            emptyFields.append(key)

    # for lineEdit in self.findChildren(QLineEdit):
    for key, element in self.uiFilePathDict.items():
        lineEdit, _, _ = element
        if not lineEdit.text() or not os.path.exists(lineEdit.text()):
            lineEdit.setStyleSheet(INVALID_LINEEDIT_STYLESHEET)
            emptyFields.append(key)

    if "samples" in emptyFields and not self.config.getboolean("GENERATE_FILE", "tss"):
        emptyFields.remove("samples")
        self.lineEdt_Sample.setStyleSheet(ACCEPTABLE_LABEL_STYLESHEET)

    if emptyFields:
        self.bar.pushMessage(
            "Misconfiguration",
            "Data entered is missing or non-existent",
            level=Qgis.Warning,
        )

    checkedBoxes = []
    for element in self.uiGenerateFilesDict.values():
        if element.isChecked():
            checkedBoxes.append(element)

    if not checkedBoxes:
        self.groupBox_GenerateFiles.setStyleSheet(INVALID_LABEL_STYLESHEET)
        self.bar.pushMessage(
            "Misconfiguration", "No output variable selected", level=Qgis.Warning
        )
    else:
        self.groupBox_GenerateFiles.setStyleSheet(ACCEPTABLE_LABEL_STYLESHEET)

    hasValidDateRange = True
    if self.dtEdt_StartSim.date() >= self.dtEdt_EndSim.date():
        hasValidDateRange = False
        self.groupBox_SimulationPeriod.setStyleSheet(INVALID_LABEL_STYLESHEET)
        self.bar.pushMessage(
            "Misconfiguration",
            "The end date must be greater than the start date",
            level=Qgis.Warning,
        )
    else:
        self.groupBox_SimulationPeriod.setStyleSheet(ACCEPTABLE_LABEL_STYLESHEET)

    hasAreaFractionAddUpTo1 = True
    if (
        not self.doubleSpinBox_ManningRelatedWeightFactor.value()
        + self.doubleSpinBox_SoilRelatedWeightFactor.value()
        + self.doubleSpinBox_SlopeRelatedWeightFactor.value()
        == 1
    ):
        hasAreaFractionAddUpTo1 = False
        self.groupBox_WeightFactors.setStyleSheet(INVALID_LABEL_STYLESHEET)
        self.bar.pushMessage(
            "Misconfiguration",
            "The sum of the area fractions must add up to 1",
            level=Qgis.Warning,
        )
    else:
        self.groupBox_WeightFactors.setStyleSheet(ACCEPTABLE_LABEL_STYLESHEET)

    if (
        not emptyFields
        and checkedBoxes
        and hasValidDateRange
        and hasAreaFractionAddUpTo1
    ):
        return True
    else:
        return False


# TODO: Add docstring information and comments
def setupUserInputValidators(self):

    self.uiDirPathDict = {
        "input": (self.lineEdit_InputFolder, self.label_InputFolder),
        "output": (self.lineEdit_OutputFolder, self.label_OutputFolder),
    }

    self.uiFilePathDict = {
        "dem": (self.lineEdt_Dem, self.label_Dem, (".map")),
        "demtif": (self.lineEdt_DemTif, self.label_DemTif, (".tif", ".tiff")),
        "clone": (self.lineEdt_Clone, self.label_Clone, (".map")),
        "samples": (self.lineEdt_Sample, self.label_SelectSample, (".map")),
        # Soil tab
        # Soil Parameters
        "solo": (self.lineEdt_SoilMap, self.label_SoilMap, (".map")),
        "dg": (self.lineEdt_DensityDg, self.label_DensityDg, (".txt", ".csv")),
        "kr": (
            self.lineEdt_HydraulicConductivityKr,
            self.label_HydraulicConductivityKr,
            (".txt", ".csv"),
        ),
        "capCampo": (
            self.lineEdt_FieldCapacityCC,
            self.label_FieldCapacityCC,
            (".txt", ".csv"),
        ),
        "pontomurcha": (
            self.lineEdt_WiltingPointWP,
            self.label_WiltingPointWP,
            (".txt", ".csv"),
        ),
        "saturacao": (
            self.lineEdt_Saturation,
            self.label_Saturation,
            (".txt", ".csv"),
        ),
        "zr": (
            self.lineEdt_RootZoneThicknessZr,
            self.label_RootZoneThickNessZr,
            (".txt", ".csv"),
        ),
        # Land Use tab
        # Land Use Series
        "landuse": (
            self.lineEdt_LandUseSeries,
            self.groupBox_LandUseSeries,
            (".001"),
        ),
        # "landuseFilePrefix", tmpPrefix
        "ndvi": (self.lineEdt_NDVISeries, self.label_NDVISeries, (".001")),
        # "ndviFilePrefix", tmpPrefix
        "ndvimax": (self.lineEdt_NDVIMax, self.label_NDVIMax, (".map")),
        "ndvimin": (self.lineEdt_NDVIMin, self.label_NDVIMin, (".map")),
        # a
        "a_i": (self.lineEdt_a_i, self.label_a_i, (".txt", ".csv")),
        "a_o": (self.lineEdt_a_o, self.label_a_o, (".txt", ".csv")),
        "a_s": (self.lineEdt_a_s, self.label_a_s, (".txt", ".csv")),
        "a_v": (self.lineEdt_a_v, self.label_a_v, (".txt", ".csv")),
        # Manning
        "manning": (self.lineEdt_Manning, self.groupBox_Manning, (".txt", ".csv")),
        # Kc
        "kcmax": (self.lineEdt_KcMax, self.label_KcMax, (".txt", ".csv")),
        "kcmin": (self.lineEdt_KcMin, self.label_KcMin, (".txt", ".csv")),
        # Climate tab
        "prec": (self.lineEdt_Precipitation, self.label_Precipitation, (".001")),
        # "precFilePrefix", tmpPrefix
        "etp": (
            self.lineEdt_EvapoTranspiration,
            self.label_Evapotranspiration,
            (".001"),
        ),
        # "etpFilePrefix", tmpPrefix
        "kp": (
            self.lineEdt_PanCoefficientKp,
            self.label_PanCoefficientKp,
            (".001"),
        ),
        # "kpFilePrefix", tmpPrefix
        "rainydays": (
            self.lineEdt_RainyDays,
            self.label_RainyDays,
            (".txt", ".csv"),
        ),
    }

    self.uiGenerateFilesDict = {
        # Run tab
        # Geneate Files
        "Int": self.checkBox_InterceptionInt,
        "bflow": self.checkBox_InterceptionEb,
        "etp": self.checkBox_EvapotranspirationEvp,
        "Rec": self.checkBox_RechargeRec,
        "ssat": self.checkBox_SoilMoistureTur,
        "Lf": self.checkBox_LateralFlowLf,
        "sfrun": self.checkBox_RunoffEsd,
        "runoff": self.checkBox_RunoffVazao,
    }

    # self.uiSpinBoxDict = {
    #     # Grid Size
    #     "grid": self.doubleSpinBox_GridSize,
    #     # Initial Soil Conditions
    #     "ftur_ini": self.doubleSpinBox_InitialSoilMoisture,
    #     "eb_ini": self.doubleSpinBox_BaseFlowInitial,
    #     "eb_lim": self.doubleSpinBox_BaseFlowLimit,
    #     "tus_ini": self.doubleSpinBox_TusInitial,
    #     # Fpar
    #     "fpar_max": self.doubleSpinBox_FparMax,
    #     "fpar_min": self.doubleSpinBox_FparMin,
    #     # Interception
    #     "i_imp": self.doubleSpinBox_Interception,
    #     # Leaf Area Index
    #     "lai_max": self.doubleSpinBox_LeafAreaIndexMax,
    #     # Parameters tab
    #     # Model Parameters
    #     "b": self.doubleSpinBox_ExponentCh,
    #     "x": self.doubleSpinBox_DelayFactor,
    #     "rcd": self.doubleSpinBox_RegionalConsecutiveDrynessLevel,
    #     "alfa_gw": self.doubleSpinBox_DelayCoefficientBaseFlow,
    #     "f": self.doubleSpinBox_PartitioningCoefficientRelatedSoil,
    #     "alfa": self.doubleSpinBox_InterceptionCalibrationAlpha,
    #     # Weight Factors
    #     "w1": self.doubleSpinBox_ManningRelatedWeightFactor,
    #     "w2": self.doubleSpinBox_SoilRelatedWeightFactor,
    #     "w3": self.doubleSpinBox_SlopeRelatedWeightFactor,
    # }

    for key, elementsTuple in self.uiDirPathDict.items():
        lineEdit, label = elementsTuple
        validator = DirectoryPathValidator(lineEdit, label)
        lineEdit.setValidator(validator)

    for key, elementsTuple in self.uiFilePathDict.items():
        lineEdit, label, allowedExt = elementsTuple
        validator = FilePathValidator(lineEdit, label, allowedExt)
        lineEdit.setValidator(validator)
