import importQt as qt
from LabelEditAndButton import LabelEditAndButton
class CustomImageProcessingWidget (qt.QWidget):
    def __init__(self, dicParameter,parent=None):
        qt.QWidget.__init__(self, parent)
        self.parent = parent
        self.dicPar = dicParameter
        self.mainLayout = qt.QGridLayout()



    def update(self):
        while self.mainLayout.count():
            child = self.mainLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.title = qt.QLabel(self.dicPar['name'])
        self.runPushButton = qt.QPushButton('run')
        self.mainLayout.addWidget(self.title)
        self.addImageSelections()
        self.addParameters()
        self.mainLayout.addWidget(self.runPushButton)
        self.setLayout(self.mainLayout)


    def addImageSelections(self):
        list_name = self.dicPar['ImageSelection']
        self.listCBImages = []
        for name in list_name:
            self.mainLayout.addWidget(qt.QLabel(name))
            cb = qt.QComboBox()

            self.parent.formatH5.openCurrentArchive()
            for i, key in enumerate(list(self.parent.formatH5.archH5.keys())):
                name = self.parent.formatH5.archH5[f'{key}'].attrs['name']
                cb.addItem(name)
            self.parent.formatH5._closeArchive()

            self.listCBImages.append(cb)
            self.mainLayout.addWidget(cb)


    def addParameters(self):

        list_parameters = self.dicPar['LineEditParameters']['Names']
        initValue  = self.dicPar['LineEditParameters']['initValues']
        self.lineEditPar = []
        for i, name in enumerate(list_parameters):
            init_txtEdit = initValue[i]
            par = LabelEditAndButton(textLabel=name,textEdit=init_txtEdit,boolButton=False)
            self.lineEditPar.append(par)
            self.mainLayout.addWidget(par)







if __name__ == "__main__":

    app = qt.QApplication(["-display"])
    m = CustomImageProcessingWidget({})
    m.show()
    sys.exit(app.exec_())


