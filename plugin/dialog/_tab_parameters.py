# Parameters tab
# Model Parameters
def setExponentCh(self):
    """Define the project's Exponent of Ch value.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_ExponentCh
    """
    self.config.set("CALIBRATION", "b", str(self.doubleSpinBox_ExponentCh.value()))


def setDelayFactor(self):
    """Define the project's Delay Factor value.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_DelayFactor
    """
    self.config.set("CALIBRATION", "x", str(self.doubleSpinBox_DelayFactor.value()))


def setRegionalConsecutiveDrynessLevel(self):
    """Define the project's Regional Consecutive Dryness (RCD) Level value.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_RegionalConsecutiveDrynessLevel
    """
    self.config.set(
        "CALIBRATION",
        "rcd",
        str(self.doubleSpinBox_RegionalConsecutiveDrynessLevel.value()),
    )


def setDelayCoefficientBaseFlow(self):
    """Define the project's Delay Coefficient Base Flow value.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_DelayCoefficientBaseFlow
    """
    self.config.set(
        "CALIBRATION",
        "alpha_gw",
        str(self.doubleSpinBox_DelayCoefficientBaseFlow.value()),
    )


def setPartitioningCoefficientRelated(self):
    """Define the project's Partitioning Coefficient Related value.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_PartitioningCoefficientRelatedSoil
    """
    self.config.set(
        "CALIBRATION",
        "f",
        str(self.doubleSpinBox_PartitioningCoefficientRelatedSoil.value()),
    )


def setInterceptionCalibration(self):
    """Define the project's Interception Calibration value.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_InterceptionCalibrationAlpha
    """
    self.config.set(
        "CALIBRATION",
        "alpha",
        str(self.doubleSpinBox_InterceptionCalibrationAlpha.value()),
    )


# Weight Factors
def setManningRelatedWeightFactor(self):
    """Define the project's Manning Related Weight Factor (w1) value.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_ManningRelatedWeightFactor
    """
    self.config.set(
        "CALIBRATION",
        "w_1",
        str(self.doubleSpinBox_ManningRelatedWeightFactor.value()),
    )


def setSoilRelatedWeightFactor(self):
    """Define the project's Soil Related Weight Factor (w2) value.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_SoilRelatedWeightFactor
    """
    self.config.set(
        "CALIBRATION",
        "w_2",
        str(self.doubleSpinBox_SoilRelatedWeightFactor.value()),
    )


def setSlopeRelatedWeightFactor(self):
    """Define the project's Slope Related Weight Factor (w3) value.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_SlopeRelatedWeightFactor
    """
    self.config.set(
        "CALIBRATION",
        "w_3",
        str(self.doubleSpinBox_SlopeRelatedWeightFactor.value()),
    )
