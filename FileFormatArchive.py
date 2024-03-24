import os
import h5py
from pathlib import Path
import xmltodict
from datetime import datetime
import glob
import importQt as Qt
import getpass
import uuid
import numpy as np
from tifffile import TiffFile
import psutil
import random


class AlignDelegate(Qt.QStyledItemDelegate):
    def initStyleOption(self, option, index, **kwargs):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = Qt.Qt.AlignCenter


class StartUpArchive(Qt.QMainWindow):
    """
    QMainWindow for the Projects manager
    Overview of all current project images
    """
    def __init__(self, parent=None):
        Qt.QMainWindow.__init__(self, parent)
        self.parent = parent
        self.dataset = None
        self.setWindowTitle('Projects Library')
        self.setWindowIcon(Qt.QIcon('./Icones/transp.png'))
        self.path_xml = Path('./config.xml')
        self._check_permission_directory()
        self._start_up_message_box()

    def _check_permission_directory(self):
        self._import_config_file()
        self.pathFolderArchive = Path(self.parameter['pini_parameters']['home_collection']['path'])
        self._check_dataset()
        # Testing if Archive Folder is writable.  It's easier to ask for forgiveness than for permission
        self.flag_writeable = False
        try:
            file = open(str(self.pathFolderArchive) + '/tmp', 'w')
            file.close()
            os.remove(str(self.pathFolderArchive) + '/tmp')
            self.flag_writeable = True
        except OSError:
            self.flag_writeable = False

    def _start_up_message_box(self):
        if self.flag_writeable:
            if len(self.list_h5_archive) != 0:
                qm = Qt.QMessageBox()
                qm.setWindowIcon(Qt.QIcon('./Icones/transp.png'))
                qm.setIcon(Qt.QMessageBox.Information)
                qm.setText("Found Archived Dataset. Do you want to import it ?")
                qm.setWindowTitle(' ')
                qm.setStandardButtons(Qt.QMessageBox.Yes | Qt.QMessageBox.No)
                answer = qm.exec()
                if answer == Qt.QMessageBox.Yes:
                    self._build_dataset_widget()
                else:
                    self.dataset = ArchiveHdf5()
                    self.dataset.clean_up_lock_file()
                    self.dataset.create_new_dataset()
            else:
                self.dataset = ArchiveHdf5()
                self.dataset.clean_up_lock_file()
                self.dataset.create_new_dataset()
        else:
            error_message_box = Qt.QMessageBox()
            error_message_box.setWindowIcon(Qt.QIcon('./Icones/transp.png'))
            error_message_box.setIcon(Qt.QMessageBox.Information)
            error_message_box.setText(
                "The Current Archive Folder is not writeable. Make sure to select a writeable archive folder")
            error_message_box.setWindowTitle(' ')
            error_message_box.setStandardButtons(Qt.QMessageBox.Yes)
            error_message_box.exec()
            self.parent.setting.show()

    def _import_config_file(self):
        with open(self.path_xml) as fd:
            doc = xmltodict.parse(fd.read())
        self.parameter = doc

    def _build_dataset_widget(self):

        self._check_dataset()

        self.w_main = Qt.QWidget(self)
        self.layoutArchiveW = Qt.QGridLayout()

        self.buttonLayout = Qt.QHBoxLayout()
        self.importButton = Qt.QPushButton('Import')
        self.newArchive = Qt.QPushButton('New')
        self.deleteButton = Qt.QPushButton('Delete')
        self.buttonLayout.addWidget(self.importButton)
        self.buttonLayout.addWidget(self.newArchive)
        self.buttonLayout.addWidget(self.deleteButton)

        self.importButton.setDisabled(True)
        self.deleteButton.setDisabled(True)

        self.importButton.clicked.connect(self._import_dataset)
        self.newArchive.clicked.connect(self._create_dataset)
        self.deleteButton.clicked.connect(self._delete_dataset)

        self.tableArchive = Qt.QTableWidget(self)
        delegate = AlignDelegate(self.tableArchive)
        self.tableArchive.setItemDelegate(delegate)
        self.tableArchive.setColumnCount(7)
        self.tableArchive.setRowCount(len(self.list_h5_archive) + 1)
        self.tableArchive.verticalHeader().setVisible(False)
        self.tableArchive.horizontalHeader().setVisible(False)

        self.tableArchive.setItem(0, 0, Qt.QTableWidgetItem("Project"))
        self.tableArchive.setItem(0, 1, Qt.QTableWidgetItem("User"))
        self.tableArchive.setItem(0, 2, Qt.QTableWidgetItem("Creation Date"))
        self.tableArchive.setItem(0, 3, Qt.QTableWidgetItem("Modification Date"))
        self.tableArchive.setItem(0, 4, Qt.QTableWidgetItem("Dataset"))
        self.tableArchive.setItem(0, 5, Qt.QTableWidgetItem("Import"))
        self.tableArchive.setItem(0, 6, Qt.QTableWidgetItem("Delete"))

        header = self.tableArchive.horizontalHeader()
        header.setSectionResizeMode(0, Qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, Qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, Qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, Qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, Qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, Qt.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, Qt.QHeaderView.ResizeToContents)

        self.list_item_delete = []
        self.list_item_load = []

        flag_current_archive = False

        for i, dataset in enumerate(self.list_h5_archive):

            with h5py.File(dataset, 'r') as h5:
                if self.dataset is not None:
                    if str(self.dataset.path_dataset) == str(dataset):
                        flag_current_archive = True
                    else:
                        flag_current_archive = False

                project_name = Qt.QLineEdit(h5.attrs['project_name'])
                project_name.editingFinished.connect(self._sig_name_dataset_changed)
                project_name.setFrame(False)
                project_name.setObjectName(str(i))

                self.tableArchive.setCellWidget(i + 1, 0, project_name)
                self.tableArchive.setItem(i + 1, 1, Qt.QTableWidgetItem(h5.attrs['user']))
                self.tableArchive.setItem(i + 1, 2, Qt.QTableWidgetItem(h5.attrs['creation_date'].split('.')[0]))
                self.tableArchive.setItem(i + 1, 3, Qt.QTableWidgetItem(h5.attrs['modification_date'].split('.')[0]))
                self.tableArchive.setItem(i + 1, 4, Qt.QTableWidgetItem(str(len(list(h5.keys())))))

            cb_imp = Qt.QCheckBox()
            cb_imp.setStyleSheet("margin-left:20%; margin-right:20%;")
            cb_delete = Qt.QCheckBox()
            cb_delete.setStyleSheet("margin-left:20%; margin-right:20%;")
            self.list_item_load.append(cb_imp)
            self.list_item_delete.append(cb_delete)

            self.tableArchive.setCellWidget(i + 1, 5, cb_imp)
            self.tableArchive.setCellWidget(i + 1, 6, cb_delete)

            if flag_current_archive:
                color = Qt.QColor(200, 200, 200)
                for j in range(0, 7):
                    if j == 0 or j >= 5:
                        w = self.tableArchive.cellWidget(i + 1, j)
                        w.setAutoFillBackground(True)
                        p = w.palette()
                        p.setColor(w.backgroundRole(), color)
                        w.setPalette(p)
                    elif j < 5:
                        self.tableArchive.item(i + 1, j).setBackground(color)

            cb_imp.setObjectName(str(i))
            cb_imp.stateChanged.connect(self._sig_import_changed)
            cb_delete.setObjectName(str(i))
            cb_delete.stateChanged.connect(self._sig_delete_changed)

        if len(self.list_h5_archive) == 1:
            self.list_item_delete[0].setEnabled(False)

        self.layoutArchiveW.addWidget(self.tableArchive)
        self.layoutArchiveW.addLayout(self.buttonLayout, 1, 0)
        self.w_main.setLayout(self.layoutArchiveW)
        self.setCentralWidget(self.w_main)
        self.resize(600, 400)
        self.show()

    def _sig_name_dataset_changed(self):
        index = int(self.sender().objectName())
        ob_h5 = self.list_h5_archive[index]
        with h5py.File(ob_h5, 'a') as h5:
            h5.attrs['project_name'] = self.sender().text()

    def _sig_delete_changed(self):
        if self.sender().isChecked():
            id_import = self.sender().objectName()
            box_import = self.list_item_load[int(id_import)]
            if box_import.isChecked():
                box_import.setChecked(False)

        nb_datasets = len(self.list_item_delete)
        total_archive_delete = 0
        for dataset in self.list_item_delete:
            if dataset.isChecked():
                total_archive_delete += 1
        if total_archive_delete > 0:
            self.deleteButton.setDisabled(False)
        else:
            self.deleteButton.setDisabled(True)

        for dataset in self.list_item_delete:
            if (nb_datasets - total_archive_delete) == 1:
                if not dataset.isChecked():
                    dataset.setEnabled(False)
            else:
                dataset.setEnabled(True)

    def _sig_import_changed(self):
        if self.sender().isChecked():
            self.importButton.setDisabled(False)
            id_import = self.sender().objectName()
            box_delete = self.list_item_delete[int(id_import)]
            if box_delete.isChecked():
                box_delete.setChecked(False)

            total_checked = 0
            for box in self.list_item_load:
                if box.objectName() != id_import:
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

    def _check_dataset(self):
        self.list_h5_archive = glob.glob(str(self.pathFolderArchive) + '/pini*.h5')
        self.list_h5_archive.sort()
        self.list_h5_archive = self.list_h5_archive[::-1]

    def _create_dataset(self):
        self.dataset = ArchiveHdf5()
        self.dataset.clean_up_lock_file()
        self.dataset.create_new_dataset()
        self._check_dataset()
        self._build_dataset_widget()

    def _import_dataset(self):

        path_to_open = None
        for i, box in enumerate(self.list_item_load):
            if box.isChecked():
                path_to_open = self.list_h5_archive[i]
                break

        current_version = self.parameter['pini_parameters']['home_collection']['hdf5_pini_version']

        if path_to_open is not None:
            self.dataset = ArchiveHdf5()
            self.dataset.clean_up_lock_file()
            self.dataset.open_dataset(path_to_open)

            current_vers_hdf5pini = self.parameter['pini_parameters']['home_collection']['hdf5_pini_version']
            file_version = self.dataset.archi_h5.attrs['hdf5_pini_version']

            if file_version != current_vers_hdf5pini:
                msg = Qt.QMessageBox()
                msg.setWindowIcon(Qt.QIcon('/Icones/transp.png'))
                msg.setIcon(Qt.QMessageBox.Warning)
                msg.setStandardButtons(Qt.QMessageBox.Yes | Qt.QMessageBox.No)

                path_file_open = Path(path_to_open).name
                txt = ("The file version '%s' don't match. (%s != %s)\n"
                       % (path_file_open, file_version, current_version))
                txt += "Some feature might not work\n."
                txt += "Do you want to load it anyway ?"

                msg.setText(txt)
                msg.setWindowTitle(' ')
                answer = msg.exec_()

                if answer == Qt.QMessageBox.Yes:
                    self.close()
                else:
                    self.dataset.close_dataset()
            else:
                self.close()
            self.dataset.close_dataset()
            self.dataset.update_streaming_flags()
            self.parent.w_main.populate_table_image_selector()

    def _delete_dataset(self):

        for i, box in enumerate(self.list_item_delete):
            if box.isChecked():
                os.remove(self.list_h5_archive[i])
        self._check_dataset()
        self._build_dataset_widget()

    def closeEvent(self, event, **kwargs):
        if self.dataset is None:
            self.dataset = ArchiveHdf5()
            self.dataset.clean_up_lock_file()
            self.dataset.create_new_dataset()
            name = Path(self.dataset.path_dataset).name

            msg = Qt.QMessageBox()
            msg.setWindowIcon(Qt.QIcon('/Icones/transp.png'))
            msg.setIcon(Qt.QMessageBox.Warning)
            msg.setStandardButtons(Qt.QMessageBox.Yes)

            txt = "No Project imported or created. Creation of %s" % name
            msg.setText(txt)
            msg.setWindowTitle(' ')
            msg.exec_()
        event.accept()


