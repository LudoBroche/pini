# -*- coding: utf-8 -*-

import importQt as qt

class LabelEditAndButton(qt.QWidget) :

    def __init__(self,boolLabel=True,textLabel="text1",booltextEdit=True,textEdit="text2", boolButton=True,textButton="text3",parent=None) :
        qt.QWidget.__init__(self, parent)
        self.textLabel=textLabel
        self.textEdit=textEdit
        self.textButton=textButton;
        self.boolLabel=boolLabel
        self.booltextEdit=booltextEdit
        self.boolButton=boolButton
        self._build()

    def _build(self) :
        self.layout=qt.QHBoxLayout()
        self.label =None
        self.lineEdit =None
        self.button =None
        if(self.boolLabel) :
            self.label=qt.QLabel(self.textLabel,self)
            self.layout.addWidget(self.label)
        if(self.booltextEdit) :
            self.lineEdit= qt.QLineEdit(self.textEdit,self)
            self.layout.addWidget(self.lineEdit)
        if(self.boolButton) :
            self.button=qt.QPushButton(self.textButton,self)
            self.layout.addWidget(self.button)

        self.setLayout(self.layout)

    def changeLabel(self,textLabel):
        self.textLabel=textLabel
        self.label.setText(self.textLabel)

    def changeLineEdit(self,textLineEit):
        self.textEdit=textLineEit
        self.lineEdit.setText(self.textEdit)

    def valueLineEdit(self):
        self.textEdit=self.lineEdit.text()
        return self.textEdit

