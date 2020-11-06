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
        BaseDialog.resize(721, 433)
        self.buttonBox = QtWidgets.QDialogButtonBox(BaseDialog)
        self.buttonBox.setGeometry(QtCore.QRect(500, 390, 193, 28))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.lineEdit = QtWidgets.QLineEdit(BaseDialog)
        self.lineEdit.setGeometry(QtCore.QRect(10, 30, 301, 31))
        self.lineEdit.setObjectName("lineEdit")
        self.pushButton = QtWidgets.QPushButton(BaseDialog)
        self.pushButton.setGeometry(QtCore.QRect(320, 30, 93, 28))
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(BaseDialog)
        self.buttonBox.accepted.connect(BaseDialog.accept)
        self.buttonBox.rejected.connect(BaseDialog.reject)
        self.pushButton.clicked.connect(BaseDialog.DemSearch)
        QtCore.QMetaObject.connectSlotsByName(BaseDialog)

    def retranslateUi(self, BaseDialog):
        _translate = QtCore.QCoreApplication.translate
        BaseDialog.setWindowTitle(_translate("BaseDialog", "Dialog"))
        self.pushButton.setText(_translate("BaseDialog", "Dem"))

