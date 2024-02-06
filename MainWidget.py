import os.path

import importQt as qt
import pyqtgraph as pg
import copy
import psutil
import fabio

from SliceViualizer import Interactor3D
from VolumeRenderingGUI import VolumeRenderingGUI
from ProgressBarWidget import ProgressBar
from FileFormatArchive import ArchiveHdf5
from LoadingDataW import LoadingDataW

class AlignDelegate(qt.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = qt.Qt.AlignCenter

class IconDelegate(qt.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(IconDelegate, self).initStyleOption(option, index)
        if option.features & qt.QStyleOptionViewItem.HasDecoration:
            s = option.decorationSize
            s.setWidth(option.rect.width())
            option.decorationSize = s

class MainWidget(qt.QWidget):
    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)

        """ Attributs """

        self.parent = parent
        self.DataRam = {}
        self.Items_list = []
        self.Name_list = []

        """ Widgets Initialisation """

        self.mainLayout = qt.QGridLayout()

        self.tabWidget = qt.QTabWidget()
        self.tabPlanesView = qt.QWidget()
        self.tab3DViewer = qt.QWidget()

        self.plt = pg.GraphicsLayoutWidget()
        self.plt.hide()

        self.layoutViewPlanes = qt.QGridLayout()
        self.buttonLayout = qt.QVBoxLayout()
        self.image3DWidget = Interactor3D(self)

        self._imageSelectionBuildTable()

        self.progressBar = ProgressBar(self)

        self.systemInfo1 = qt.QLabel()
        fontSystem = self.systemInfo1.font()
        fontSystem.setPointSize(10)
        self.systemInfo1.setFont(fontSystem)

        self.systemInfo2 = qt.QLabel()
        fontSystem = self.systemInfo2.font()
        fontSystem.setPointSize(10)
        self.systemInfo2.setFont(fontSystem)

        self.timer = qt.QTimer()
        self.timer.start(1000)


        self.layout3d = qt.QGridLayout()
        self.volumeRenderingGUI = VolumeRenderingGUI()

        """ Widgets Design """
        self.imageSelection.setMaximumWidth(250)

        """Signals"""

        self.timer.timeout.connect(self._updatePcInfo)

        #self.imageSelection.customContextMenuRequested.connect(self._listItemRightClicked)
        #self.imageSelection.currentRowChanged.connect(self._dataToShowChanged)

        self.image3DWidget.axialWidget.MovedOnVizualizer.connect(self._moved)
        self.image3DWidget.coronalWidget.MovedOnVizualizer.connect(self._moved)
        self.image3DWidget.sagittalWidget.MovedOnVizualizer.connect(self._moved)
        self.image3DWidget.axialWidget.clickedOnVizualizer.connect(self._cliked)
        self.image3DWidget.coronalWidget.clickedOnVizualizer.connect(self._cliked)
        self.image3DWidget.sagittalWidget.clickedOnVizualizer.connect(self._cliked)
        self.image3DWidget.axialWidget.releasedOnVizualizer.connect(self._released)
        self.image3DWidget.coronalWidget.releasedOnVizualizer.connect(self._released)
        self.image3DWidget.sagittalWidget.releasedOnVizualizer.connect(self._released)
        self.image3DWidget.toolBar.radius.lineEdit.textChanged.connect(self._changeRadius)
        self.image3DWidget.toolBar.pointRemoveAction.triggered.connect(self._removeItems)

        self.tabWidget.currentChanged.connect(self._tabChanged)

        """Widget Placement"""
        self.buttonLayout.addWidget(self.imageSelection)
        self.buttonLayout.setAlignment(qt.Qt.AlignTop)

        self.layoutViewPlanes.addWidget(self.image3DWidget, 0, 0)
        self.layoutViewPlanes.addWidget(self.plt, 0, 1)
        self.layoutViewPlanes.addLayout(self.buttonLayout, 0, 2)
        self.layoutViewPlanes.addWidget(self.progressBar, 1, 0)
        self.layoutViewPlanes.addWidget(self.systemInfo1, 1, 2)
        self.layoutViewPlanes.addWidget(self.systemInfo2, 2, 2)

        self.tabPlanesView.setLayout(self.layoutViewPlanes)

        self.layout3d.addWidget(self.volumeRenderingGUI)
        self.tab3DViewer.setLayout(self.layout3d)

        self.tabWidget.addTab(self.tabPlanesView, '2D Viewer')
        self.tabWidget.addTab(self.tab3DViewer, '3D Viewer')

        self.mainLayout.addWidget(self.tabWidget)
        self.setLayout(self.mainLayout)


    def _imageSelectionBuildTable(self):


        self.imageSelection = qt.QTableWidget(self)

        self.imageSelection.setRowCount(0)
        self.imageSelection.setColumnCount(3)
        self.imageSelection.setShowGrid(False)
        self.imageSelection.horizontalHeader().hide()


    def _imageSelectionUpdateImage(self):
        self.parent.startUpArchive.arch.openCurrentArchive()
        self.formatH5 = self.parent.startUpArchive.arch
        self.formatH5.openCurrentArchive()


        currentRowCount = self.imageSelection.rowCount()

        while len(list(self.formatH5.archH5.keys())) < currentRowCount:
            self.imageSelection.removeRow(0)
            currentRowCount = self.imageSelection.rowCount()


        for i, key in  enumerate(list(self.formatH5.archH5.keys())):
            if i >= currentRowCount:
                self.imageSelection.insertRow(i)


            wRamHdd = qt.QPushButton()
            #wRamHdd.setIcon(qt.QIcon('./Icones/hdd.png'))
            wRamHdd.setFlat(True)
            wRamHdd.setCheckable(True)
            wRamHdd.setStyleSheet("QPushButton: flat;border: none")
            wRamHdd.setObjectName(f'{i}')
            if self.formatH5.archH5[f'{key}'].attrs['flag_streaming']:
                wRamHdd.setIcon(qt.QIcon('./Icones/hdd.png'))
                wRamHdd.setChecked(False)
            else:
                wRamHdd.setIcon(qt.QIcon('./Icones/ram.png'))
                wRamHdd.setChecked(True)


            deleteButton = qt.QPushButton()
            deleteButton.setIcon(qt.QIcon('./Icones/trash.png'))
            deleteButton.setFlat(True)
            deleteButton.setCheckable(True)
            deleteButton.setStyleSheet("QPushButton: flat;border: none")
            deleteButton.setObjectName(f'{i}')


            label = qt.QLineEdit(self.formatH5.archH5[f'{key}'].attrs['name'])
            label.setFrame(False)
            label.editingFinished.connect(self.nameDataSetChange)
            label.setObjectName(f'{i}')

            txt = self.formatH5.generateInfotxt(key)
            label.setToolTip(txt)

            self.imageSelection.setCellWidget(i,0,label)
            self.imageSelection.setCellWidget(i,1,wRamHdd)
            self.imageSelection.setCellWidget(i, 2, deleteButton)

            wRamHdd.clicked.connect(self._ImageSelectionRamHddButtonClicked)
            deleteButton.clicked.connect(self._ImageSelectionDeleteData)

        self.imageSelection.horizontalHeader().setSectionResizeMode(0, qt.QHeaderView.ResizeToContents)
        self.imageSelection.horizontalHeader().setSectionResizeMode(1, qt.QHeaderView.ResizeToContents)
        self.imageSelection.horizontalHeader().setSectionResizeMode(2, qt.QHeaderView.ResizeToContents)
        self.formatH5._closeArchive()

    def nameDataSetChange(self):
        self.formatH5.openCurrentArchive()
        index = int(self.sender().objectName())
        name = self.sender().text()
        self.formatH5.archH5[f'{index:05}'].attrs['name'] = name
        self.formatH5._closeArchive()
        self._imageSelectionUpdateImage()

    def _ImageSelectionDeleteData(self):
        indexDelete = self.sender().objectName()
        self.formatH5.deleteImage(int(indexDelete))
        self._imageSelectionUpdateImage()
        #self.imageSelection.setCellWidget(int(indexDelete),2)



    def _ImageSelectionRamHddButtonClicked(self):
        index = self.sender().objectName()
        if self.sender().isChecked():
            self.sender().setIcon(qt.QIcon('./Icones/ram.png'))
            error = self.formatH5.loadDataToRam(int(index))
            if not error:
                self.sender().setChecked(False)
                self.sender().setIcon(qt.QIcon('./Icones/hdd.png'))
        else:
            self.sender().setIcon(qt.QIcon('./Icones/hdd.png'))
            self.formatH5.removeDataFromRam(int(index))


    def _updatePcInfo(self):

            path = self.parent.setting.parameter['pini_parameters']['home_collection']['path']
            hdd = psutil.disk_usage(str(path))

            if (hdd.total // (2 ** 30)) > 1000:
                string_space = f'HDD: {hdd.used//(2 ** 30 * 1000)}/{ hdd.total // (2 ** 30 * 1000)} TiB [{hdd.percent} %]'

            else:
                string_space = f'HDD: {hdd.used//2 ** 30}/{hdd.total // 2 ** 30} GiB ( {hdd.percent} % )'

            mem = psutil.virtual_memory()
            cpu = psutil.cpu_percent()

            if (mem.total // (2**30)) > 1000:
                string_mem = f'CPU: {cpu} % | RAM: {mem.used//(2 ** 30 * 1000)}/{mem.total // (2 ** 30 * 1000)} TiB [{mem.percent} %]'
            else:
                string_mem = f'CPU: {cpu} % | RAM: {mem.used // (2 ** 30)}/{mem.total // (2 ** 30)} GiB [{mem.percent} %]'

            self.systemInfo1.setText(string_space)
            self.systemInfo2.setText(string_mem)


    def _listItemRightClicked(self, QPos):
        listMenu = qt.QMenu()
        remove_item = listMenu.addAction("Delete")
        remove_item.triggered.connect(self.removeImage)
        parentPosition = self.imageSelection.mapToGlobal(qt.QPoint(0, 0))
        listMenu.move(parentPosition + QPos)
        listMenu.show()

    def _dataToShowChanged(self):
        self.image3DWidget._setDataVolume(self.Data_list[self.imageSelection.currentRow()])
        if len(self.Items_list) > self.imageSelection.currentRow():
            self.image3DWidget.updateItems(self.Items_list[self.imageSelection.currentRow()])
        if len(self.Overlays) > self.imageSelection.currentRow():
            self.image3DWidget.updateOverlays(self.Overlays[self.imageSelection.currentRow()])

    def _moved(self, ddict):
        x = ddict['x']
        y = ddict['y']
        z = ddict['z']
        try:
            stringMouse = '(' + str(x) + ' , ' + str(y) + ' , ' + str(z) + ')     '
            textValue = '%.5f' % (self.Data_list[self.imageSelection.currentRow()][z, y, x])
            stringMouse += textValue
        except:
            stringMouse = '(' + str(int(ddict['x'])) + ' , ' + str(int(ddict['y'])) + ' , ' + str(z) + ')'

        self.image3DWidget.toolBar.mouseInfo.setText(stringMouse)

    def _cliked(self,ddict):
        x = ddict['x']
        y = ddict['y']
        z = ddict['z']
        PlaneSection = ddict['PlaneSection']
        if self.imageSelection.currentRow() != -1:
            if self.image3DWidget.toolBar.pointerAction.isChecked() == True:
                seed = [x, y, z]

                self.Items_list[self.imageSelection.currentRow()]['Seeds']['Direction0'].append(seed)
                self.Items_list[self.imageSelection.currentRow()]['Seeds']['Direction1'].append(seed)
                self.Items_list[self.imageSelection.currentRow()]['Seeds']['Direction2'].append(seed)
                self.image3DWidget.updateItems(self.Items_list[self.imageSelection.currentRow()])

            if self.image3DWidget.toolBar.zone1Action.isChecked() == True:
                self.clic_zone = [x, y, z]

            if self.image3DWidget.toolBar.polygonAction.isChecked() == True:

                seed = [x, y, z]
                if (ddict['event'] != 'RMousePressed'):
                    if PlaneSection == 0:

                        if len(self.Items_list[self.imageSelection.currentRow()]['Poly']['Direction0'][-1]) != 0:
                            if self.Items_list[self.imageSelection.currentRow()]['Poly']['Direction0'][-1][-1][2] != z:
                                self.Items_list[self.imageSelection.currentRow()]['Poly']['Direction0'].append([])

                            self.Items_list[self.imageSelection.currentRow()]['Poly']['Direction0'][-1].append(
                                [seed[0] + 0.5, seed[1] + 0.5, seed[2]])
                        else:
                            self.Items_list[self.imageSelection.currentRow()]['Poly']['Direction0'][-1].append(
                                [seed[0] + 0.5, seed[1] + 0.5, seed[2]])

                    if PlaneSection == 1:
                        if len(self.Items_list[self.imageSelection.currentRow()]['Poly']['Direction1'][-1]) != 0:
                            if self.Items_list[self.imageSelection.currentRow()]['Poly']['Direction1'][-1][-1][1] != y:
                                self.Items_list[self.imageSelection.currentRow()]['Poly']['Direction1'].append([])
                            self.Items_list[self.imageSelection.currentRow()]['Poly']['Direction1'][-1].append(
                                [seed[0] + 0.5, seed[1], seed[2] + 0.5])


                        else:
                            self.Items_list[self.imageSelection.currentRow()]['Poly']['Direction1'][-1].append(
                                [seed[0] + 0.5, seed[1], seed[2] + 0.5])

                    if PlaneSection == 2:
                        if len(self.Items_list[self.imageSelection.currentRow()]['Poly']['Direction2'][-1]) != 0:
                            if self.Items_list[self.imageSelection.currentRow()]['Poly']['Direction2'][-1][-1][0] != x:
                                self.Items_list[self.imageSelection.currentRow()]['Poly']['Direction2'].append([])

                            self.Items_list[self.imageSelection.currentRow()]['Poly']['Direction2'][-1].append(
                                [seed[0], seed[1] + 0.5, seed[2] + 0.5])
                        else:
                            self.Items_list[self.imageSelection.currentRow()]['Poly']['Direction2'][-1].append(
                                [seed[0], seed[1] + 0.5, seed[2] + 0.5])
                else:
                    if PlaneSection == 0:
                        self.Items_list[self.imageSelection.currentRow()]['Poly']['Direction0'].append([])
                    if PlaneSection == 1:
                        self.Items_list[self.imageSelection.currentRow()]['Poly']['Direction1'].append([])
                    if PlaneSection == 2:
                        self.Items_list[self.imageSelection.currentRow()]['Poly']['Direction2'].append([])

                self.image3DWidget.updateItems(self.Items_list[self.imageSelection.currentRow()])

            if self.image3DWidget.toolBar.drawingAction.isChecked() == True:
                seed = [x, y, z, float(self.image3DWidget.toolBar.radius.lineEdit.text())]
                if PlaneSection == 0:
                    flag_in_circle = False
                    for i, circle in enumerate(self.Items_list[self.imageSelection.currentRow()]['Circles']['Direction0']):
                        if (((circle[0] - x) ** 2 + (circle[1] - y) ** 2) ** 0.5) < (circle[3]):
                            flag_in_circle = True
                            self.circleToMove = [i, x, y]

                    if not flag_in_circle:
                        self.circleToMove = [0]
                        self.Items_list[self.imageSelection.currentRow()]['Circles']['Direction0'].append(seed)
                if PlaneSection == 1:
                    flag_in_circle = False
                    for i, circle in enumerate(self.Items_list[self.imageSelection.currentRow()]['Circles']['Direction1']):
                        if (((circle[0] - x) ** 2 + (circle[2] - z) ** 2) ** 0.5) < (circle[3]):
                            flag_in_circle = True
                            self.circleToMove = [i, x, z]
                    if not flag_in_circle:
                        self.circleToMove = [1]
                        self.Items_list[self.imageSelection.currentRow()]['Circles']['Direction1'].append(seed)
                if PlaneSection == 2:
                    flag_in_circle = False
                    for i, circle in enumerate(self.Items_list[self.imageSelection.currentRow()]['Circles']['Direction2']):
                        if (((circle[1] - y) ** 2 + (circle[2] - z) ** 2) ** 0.5) < (circle[3]):
                            flag_in_circle = True
                            self.circleToMove = [i, y, z]
                    if not flag_in_circle:
                        self.circleToMove = [2]
                        self.Items_list[self.imageSelection.currentRow()]['Circles']['Direction2'].append(seed)

                self.image3DWidget.updateItems(self.Items_list[self.imageSelection.currentRow()])

    def _released(self,ddict):
        x = ddict['x']
        y = ddict['y']
        z = ddict['z']
        PlaneSection = ddict['PlaneSection']
        if self.imageSelection.currentRow() != -1:
            if self.image3DWidget.toolBar.zone1Action.isChecked() == True:
    
                if PlaneSection == 0:
                    self.Items_list[self.imageSelection.currentRow()]['Zones']['Direction0'].append(
                        [self.clic_zone[0], self.clic_zone[1], self.clic_zone[2], x, y, z])
                if PlaneSection == 1:
                    self.Items_list[self.imageSelection.currentRow()]['Zones']['Direction1'].append(
                        [self.clic_zone[0], self.clic_zone[1], self.clic_zone[2], x, y, z])
                if PlaneSection == 2:
                    self.Items_list[self.imageSelection.currentRow()]['Zones']['Direction2'].append(
                        [self.clic_zone[0], self.clic_zone[1], self.clic_zone[2], x, y, z])
    
                self.image3DWidget.updateItems(self.Items_list[self.imageSelection.currentRow()])
    
            if self.image3DWidget.toolBar.drawingAction.isChecked() == True:
                if PlaneSection == 0:
                    if len(self.circleToMove) > 1:
                        circleToMove = self.circleToMove[0]
    
                        for i, circle in enumerate(
                                self.Items_list[self.imageSelection.currentRow()]['Circles']['Direction0']):
                            if i == circleToMove:
                                dx = x - self.circleToMove[1]
                                dy = y - self.circleToMove[2]
                                self.circleToMove = [0]
                                self.Items_list[self.imageSelection.currentRow()]['Circles']['Direction0'][i][0] += dx
                                self.Items_list[self.imageSelection.currentRow()]['Circles']['Direction0'][i][1] += dy
                                self.image3DWidget.updateItems(self.Items_list[self.imageSelection.currentRow()])
    
                if PlaneSection == 1:
                    if len(self.circleToMove) > 1:
                        circleToMove = self.circleToMove[0]
    
                        for i, circle in enumerate(
                                self.Items_list[self.imageSelection.currentRow()]['Circles']['Direction1']):
                            if i == circleToMove:
                                dx = x - self.circleToMove[1]
                                dz = z - self.circleToMove[2]
                                self.circleToMove = [1]
                                self.Items_list[self.imageSelection.currentRow()]['Circles']['Direction1'][i][0] += dx
                                self.Items_list[self.imageSelection.currentRow()]['Circles']['Direction1'][i][2] += dz
                                self.image3DWidget.updateItems(self.Items_list[self.imageSelection.currentRow()])
    
                if PlaneSection == 2:
                    if len(self.circleToMove) > 1:
                        circleToMove = self.circleToMove[0]
    
                        for i, circle in enumerate(
                                self.Items_list[self.imageSelection.currentRow()]['Circles']['Direction2']):
                            if i == circleToMove:
                                dy = y - self.circleToMove[1]
                                dz = z - self.circleToMove[2]
                                self.circleToMove = [2]
                                self.Items_list[self.imageSelection.currentRow()]['Circles']['Direction2'][i][1] += dy
                                self.Items_list[self.imageSelection.currentRow()]['Circles']['Direction2'][i][2] += dz
                                self.image3DWidget.updateItems(self.Items_list[self.imageSelection.currentRow()])

    def _changeRadius(self,radius):
        newRadius = float(radius)
        if self.imageSelection.currentRow() != -1:
            if self.image3DWidget.toolBar.drawingAction.isChecked() == True:
    
                if self.circleToMove[0] == 0:
                    self.Items_list[self.imageSelection.currentRow()]['Circles']['Direction0'][-1][3] = newRadius
                if self.circleToMove[0] == 1:
                    self.Items_list[self.imageSelection.currentRow()]['Circles']['Direction1'][-1][3] = newRadius
                if self.circleToMove[0] == 2:
                    self.Items_list[self.imageSelection.currentRow()]['Circles']['Direction2'][-1][3] = newRadius
    
                self.image3DWidget.updateItems(self.Items_list[self.imageSelection.currentRow()])

    def _removeItems(self):
        self.Items_list[self.imageSelection.currentRow()] = {}
        self.Items_list[self.imageSelection.currentRow()] = copy.deepcopy(self.ItemsInit)
        self.image3DWidget.updateItems(self.Items_list[self.imageSelection.currentRow()])
        self.image3DWidget.axialWidget._changeSlice()
        self.image3DWidget.coronalWidget._changeSlice()
        self.image3DWidget.sagittalWidget._changeSlice()

    def _tabChanged(self, tabIndex):
        if tabIndex == 1:
            self.volumeRenderingGUI.ImagesList = self.Name_list
            self.volumeRenderingGUI.setImages()
            self.volumeRenderingGUI.DataList = self.Data_list
            self.volumeRenderingGUI.ItemLists = self.Items_list

    def loadImageSequence(self,filenames):

        filenames.sort()
        imageSamplePath = filenames[0]
        tiff_file = fabio.open(imageSamplePath)

        self.dicPar = {}
        self.dicPar['name'] = os.path.basename(filenames[0])
        self.dicPar['format'] = 'tiff'
        self.dicPar['path_original_source_file'] = os.path.dirname(filenames[0])
        self.dicPar['path_current_source_file'] = os.path.dirname(filenames[0])

        self.dicPar['path_data'] = filenames
        self.dicPar['flag_streaming'] = True
        self.dicPar['local'] = False

        if len(filenames) > 1:
            self.dicPar['shape_image'] = (tiff_file.shape[0],tiff_file.shape[1],len(filenames))
        elif len(filenames) == 1:
            self.dicPar['shape_image'] = (tiff_file.shape[0], tiff_file.shape[1])
        else:
            msg = qt.QMessageBox()
            msg.setIcon(qt.QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('No File selected')
            msg.setWindowTitle("Error")
            msg.exec_()
            return 0

        self.dicPar['data_type'] = tiff_file.dtype
        tiff_file.close()

        self.loader = LoadingDataW(self.dicPar['shape_image'], self.dicPar['data_type'], self.dicPar['name'],
                                   self.dicPar['path_current_source_file'], self)
        self.loader.validateButton.clicked.connect(self._loadData)
        self.loader.show()


    def loadHDF5(self,pathFile,pathData,hdf):

        self.dicPar = {}
        self.dicPar['name'] = os.path.basename( pathFile[0])
        self.dicPar['format'] = 'hdf5'
        self.dicPar['path_current_source_file'] = pathFile[0]
        self.dicPar['path_data'] = [pathData]
        self.dicPar['flag_streaming'] = True
        self.dicPar['shape_image'] = hdf[pathData].shape
        self.dicPar['data_type'] = hdf[pathData].dtype
        self.dicPar['local'] = False
        self.loader = LoadingDataW(self.dicPar['shape_image'],self.dicPar['data_type'],self.dicPar['name'],self.dicPar['path_current_source_file'],self)
        self.loader.validateButton.clicked.connect(self._loadData)
        self.loader.show()


    def _loadData(self):

        self.dicPar['name'] = self.loader.nameImage
        self.dicPar['axes'] = self.loader.returnAxesInfo()
        self.dicPar['units'] = self.loader.returnUnitsInfo()
        self.dicPar['pixel_size'] = self.loader.returnPixelsInfo()

        """Data Dictionary"""
        self.parent.startUpArchive.arch.openCurrentArchive()
        self.formatH5 = self.parent.startUpArchive.arch
        self.formatH5.createEmptyImage()
        self.formatH5.populateImage(self.dicPar)

        self._imageSelectionUpdateImage()
        self.loader.close()



