import os.path

import importQt as qt
import pyqtgraph as pg
import copy
import psutil
import fabio

from SliceViualizer import Interactor3D
from VolumeRenderingGUI import VolumeRenderingGUI
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
        self.timer = qt.QTimer()
        self.timer.start(1000)
        self.timer.timeout.connect(self._updatePcInfo)
        self.buildMainLayout()

    def buildMainLayout(self):

        """ Widgets Initialisation """

        mainLayout = qt.QGridLayout()
        tabWidget = qt.QTabWidget()
        tab3DViewer = qt.QWidget()
        image3DWidget = Interactor3D(self)

        self._imageSelectionBuildTable()

        self.systemInfo1 = qt.QLabel()
        fontSystem =self.systemInfo1.font()
        fontSystem.setPointSize(10)
        self.systemInfo1.setFont(fontSystem)
        self.systemInfo2 = qt.QLabel()
        fontSystem = self.systemInfo2.font()
        fontSystem.setPointSize(10)
        self.systemInfo2.setFont(fontSystem)

        layout3d = qt.QGridLayout()
        volumeRenderingGUI = VolumeRenderingGUI()

        """Signals"""


        tabWidget.currentChanged.connect(self._tabChanged)

        """Widget Placement"""

        vButtonLayout = qt.QVBoxLayout()
        vButtonLayout.addWidget(self.imageSelection)
        vButtonLayout.addWidget(self.systemInfo1)
        vButtonLayout.addWidget(self.systemInfo2)

        right_widget = qt.QWidget()
        right_widget.setLayout(vButtonLayout)

        splitter = qt.QSplitter(qt.Qt.Horizontal)
        splitter.addWidget(image3DWidget)
        splitter.addWidget(right_widget)

        width = qt.QDesktopWidget().screenGeometry().width()
        splitter.setSizes([width-500,250])

        layout3d.addWidget(volumeRenderingGUI)
        tab3DViewer.setLayout(layout3d)

        tabWidget.addTab(splitter, '2D Viewer')
        tabWidget.addTab(tab3DViewer, '3D Viewer')

        mainLayout.addWidget(tabWidget)
        self.setLayout(mainLayout)


    def _imageSelectionBuildTable(self):

        self.imageSelection = qt.QTableWidget(self)
        self.imageSelection.setRowCount(0)
        self.imageSelection.setColumnCount(4)
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

            wDisplay = qt.QPushButton()
            wDisplay.setFlat(True)
            wDisplay.setCheckable(True)
            wDisplay.setStyleSheet("QPushButton: flat;border: none")
            wDisplay.setObjectName(f'{i}')
            wDisplay.setIcon(qt.QIcon('./Icones/eye_close.png'))
            wDisplay.setChecked(False)

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
            self.imageSelection.setCellWidget(i, 1, wDisplay)
            self.imageSelection.setCellWidget(i,2,wRamHdd)
            self.imageSelection.setCellWidget(i, 3, deleteButton)

            wRamHdd.clicked.connect(self._ImageSelectionRamHddButtonClicked)
            deleteButton.clicked.connect(self._ImageSelectionDeleteData)

        self.imageSelection.horizontalHeader().setSectionResizeMode(0, qt.QHeaderView.ResizeToContents)
        self.imageSelection.horizontalHeader().setSectionResizeMode(1, qt.QHeaderView.ResizeToContents)
        self.imageSelection.horizontalHeader().setSectionResizeMode(2, qt.QHeaderView.ResizeToContents)
        self.imageSelection.horizontalHeader().setSectionResizeMode(3, qt.QHeaderView.ResizeToContents)
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



