try:
    from ._project import _spin_text
except ImportError:
    from _project import _spin_text

# Parameters tab
# Model Parameters
def setExponentCh(self):
    """Define the project's Exponent of Ch value.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_ExponentCh
    """
    self.config.set(
        "CALIBRATION",
        "b",
        _spin_text(
            self,
            self.doubleSpinBox_ExponentCh,
            "CALIBRATION",
            "b",
        ),
    )


def setDelayFactor(self):
    """Define the project's Delay Factor value.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_DelayFactor
    """
    self.config.set(
        "CALIBRATION",
        "x",
        _spin_text(
            self,
            self.doubleSpinBox_DelayFactor,
            "CALIBRATION",
            "x",
        ),
    )


def setRegionalConsecutiveDrynessLevel(self):
    """Define the project's Regional Consecutive Dryness (RCD) Level value.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_RegionalConsecutiveDrynessLevel
    """
    self.config.set(
        "CALIBRATION",
        "rcd",
        _spin_text(
            self,
            self.doubleSpinBox_RegionalConsecutiveDrynessLevel,
            "CALIBRATION",
            "rcd",
        ),
    )


def setDelayCoefficientBaseFlow(self):
    """Define the project's Delay Coefficient Base Flow value.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_DelayCoefficientBaseFlow
    """
    self.config.set(
        "CALIBRATION",
        "alpha_gw",
        _spin_text(
            self,
            self.doubleSpinBox_DelayCoefficientBaseFlow,
            "CALIBRATION",
            "alpha_gw",
        ),
    )


def setPartitioningCoefficientRelated(self):
    """Define the project's Partitioning Coefficient Related value.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_PartitioningCoefficientRelatedSoil
    """
    self.config.set(
        "CALIBRATION",
        "f",
        _spin_text(
            self,
            self.doubleSpinBox_PartitioningCoefficientRelatedSoil,
            "CALIBRATION",
            "f",
        ),
    )


def setInterceptionCalibration(self):
    """Define the project's Interception Calibration value.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_InterceptionCalibrationAlpha
    """
    self.config.set(
        "CALIBRATION",
        "alpha",
        _spin_text(
            self,
            self.doubleSpinBox_InterceptionCalibrationAlpha,
            "CALIBRATION",
            "alpha",
        ),
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
        _spin_text(
            self,
            self.doubleSpinBox_ManningRelatedWeightFactor,
            "CALIBRATION",
            "w_1",
        ),
    )


def setSoilRelatedWeightFactor(self):
    """Define the project's Soil Related Weight Factor (w2) value.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_SoilRelatedWeightFactor
    """
    self.config.set(
        "CALIBRATION",
        "w_2",
        _spin_text(
            self,
            self.doubleSpinBox_SoilRelatedWeightFactor,
            "CALIBRATION",
            "w_2",
        ),
    )


def setSlopeRelatedWeightFactor(self):
    """Define the project's Slope Related Weight Factor (w3) value.

    :Slot signal: editingFinished
    :Signal sender: doubleSpinBox_SlopeRelatedWeightFactor
    """
    self.config.set(
        "CALIBRATION",
        "w_3",
        _spin_text(
            self,
            self.doubleSpinBox_SlopeRelatedWeightFactor,
            "CALIBRATION",
            "w_3",
        ),
    )
