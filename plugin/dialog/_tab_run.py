# Run tab
# Geneate Files
def setInterceptionGenerateFile(self):
    """Define whether the Interception file will be generated as output
        from the model execution.

    :Slot signal: checked
    :Signal sender: checkBox_InterceptionInt
    """
    self.config.set(
        "GENERATE_FILE", "itp", str(self.checkBox_InterceptionInt.isChecked())
    )


def setInterceptionEbGenerateFile(self):
    """Define whether the Interception Eb file will be generated as output
        from the model execution.

    :Slot signal: checked
    :Signal sender: checkBox_InterceptionEb
    """
    self.config.set(
        "GENERATE_FILE", "bfw", str(self.checkBox_InterceptionEb.isChecked())
    )


def setEvapotranspirationGenerateFile(self):
    """Define whether the Evapotranspiration file will be generated as
        output from the model execution.

    :Slot signal: checked
    :Signal sender: checkBox_EvapotranspirationEvp
    """
    self.config.set(
        "GENERATE_FILE", "eta", str(self.checkBox_EvapotranspirationEvp.isChecked())
    )


def setRechargeGenerateFile(self):
    """Define whether the Recharge file will be generated as output
        from the model execution.

    :Slot signal: checked
    :Signal sender: checkBox_RechargeRec
    """
    self.config.set("GENERATE_FILE", "rec", str(self.checkBox_RechargeRec.isChecked()))


def setSoilMoistureGenerateFile(self):
    """Define whether the Soil Moisture file will be generated as output
        from the model execution.

    :Slot signal: checked
    :Signal sender: checkBox_SoilMoistureTur
    """
    self.config.set(
        "GENERATE_FILE", "smc", str(self.checkBox_SoilMoistureTur.isChecked())
    )


def setLateralFLowGenerateFile(self):
    """Define whether the Lateral FLow file will be generated as output
        from the model execution.

    :Slot signal: checked
    :Signal sender: checkBox_LateralFlowLf
    """
    self.config.set(
        "GENERATE_FILE", "lfw", str(self.checkBox_LateralFlowLf.isChecked())
    )


def setRunoffEsdGenerateFile(self):
    """Define whether the Runoff Esd file will be generated as output
        from the model execution.

    :Slot signal: checked
    :Signal sender: checkBox_RunoffEsd
    """
    self.config.set("GENERATE_FILE", "srn", str(self.checkBox_RunoffEsd.isChecked()))


# TODO: Rename setRunoffVazaoGenerateFile, checkBox_RunoffVazao, GUI and
#  config section GENERATE_FILES option Vazao
def setRunoffVazaoGenerateFile(self):
    """Define whether the Runoff Vazao file will be generated as output
        from the model execution.

    :Slot signal: checked
    :Signal sender: checkBox_RunoffVazao
    """
    self.config.set("GENERATE_FILE", "rnf", str(self.checkBox_RunoffVazao.isChecked()))
