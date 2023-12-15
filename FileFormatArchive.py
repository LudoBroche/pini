import os

import h5py
from pathlib import Path
import xmltodict
from datetime import datetime
import glob
import importQt as qt
import getpass
from lib import h5pyImport

class AlignDelegate(qt.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = qt.Qt.AlignCenter


class StartUpArchive(qt.QMainWindow):
    def __init__(self, parent=None ):
        qt.QMainWindow.__init__(self, parent)
        self.parent = parent
        self.setWindowTitle('Archive')
        self.setWindowIcon(qt.QIcon('./Icones/transp.png'))
        self.path_xml = Path('./config.xml')
        self._testFolderWriteable()
        self._startUpMessageBox()


    def _testFolderWriteable(self):
        self._loadConfigFile()
        self.pathFolderArchive = Path(self.parameter['pini_parameters']['home_collection']['path'])
        self._check4Archive()

        print("Folder Archive",self.pathFolderArchive)
        # Testing if Archive Folder is writable.  It's easier to ask for forgiveness than for permission
        self.flag_writeable = False
        try:
            file = open(str(self.pathFolderArchive) + '/tmp', 'w')
            file.close()
            os.remove(str(self.pathFolderArchive) + '/tmp')
            self.flag_writeable = True
        except:
            self.flag_writeable = False

    def _startUpMessageBox(self):
        if self.flag_writeable :
            if len(self.list_h5_archive) != 0:
                qm = qt.QMessageBox()
                qm.setWindowIcon(qt.QIcon('./Icones/transp.png'))
                qm.setIcon(qt.QMessageBox.Information)
                qm.setText("Found Archived Dataset. Do you want to import it ?")
                qm.setWindowTitle(' ')
                qm.setStandardButtons(qt.QMessageBox.Ok | qt.QMessageBox.No)
                returnValue = qm.exec()
                if returnValue == qt.QMessageBox.Ok:
                    self._buildArchiveWidget()
                else:
                    self.arch = ArchiveHdf5()
                    self.arch.createNewArchive()
            else:
                self.arch = ArchiveHdf5()
                self.arch.createNewArchive()
        else:
            qmError = qt.QMessageBox()
            qmError.setWindowIcon(qt.QIcon('./Icones/transp.png'))
            qmError.setIcon(qt.QMessageBox.Information)
            qmError.setText("The Current Archive Folder is not writeable. Make sure to select a writeable archive folder")
            qmError.setWindowTitle(' ')
            qmError.setStandardButtons(qt.QMessageBox.Ok)
            qmError.exec()
            self.parent.setting.show()

    def _loadConfigFile(self):
        with open(self.path_xml) as fd:
            doc = xmltodict.parse(fd.read())
        self.parameter = doc

    def _buildArchiveWidget(self):
        self.mainWidget = qt.QWidget()
        self.layoutArchiveW = qt.QGridLayout()

        self.buttonLayout = qt.QHBoxLayout()
        self.importButton = qt.QPushButton('Import Archive')
        self.deleteButton = qt.QPushButton('Delete')
        self.buttonLayout.addWidget(self.importButton)
        self.buttonLayout.addWidget(self.deleteButton)

        self.importButton.clicked.connect(self._importArchive)
        self.deleteButton.clicked.connect(self._deleteArchive)

        self.tableArchive = qt.QTableWidget()
        delegate = AlignDelegate(self.tableArchive)
        self.tableArchive.setItemDelegate(delegate)
        self.tableArchive.setColumnCount(6)
        self.tableArchive.setRowCount(len(self.list_h5_archive)+1)
        self.tableArchive.verticalHeader().setVisible(False)
        self.tableArchive.horizontalHeader().setVisible(False)

        self.tableArchive.setItem(0, 0, qt.QTableWidgetItem("User"))
        self.tableArchive.setItem(0,1,qt.QTableWidgetItem("Creation Date"))
        self.tableArchive.setItem(0,2,qt.QTableWidgetItem("Modification Date"))
        self.tableArchive.setItem(0,3,qt.QTableWidgetItem("Dataset"))
        self.tableArchive.setItem(0, 4, qt.QTableWidgetItem("Import"))
        self.tableArchive.setItem(0, 5, qt.QTableWidgetItem("Delete"))

        header = self.tableArchive.horizontalHeader()
        header.setSectionResizeMode(0, qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, qt.QHeaderView.ResizeToContents)

        self.list_item_delete = []
        self.list_item_load = []

        for i, arch in enumerate(self.list_h5_archive):
            h5 = h5py.File(arch,'r')
            self.tableArchive.setItem(i + 1, 0, qt.QTableWidgetItem(h5.attrs['name']))
            self.tableArchive.setItem(i + 1, 1, qt.QTableWidgetItem(h5.attrs['creation_date'].split('.')[0]))
            self.tableArchive.setItem(i + 1, 2, qt.QTableWidgetItem(h5.attrs['modification_date'].split('.')[0]))
            self.tableArchive.setItem(i + 1, 3, qt.QTableWidgetItem(str(len(list(h5.keys())))))

            cBImp = qt.QCheckBox()
            cBImp.setStyleSheet("margin-left:20%; margin-right:20%;")
            cBDelete = qt.QCheckBox()
            cBDelete.setStyleSheet("margin-left:20%; margin-right:20%;")
            self.list_item_load.append(cBImp)
            self.list_item_delete.append(cBDelete)

            self.tableArchive.setCellWidget(i + 1, 4, cBImp)
            self.tableArchive.setCellWidget(i + 1, 5, cBDelete)

            cBImp.setObjectName(str(i))
            cBImp.stateChanged.connect(self._selectImportChange)
            cBDelete.setObjectName(str(i))
            cBDelete.stateChanged.connect(self._selectDeleteChange)
        h5.close()
        self.layoutArchiveW.addWidget(self.tableArchive)
        self.layoutArchiveW.addLayout(self.buttonLayout,1,0)
        self.mainWidget.setLayout(self.layoutArchiveW)
        self.setCentralWidget(self.mainWidget)
        self.resize(459, 400)
        self.show()

    def _selectDeleteChange(self):
        if self.sender().isChecked():
            idImport = self.sender().objectName()
            boxImport = self.list_item_load[int(idImport)]
            if boxImport.isChecked():
                boxImport.setChecked(False)

    def _selectImportChange(self):
        if self.sender().isChecked():
            idImport = self.sender().objectName()
            boxDelete = self.list_item_delete[int(idImport)]
            if boxDelete.isChecked():
                boxDelete.setChecked(False)
            for box in self.list_item_load:
                if box.objectName() != idImport:
                    box.setChecked(False)

    def _check4Archive(self):
        self.list_h5_archive = glob.glob(str(self.pathFolderArchive) + '/*.h5')

    def _importArchive(self):
        for i, box in enumerate(self.list_item_load):
            if box.isChecked():
                path_to_open = self.list_h5_archive[i]
                break
        self.close()
        self.parent.h5Import.show()
        self.parent.h5Import.open_file(path_to_open)

    def _deleteArchive(self):
        for i, box in enumerate(self.list_item_delete):
            if box.isChecked():
                os.remove(self.list_h5_archive[i])

        self._check4Archive()
        self._buildArchiveWidget()




class ArchiveHdf5:
    def __init__(self):
        self.path_xml = Path('./config.xml')
        self.pathArchive = ''
        self.archH5 = None
        self._loadConfigFile()

    def _loadConfigFile(self):
        with open(self.path_xml) as fd:
            doc = xmltodict.parse(fd.read())
        self.parameter = doc
        self.pathFolderArchive = Path(self.parameter['pini_parameters']['home_collection']['path'])

    def createNewArchive(self):
        dateTime = datetime.now()
        current_date = str(dateTime).split('.')[0]
        current_date = '_'.join(current_date.split(' '))
        current_date = ''.join(current_date.split(':'))
        nameArchive = 'pini_'+current_date+'.h5'
        self._loadConfigFile()
        self.pathArchive = Path(self.pathFolderArchive,nameArchive)
        self.archH5 = h5py.File(self.pathArchive,'a')

        dt = h5py.special_dtype(vlen=str)
        self.archH5.attrs["name"] = getpass.getuser()
        self.archH5.attrs["creation_date"] = str(dateTime)
        self.archH5.attrs["modification_date"] = str(dateTime)


        self.archH5.close()

    def openArchive(self,archivePath):
        self.pathArchive = Path(archivePath)
        self.archH5 = h5py.File(self.pathArchive,'a')

    def _closeArchive(self):
        self.archH5.close()

    def cleanUpAllArchive(self):
        if self.archH5 != None:
            self._closeArchive()
        self._loadConfigFile()
        list_h5 = glob.glob(str(self.pathFolderArchive)+'/*.h5')
        for h5files in list_h5:
            os.remove(h5files)

    def createEmptyImage(self):
        index_list = [int(k) for k in list(self.archH5.keys())]
        if len(index_list) == 0 :
            index = '0'.zfill(5)
        else:
            index = max(index_list)+1
            index = str(index).zfill(5)

        dt = h5py.special_dtype(vlen=str)

        self.archH5.create_group(index)
        self.archH5[index].attrs["name"] = h5py.Empty(dt)
        self.archH5[index].attrs["path_source"] = h5py.Empty(dt)
        self.archH5[index].attrs["data_type"] = h5py.Empty(dt)
        self.archH5[index].create_dataset("pixel_size", dtype="f")
        self.archH5[index].create_dataset("data", dtype="f")
        self.archH5[index].create_group("roi")
        self.archH5[index].create_group("pipeline")

        self._closeArchive()

    def populateImage(self,dicPar):
        pass


if __name__ == "__main__":

    archive = ArchiveHdf5()
    #archive.createNewArchive()
    archive.openArchive("./pini_2023-12-15_105149.h5")
    archive.createEmptyImage()



        