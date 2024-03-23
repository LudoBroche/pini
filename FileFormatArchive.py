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

        self.w_main = qt.QWidget()
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
        self.w_main.setLayout(self.layoutArchiveW)
        self.setCentralWidget(self.w_main)
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
        file_version = self.arch.archi_h5.attrs['hdf5_pini_version']

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
                self.arch.close_dataset()
        else:
            self.close()
        self.arch.close_dataset()
        self.arch.updateStreamingFlags()
        self.parent.w_main._populate_table_image_selector()


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
        self.archi_h5 = None
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

        self.archi_h5 = h5py.File(self.pathArchive,'a')

        dt = h5py.special_dtype(vlen=str)
        self.archi_h5.attrs['hdf5_pini_version'] = self.parameter['pini_parameters']['home_collection']['hdf5_pini_version']
        self.archi_h5.attrs["project_name"] = f'{random.randint(0,9999):04}'
        self.archi_h5.attrs["user"] = getpass.getuser()
        self.archi_h5.attrs["creation_date"] = str(dateTime)
        self.archi_h5.attrs["modification_date"] = str(dateTime)
        self.archi_h5.attrs["code"] = str(uuid.uuid4())
        self.close_dataset()

    def updateStreamingFlags(self):
        self.open_current_archive()
        for key in self.archi_h5.keys():
            self.archi_h5[key].attrs["flag_streaming"] = True
        self.close_dataset()


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
        self.archi_h5 = h5py.File(self.pathArchive,'a')
        for key in self.archi_h5.keys():
            self.dataRam[key] = []
        self.generate_lock_file()

    def open_current_archive(self):
        self.archi_h5 = h5py.File(self.pathArchive,'a')
        self.generate_lock_file()

    def open_current_archiveRead(self):
        self.archi_h5 = h5py.File(self.pathArchive,'r')
        self.generate_lock_file()

    def close_dataset(self):
        self.archi_h5.flush()
        self.archi_h5.close()
        self.remove_lock_file()

    def cleanUpAllArchive(self):
        if self.archi_h5 != None:
            self.close_dataset()
        self._loadConfigFile()
        list_h5 = glob.glob(str(self.pathFolderArchive)+'/*.h5')
        for h5files in list_h5:
            os.remove(h5files)

    def createEmptyImage(self):
        index_list = [int(k) for k in list(self.archi_h5.keys())]
        if len(index_list) == 0 :
            index = '0'.zfill(5)
        else:
            index = max(index_list)+1
            index = str(index).zfill(5)

        self.currentIndex = index

        dt = h5py.special_dtype(vlen=str)

        self.archi_h5.create_group(index)
        self.archi_h5[index].attrs["name"] = h5py.Empty(dt)
        self.archi_h5[index].attrs["format"] = h5py.Empty(dt)
        self.archi_h5[index].attrs["type"] = h5py.Empty(dt)
        self.archi_h5[index].attrs["path_current_source_file"] = h5py.Empty(dt)
        self.archi_h5[index].attrs["flag_streaming"] = h5py.Empty(np.dtype('?'))
        self.archi_h5[index].attrs["local"] = h5py.Empty(np.dtype('?'))

        self.archi_h5[index].create_image("path_data",dtype=dt)
        self.archi_h5[index].create_image("axes",dtype=dt)
        self.archi_h5[index].create_image("units",dtype=dt)
        self.archi_h5[index].create_image("pixel_size",dtype=np.dtype('f'))
        self.archi_h5[index].create_image("data",dtype=np.dtype('f'))
        self.archi_h5[index].create_group("roi")
        self.archi_h5[index].create_group("pipeline")

        self.dataRam[index] = []

        self.close_dataset()

    def display_image_info(self,indexh5):
        self.open_current_archive()
        txt = ''

        name = self.archi_h5[indexh5].attrs["name"]
        format = self.archi_h5[indexh5].attrs["format"]
        dtype =  self.archi_h5[f'{indexh5}/data'].dtype
        txt += f'{name} [{format} - {dtype}]\n'

        shape = self.archi_h5[f'{indexh5}/data'].shape[:]

        px_sizes = self.archi_h5[f'{indexh5}/pixel_size'][:]
        txtUnit = ''
        for i,px_size in enumerate(px_sizes):
            if hasattr(self.archi_h5[f'{indexh5}/units'][i],'decode'):
                unit = self.archi_h5[f'{indexh5}/units'][i].decode('utf-8 ')
            else:
                unit = self.archi_h5[f'{indexh5}/units'][i]
            txtUnit += f'{px_size} {unit} '

        txt += f'{shape} [ {txtUnit}]\n'
        axes = self.archi_h5[f'{indexh5}/axes'][:]
        txtAxes = ''
        for axe in axes:
            if hasattr(axe, 'decode'):
                txtAxes += f'{axe.decode("utf-8")} '
            else:
                txtAxes += f'{axe} '

        txt += f'{txtAxes}\n'

        path = self.archi_h5[indexh5].attrs["path_current_source_file"]
        txt += path

        return txt

    def loadDataToRam(self,indexLoad):
        self.open_current_archive()
        indexh5 = str(indexLoad).zfill(5)

        type = self.archi_h5[f'{indexh5}/data'].dtype
        fullSize = type.itemsize
        shape = self.archi_h5[f'{indexh5}/data'].shape
        for ishape in shape:
            fullSize *= ishape
        mem = psutil.virtual_memory()
        if fullSize > mem.available:
            msg = qt.QMessageBox()
            msg.setWindowIcon(qt.QIcon('/Icones/transp.png'))
            msg.setIcon(qt.QMessageBox.Warning)
            msg.setStandardButtons(qt.QMessageBox.Ok)
            txt = "No enough available  Virtual Memory to load the image"
            msg.setText(txt)
            msg.setWindowTitle(' ')
            msg.exec()
            return 0


        self.dataRam[indexh5] = self.archi_h5[f'{indexh5}/data'][:]
        self.archi_h5[f'{indexh5}'].attrs['flag_streaming'] = False
        self.close_dataset()
        return 1

    def free_ram(self,indexDel):
        self.open_current_archive()
        indexh5 = str(indexDel).zfill(5)
        self.archi_h5[f'{indexh5}'].attrs['flag_streaming'] = True
        self.close_dataset()
        if indexh5 in list(self.dataRam.keys()):
            del self.dataRam[indexh5]

        self.dataRam[indexh5] = []


    def delete_image(self,indexDelete):
        self.open_current_archive()
        indexh5 = str(indexDelete).zfill(5)
        if self.archi_h5[f'{indexh5}'].attrs['local']:
            #del self.archi_h5[f'{indexh5}']
            # Todo delete_H5 in local folder
            pass
        with h5py.File('./tmp.h5','w') as newh5:

            i = 0
            for key in list(self.archi_h5.keys()):
                if key != indexh5:
                    self.archi_h5.copy(self.archi_h5[key],newh5,str(i).zfill(5))
                    i += 1
            for attr in self.archi_h5.attrs.keys():
                newh5.attrs[attr] = self.archi_h5.attrs[attr]

        self.close_dataset()
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

    def populateImage(self,par_dataset):

        dt = h5py.special_dtype(vlen=str)

        self.open_current_archive()
        index_list = [int(k) for k in list(self.archi_h5.keys())]
        indexh5 = max(index_list)
        indexh5 = str(indexh5).zfill(5)
        self.archi_h5[indexh5].attrs["name"] = par_dataset["name"]
        self.archi_h5[indexh5].attrs["format"] = par_dataset["format"]
        self.archi_h5[indexh5].attrs["path_current_source_file"] = par_dataset["path_current_source_file"]
        self.archi_h5[indexh5].attrs["flag_streaming"] = par_dataset["flag_streaming"]
        self.archi_h5[indexh5].attrs["local"] = par_dataset["local"]
        del self.archi_h5[indexh5]["axes"]
        self.archi_h5[indexh5].create_image("axes", data=np.array(par_dataset["axes"], dtype='S'))
        del self.archi_h5[indexh5]["units"]
        self.archi_h5[indexh5].create_image("units", data=np.array(par_dataset["units"], dtype=dt))
        del self.archi_h5[indexh5]["path_data"]
        self.archi_h5[indexh5].create_image("path_data", data=np.array(par_dataset["path_data"], dtype='S'))
        del self.archi_h5[indexh5]["pixel_size"]
        self.archi_h5[indexh5].create_image("pixel_size", data=np.array(par_dataset["pixel_size"], dtype=np.dtype('f')))

        if par_dataset['format'] == 'hdf5':

            del self.archi_h5[indexh5]["data"]
            vlayout = h5py.VirtualLayout(shape = par_dataset['shape_image'],dtype= par_dataset['data_type'])
            vsource = h5py.VirtualSource(par_dataset["path_current_source_file"],par_dataset["path_data"][0],shape= par_dataset['shape_image'])
            vlayout[...] = vsource
            self.archi_h5[indexh5].create_virtual_image("data",vlayout,fillvalue=-1)

        elif par_dataset['format'] == 'tiff':
            external_images = []
            if not 'tiff_links' in list(self.archi_h5.keys()):
                self.archi_h5[indexh5].create_group('tiff_links')
            dtype = None
            for i,pathTiff in enumerate(self.archi_h5[indexh5]["path_data"]):
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
                            external_image = self.archi_h5[indexh5]['tiff_links'].create_image(name=f'tmp{i}', shape=shape, dtype=dtype,
                                                                 external=[(pathTiff, offset, bytecount)])
                            external_images.append(external_image)

            vlayout = h5py.VirtualLayout(shape=(len(self.archi_h5[indexh5]["path_data"]), shape[0], shape[1]), dtype=dtype)
            for i, ed in enumerate(external_images):
                vsource = h5py.VirtualSource(ed)
                vlayout[i] = vsource

            del self.archi_h5[indexh5]["data"]
            self.archi_h5[indexh5].create_virtual_image("data", vlayout, fillvalue=-1)

        self.archi_h5.close()

if __name__ == "__main__":

    archive = ArchiveHdf5()
    #archive.createNewArchive()
    archive.openArchive("./pini_2023-12-15_105149.h5")
    archive.createEmptyImage()



        