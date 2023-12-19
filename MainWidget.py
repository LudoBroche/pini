import importQt as qt
import pyqtgraph as pg
import copy
import psutil

from SliceViualizer import Interactor3D
from VolumeRenderingGUI import VolumeRenderingGUI
from ProgressBarWidget import ProgressBar
from FileFormatArchive import ArchiveHdf5


class MainWidget(qt.QWidget):
    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)

        """ Attributs """

        self.arch = ArchiveHdf5()
        self.parent = parent
        self.Data_list = []
        self.Items_list = []
        self.Name_list = []

        """Data Dictionary"""

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
        self.imageSelection = qt.QListWidget(self)
        self.imageSelection.setContextMenuPolicy(qt.Qt.CustomContextMenu)
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

        self.imageSelection.customContextMenuRequested.connect(self._listItemRightClicked)
        self.imageSelection.currentRowChanged.connect(self._dataToShowChanged)

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

    def _updatePcInfo(self):

            path = self.parent.setting.parameter['pini_parameters']['home_collection']['path']
            hdd = psutil.disk_usage(str(path))

            if (hdd.total // (2 ** 30)) > 1000:
                string_space = 'HDD: {}/{} TiB [{} %]'.format(hdd.used//(2 ** 30 * 1000), hdd.total // (2 ** 30 * 1000),hdd.percent)

            else:
                string_space = 'HDD: {}/{} GiB ( {} % )'.format(hdd.used//2 ** 30, hdd.total // 2 ** 30,hdd.percent)

            mem = psutil.virtual_memory()
            cpu = psutil.cpu_percent()

            if (mem.total // (2**30)) > 1000:
                string_mem = 'CPU: {} % | RAM: {}/{} TiB [{} %]'.format(cpu,mem.used//(2 ** 30 * 1000), mem.total // (2 ** 30 * 1000),mem.percent)
            else:
                string_mem = 'CPU: {} % | RAM: {}/{} GiB [{} %]'.format(cpu,mem.used // (2 ** 30),mem.total // (2 ** 30), mem.percent)

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

    def loadHDF5(self,pathFile,pathData,hdf):
        print(pathFile, pathData,hdf)








