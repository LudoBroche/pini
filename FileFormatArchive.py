import os

import h5py
from pathlib import Path
import xmltodict
from datetime import datetime
import glob
import importQt as qt
import getpass
import uuid
import numpy as np
from lib import h5pyImport

class AlignDelegate(qt.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = qt.Qt.AlignCenter


class StartUpArchive(qt.QMainWindow):
    def __init__(self, parent=None ):
        qt.QMainWindow.__init__(self, parent)
        self.parent = parent
        self.arch = None
        self.setWindowTitle('Projects Library')
        self.setWindowIcon(qt.QIcon('./Icones/transp.png'))
        self.path_xml = Path('./config.xml')
        self._testFolderWriteable()
        self._startUpMessageBox()

    def _testFolderWriteable(self):
        self._loadConfigFile()
        self.pathFolderArchive = Path(self.parameter['pini_parameters']['home_collection']['path'])
        self._check4Archive()
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
                qm.setStandardButtons(qt.QMessageBox.Yes | qt.QMessageBox.No)
                returnValue = qm.exec()
                if returnValue == qt.QMessageBox.Yes:
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
            qmError.setStandardButtons(qt.QMessageBox.Yes)
            qmError.exec()
            self.parent.setting.show()

    def _loadConfigFile(self):
        with open(self.path_xml) as fd:
            doc = xmltodict.parse(fd.read())
        self.parameter = doc

    def _buildArchiveWidget(self):

        self._check4Archive()

        self.mainWidget = qt.QWidget()
        self.layoutArchiveW = qt.QGridLayout()

        self.buttonLayout = qt.QHBoxLayout()
        self.importButton = qt.QPushButton('Import')
        self.newArchive = qt.QPushButton('New')
        self.deleteButton = qt.QPushButton('Delete')
        self.buttonLayout.addWidget(self.importButton)
        self.buttonLayout.addWidget(self.newArchive)
        self.buttonLayout.addWidget(self.deleteButton)

        self.importButton.setDisabled(True)
        self.deleteButton.setDisabled(True)

        self.importButton.clicked.connect(self._importArchive)
        self.newArchive.clicked.connect(self._newArchive)
        self.deleteButton.clicked.connect(self._deleteArchive)

        self.tableArchive = qt.QTableWidget()
        delegate = AlignDelegate(self.tableArchive)
        self.tableArchive.setItemDelegate(delegate)
        self.tableArchive.setColumnCount(7)
        self.tableArchive.setRowCount(len(self.list_h5_archive)+1)
        self.tableArchive.verticalHeader().setVisible(False)
        self.tableArchive.horizontalHeader().setVisible(False)

        self.tableArchive.setItem(0, 0, qt.QTableWidgetItem("Project"))
        self.tableArchive.setItem(0, 1, qt.QTableWidgetItem("User"))
        self.tableArchive.setItem(0,2,qt.QTableWidgetItem("Creation Date"))
        self.tableArchive.setItem(0,3,qt.QTableWidgetItem("Modification Date"))
        self.tableArchive.setItem(0,4,qt.QTableWidgetItem("Dataset"))
        self.tableArchive.setItem(0, 5, qt.QTableWidgetItem("Import"))
        self.tableArchive.setItem(0, 6, qt.QTableWidgetItem("Delete"))

        header = self.tableArchive.horizontalHeader()
        header.setSectionResizeMode(0, qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, qt.QHeaderView.ResizeToContents)

        self.list_item_delete = []
        self.list_item_load = []


        flag_current_archive = False



        for i, arch in enumerate(self.list_h5_archive):
            h5 = h5py.File(arch,'r')
            if self.arch != None:
                if str(self.arch.pathArchive)==str(arch):
                    flag_current_archive = True
                else:
                    flag_current_archive = False

            self.tableArchive.setItem(i + 1, 0, qt.QTableWidgetItem(h5.attrs['project_name']))
            self.tableArchive.setItem(i + 1, 1, qt.QTableWidgetItem(h5.attrs['user']))
            self.tableArchive.setItem(i + 1, 2, qt.QTableWidgetItem(h5.attrs['creation_date'].split('.')[0]))
            self.tableArchive.setItem(i + 1, 3, qt.QTableWidgetItem(h5.attrs['modification_date'].split('.')[0]))
            self.tableArchive.setItem(i + 1, 4, qt.QTableWidgetItem(str(len(list(h5.keys())))))

            cBImp = qt.QCheckBox()
            cBImp.setStyleSheet("margin-left:20%; margin-right:20%;")
            cBDelete = qt.QCheckBox()
            cBDelete.setStyleSheet("margin-left:20%; margin-right:20%;")
            self.list_item_load.append(cBImp)
            self.list_item_delete.append(cBDelete)

            self.tableArchive.setCellWidget(i + 1, 5, cBImp)
            self.tableArchive.setCellWidget(i + 1, 6, cBDelete)


            if flag_current_archive:
                color = qt.QColor(200, 200, 200)
                for j in range(0,7):
                    if j < 5 :
                        self.tableArchive.item(i + 1, j).setBackground(color)
                    else:
                        w = self.tableArchive.cellWidget(i + 1, j)
                        w.setAutoFillBackground(True)
                        p = w.palette()
                        p.setColor(w.backgroundRole(), color)
                        w.setPalette(p)

            cBImp.setObjectName(str(i))
            cBImp.stateChanged.connect(self._selectImportChange)
            cBDelete.setObjectName(str(i))
            cBDelete.stateChanged.connect(self._selectDeleteChange)
            h5.close()


        if len(self.list_h5_archive) == 1:
            self.list_item_delete[0].setEnabled(False)

        self.layoutArchiveW.addWidget(self.tableArchive)
        self.layoutArchiveW.addLayout(self.buttonLayout,1,0)
        self.mainWidget.setLayout(self.layoutArchiveW)
        self.setCentralWidget(self.mainWidget)
        self.resize(504, 400)
        self.show()

    def _selectDeleteChange(self):


        if self.sender().isChecked():
            idImport = self.sender().objectName()
            boxImport = self.list_item_load[int(idImport)]
            if boxImport.isChecked():
                boxImport.setChecked(False)

        Total_archive = len(self.list_item_delete)
        total_archive_delete = 0
        for arch in self.list_item_delete:
            if arch.isChecked():
                total_archive_delete +=1
        if total_archive_delete > 0:
            self.deleteButton.setDisabled(False)
        else:
            self.deleteButton.setDisabled(True)


        for arch in self.list_item_delete:
            if ((Total_archive - total_archive_delete) == 1):
                if not arch.isChecked():
                    arch.setEnabled(False)
            else:
                arch.setEnabled(True)

    def _selectImportChange(self):
        if self.sender().isChecked():
            self.importButton.setDisabled(False)
            idImport = self.sender().objectName()
            boxDelete = self.list_item_delete[int(idImport)]
            if boxDelete.isChecked():
                boxDelete.setChecked(False)

            total_checked = 0
            for box in self.list_item_load:
                if box.objectName() != idImport:
                    box.setChecked(False)
                if box.isChecked():
                    total_checked += 1

        else:
            total_checked = 0
            for box in self.list_item_load:
                if box.isChecked():
                    total_checked += 1
            if total_checked:
                self.importButton.setDisabled(False)
            else:
                self.importButton.setDisabled(True)


    def _check4Archive(self):
        self.list_h5_archive = glob.glob(str(self.pathFolderArchive) + '/pini*.h5')
        self.list_h5_archive = self.list_h5_archive[::-1]

    def _newArchive(self):
        self.arch = ArchiveHdf5()
        self.arch.createNewArchive()
        self._check4Archive()
        self._buildArchiveWidget()

    def _importArchive(self):
        for i, box in enumerate(self.list_item_load):
            if box.isChecked():
                path_to_open = self.list_h5_archive[i]
                break

        current_version = self.parameter['pini_parameters']['home_collection']['hdf5_pini_version']


        self.arch = ArchiveHdf5()
        self.arch.openArchive(path_to_open)

        current_vers_hdf5pini = self.parameter['pini_parameters']['home_collection']['hdf5_pini_version']
        file_version = self.arch.archH5.attrs['hdf5_pini_version']

        if file_version != current_vers_hdf5pini:
            msg = qt.QMessageBox()
            msg.setWindowIcon(qt.QIcon('/Icones/transp.png'))
            msg.setIcon(qt.QMessageBox.Warning)
            msg.setStandardButtons(qt.QMessageBox.Yes|qt.QMessageBox.No)

            fileOpen = Path(path_to_open).name
            txt = "The file version '%s' don't match. (%s != %s)\n" %(fileOpen, file_version, current_version)
            txt += "Some feature might not work\n."
            txt += "Do you want to load it anyway ?"

            msg.setText(txt)
            msg.setWindowTitle(' ')
            returnValue = msg.exec_()

            if returnValue == qt.QMessageBox.Yes:
                self.close()
            else:
                self.arch.archH5.close()
        else:
            self.close()


    def _deleteArchive(self):

        for i, box in enumerate(self.list_item_delete):
            if box.isChecked():
                os.remove(self.list_h5_archive[i])
        self._check4Archive()
        self._buildArchiveWidget()

    def closeEvent(self,event):
        if self.arch == None:
            self.arch = ArchiveHdf5()
            self.arch.createNewArchive()
            name = Path(self.arch.pathArchive).name

            msg = qt.QMessageBox()
            msg.setWindowIcon(qt.QIcon('/Icones/transp.png'))
            msg.setIcon(qt.QMessageBox.Warning)
            msg.setStandardButtons(qt.QMessageBox.Yes)

            txt = "No Project imported or created. Creation of %s"%(name)
            msg.setText(txt)
            msg.setWindowTitle(' ')
            returnValue = msg.exec_()

        event.accept()

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
        self.archH5.attrs['hdf5_pini_version'] = self.parameter['pini_parameters']['home_collection']['hdf5_pini_version']
        self.archH5.attrs["project_name"] = ''
        self.archH5.attrs["user"] = getpass.getuser()
        self.archH5.attrs["creation_date"] = str(dateTime)
        self.archH5.attrs["modification_date"] = str(dateTime)
        self.archH5.attrs["code"] = str(uuid.uuid4())
        self.archH5.close()


    def openArchive(self,archivePath):
        self.pathArchive = Path(archivePath)
        self.archH5 = h5py.File(self.pathArchive,'a')

    def openCurrentArchive(self):
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

        self.currentIndex = index

        dt = h5py.special_dtype(vlen=str)

        self.archH5.create_group(index)
        self.archH5[index].attrs["name"] = h5py.Empty(dt)
        self.archH5[index].attrs["format"] = h5py.Empty(dt)
        self.archH5[index].attrs["path_original_source_file"] = h5py.Empty(dt)
        self.archH5[index].attrs["path_current_source_file"] = h5py.Empty(dt)
        self.archH5[index].attrs["flag_streaming"] = h5py.Empty(np.dtype('?'))

        self.archH5[index].create_dataset("path_data",dtype=dt)
        self.archH5[index].create_dataset("axes",dtype=dt)
        self.archH5[index].create_dataset("units",dtype=dt)
        self.archH5[index].create_dataset("pixel_size",dtype=np.dtype('f'))
        self.archH5[index].create_dataset("data",dtype=np.dtype('f'))
        self.archH5[index].create_group("roi")
        self.archH5[index].create_group("pipeline")

        self._closeArchive()

    def populateImage(self,dicPar):

        self.openCurrentArchive()
        index_list = [int(k) for k in list(self.archH5.keys())]
        index = max(index_list)
        index = str(index).zfill(5)

        if dicPar['format'] == 'hdf5':

            dt = h5py.special_dtype(vlen=str)

            self.archH5[index].attrs["name"] = dicPar["name"]
            self.archH5[index].attrs["format"] = dicPar["format"]
            self.archH5[index].attrs["path_original_source_file"] = dicPar["path_original_source_file"]
            self.archH5[index].attrs["path_current_source_file"] = dicPar["path_current_source_file"]
            self.archH5[index].attrs["flag_streaming"] = dicPar["flag_streaming"]

            del self.archH5[index]["path_data"]
            self.archH5[index].create_dataset("path_data",data = np.array([dicPar["path_data"]],dtype = 'S'))
            del self.archH5[index]["axes"]
            self.archH5[index].create_dataset("axes", data=np.array(dicPar["axes"], dtype='S'))
            del self.archH5[index]["units"]
            self.archH5[index].create_dataset("units", data=np.array(dicPar["units"], dtype=dt))
            del self.archH5[index]["pixel_size"]
            self.archH5[index].create_dataset("pixel_size", data=np.array(dicPar["pixel_size"], dtype=np.dtype('f')))

            del self.archH5[index]["data"]

            vlayout = h5py.VirtualLayout(shape = dicPar['shape_image'],dtype= dicPar['data_type'])

            vsource = h5py.VirtualSource(dicPar["path_current_source_file"],dicPar["path_data"],shape= dicPar['shape_image'])
            vlayout[...] = vsource
            self.archH5[index].create_virtual_dataset("data",vlayout,fillvalue=-1)

        self._closeArchive()



if __name__ == "__main__":

    archive = ArchiveHdf5()
    #archive.createNewArchive()
    archive.openArchive("./pini_2023-12-15_105149.h5")
    archive.createEmptyImage()



        