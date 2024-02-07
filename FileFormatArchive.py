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
from tifffile import TiffFile
import psutil
import random
import time

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
                    self.arch.clean_up_lock_file()
                    self.arch.createNewArchive()
            else:
                self.arch = ArchiveHdf5()
                self.arch.clean_up_lock_file()
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

            with  h5py.File(arch,'r') as h5:
                if self.arch != None:
                    if str(self.arch.pathArchive)==str(arch):
                        flag_current_archive = True
                    else:
                        flag_current_archive = False

                projectName = qt.QLineEdit(h5.attrs['project_name'])
                projectName.editingFinished.connect(self.nameProjectChanged)
                projectName.setFrame(False)
                projectName.setObjectName(str(i))


                self.tableArchive.setCellWidget(i + 1, 0, projectName)
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
                    if j == 0 or j >= 5 :
                        w = self.tableArchive.cellWidget(i + 1, j)
                        w.setAutoFillBackground(True)
                        p = w.palette()
                        p.setColor(w.backgroundRole(), color)
                        w.setPalette(p)
                    elif j < 5:
                        self.tableArchive.item(i + 1, j).setBackground(color)


            cBImp.setObjectName(str(i))
            cBImp.stateChanged.connect(self._selectImportChange)
            cBDelete.setObjectName(str(i))
            cBDelete.stateChanged.connect(self._selectDeleteChange)



        if len(self.list_h5_archive) == 1:
            self.list_item_delete[0].setEnabled(False)

        self.layoutArchiveW.addWidget(self.tableArchive)
        self.layoutArchiveW.addLayout(self.buttonLayout,1,0)
        self.mainWidget.setLayout(self.layoutArchiveW)
        self.setCentralWidget(self.mainWidget)
        self.resize(600, 400)
        self.show()

    def nameProjectChanged(self):
        index = int(self.sender().objectName())
        fileH5 = self.list_h5_archive[index]
        with  h5py.File(fileH5,'a') as h5:
            h5.attrs['project_name'] = self.sender().text()

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
        self.list_h5_archive.sort()
        self.list_h5_archive = self.list_h5_archive[::-1]

    def _newArchive(self):
        self.arch = ArchiveHdf5()
        self.arch.clean_up_lock_file()
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
        self.arch.clean_up_lock_file()
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
                self.arch._closeArchive()
        else:
            self.close()
        self.arch._closeArchive()
        self.arch.updateStreamingFlags()
        self.parent.mainWidget._imageSelectionUpdateImage()


    def _deleteArchive(self):

        for i, box in enumerate(self.list_item_delete):
            if box.isChecked():
                os.remove(self.list_h5_archive[i])
        self._check4Archive()
        self._buildArchiveWidget()

    def closeEvent(self,event):
        if self.arch == None:
            self.arch = ArchiveHdf5()
            self.arch.clean_up_lock_file()
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
        self.dataRam = {}

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
        self.archH5.attrs["project_name"] = f'{random.randint(0,9999):04}'
        self.archH5.attrs["user"] = getpass.getuser()
        self.archH5.attrs["creation_date"] = str(dateTime)
        self.archH5.attrs["modification_date"] = str(dateTime)
        self.archH5.attrs["code"] = str(uuid.uuid4())
        self._closeArchive()

    def updateStreamingFlags(self):
        self.openCurrentArchive()
        for key in self.archH5.keys():
            self.archH5[key].attrs["flag_streaming"] = True
        self._closeArchive()


    def generate_lock_file(self):
        lock_file = os.path.splitext(self.pathArchive)[0]+'.lock'
        f = open(lock_file,'w')
        f.close()

    def remove_lock_file(self):
        lock_file = os.path.splitext(self.pathArchive)[0]+'.lock'
        if os.path.exists(lock_file):
            os.remove(lock_file)

    def clean_up_lock_file(self):
        list_lock = glob.glob(str(self.pathFolderArchive) + '/*.lock')
        for lock in list_lock:
            os.remove(lock)



    def openArchive(self,archivePath):
        self.dataRam = {}
        self.pathArchive = Path(archivePath)
        self.archH5 = h5py.File(self.pathArchive,'a')
        for key in self.archH5.keys():
            self.dataRam[key] = []
        self.generate_lock_file()

    def openCurrentArchive(self):
        self.archH5 = h5py.File(self.pathArchive,'a')
        self.generate_lock_file()

    def openCurrentArchiveRead(self):
        self.archH5 = h5py.File(self.pathArchive,'r')
        self.generate_lock_file()

    def _closeArchive(self):
        self.archH5.flush()
        self.archH5.close()
        self.remove_lock_file()

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
        self.archH5[index].attrs["type"] = h5py.Empty(dt)
        self.archH5[index].attrs["path_current_source_file"] = h5py.Empty(dt)
        self.archH5[index].attrs["flag_streaming"] = h5py.Empty(np.dtype('?'))
        self.archH5[index].attrs["local"] = h5py.Empty(np.dtype('?'))

        self.archH5[index].create_dataset("path_data",dtype=dt)
        self.archH5[index].create_dataset("axes",dtype=dt)
        self.archH5[index].create_dataset("units",dtype=dt)
        self.archH5[index].create_dataset("pixel_size",dtype=np.dtype('f'))
        self.archH5[index].create_dataset("data",dtype=np.dtype('f'))
        self.archH5[index].create_group("roi")
        self.archH5[index].create_group("pipeline")

        self.dataRam[index] = []

        self._closeArchive()

    def generateInfotxt(self,indexh5):
        self.openCurrentArchive()
        txt = ''

        name = self.archH5[indexh5].attrs["name"]
        format = self.archH5[indexh5].attrs["format"]
        dtype =  self.archH5[f'{indexh5}/data'].dtype
        txt += f'{name} [{format} - {dtype}]\n'

        shape = self.archH5[f'{indexh5}/data'].shape[:]

        px_sizes = self.archH5[f'{indexh5}/pixel_size'][:]
        txtUnit = ''
        for i,px_size in enumerate(px_sizes):
            if hasattr(self.archH5[f'{indexh5}/units'][i],'decode'):
                unit = self.archH5[f'{indexh5}/units'][i].decode('utf-8 ')
            else:
                unit = self.archH5[f'{indexh5}/units'][i]
            txtUnit += f'{px_size} {unit} '

        txt += f'{shape} [ {txtUnit}]\n'
        axes = self.archH5[f'{indexh5}/axes'][:]
        txtAxes = ''
        for axe in axes:
            if hasattr(axe, 'decode'):
                txtAxes += f'{axe.decode("utf-8")} '
            else:
                txtAxes += f'{axe} '

        txt += f'{txtAxes}\n'

        path = self.archH5[indexh5].attrs["path_current_source_file"]
        txt += path

        return txt

    def loadDataToRam(self,indexLoad):
        self.openCurrentArchive()
        indexh5 = str(indexLoad).zfill(5)

        type = self.archH5[f'{indexh5}/data'].dtype
        fullSize = type.itemsize
        shape = self.archH5[f'{indexh5}/data'].shape
        for ishape in shape:
            fullSize *= ishape
        mem = psutil.virtual_memory()
        if fullSize > mem.available:
            msg = qt.QMessageBox()
            msg.setWindowIcon(qt.QIcon('/Icones/transp.png'))
            msg.setIcon(qt.QMessageBox.Warning)
            msg.setStandardButtons(qt.QMessageBox.Ok)
            txt = "No enough available  Virtual Memory to load the dataset"
            msg.setText(txt)
            msg.setWindowTitle(' ')
            msg.exec()
            return 0


        self.dataRam[indexh5] = self.archH5[f'{indexh5}/data'][:]
        self.archH5[f'{indexh5}'].attrs['flag_streaming'] = False
        self._closeArchive()
        return 1

    def removeDataFromRam(self,indexDel):
        self.openCurrentArchive()
        indexh5 = str(indexDel).zfill(5)
        self.archH5[f'{indexh5}'].attrs['flag_streaming'] = True
        self._closeArchive()
        if indexh5 in list(self.dataRam.keys()):
            del self.dataRam[indexh5]

        self.dataRam[indexh5] = []


    def deleteImage(self,indexDelete):
        self.openCurrentArchive()
        indexh5 = str(indexDelete).zfill(5)
        if self.archH5[f'{indexh5}'].attrs['local']:
            #del self.archH5[f'{indexh5}']
            # Todo delete_H5 in local folder
            pass
        with h5py.File('./tmp.h5','w') as newh5:

            i = 0
            for key in list(self.archH5.keys()):
                if key != indexh5:
                    self.archH5.copy(self.archH5[key],newh5,str(i).zfill(5))
                    i += 1
            for attr in self.archH5.attrs.keys():
                newh5.attrs[attr] = self.archH5.attrs[attr]

        self._closeArchive()
        self._updateTmp()

        del self.dataRam[indexh5]
        dictmp = {}

        for key in self.dataRam.keys():
            key_num = int(key)
            if key_num > int(indexDelete):
                dictmp[str(key_num-1).zfill(5)] = self.dataRam[key]
            else:
                dictmp[key] = self.dataRam[key]

        self.dataRam = dictmp
    def _updateTmp(self):
        os.remove(self.pathArchive)
        os.rename('./tmp.h5',self.pathArchive)

    def populateImage(self,dicPar):

        dt = h5py.special_dtype(vlen=str)

        self.openCurrentArchive()
        index_list = [int(k) for k in list(self.archH5.keys())]
        indexh5 = max(index_list)
        indexh5 = str(indexh5).zfill(5)
        self.archH5[indexh5].attrs["name"] = dicPar["name"]
        self.archH5[indexh5].attrs["format"] = dicPar["format"]
        self.archH5[indexh5].attrs["path_current_source_file"] = dicPar["path_current_source_file"]
        self.archH5[indexh5].attrs["flag_streaming"] = dicPar["flag_streaming"]
        self.archH5[indexh5].attrs["local"] = dicPar["local"]
        del self.archH5[indexh5]["axes"]
        self.archH5[indexh5].create_dataset("axes", data=np.array(dicPar["axes"], dtype='S'))
        del self.archH5[indexh5]["units"]
        self.archH5[indexh5].create_dataset("units", data=np.array(dicPar["units"], dtype=dt))
        del self.archH5[indexh5]["path_data"]
        self.archH5[indexh5].create_dataset("path_data", data=np.array(dicPar["path_data"], dtype='S'))
        del self.archH5[indexh5]["pixel_size"]
        self.archH5[indexh5].create_dataset("pixel_size", data=np.array(dicPar["pixel_size"], dtype=np.dtype('f')))

        if dicPar['format'] == 'hdf5':

            del self.archH5[indexh5]["data"]
            vlayout = h5py.VirtualLayout(shape = dicPar['shape_image'],dtype= dicPar['data_type'])
            vsource = h5py.VirtualSource(dicPar["path_current_source_file"],dicPar["path_data"][0],shape= dicPar['shape_image'])
            vlayout[...] = vsource
            self.archH5[indexh5].create_virtual_dataset("data",vlayout,fillvalue=-1)

        elif dicPar['format'] == 'tiff':
            external_datasets = []
            if not 'tiff_links' in list(self.archH5.keys()):
                self.archH5[indexh5].create_group('tiff_links')
            dtype = None
            for i,pathTiff in enumerate(self.archH5[indexh5]["path_data"]):
                if hasattr(pathTiff,'decode'):
                    pathTiff = pathTiff.decode('ascii')

                with TiffFile(pathTiff) as tif:
                    fh = tif.filehandle
                    for page in tif.pages:
                        if dtype is not None:
                            assert dtype == page.dtype, "incoherent data type"
                        dtype = page.dtype
                        for index, (offset, bytecount) in enumerate(zip(page.dataoffsets, page.databytecounts)):
                            _ = fh.seek(offset)
                            data = fh.read(bytecount)
                            _, _, shape = page.decode(data, index, jpegtables=page.jpegtables)
                            shape = shape[1:-1]
                            external_dataset = self.archH5[indexh5]['tiff_links'].create_dataset(name=f'tmp{i}', shape=shape, dtype=dtype,
                                                                 external=[(pathTiff, offset, bytecount)])
                            external_datasets.append(external_dataset)

            vlayout = h5py.VirtualLayout(shape=(len(self.archH5[indexh5]["path_data"]), shape[0], shape[1]), dtype=dtype)
            for i, ed in enumerate(external_datasets):
                vsource = h5py.VirtualSource(ed)
                vlayout[i] = vsource

            del self.archH5[indexh5]["data"]
            self.archH5[indexh5].create_virtual_dataset("data", vlayout, fillvalue=-1)

        self.archH5.close()
        self.createPyramid(indexh5)

    def createPyramid(self,indexh5):

        self.openCurrentArchiveRead()

        dataSet = self.archH5[f'{indexh5}/data']
        dataType = dataSet.dtype
        shapeVol = dataSet.shape
        pyramid_resolution = []
        nb_axis = len(shapeVol)

        for ax, shape in enumerate(shapeVol):
            pyramid_resolution.append([])
            deltaTime = 1
            factor = 1
            while (deltaTime > (1 / 24.0)):
                pyramid_resolution[ax].append(factor)
                start = time.time()
                if ax == 0:
                    if nb_axis == 2:
                        tmp = dataSet[::factor, ::factor]
                    elif nb_axis == 3:
                        tmp = dataSet[0, ::factor, ::factor]
                    elif nb_axis == 4:
                        tmp = dataSet[0, ::factor, ::factor, ::factor]
                elif ax == 1:
                    if nb_axis == 2:
                        tmp = dataSet[::factor, ::factor]
                    elif nb_axis == 3:
                        tmp = dataSet[::factor, 0, ::factor]
                    elif nb_axis == 4:
                        tmp = dataSet[::factor, 0, ::factor, ::factor]
                elif ax == 2:
                    if nb_axis == 3:
                        tmp = dataSet[::factor, ::factor, 0]
                    elif nb_axis == 4:
                        tmp = dataSet[::factor, ::factor, 0, ::factor]
                elif ax == 3:
                    tmp = dataSet[::factor, ::factor, ::factor, 0]

                deltaTime = time.time() - start
                factor *= 4
        self._closeArchive()
        self.openCurrentArchive()

        for ax in pyramid_resolution:
            for res in ax:
                if res != 1:
                    new_dataset_name = f'dataX{res}'
                    list_dataset = list(self.archH5[indexh5].keys())
                    if not (new_dataset_name in list_dataset):
                        new_shape = (-(-shapeVol[0]//res),-(-shapeVol[1]//res),-(-shapeVol[2]//res))
                        path_source_file = self.archH5[indexh5].attrs["path_current_source_file"]
                        path_data = self.archH5[indexh5]["path_data"][0].decode('UTF-8')
                        vlayout = h5py.VirtualLayout(shape = new_shape,dtype= dataType)
                        vsource = h5py.VirtualSource(path_source_file,path_data,shape= shapeVol)
                        print(new_dataset_name,new_shape,path_data,path_source_file)
                        vlayout[:,:,:] = vsource[::res,::res,::res]
                        self.archH5[indexh5].create_virtual_dataset(new_dataset_name,vlayout,fillvalue=-1)
        self._closeArchive()

if __name__ == "__main__":

    archive = ArchiveHdf5()
    #archive.createNewArchive()
    archive.openArchive("./pini_2023-12-15_105149.h5")
    archive.createEmptyImage()



        