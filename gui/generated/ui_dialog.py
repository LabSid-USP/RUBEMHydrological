# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui.resources\ui_BaseDialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_BaseDialog(object):
    def setupUi(self, BaseDialog):
        BaseDialog.setObjectName("BaseDialog")
        BaseDialog.resize(506, 646)
        self.tabWidget = QtWidgets.QTabWidget(BaseDialog)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 501, 621))
        self.tabWidget.setObjectName("tabWidget")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.Label_Project = QtWidgets.QLabel(self.tab_4)
        self.Label_Project.setGeometry(QtCore.QRect(10, 20, 251, 31))
        self.Label_Project.setObjectName("Label_Project")
        self.label_26 = QtWidgets.QLabel(self.tab_4)
        self.label_26.setGeometry(QtCore.QRect(140, 250, 131, 21))
        self.label_26.setObjectName("label_26")
        self.label_27 = QtWidgets.QLabel(self.tab_4)
        self.label_27.setGeometry(QtCore.QRect(140, 190, 131, 21))
        self.label_27.setObjectName("label_27")
        self.txtEdt_GridSize = QtWidgets.QLineEdit(self.tab_4)
        self.txtEdt_GridSize.setGeometry(QtCore.QRect(10, 190, 111, 25))
        self.txtEdt_GridSize.setMinimumSize(QtCore.QSize(100, 25))
        self.txtEdt_GridSize.setObjectName("txtEdt_GridSize")
        self.dtEdt_EndSim = QtWidgets.QDateEdit(self.tab_4)
        self.dtEdt_EndSim.setGeometry(QtCore.QRect(10, 250, 110, 22))
        self.dtEdt_EndSim.setObjectName("dtEdt_EndSim")
        self.dtEdt_StartSim = QtWidgets.QDateEdit(self.tab_4)
        self.dtEdt_StartSim.setGeometry(QtCore.QRect(10, 220, 110, 22))
        self.dtEdt_StartSim.setObjectName("dtEdt_StartSim")
        self.label_28 = QtWidgets.QLabel(self.tab_4)
        self.label_28.setGeometry(QtCore.QRect(140, 220, 131, 21))
        self.label_28.setObjectName("label_28")
        self.label_29 = QtWidgets.QLabel(self.tab_4)
        self.label_29.setGeometry(QtCore.QRect(10, 150, 251, 31))
        self.label_29.setObjectName("label_29")
        self.buttonBox_2 = QtWidgets.QDialogButtonBox(self.tab_4)
        self.buttonBox_2.setGeometry(QtCore.QRect(290, 540, 193, 28))
        self.buttonBox_2.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox_2.setObjectName("buttonBox_2")
        self.formLayoutWidget = QtWidgets.QWidget(self.tab_4)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 50, 471, 102))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.txtEdt_InputFolder = QtWidgets.QLineEdit(self.formLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtEdt_InputFolder.sizePolicy().hasHeightForWidth())
        self.txtEdt_InputFolder.setSizePolicy(sizePolicy)
        self.txtEdt_InputFolder.setMinimumSize(QtCore.QSize(330, 25))
        self.txtEdt_InputFolder.setObjectName("txtEdt_InputFolder")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.txtEdt_InputFolder)
        self.Btn_InputFolder = QtWidgets.QPushButton(self.formLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Btn_InputFolder.sizePolicy().hasHeightForWidth())
        self.Btn_InputFolder.setSizePolicy(sizePolicy)
        self.Btn_InputFolder.setMinimumSize(QtCore.QSize(30, 25))
        self.Btn_InputFolder.setObjectName("Btn_InputFolder")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.Btn_InputFolder)
        self.txtEdt_OutputFolder = QtWidgets.QLineEdit(self.formLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtEdt_OutputFolder.sizePolicy().hasHeightForWidth())
        self.txtEdt_OutputFolder.setSizePolicy(sizePolicy)
        self.txtEdt_OutputFolder.setMinimumSize(QtCore.QSize(330, 25))
        self.txtEdt_OutputFolder.setObjectName("txtEdt_OutputFolder")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.txtEdt_OutputFolder)
        self.Btn_OutpuFolder = QtWidgets.QPushButton(self.formLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Btn_OutpuFolder.sizePolicy().hasHeightForWidth())
        self.Btn_OutpuFolder.setSizePolicy(sizePolicy)
        self.Btn_OutpuFolder.setMinimumSize(QtCore.QSize(30, 25))
        self.Btn_OutpuFolder.setObjectName("Btn_OutpuFolder")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.Btn_OutpuFolder)
        self.Btn_Save = QtWidgets.QPushButton(self.tab_4)
        self.Btn_Save.setGeometry(QtCore.QRect(180, 540, 93, 28))
        self.Btn_Save.setObjectName("Btn_Save")
        self.tabWidget.addTab(self.tab_4, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.lineEdit_6 = QtWidgets.QLineEdit(self.tab_3)
        self.lineEdit_6.setGeometry(QtCore.QRect(30, 210, 241, 21))
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.observed = QtWidgets.QPushButton(self.tab_3)
        self.observed.setGeometry(QtCore.QRect(280, 200, 93, 28))
        self.observed.setObjectName("observed")
        self.check_calibration = QtWidgets.QCheckBox(self.tab_3)
        self.check_calibration.setGeometry(QtCore.QRect(30, 180, 70, 17))
        self.check_calibration.setObjectName("check_calibration")
        self.label_6 = QtWidgets.QLabel(self.tab_3)
        self.label_6.setGeometry(QtCore.QRect(180, 250, 131, 21))
        self.label_6.setObjectName("label_6")
        self.kc_max = QtWidgets.QLineEdit(self.tab_3)
        self.kc_max.setGeometry(QtCore.QRect(30, 250, 141, 20))
        self.kc_max.setObjectName("kc_max")
        self.kc_min = QtWidgets.QLineEdit(self.tab_3)
        self.kc_min.setGeometry(QtCore.QRect(30, 280, 141, 20))
        self.kc_min.setObjectName("kc_min")
        self.label_7 = QtWidgets.QLabel(self.tab_3)
        self.label_7.setGeometry(QtCore.QRect(180, 280, 131, 21))
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(self.tab_3)
        self.label_8.setGeometry(QtCore.QRect(180, 310, 131, 21))
        self.label_8.setObjectName("label_8")
        self.Fpar_max = QtWidgets.QLineEdit(self.tab_3)
        self.Fpar_max.setGeometry(QtCore.QRect(30, 310, 141, 20))
        self.Fpar_max.setObjectName("Fpar_max")
        self.label_9 = QtWidgets.QLabel(self.tab_3)
        self.label_9.setGeometry(QtCore.QRect(180, 340, 131, 21))
        self.label_9.setObjectName("label_9")
        self.Fpar_min = QtWidgets.QLineEdit(self.tab_3)
        self.Fpar_min.setGeometry(QtCore.QRect(30, 340, 141, 20))
        self.Fpar_min.setObjectName("Fpar_min")
        self.label_10 = QtWidgets.QLabel(self.tab_3)
        self.label_10.setGeometry(QtCore.QRect(180, 370, 131, 21))
        self.label_10.setObjectName("label_10")
        self.intercept = QtWidgets.QLineEdit(self.tab_3)
        self.intercept.setGeometry(QtCore.QRect(30, 370, 141, 20))
        self.intercept.setObjectName("intercept")
        self.label_19 = QtWidgets.QLabel(self.tab_3)
        self.label_19.setGeometry(QtCore.QRect(170, 490, 131, 21))
        self.label_19.setObjectName("label_19")
        self.label_21 = QtWidgets.QLabel(self.tab_3)
        self.label_21.setGeometry(QtCore.QRect(30, 420, 141, 31))
        self.label_21.setObjectName("label_21")
        self.lineEdit_24 = QtWidgets.QLineEdit(self.tab_3)
        self.lineEdit_24.setGeometry(QtCore.QRect(20, 460, 141, 20))
        self.lineEdit_24.setText("")
        self.lineEdit_24.setObjectName("lineEdit_24")
        self.lineEdit_25 = QtWidgets.QLineEdit(self.tab_3)
        self.lineEdit_25.setGeometry(QtCore.QRect(20, 490, 141, 20))
        self.lineEdit_25.setText("")
        self.lineEdit_25.setObjectName("lineEdit_25")
        self.label_22 = QtWidgets.QLabel(self.tab_3)
        self.label_22.setGeometry(QtCore.QRect(170, 520, 131, 21))
        self.label_22.setObjectName("label_22")
        self.label_23 = QtWidgets.QLabel(self.tab_3)
        self.label_23.setGeometry(QtCore.QRect(170, 460, 131, 21))
        self.label_23.setObjectName("label_23")
        self.lineEdit_26 = QtWidgets.QLineEdit(self.tab_3)
        self.lineEdit_26.setGeometry(QtCore.QRect(20, 520, 141, 20))
        self.lineEdit_26.setText("")
        self.lineEdit_26.setObjectName("lineEdit_26")
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_6 = QtWidgets.QWidget()
        self.tab_6.setObjectName("tab_6")
        self.tabWidget.addTab(self.tab_6, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.dem_box = QtWidgets.QLineEdit(self.tab)
        self.dem_box.setGeometry(QtCore.QRect(20, 60, 301, 31))
        self.dem_box.setObjectName("dem_box")
        self.dem = QtWidgets.QPushButton(self.tab)
        self.dem.setGeometry(QtCore.QRect(330, 60, 93, 28))
        self.dem.setObjectName("dem")
        self.samples = QtWidgets.QPushButton(self.tab)
        self.samples.setGeometry(QtCore.QRect(330, 110, 93, 28))
        self.samples.setObjectName("samples")
        self.sample_box = QtWidgets.QLineEdit(self.tab)
        self.sample_box.setGeometry(QtCore.QRect(20, 110, 301, 31))
        self.sample_box.setObjectName("sample_box")
        self.land_use = QtWidgets.QPushButton(self.tab)
        self.land_use.setGeometry(QtCore.QRect(330, 160, 93, 28))
        self.land_use.setObjectName("land_use")
        self.land_box = QtWidgets.QLineEdit(self.tab)
        self.land_box.setGeometry(QtCore.QRect(20, 160, 301, 31))
        self.land_box.setObjectName("land_box")
        self.label_11 = QtWidgets.QLabel(self.tab)
        self.label_11.setGeometry(QtCore.QRect(30, 220, 141, 31))
        self.label_11.setObjectName("label_11")
        self.label_12 = QtWidgets.QLabel(self.tab)
        self.label_12.setGeometry(QtCore.QRect(170, 290, 131, 21))
        self.label_12.setObjectName("label_12")
        self.bf_lm = QtWidgets.QLineEdit(self.tab)
        self.bf_lm.setGeometry(QtCore.QRect(20, 320, 141, 20))
        self.bf_lm.setText("")
        self.bf_lm.setObjectName("bf_lm")
        self.ini_tus = QtWidgets.QLineEdit(self.tab)
        self.ini_tus.setGeometry(QtCore.QRect(20, 350, 141, 20))
        self.ini_tus.setText("")
        self.ini_tus.setObjectName("ini_tus")
        self.label_13 = QtWidgets.QLabel(self.tab)
        self.label_13.setGeometry(QtCore.QRect(170, 320, 131, 21))
        self.label_13.setObjectName("label_13")
        self.ini_bf = QtWidgets.QLineEdit(self.tab)
        self.ini_bf.setGeometry(QtCore.QRect(20, 290, 141, 20))
        self.ini_bf.setText("")
        self.ini_bf.setObjectName("ini_bf")
        self.ini_moist = QtWidgets.QLineEdit(self.tab)
        self.ini_moist.setGeometry(QtCore.QRect(20, 260, 141, 20))
        self.ini_moist.setText("")
        self.ini_moist.setObjectName("ini_moist")
        self.label_14 = QtWidgets.QLabel(self.tab)
        self.label_14.setGeometry(QtCore.QRect(170, 260, 131, 21))
        self.label_14.setObjectName("label_14")
        self.label_15 = QtWidgets.QLabel(self.tab)
        self.label_15.setGeometry(QtCore.QRect(170, 350, 131, 21))
        self.label_15.setObjectName("label_15")
        self.delay_runoff = QtWidgets.QLineEdit(self.tab)
        self.delay_runoff.setGeometry(QtCore.QRect(20, 520, 141, 20))
        self.delay_runoff.setText("")
        self.delay_runoff.setObjectName("delay_runoff")
        self.label_16 = QtWidgets.QLabel(self.tab)
        self.label_16.setGeometry(QtCore.QRect(170, 520, 131, 21))
        self.label_16.setObjectName("label_16")
        self.label_17 = QtWidgets.QLabel(self.tab)
        self.label_17.setGeometry(QtCore.QRect(170, 490, 131, 21))
        self.label_17.setObjectName("label_17")
        self.label_18 = QtWidgets.QLabel(self.tab)
        self.label_18.setGeometry(QtCore.QRect(30, 420, 141, 31))
        self.label_18.setObjectName("label_18")
        self.partitioning = QtWidgets.QLineEdit(self.tab)
        self.partitioning.setGeometry(QtCore.QRect(20, 460, 141, 20))
        self.partitioning.setText("")
        self.partitioning.setObjectName("partitioning")
        self.delay_bf = QtWidgets.QLineEdit(self.tab)
        self.delay_bf.setGeometry(QtCore.QRect(20, 490, 141, 20))
        self.delay_bf.setText("")
        self.delay_bf.setObjectName("delay_bf")
        self.label_20 = QtWidgets.QLabel(self.tab)
        self.label_20.setGeometry(QtCore.QRect(170, 460, 131, 21))
        self.label_20.setObjectName("label_20")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.prep_box = QtWidgets.QLineEdit(self.tab_2)
        self.prep_box.setGeometry(QtCore.QRect(10, 40, 301, 31))
        self.prep_box.setObjectName("prep_box")
        self.prep = QtWidgets.QPushButton(self.tab_2)
        self.prep.setGeometry(QtCore.QRect(320, 40, 93, 28))
        self.prep.setObjectName("prep")
        self.evapo = QtWidgets.QPushButton(self.tab_2)
        self.evapo.setGeometry(QtCore.QRect(320, 90, 101, 28))
        self.evapo.setObjectName("evapo")
        self.evapo_box = QtWidgets.QLineEdit(self.tab_2)
        self.evapo_box.setGeometry(QtCore.QRect(10, 90, 301, 31))
        self.evapo_box.setObjectName("evapo_box")
        self.Kp_box = QtWidgets.QLineEdit(self.tab_2)
        self.Kp_box.setGeometry(QtCore.QRect(10, 140, 301, 31))
        self.Kp_box.setObjectName("Kp_box")
        self.Kp = QtWidgets.QPushButton(self.tab_2)
        self.Kp.setGeometry(QtCore.QRect(320, 140, 111, 28))
        self.Kp.setObjectName("Kp")
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.check_config = QtWidgets.QPushButton(self.tab_5)
        self.check_config.setGeometry(QtCore.QRect(80, 200, 75, 23))
        self.check_config.setObjectName("check_config")
        self.run = QtWidgets.QPushButton(self.tab_5)
        self.run.setGeometry(QtCore.QRect(220, 200, 75, 23))
        self.run.setObjectName("run")
        self.exit = QtWidgets.QPushButton(self.tab_5)
        self.exit.setGeometry(QtCore.QRect(340, 200, 75, 23))
        self.exit.setObjectName("exit")
        self.progressBar = QtWidgets.QProgressBar(self.tab_5)
        self.progressBar.setGeometry(QtCore.QRect(90, 170, 321, 23))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.model_image = QtWidgets.QLabel(self.tab_5)
        self.model_image.setGeometry(QtCore.QRect(80, 80, 91, 16))
        self.model_image.setObjectName("model_image")
        self.labsid_image = QtWidgets.QLabel(self.tab_5)
        self.labsid_image.setGeometry(QtCore.QRect(250, 80, 91, 16))
        self.labsid_image.setObjectName("labsid_image")
        self.buttonBox = QtWidgets.QDialogButtonBox(self.tab_5)
        self.buttonBox.setGeometry(QtCore.QRect(150, 260, 193, 28))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.tabWidget.addTab(self.tab_5, "")
        self.tab_7 = QtWidgets.QWidget()
        self.tab_7.setObjectName("tab_7")
        self.poli_image = QtWidgets.QLabel(self.tab_7)
        self.poli_image.setGeometry(QtCore.QRect(30, 260, 47, 13))
        self.poli_image.setObjectName("poli_image")
        self.adp_image = QtWidgets.QLabel(self.tab_7)
        self.adp_image.setGeometry(QtCore.QRect(210, 260, 47, 13))
        self.adp_image.setObjectName("adp_image")
        self.labsid_image_2 = QtWidgets.QLabel(self.tab_7)
        self.labsid_image_2.setGeometry(QtCore.QRect(380, 260, 47, 13))
        self.labsid_image_2.setObjectName("labsid_image_2")
        self.info_text = QtWidgets.QPlainTextEdit(self.tab_7)
        self.info_text.setGeometry(QtCore.QRect(20, 20, 451, 211))
        self.info_text.setObjectName("info_text")
        self.tabWidget.addTab(self.tab_7, "")
        self.label_25 = QtWidgets.QLabel(BaseDialog)
        self.label_25.setGeometry(QtCore.QRect(210, 610, 61, 31))
        self.label_25.setObjectName("label_25")

        self.retranslateUi(BaseDialog)
        self.tabWidget.setCurrentIndex(4)
        self.Btn_InputFolder.clicked.connect(BaseDialog.SetInput)
        self.Btn_OutpuFolder.clicked.connect(BaseDialog.SetOutput)
        self.buttonBox_2.clicked['QAbstractButton*'].connect(BaseDialog.close)
        self.Btn_Save.clicked.connect(BaseDialog.BtnSave_Click)
        self.dem.clicked.connect(BaseDialog.SearchDem)
        self.ini_moist.editingFinished.connect(BaseDialog.Initial_Soil_Moisture)
        self.prep.clicked.connect(BaseDialog.SearchPrec)
        self.evapo.clicked.connect(BaseDialog.Search_ETP)
        self.Kp.clicked.connect(BaseDialog.Search_Kp)
        QtCore.QMetaObject.connectSlotsByName(BaseDialog)

    def retranslateUi(self, BaseDialog):
        _translate = QtCore.QCoreApplication.translate
        BaseDialog.setWindowTitle(_translate("BaseDialog", "RUBEM"))
        self.Label_Project.setText(_translate("BaseDialog", "Choose Project Folder"))
        self.label_26.setText(_translate("BaseDialog", "End simulation"))
        self.label_27.setText(_translate("BaseDialog", "Grid size (m)"))
        self.txtEdt_GridSize.setText(_translate("BaseDialog", "enter the model grid size"))
        self.label_28.setText(_translate("BaseDialog", "Start simulation"))
        self.label_29.setText(_translate("BaseDialog", "Model General Configuration"))
        self.txtEdt_InputFolder.setText(_translate("BaseDialog", "chose folder with input files"))
        self.Btn_InputFolder.setText(_translate("BaseDialog", "Input"))
        self.txtEdt_OutputFolder.setText(_translate("BaseDialog", "chose folder to write the output results"))
        self.Btn_OutpuFolder.setText(_translate("BaseDialog", "Output"))
        self.Btn_Save.setText(_translate("BaseDialog", "Save"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("BaseDialog", "Project"))
        self.lineEdit_6.setText(_translate("BaseDialog", "Select the observed discharge file"))
        self.observed.setText(_translate("BaseDialog", "Q obs"))
        self.check_calibration.setText(_translate("BaseDialog", "Calibration"))
        self.label_6.setText(_translate("BaseDialog", "Kc maximum"))
        self.kc_max.setText(_translate("BaseDialog", "Kc maximum (0 to 1)"))
        self.kc_min.setText(_translate("BaseDialog", "Kc minimum (0 to 1)"))
        self.label_7.setText(_translate("BaseDialog", "Kc minimum"))
        self.label_8.setText(_translate("BaseDialog", "Fpar maximum"))
        self.Fpar_max.setText(_translate("BaseDialog", "Fpar maximum"))
        self.label_9.setText(_translate("BaseDialog", "Fpar minimum"))
        self.Fpar_min.setText(_translate("BaseDialog", "Fpar miniimum"))
        self.label_10.setText(_translate("BaseDialog", "Interceptation"))
        self.intercept.setText(_translate("BaseDialog", "Interceptation "))
        self.label_19.setText(_translate("BaseDialog", "CALIBRATION PARAMETER"))
        self.label_21.setText(_translate("BaseDialog", "CALIBRATION PARAMETER"))
        self.label_22.setText(_translate("BaseDialog", "CALIBRATION PARAMETER"))
        self.label_23.setText(_translate("BaseDialog", "CALIBRATION PARAMETER"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("BaseDialog", "Configuration"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_6), _translate("BaseDialog", "Ground Surface"))
        self.dem_box.setText(_translate("BaseDialog", "Select the ground elevation file"))
        self.dem.setText(_translate("BaseDialog", "Dem"))
        self.samples.setText(_translate("BaseDialog", "Samples"))
        self.sample_box.setText(_translate("BaseDialog", "Select the sample file"))
        self.land_use.setText(_translate("BaseDialog", "Land use"))
        self.land_box.setText(_translate("BaseDialog", "Select the Land use file"))
        self.label_11.setText(_translate("BaseDialog", "INITIAL SOIL CONDITIONS"))
        self.label_12.setText(_translate("BaseDialog", "Base flow initial (mm)"))
        self.label_13.setText(_translate("BaseDialog", "Base flow limit (mm)"))
        self.label_14.setText(_translate("BaseDialog", "Initial Soil Moisture (mm)"))
        self.label_15.setText(_translate("BaseDialog", "Tus initial (mm)"))
        self.label_16.setText(_translate("BaseDialog", "Delay Runoff"))
        self.label_17.setText(_translate("BaseDialog", "Delay base flow"))
        self.label_18.setText(_translate("BaseDialog", "SOIL PARAMETERS"))
        self.label_20.setText(_translate("BaseDialog", "Partitioning"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("BaseDialog", "Land use and Soil"))
        self.prep_box.setText(_translate("BaseDialog", "Select the precipitation file"))
        self.prep.setText(_translate("BaseDialog", "Precipitation"))
        self.evapo.setText(_translate("BaseDialog", "Evapotranspiration"))
        self.evapo_box.setText(_translate("BaseDialog", "Select the evapotranspiraton file"))
        self.Kp_box.setText(_translate("BaseDialog", "Select class A pan coefficient"))
        self.Kp.setText(_translate("BaseDialog", "Pan coefficient (Kp)"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("BaseDialog", "Weather"))
        self.check_config.setText(_translate("BaseDialog", "Check files"))
        self.run.setText(_translate("BaseDialog", "Run it"))
        self.exit.setText(_translate("BaseDialog", "Cancel"))
        self.model_image.setText(_translate("BaseDialog", "Figure model"))
        self.labsid_image.setText(_translate("BaseDialog", "Figure LabSid"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), _translate("BaseDialog", "Run"))
        self.poli_image.setText(_translate("BaseDialog", "Logo poli"))
        self.adp_image.setText(_translate("BaseDialog", "Logo ADP"))
        self.labsid_image_2.setText(_translate("BaseDialog", "LabSid"))
        self.info_text.setPlainText(_translate("BaseDialog", "Model description\n"
"\n"
"Model version\n"
"\n"
"Team development\n"
"\n"
"github and paper citation\n"
"\n"
"Acknowledge\n"
"\n"
"contact information\n"
""))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_7), _translate("BaseDialog", "Info"))
        self.label_25.setText(_translate("BaseDialog", "R.U.B.E.M."))