class ArchiveHdf5:
    def __init__(self):
        self.path_xml = Path('./config.xml')
        self.path_dataset = ''
        self.archi_h5 = None
        self._import_config_file()
        self.dataRam = {}

    def _import_config_file(self):
        with open(self.path_xml) as fd:
            doc = xmltodict.parse(fd.read())
        self.parameter = doc
        self.pathFolderArchive = Path(self.parameter['pini_parameters']['home_collection']['path'])

    def create_new_dataset(self):
        date = datetime.now()
        current_date = str(date).split('.')[0]
        current_date = '_'.join(current_date.split(' '))
        current_date = ''.join(current_date.split(':'))
        dataset_name = 'pini_' + current_date + '.h5'
        self._import_config_file()
        self.path_dataset = Path(self.pathFolderArchive, dataset_name)

        self.archi_h5 = h5py.File(self.path_dataset, 'a')

        self.archi_h5.attrs['hdf5_pini_version'] = self.parameter['pini_parameters']['home_collection'][
            'hdf5_pini_version']
        self.archi_h5.attrs["project_name"] = f'{random.randint(0, 9999):04}'
        self.archi_h5.attrs["user"] = getpass.getuser()
        self.archi_h5.attrs["creation_date"] = str(date)
        self.archi_h5.attrs["modification_date"] = str(date)
        self.archi_h5.attrs["code"] = str(uuid.uuid4())
        self.close_dataset()

    def update_streaming_flags(self):
        self.open_current_dataset()
        for key in self.archi_h5.keys():
            self.archi_h5[key].attrs["flag_streaming"] = True
        self.close_dataset()

    def generate_lock_file(self):
        lock_file = os.path.splitext(self.path_dataset)[0] + '.lock'
        f = open(lock_file, 'w')
        f.close()

    def remove_lock_file(self):
        lock_file = os.path.splitext(self.path_dataset)[0] + '.lock'
        if os.path.exists(lock_file):
            os.remove(lock_file)

    def clean_up_lock_file(self):
        list_lock = glob.glob(str(self.pathFolderArchive) + '/*.lock')
        for lock in list_lock:
            os.remove(lock)

    def open_dataset(self, path_dataset):
        self.dataRam = {}
        self.path_dataset = Path(path_dataset)
        self.archi_h5 = h5py.File(self.path_dataset, 'a')
        for key in self.archi_h5.keys():
            self.dataRam[key] = []
        self.generate_lock_file()

    def open_current_dataset(self):
        self.archi_h5 = h5py.File(self.path_dataset, 'a')
        self.generate_lock_file()

    def open_current_dataset_read_only(self):
        self.archi_h5 = h5py.File(self.path_dataset, 'r')
        self.generate_lock_file()

    def close_dataset(self):
        self.archi_h5.flush()
        self.archi_h5.close()
        self.remove_lock_file()

    def remove_all_datasets(self):
        if self.archi_h5 is not None:
            self.close_dataset()
        self._import_config_file()
        list_h5 = glob.glob(str(self.pathFolderArchive) + '/*.h5')
        for h5files in list_h5:
            os.remove(h5files)

    def generate_empty_image(self):
        index_list = [int(k) for k in list(self.archi_h5.keys())]
        if len(index_list) == 0:
            index = '0'.zfill(5)
        else:
            index = max(index_list) + 1
            index = str(index).zfill(5)

        dt = h5py.special_dtype(vlen=str)

        self.archi_h5.create_group(index)
        self.archi_h5[index].attrs["name"] = h5py.Empty(dt)
        self.archi_h5[index].attrs["format"] = h5py.Empty(dt)
        self.archi_h5[index].attrs["type"] = h5py.Empty(dt)
        self.archi_h5[index].attrs["path_current_source_file"] = h5py.Empty(dt)
        self.archi_h5[index].attrs["flag_streaming"] = h5py.Empty(np.dtype('?'))
        self.archi_h5[index].attrs["local"] = h5py.Empty(np.dtype('?'))

        self.archi_h5[index].create_dataset("path_data", dtype=dt)
        self.archi_h5[index].create_dataset("axes", dtype=dt)
        self.archi_h5[index].create_dataset("units", dtype=dt)
        self.archi_h5[index].create_dataset("pixel_size", dtype=np.dtype('f'))
        self.archi_h5[index].create_dataset("data", dtype=np.dtype('f'))
        self.archi_h5[index].create_group("roi")
        self.archi_h5[index].create_group("pipeline")

        self.dataRam[index] = []

        self.close_dataset()

    def display_image_info(self, indexh5):
        self.open_current_dataset()
        txt = ''

        name = self.archi_h5[indexh5].attrs["name"]
        format_image = self.archi_h5[indexh5].attrs["format"]
        dtype = self.archi_h5[f'{indexh5}/data'].dtype
        txt += f'{name} [{format_image} - {dtype}]\n'

        shape = self.archi_h5[f'{indexh5}/data'].shape[:]

        px_sizes = self.archi_h5[f'{indexh5}/pixel_size'][:]
        unit_text = ''
        for i, px_size in enumerate(px_sizes):
            if hasattr(self.archi_h5[f'{indexh5}/units'][i], 'decode'):
                unit = self.archi_h5[f'{indexh5}/units'][i].decode('utf-8 ')
            else:
                unit = self.archi_h5[f'{indexh5}/units'][i]
            unit_text += f'{px_size} {unit} '

        txt += f'{shape} [ {unit_text}]\n'
        axes = self.archi_h5[f'{indexh5}/axes'][:]
        axe_text = ''
        for axe in axes:
            if hasattr(axe, 'decode'):
                axe_text += f'{axe.decode("utf-8")} '
            else:
                axe_text += f'{axe} '

        txt += f'{axe_text}\n'

        path = self.archi_h5[indexh5].attrs["path_current_source_file"]
        txt += path

        return txt

    def load_image_to_ram(self, loading_index):
        self.open_current_dataset()
        indexh5 = str(loading_index).zfill(5)

        image_type = self.archi_h5[f'{indexh5}/data'].dtype
        mem_usage_image = image_type.itemsize
        shape = self.archi_h5[f'{indexh5}/data'].shape
        for ishape in shape:
            mem_usage_image *= ishape
        mem = psutil.virtual_memory()
        if mem_usage_image > mem.available:
            msg = Qt.QMessageBox()
            msg.setWindowIcon(Qt.QIcon('/Icones/transp.png'))
            msg.setIcon(Qt.QMessageBox.Warning)
            msg.setStandardButtons(Qt.QMessageBox.Ok)
            txt = "No enough available  Virtual Memory to load the image"
            msg.setText(txt)
            msg.setWindowTitle(' ')
            msg.exec()
            return 0

        self.dataRam[indexh5] = self.archi_h5[f'{indexh5}/data'][:]
        self.archi_h5[f'{indexh5}'].attrs['flag_streaming'] = False
        self.close_dataset()
        return 1

    def free_ram(self, delete_index):
        self.open_current_dataset()
        indexh5 = str(delete_index).zfill(5)
        self.archi_h5[f'{indexh5}'].attrs['flag_streaming'] = True
        self.close_dataset()
        if indexh5 in list(self.dataRam.keys()):
            del self.dataRam[indexh5]

        self.dataRam[indexh5] = []

    def delete_image(self, index_delete):
        self.open_current_dataset()
        indexh5 = str(index_delete).zfill(5)
        if self.archi_h5[f'{indexh5}'].attrs['local']:
            # del self.archi_h5[f'{indexh5}']
            # Todo delete_H5 in local folder
            pass
        with h5py.File('./tmp.h5', 'w') as newh5:

            i = 0
            for key in list(self.archi_h5.keys()):
                if key != indexh5:
                    self.archi_h5.copy(self.archi_h5[key], newh5, str(i).zfill(5))
                    i += 1
            for attr in self.archi_h5.attrs.keys():
                newh5.attrs[attr] = self.archi_h5.attrs[attr]

        self.close_dataset()
        self._update_tmp_file()

        del self.dataRam[indexh5]
        dictmp = {}

        for key in self.dataRam.keys():
            key_num = int(key)
            if key_num > int(index_delete):
                dictmp[str(key_num - 1).zfill(5)] = self.dataRam[key]
            else:
                dictmp[key] = self.dataRam[key]

        self.dataRam = dictmp

    def _update_tmp_file(self):
        os.remove(self.path_dataset)
        os.rename('./tmp.h5', self.path_dataset)

    def populate_image(self, par_dataset):

        dt = h5py.special_dtype(vlen=str)

        self.open_current_dataset()
        index_list = [int(k) for k in list(self.archi_h5.keys())]
        indexh5 = max(index_list)
        indexh5 = str(indexh5).zfill(5)
        self.archi_h5[indexh5].attrs["name"] = par_dataset["name"]
        self.archi_h5[indexh5].attrs["format"] = par_dataset["format"]
        self.archi_h5[indexh5].attrs["path_current_source_file"] = par_dataset["path_current_source_file"]
        self.archi_h5[indexh5].attrs["flag_streaming"] = par_dataset["flag_streaming"]
        self.archi_h5[indexh5].attrs["local"] = par_dataset["local"]
        del self.archi_h5[indexh5]["axes"]
        self.archi_h5[indexh5].create_dataset("axes", data=np.array(par_dataset["axes"], dtype='S'))
        del self.archi_h5[indexh5]["units"]
        self.archi_h5[indexh5].create_dataset("units", data=np.array(par_dataset["units"], dtype=dt))
        del self.archi_h5[indexh5]["path_data"]
        self.archi_h5[indexh5].create_dataset("path_data", data=np.array(par_dataset["path_data"], dtype='S'))
        del self.archi_h5[indexh5]["pixel_size"]
        self.archi_h5[indexh5].create_dataset("pixel_size", data=np.array(par_dataset["pixel_size"],
                                                                          dtype=np.dtype('f')))

        if par_dataset['format'] == 'hdf5':

            del self.archi_h5[indexh5]["data"]
            vlayout = h5py.VirtualLayout(shape=par_dataset['shape_image'], dtype=par_dataset['data_type'])
            vsource = h5py.VirtualSource(par_dataset["path_current_source_file"], par_dataset["path_data"][0],
                                         shape=par_dataset['shape_image'])
            vlayout[...] = vsource
            self.archi_h5[indexh5].create_virtual_dataset("data", vlayout, fillvalue=-1)

        elif par_dataset['format'] == 'tiff':
            external_images = []
            if 'tiff_links' not in list(self.archi_h5.keys()):
                self.archi_h5[indexh5].create_group('tiff_links')
            dtype = None
            for i, path_tiff_file in enumerate(self.archi_h5[indexh5]["path_data"]):
                if hasattr(path_tiff_file, 'decode'):
                    path_tiff_file = path_tiff_file.decode('ascii')

                with TiffFile(path_tiff_file) as tif:
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
                            external_image = self.archi_h5[indexh5]['tiff_links'].create_dataset(name=f'tmp{i}',
                                                                                                 shape=shape,
                                                                                                 dtype=dtype,
                                                                                                 external=[
                                                                                                     (path_tiff_file,
                                                                                                      offset,
                                                                                                      bytecount)])
                            external_images.append(external_image)

            vlayout = h5py.VirtualLayout(shape=(len(self.archi_h5[indexh5]["path_data"]), shape[0], shape[1]),
                                         dtype=dtype)
            for i, ed in enumerate(external_images):
                vsource = h5py.VirtualSource(ed)
                vlayout[i] = vsource

            del self.archi_h5[indexh5]["data"]
            self.archi_h5[indexh5].create_virtual_dataset("data", vlayout, fillvalue=-1)

        self.archi_h5.close()


if __name__ == "__main__":
    archive = ArchiveHdf5()
    # archive.create_new_dataset()
    archive.open_dataset("./pini_2023-12-15_105149.h5")
    archive.generate_empty_image()
