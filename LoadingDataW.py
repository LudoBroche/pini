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


        if (nb_vector_3d != 0) or (nb_vector_2d !=0):
            if (nb_vector_3d != 0) and (nb_vector_2d !=0):
                print('error')
            elif (nb_vector_3d != 0):
                infoTxt += " including 3D vector field(s)"
                flag_vector_3D = True
                pos_axis_v3D = shapeImage.index(3)
            else:
                infoTxt += " including 2D vector field(s)"
                flag_vector_2D = True
                pos_axis_v2D = shapeImage.index(2)

        listWidgetAxis = []


        layoutHorizontal = qt.QHBoxLayout()
        for i in range(0,nbAxis):
            comboBox = qt.QComboBox()
            if nbAxis == 2:
                listToDisplay = ['X','Y','Angle']
            elif nbAxis == 3:
                if not flag_vector_2D:
                    listToDisplay = ['X','Y','Z','Time','Angle']
                else:
                    if i == pos_axis_v2D:
                        listToDisplay = ['(Dx,Dy)']
                    else:
                        listToDisplay = ['X', 'Y']
            elif nbAxis == 4:
                if not flag_vector_2D and not flag_vector_3D:
                    listToDisplay = ['X','Y','Z','Time']
                elif flag_vector_2D:
                    if i == pos_axis_v2D:
                        listToDisplay = ['(Dx,Dy)']
                    else:
                        listToDisplay = ['X', 'Y' , 'T']
                else:
                    if i == pos_axis_v3D:
                        listToDisplay = ['(Dx,Dy,Dz)']
                    else:
                        listToDisplay = ['X', 'Y' , 'Z']
            elif nbAxis == 5:
                if flag_vector_3D:
                    if i == pos_axis_v3D:
                        listToDisplay = ['(Dx,Dy,Dz)']
                    else:
                        listToDisplay = ['X', 'Y', 'Z', 'T']

                else:
                    print('error')
            comboBox.addItems(listToDisplay)
            layoutHorizontal.addWidget(comboBox)


        label = qt.QLabel(infoTxt)

        self.layoutLoadingData.addWidget(label)
        self.layoutLoadingData.addLayout(layoutHorizontal,1,0)


        self.mainWidget.setLayout(self.layoutLoadingData)
        self.setCentralWidget(self.mainWidget)
        self.show()

if __name__ == "__main__":
    name = 'Image'
    Path = '\\data\\'
    dtype = type('uint16')
    shapeImage = (400,500)

    app = qt.QApplication(["-display"])
    m =  LoadingDataW(shapeImage=shapeImage,dtypeData=dtype,nameImage=name,pathImage=Path)
    #m.show()
    sys.exit(app.exec_())



