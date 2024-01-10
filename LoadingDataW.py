
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

        nbAxis = len(self.shapeData)
        nb_vector_2d = self.shapeData.count(2)
        nb_vector_3d = self.shapeData.count(3)


        infoTxt = "%d axis detected"%nbAxis
        self.flag_vector_3D = False
        self.flag_vector_2D = False
        self.pos_axis_v2D = -1
        self.pos_axis_v3D = -1

        if (nb_vector_3d != 0) or (nb_vector_2d !=0):
            if (nb_vector_3d != 0) and (nb_vector_2d !=0):
                msg = qt.QMessageBox()
                msg.setIcon(qt.QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText('Incorect Vector field format')
                msg.setWindowTitle("Error")
                msg.exec_()
                self.close()
                return 0
            elif (nb_vector_3d != 0):
                infoTxt += " including 3D vector field(s)"
                self.flag_vector_3D = True
                self.pos_axis_v3D = self.shapeData.index(3)
            else:
                infoTxt += " including 2D vector field(s)"
                self.flag_vector_2D = True
                self.pos_axis_v2D = self.shapeData.index(2)


        layoutName = qt.QHBoxLayout()
        label = qt.QLabel('Image Name')
        self.nameEdit = qt.QLineEdit(self.nameImage)

        layoutName.addWidget(label)
        layoutName.addWidget(self.nameEdit)

        self.nameEdit.textChanged.connect(self._changeNameImage)

        self.listWidgetAxis = []
        self.listUnitCB = []
        self.listUnitLineEdit = []
        self.listWidgetLabels = []


        layoutHorizontal = qt.QHBoxLayout()
        labelLayout = qt.QHBoxLayout()
        layoutHorizontalU = qt.QHBoxLayout()

        indexPreSelect = 0

        for i in range(0,nbAxis):
            comboBox = qt.QComboBox()
            unitCB = UnitEditor()
            unitCB.unitValueEdit.editingFinished.connect(self._unitValueChanged)
            unitCB.unitValueEdit.textChanged.connect(self._unitValueEditing)
            unitCB.unitCB.currentIndexChanged.connect(self._unitComboChanged)
            unitCB.unitValueEdit.setObjectName(str(i))
            unitCB.unitCB.setObjectName(str(i))
            self.listUnitCB.append(unitCB)
            if nbAxis == 1:
                msg = qt.QMessageBox()
                msg.setIcon(qt.QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText('1D Data detected')
                msg.setWindowTitle("Error")
                msg.exec_()
                self.close()
                return 0

            elif nbAxis == 2:
                listToDisplay = ['X','Y','Angle']
                indexPreSelect += 1
            elif nbAxis == 3:
                if self.flag_vector_3D:
                    msg = qt.QMessageBox()
                    msg.setIcon(qt.QMessageBox.Critical)
                    msg.setText("Error")
                    msg.setInformativeText('3D Vector Field is not compatible with 2D images')
                    msg.setWindowTitle("Error")
                    msg.exec_()
                    self.close()
                    return 0

                elif not self.flag_vector_2D:
                    listToDisplay = ['X','Y','Z','Time','Angle']
                    indexPreSelect += 1
                else:
                    if i == self.pos_axis_v2D:
                        listToDisplay = ['(Dx,Dy)']
                    else:
                        listToDisplay = ['X', 'Y']
                        indexPreSelect += 1
            elif nbAxis == 4:
                if not self.flag_vector_2D and not self.flag_vector_3D:
                    listToDisplay = ['X','Y','Z','Time']
                    indexPreSelect += 1
                elif self.flag_vector_2D:
                    if i == self.pos_axis_v2D:
                        listToDisplay = ['(Dx,Dy)']
                    else:
                        listToDisplay = ['X', 'Y', 'Time']
                        indexPreSelect += 1
                else:
                    if i == self.pos_axis_v3D:
                        listToDisplay = ['(Dx,Dy,Dz)']
                    else:
                        listToDisplay = ['X', 'Y', 'Z']
                        indexPreSelect += 1
            elif nbAxis == 5:
                if self.flag_vector_3D:
                    if i == self.pos_axis_v3D:
                        listToDisplay = ['(Dx,Dy,Dz)']
                    else:
                        listToDisplay = ['X', 'Y', 'Z', 'Time']
                        indexPreSelect += 1

                else:
                    msg = qt.QMessageBox()
                    msg.setIcon(qt.QMessageBox.Critical)
                    msg.setText("Error")
                    msg.setInformativeText('Data with too many axis')
                    msg.setWindowTitle("Error")
                    msg.exec_()
                    self.close()

            comboBox.addItems(listToDisplay)

            if (not self.flag_vector_2D and not self.flag_vector_3D) or ((i != self.pos_axis_v2D) and (i != self.pos_axis_v3D)):
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

            unitType = unitCB.unitCB.currentText()
            pxSize = unitCB.unitValueEdit.text()
            value = float(pxSize) * self.shapeData[i]

            unitType, value = self._convertUnit(unitType,value)

            if (not self.flag_vector_2D and not self.flag_vector_3D) or ((i != self.pos_axis_v2D) and (i != self.pos_axis_v3D)):
                labelAxis = qt.QLabel(f'Axe{i} ({self.shapeData[i]} px - {value:.2f} {unitType})')
            elif  self.flag_vector_3D:
                labelAxis = qt.QLabel(f'Axe{i} (3D Vector Field)')
            else:
                labelAxis = qt.QLabel(f'Axe{i} (2D Vector Field)')


            labelAxis.setAlignment(qt.Qt.AlignCenter)
            self.listWidgetLabels.append(labelAxis)
            labelLayout.addWidget(labelAxis)


        label = qt.QLabel(infoTxt)
        label.setAlignment(qt.Qt.AlignCenter)

        self.validateButton = qt.QPushButton('Load')
        verticalSpacerBig = qt.QSpacerItem(20, 20, qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        verticalSpacerSmall = qt.QSpacerItem(20, 5, qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)

        self.layoutLoadingData.addLayout(layoutName,0,0)
        self.layoutLoadingData.addItem(verticalSpacerBig)
        self.layoutLoadingData.addWidget(label)
        self.layoutLoadingData.addItem(verticalSpacerSmall)
        self.layoutLoadingData.addLayout(labelLayout,4,0)
        self.layoutLoadingData.addLayout(layoutHorizontal,5,0)
        self.layoutLoadingData.addLayout(layoutHorizontalU, 6, 0)
        self.layoutLoadingData.addItem(verticalSpacerBig)
        self.layoutLoadingData.addWidget(self.validateButton)


        self.mainWidget.setLayout(self.layoutLoadingData)
        self.setCentralWidget(self.mainWidget)


    def _convertUnit(self,unitType, value):

        distanceList = ['m','mm','μm','nm','pm']
        angleList = ['°','rad','mrad','μrad']
        timeList = ['Days','Hours','min','s','ms','μs','ns','ps','fs']

        if unitType in distanceList:
            if value < 1 and unitType != 'pm':
                unitTypeNew = distanceList[distanceList.index(unitType)+1]
                valueNew = value * 1000.0
                unitTypeNew, valueNew = self._convertUnit(unitTypeNew,valueNew)
            elif value > 1000.0 and unitType != 'm':
                unitTypeNew = distanceList[distanceList.index(unitType)-1]
                valueNew = value / 1000.0
                unitTypeNew, valueNew = self._convertUnit(unitTypeNew, valueNew)
            else:
                unitTypeNew = unitType
                valueNew = value

        elif unitType in  angleList:
            if unitType in ['rad','mrad','μrad']:

                if value < 1  and unitType != 'μrad':
                    unitTypeNew = angleList[angleList.index(unitType) + 1]
                    valueNew = value * 1000.0
                    unitTypeNew, valueNew = self._convertUnit(unitTypeNew, valueNew)
                elif value > 1000  and unitType != 'rad':
                    unitTypeNew = angleList[angleList.index(unitType) - 1]
                    valueNew = value / 1000.0
                    unitTypeNew, valueNew = self._convertUnit(unitTypeNew, valueNew)
                else:
                    unitTypeNew = unitType
                    valueNew = value

            elif unitType == '°':
                unitTypeNew = unitType
                valueNew = value
            elif unitType == '360/°':
                unitTypeNew = unitType
                valueNew = int(value)


        elif unitType in timeList:
            if value > 24 and unitType  ==  'Hours':
                valueNew = value/24.0
                unitTypeNew = timeList[timeList.index(unitType)-1]
            elif value > 60 and (unitType in ['min','s']):
                valueNew = value/60.0
                unitTypeNew = timeList[timeList.index(unitType)-1]
                unitTypeNew, valueNew = self._convertUnit(unitTypeNew, valueNew)
            elif value > 1000.0 and unitType != 'Days':
                valueNew = value / 1000.0
                unitTypeNew = timeList[timeList.index(unitType) - 1]
                unitTypeNew, valueNew = self._convertUnit(unitTypeNew, valueNew)
            elif value < 1 and unitType  ==  'Days':
                valueNew = 24.0 * value
                unitTypeNew = timeList[timeList.index(unitType)+1]
                unitTypeNew, valueNew = self._convertUnit(unitTypeNew, valueNew)
            elif value <1 and (unitType in ['Hours','min']):
                valueNew = value * 60
                unitTypeNew = timeList[timeList.index(unitType) + 1]
                unitTypeNew, valueNew = self._convertUnit(unitTypeNew, valueNew)
            elif value <1 and unitType != 'fs':
                valueNew = value *1000.0
                unitTypeNew = timeList[timeList.index(unitType) + 1]
                unitTypeNew, valueNew = self._convertUnit(unitTypeNew, valueNew)
            else:
                unitTypeNew = unitType
                valueNew = value
        else:
            unitTypeNew = unitType
            valueNew =value

        return unitTypeNew, valueNew

    def _unitComboChanged(self):

        indexChanged = int(self.sender().objectName())
        if len(self.listWidgetLabels) > indexChanged:
            unitSelect = self.sender().currentText()
            unitLineEdit =  self.listUnitCB[indexChanged].unitValueEdit

            if unitSelect == 'px':
                unitLineEdit.setText('1.0')
                unitLineEdit.setDisabled(True)
            else:
                unitLineEdit.setDisabled(False)
            indexTxt = unitLineEdit.text()

            unitLineEdit.setText(str(indexTxt))


            labelW = self.listWidgetLabels[indexChanged]
            try:
                float(indexTxt)
            except ValueError:
                indexTxt = '1.0'

            indexTxt = str(abs(float(indexTxt)))


            value = self.shapeData[indexChanged] * float(indexTxt)

            unitLabel, valueLabel = self._convertUnit(unitSelect,value)


            if (not self.flag_vector_2D and not self.flag_vector_3D) or ((indexChanged != self.pos_axis_v2D) and (indexChanged != self.pos_axis_v3D)):
                txtToDisplay = f'Axe{indexChanged} ({self.shapeData[indexChanged]} px - {valueLabel:.2f} {unitLabel})'
            elif  self.flag_vector_3D:
                txtToDisplay = f'Axe{indexChanged} (3D Vector Field)'
            else:
                txtToDisplay = f'Axe{indexChanged} (2D Vector Field)'



            labelW.setText(txtToDisplay)
            labelW.setAlignment(qt.Qt.AlignCenter)
    def _unitValueEditing(self):
        indexChanged = int(self.sender().objectName())
        unitCB = self.listUnitCB[indexChanged].unitCB
        unitCB.setDisabled(True)

    def _unitValueChanged(self):
        indexTxt = self.sender().text()
        indexChanged = int(self.sender().objectName())
        unitCB =  self.listUnitCB[indexChanged].unitCB
        labelW = self.listWidgetLabels[indexChanged]

        try:
            float(indexTxt)
        except ValueError:
            indexTxt = '1.0'

        indexTxt = str(abs(float(indexTxt)))


        value = self.shapeData[indexChanged] * float(indexTxt)
        unitLabel, valueLabel = self._convertUnit(unitCB.currentText(),value)
        unit, value = self._convertUnit(unitCB.currentText(), float(indexTxt))

        unitCB.setCurrentText(unit)
        self.sender().setText(str(value))


        if (not self.flag_vector_2D and not self.flag_vector_3D) or (
                (indexChanged != self.pos_axis_v2D) and (indexChanged != self.pos_axis_v3D)):
            txtToDisplay = f'Axe{indexChanged} ({self.shapeData[indexChanged]} px - {valueLabel:.2f} {unitLabel})'
        elif self.flag_vector_3D:
            txtToDisplay = f'Axe{indexChanged} (3D Vector Field)'
        else:
            txtToDisplay = f'Axe{indexChanged} (2D Vector Field)'


        labelW.setText(txtToDisplay)
        labelW.setAlignment(qt.Qt.AlignCenter)
        unitCB.setDisabled(False)

    def _changeNameImage(self):

        nameWindow = f'{self.nameEdit.text()}    {self.pathData}'
        self.setWindowTitle(nameWindow)

    def _comboBoxChanged(self):

        indexTxt = self.sender().currentText()
        indexChanged = int(self.sender().objectName())
        unitCB = self.listUnitCB[indexChanged]

        labelW = self.listWidgetLabels[indexChanged]


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


        value = self.shapeData[indexChanged] * float(unitCB.unitValueEdit.text())
        unitType =  unitCB.unitCB.currentText()
        unit, value = self._convertUnit(unitType,value)


        if (not self.flag_vector_2D and not self.flag_vector_3D) or (
                (indexChanged != self.pos_axis_v2D) and (indexChanged != self.pos_axis_v3D)):
            txtToDisplay = f'Axe{indexChanged} ({self.shapeData[indexChanged]} px - {value:.2f} {unit})'
        elif self.flag_vector_3D:
            txtToDisplay = f'Axe{indexChanged} (3D Vector Field)'
        else:
            txtToDisplay = f'Axe{indexChanged} (2D Vector Field)'

        labelW.setText(txtToDisplay)
        labelW.setAlignment(qt.Qt.AlignCenter)
        unitCB.unitCB.setDisabled(False)

class EditableComboBox(qt.QComboBox):
    def __init__(self):
        qt.QComboBox.__init__(self)
        self.currentIndexChanged.connect(self.fix)
        self.setInsertPolicy(qt.QComboBox.InsertAtCurrent)
        setattr(self, "allItems", lambda: [self.itemText(i) for i in range(self.count())])

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

        self.distanceList = ['m','mm','μm','nm','pm']
        self.angleList = ['°','rad','mrad','μrad']
        self.timeList = ['Days','Hours','min','s','ms','μs','ns','ps','fs']


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
        self.unitCB.addItems(list)
        self.unitCB.addItem('px')

        self.unitCB.addItem('---','Custom')
        a = self.unitCB.allItems()

if __name__ == "__main__":

    name = 'Image'
    Path = '\\data\\'
    dtype = type('uint16')
    shapeImage = (500,2,300,20)



    app = qt.QApplication(["-display"])
    m =  LoadingDataW(shapeImage=shapeImage,dtypeData=dtype,nameImage=name,pathImage=Path)
    m.show()
    sys.exit(app.exec_())


