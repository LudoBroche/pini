import importQt as qt
import sys
class LoadingDataW(qt.QMainWindow):
    def __init__(self,shapeImage,dtypeData, nameImage,pathImage,parent=None ):
        qt.QMainWindow.__init__(self, parent)

        self.shapeData = shapeImage
        self.dtypeData = dtypeData
        self.nameImage = nameImage
        self.pathData = pathImage
        self._buildLayout()

    def _buildLayout(self):
        stringLabel = self.nameImage + ' '*5 + self.pathData
        self.setWindowTitle(stringLabel)
        self.setWindowIcon(qt.QIcon('./Icones/transp.png'))

        self.mainWidget = qt.QWidget()
        self.layoutLoadingData = qt.QGridLayout()

        nbAxis = len(shapeImage)
        nb_vector_2d = shapeImage.count(2)
        nb_vector_3d = shapeImage.count(3)


        infoTxt = "%d axis detected"%nbAxis
        flag_vector_3D = False
        flag_vector_2D = False
        pos_axis_v2D = -1
        pos_axis_v3D = -1

        if (nb_vector_3d != 0) or (nb_vector_2d !=0):
            if (nb_vector_3d != 0) and (nb_vector_2d !=0):
                msg = qt.QMessageBox()
                msg.setIcon(qt.QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText('Incorect Vector field format')
                msg.setWindowTitle("Error")
                msg.exec_()
            elif (nb_vector_3d != 0):
                infoTxt += " including 3D vector field(s)"
                flag_vector_3D = True
                pos_axis_v3D = shapeImage.index(3)
            else:
                infoTxt += " including 2D vector field(s)"
                flag_vector_2D = True
                pos_axis_v2D = shapeImage.index(2)

        self.listWidgetAxis = []
        self.listUnitCB = []
        listWidgetLabels = []


        layoutHorizontal = qt.QHBoxLayout()
        labelLayout = qt.QHBoxLayout()
        layoutHorizontalU = qt.QHBoxLayout()

        indexPreSelect = 0

        for i in range(0,nbAxis):
            comboBox = qt.QComboBox()
            unitCB = UnitEditor()
            self.listUnitCB.append(unitCB)
            if nbAxis == 1:
                msg = qt.QMessageBox()
                msg.setIcon(qt.QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText('1D Data detected')
                msg.setWindowTitle("Error")
                msg.exec_()

            elif nbAxis == 2:
                listToDisplay = ['X','Y','Angle']
                indexPreSelect += 1
            elif nbAxis == 3:
                if not flag_vector_2D:
                    listToDisplay = ['X','Y','Z','Time','Angle']
                    indexPreSelect += 1
                else:
                    if i == pos_axis_v2D:
                        listToDisplay = ['(Dx,Dy)']
                    else:
                        listToDisplay = ['X', 'Y']
                        indexPreSelect += 1
            elif nbAxis == 4:
                if not flag_vector_2D and not flag_vector_3D:
                    listToDisplay = ['X','Y','Z','Time']
                    indexPreSelect += 1
                elif flag_vector_2D:
                    if i == pos_axis_v2D:
                        listToDisplay = ['(Dx,Dy)']
                    else:
                        listToDisplay = ['X', 'Y', 'T']
                        indexPreSelect += 1
                else:
                    if i == pos_axis_v3D:
                        listToDisplay = ['(Dx,Dy,Dz)']
                    else:
                        listToDisplay = ['X', 'Y', 'Z']
                        indexPreSelect += 1
            elif nbAxis == 5:
                if flag_vector_3D:
                    if i == pos_axis_v3D:
                        listToDisplay = ['(Dx,Dy,Dz)']
                    else:
                        listToDisplay = ['X', 'Y', 'Z', 'T']
                        indexPreSelect += 1

                else:
                    msg = qt.QMessageBox()
                    msg.setIcon(qt.QMessageBox.Critical)
                    msg.setText("Error")
                    msg.setInformativeText('Data with too many axis')
                    msg.setWindowTitle("Error")
                    msg.exec_()

            comboBox.addItems(listToDisplay)
            if (not flag_vector_2D and not flag_vector_3D) or ((i != pos_axis_v2D) and (i != pos_axis_v3D)):
                comboBox.setCurrentIndex(indexPreSelect-1)
                comboBox.setEnabled(True)
                comboBox.currentTextChanged.connect(self._comboBoxChanged)
            else :
                comboBox.setCurrentIndex(0)
                comboBox.setEnabled(False)

            if comboBox.currentText() in ['X', 'Y', 'Z', '(Dx,Dy)', '(Dx,Dy,Dz)']:
                unitCB.setDistanceList()
            elif comboBox.currentText() == 'Time':
                unitCB.setTimeList()
            elif comboBox.currentText() == 'Angle':
                unitCB.setAngleList()

            comboBox.setObjectName(str(i))
            self.listWidgetAxis.append(comboBox)
            layoutHorizontal.addWidget(comboBox)
            layoutHorizontalU.addLayout(unitCB)
            labelAxis = qt.QLabel('Axe%d (%d px)'%(i,shapeImage[i]))
            listWidgetLabels.append(labelAxis)
            labelLayout.addWidget(labelAxis)


        label = qt.QLabel(infoTxt)

        self.layoutLoadingData.addWidget(label)
        self.layoutLoadingData.addLayout(labelLayout,1,0)
        self.layoutLoadingData.addLayout(layoutHorizontal,2,0)
        self.layoutLoadingData.addLayout(layoutHorizontalU, 3, 0)


        self.mainWidget.setLayout(self.layoutLoadingData)
        self.setCentralWidget(self.mainWidget)
        self.show()

    def _comboBoxChanged(self):
        indexTxt = self.sender().currentText()
        indexChanged = int(self.sender().objectName())
        unitCB = self.listUnitCB[indexChanged]

        if indexTxt in ['X','Y','Z','(Dx,Dy)','(Dx,Dy,Dz)']:
            unitCB.setDistanceList()
        elif indexTxt == 'Time':
            unitCB.setTimeList()
        elif indexTxt == 'Angle':
            unitCB.setAngleList()

        for w in self.listWidgetAxis:
            if (w.objectName() != self.sender().objectName()) and (indexTxt == w.currentText()):
                AllItems = [w.itemText(i) for i in range(w.count())]

                for item in AllItems:
                    flag_item_good = True
                    for wi in self.listWidgetAxis:
                        if item == wi.currentText():
                            flag_item_good = False
                    if flag_item_good:
                        itemToUse = item
                        break
                w.setCurrentText(itemToUse)




        # if self.sender().isChecked():
        #     idImport = self.sender().objectName()
        #     boxImport = self.list_item_load[int(idImport)]
        #     if boxImport.isChecked():
        #         boxImport.setChecked(False)

class EditableComboBox(qt.QComboBox):
    def __init__(self):
        qt.QComboBox.__init__(self)
        self.currentIndexChanged.connect(self.fix)
        self.setInsertPolicy(qt.QComboBox.InsertAtCurrent)

    def fix(self, index):
        if (self.currentData() == 'Custom'):
            self.setEditable(True)
        else:
            self.setEditable(False)


class UnitEditor(qt.QHBoxLayout):
    def __init__(self):
        qt.QWidget.__init__(self)
        self.unitValueEdit = qt.QLineEdit()
        self.unitValueEdit.setText('1.0')
        self.unitCB = EditableComboBox()

        self.addWidget(self.unitValueEdit)
        self.addWidget(self.unitCB)

        self.distanceList = ['m','mm','μm','nm','Å','pm']
        self.angleList = ['°','rad','projections (360)']
        self.timeList = ['Days','Hours','m','s','ms','μs','ns','ps','fs']


    def setDistanceList(self):
        self.addItemsCB(self.distanceList)
        self.unitCB.setCurrentIndex(2)
    def setAngleList(self):
        self.addItemsCB(self.angleList)
        self.unitValueEdit.setText(str(360.0/1000.0))
    def setTimeList(self):
        self.addItemsCB(self.timeList)
        self.unitCB.setCurrentIndex(3)

    def addItemsCB(self,list):
        self.unitCB.clear()
        for item in list:
            self.unitCB.addItem(item,item)

        self.unitCB.addItem('---','Custom')



if __name__ == "__main__":
    name = 'Image'
    Path = '\\data\\'
    dtype = type('uint16')
    shapeImage = (500,500)

    app = qt.QApplication(["-display"])
    m =  LoadingDataW(shapeImage=shapeImage,dtypeData=dtype,nameImage=name,pathImage=Path)
    #m.show()
    sys.exit(app.exec_())



