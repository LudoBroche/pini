# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 17:50:34 2023

@author: broche
"""

import os.path
import importQt as Qt
import psutil
import fabio

from SliceViualizer import Interactor3D
from VolumeRenderingGUI import VolumeRenderingGUI
from LoadingDataW import LoadingDataW
from WidgetImageProcessing import CustomImageProcessingWidget


class AlignDelegate(Qt.QStyledItemDelegate):
    """
    class to modify the QLabel alignment in a table
    """

    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.display_alignment = Qt.Qt.AlignCenter


class IconDelegate(Qt.QStyledItemDelegate):
    """
    class to modify the QIcon alignment in a table
    """

    def initStyleOption(self, option, index):
        super(IconDelegate, self).initStyleOption(option, index)
        if option.features & Qt.QStyleOptionViewItem.HasDecoration:
            s = option.decorationSize
            s.setWidth(option.rect.width())
            option.decorationSize = s


class MainWidget(Qt.QWidget):
    """
    Main Central Widget to the PINI application 
    """

    def __init__(self, parent=None):
        Qt.QWidget.__init__(self, parent)
        
        """ Attributes """
        self.icon_display_on = None
        self.icon_display_off = None
        self.icon_ram = None
        self.icon_hdd = None
        self.h5_archive = None
        self.loader = None
        self.par_dataset = None
        self.parent = parent
        self.timer = Qt.QTimer(self)
        
        self.timer.start(1000)
        self._build_ly_main()

    def _build_ly_main(self):

        """ Widgets Initialisation """

        ly_main = Qt.QGridLayout()
        w_tab = Qt.QTabWidget(self)
        w_volume_viewer = Qt.QWidget(self)
        w_main_volume_viewer = VolumeRenderingGUI()
        ly_viewer = Qt.QGridLayout()
        w_right_panel = Qt.QWidget(self)
        self.w_image_viewer = Interactor3D(self)
        self.system_info_hdd = Qt.QLabel()
        self.system_info_ram = Qt.QLabel()
        w_left_right_splitter = Qt.QSplitter(Qt.Qt.Horizontal)

        # Testing Will be removed when Image Processing Main Class is implemented
        par_test = {'name': '', 'ImageSelection': [], 'LineEditParameters': {}}
        par_test['LineEditParameters']['Names'] = []
        par_test['LineEditParameters']['initValues'] = []
        self.w_image_processing = CustomImageProcessingWidget(par_test, self)
        self.w_image_processing.hide()
        # ------

        """Methods Call """
        self._build_image_selector()

        """Signals"""
        w_tab.currentChanged.connect(self._sig_tab_changed)
        self.timer.timeout.connect(self._sig_generate_pc_info_string)

        """Widget Placement"""
        ly_right_panel = Qt.QVBoxLayout()
        ly_right_panel.addWidget(self.w_image_selector)
        ly_right_panel.addWidget(self.w_image_processing)
        ly_right_panel.addWidget(self.system_info_hdd)
        ly_right_panel.addWidget(self.system_info_ram)

        w_right_panel.setLayout(ly_right_panel)
        w_left_right_splitter.addWidget(self.w_image_viewer)
        w_left_right_splitter.addWidget(w_right_panel)

        width = Qt.QDesktopWidget().screenGeometry().width()
        w_left_right_splitter.setSizes([width - 500, 280])

        ly_viewer.addWidget(w_main_volume_viewer)
        w_volume_viewer.setLayout(ly_viewer)

        w_tab.addTab(w_left_right_splitter, '2D Viewer')
        w_tab.addTab(w_volume_viewer, '3D Viewer')

        ly_main.addWidget(w_tab)
        self.setLayout(ly_main)

    def _init_system_info(self):
        """
        Set font size for system info w_label_image_names
        :return: 
        """
        font_system = self.system_info_hdd.font()
        font_system.setPointSize(10)
        self.system_info_hdd.setFont(font_system)
        self.system_info_ram = Qt.QLabel()
        font_system = self.system_info_ram.font()
        font_system.setPointSize(10)
        self.system_info_ram.setFont(font_system)

    def _sig_generate_pc_info_string(self):
        """
        Generate string to display computer info ram / hdd
        :return: 
        """
        path = self.parent.w_setting.parameter['pini_parameters']['home_collection']['path']
        hdd = psutil.disk_usage(str(path))

        if (hdd.total // (2 ** 30)) > 1000:
            string_space = (f'HDD: {hdd.used // (2 ** 30 * 1000)}/'
                            f'{hdd.total // (2 ** 30 * 1000)} TiB [{hdd.percent} %]')

        else:
            string_space = f'HDD: {hdd.used // 2 ** 30}/{hdd.total // 2 ** 30} GiB ( {hdd.percent} % )'

        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent()

        if (mem.total // (2 ** 30)) > 1000:
            string_mem = (f'CPU: {cpu} % | RAM: {mem.used // (2 ** 30 * 1000)}'
                          f'/{mem.total // (2 ** 30 * 1000)} TiB [{mem.percent} %]')
        else:
            string_mem = (f'CPU: {cpu} % | RAM: {mem.used // (2 ** 30)}'
                          f'/{mem.total // (2 ** 30)} GiB [{mem.percent} %]')

        self.system_info_hdd.setText(string_space)
        self.system_info_ram.setText(string_mem)

    def _build_image_selector(self):
        """
        Initialization of the image selector
        :return: 
        """
        self.w_image_selector = Qt.QTableWidget(self)
        self.w_image_selector.setRowCount(0)
        self.w_image_selector.setColumnCount(4)
        self.w_image_selector.setShowGrid(False)
        self.w_image_selector.horizontalHeader().hide()

    def populate_table_image_selector(self):
        """
        Populate image selector from project data content
        To Do: Should be moved to separate widget file
        :return: 
        """
        # opening of the project archived
        self.parent.start_up_archive.dataset.open_current_dataset()
        self.h5_archive = self.parent.start_up_archive.dataset
        self.h5_archive.open_current_dataset()

        table_row_count = self.w_image_selector.rowCount()

        # Remove all already archive image
        while len(list(self.h5_archive.archi_h5.keys())) < table_row_count:
            self.w_image_selector.removeRow(0)
            table_row_count = self.w_image_selector.rowCount()

        # Populate image into table
        for i, key in enumerate(list(self.h5_archive.archi_h5.keys())):
            if i >= table_row_count:
                self.w_image_selector.insertRow(i)

            # Button to switch from ram to live hdf5 view
            w_button_ram_hdd = Qt.QPushButton()
            w_button_ram_hdd.setFlat(True)
            w_button_ram_hdd.setCheckable(True)
            w_button_ram_hdd.setStyleSheet("QPushButton: flat;border: none")
            w_button_ram_hdd.setObjectName(f'{i}')
            self.icon_hdd = Qt.QIcon('./Icones/hdd.png')
            self.icon_ram = Qt.QIcon('./Icones/ram.png')

            # Set the state of button if the image is on streaming mode or not
            if self.h5_archive.archi_h5[f'{key}'].attrs['flag_streaming']:
                w_button_ram_hdd.setIcon(self.icon_hdd)
                w_button_ram_hdd.setChecked(False)
            else:
                w_button_ram_hdd.setIcon(self.icon_ram)
                w_button_ram_hdd.setChecked(True)

            # Init button to display image
            self.icon_display_off = Qt.QIcon('./Icones/eye_close.png')
            self.icon_display_on = Qt.QIcon('./Icones/eye_open.png')

            w_display = Qt.QPushButton()
            w_display.setFlat(True)
            w_display.setCheckable(True)
            w_display.setStyleSheet("QPushButton: flat;border: none")
            w_display.setObjectName(f'{i}')
            w_display.setIcon(Qt.QIcon('./Icones/eye_close.png'))
            w_display.setChecked(False)

            # Init delete Button
            w_delete_button = Qt.QPushButton()
            w_delete_button.setIcon(Qt.QIcon('./Icones/trash.png'))
            w_delete_button.setFlat(True)
            w_delete_button.setCheckable(True)
            w_delete_button.setStyleSheet("QPushButton: flat;border: none")
            w_delete_button.setObjectName(f'{i}')

            # Init editable label of image
            w_label_image_name = Qt.QLineEdit(self.h5_archive.archi_h5[f'{key}'].attrs['name'])
            w_label_image_name.setFrame(False)
            w_label_image_name.editingFinished.connect(self._sig_name_image_changed)
            w_label_image_name.setObjectName(f'{i}')

            txt = self.h5_archive.display_image_info(key)
            w_label_image_name.setToolTip(txt)

            self.w_image_selector.setCellWidget(i, 0, w_label_image_name)
            self.w_image_selector.setCellWidget(i, 1, w_display)
            self.w_image_selector.setCellWidget(i, 2, w_button_ram_hdd)
            self.w_image_selector.setCellWidget(i, 3, w_delete_button)

            w_display.clicked.connect(self._sig_display_image)
            w_button_ram_hdd.clicked.connect(self._sig_ram_hdd_button_clicked)
            w_delete_button.clicked.connect(self._sig_delete_image)

        self.w_image_selector.horizontalHeader().setSectionResizeMode(0, Qt.QHeaderView.ResizeToContents)
        self.w_image_selector.horizontalHeader().setSectionResizeMode(1, Qt.QHeaderView.ResizeToContents)
        self.w_image_selector.horizontalHeader().setSectionResizeMode(2, Qt.QHeaderView.ResizeToContents)
        self.w_image_selector.horizontalHeader().setSectionResizeMode(3, Qt.QHeaderView.ResizeToContents)
        self.h5_archive.close_dataset()

        # Update the image processing widget when new image is imported
        self.w_image_processing.update()

    def _sig_name_image_changed(self):
        """
        Change name of image online edit editing
        To Do : Move with populate_table_image_selector
        :return: 
        """
        self.h5_archive.open_current_dataset()
        index = int(self.sender().objectName())
        name = self.sender().text()
        self.h5_archive.archi_h5[f'{index:05}'].attrs['name'] = name
        self.h5_archive.close_dataset()
        self.populate_table_image_selector()

    def _sig_delete_image(self):
        """
        Remove Image From project and update image selector
        To Do : Move with populate_table_image_selector
        :return: 
        """
        pos_deletion = self.sender().objectName()
        self.h5_archive.delete_image(int(pos_deletion))
        self.populate_table_image_selector()

    def _sig_display_image(self):
        """
        Call image viewer for new display
        To Do : Move with populate_table_image_selector
        :return: 
        """
        index = self.sender().objectName()
        if self.sender().isChecked():
            self.sender().setIcon(self.icon_display_on)
            for i in range(0, self.w_image_selector.rowCount()):
                w = self.w_image_selector.cellWidget(i, 1)
                if w.objectName() != index:
                    w.setChecked(False)
                    w.setIcon(self.icon_display_off)
            self.w_image_viewer.launch_display(self.h5_archive, index)

        else:
            self.sender().setIcon(self.icon_display_off)

    def _sig_ram_hdd_button_clicked(self):
        """
        Change from hdf5 streaming to ram or vise versa
        To Do : Move with populate_table_image_selector
        :return: 
        """
        index = self.sender().objectName()
        if self.sender().isChecked():
            self.sender().setIcon(self.icon_ram)
            error = self.h5_archive.loadDataToRam(int(index))
            if not error:
                self.sender().setChecked(False)
                self.sender().setIcon(self.icon_hdd)
        else:
            self.sender().setIcon(self.icon_hdd)
            self.h5_archive.free_ram(int(index))

    def import_tiff_sequence(self, path_tiff_sequence):
        """
        Initialize tiff sequence import 
        To Do: Move to a new import python file
        :param path_tiff_sequence: list of all files to import
        :return: 
        """

        path_tiff_sequence.sort()
        path_first_tiff = path_tiff_sequence[0]
        tiff_file = fabio.open(path_first_tiff)

        self.par_dataset = {'name': os.path.basename(path_tiff_sequence[0]), 'format': 'tiff',
                            'path_original_source_file': os.path.dirname(path_tiff_sequence[0]),
                            'path_current_source_file': os.path.dirname(path_tiff_sequence[0]),
                            'path_data': path_tiff_sequence, 'flag_streaming': True, 'local': False}

        if len(path_tiff_sequence) > 1:
            self.par_dataset['shape_image'] = (tiff_file.shape[0], tiff_file.shape[1], len(path_tiff_sequence))
        elif len(path_tiff_sequence) == 1:
            self.par_dataset['shape_image'] = (tiff_file.shape[0], tiff_file.shape[1])
        else:
            msg = Qt.QMessageBox()
            msg.setIcon(Qt.QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('No File selected')
            msg.setWindowTitle("Error")
            msg.exec_()
            return 0

        self.par_dataset['data_type'] = tiff_file.dtype
        tiff_file.close()

        self.loader = LoadingDataW(self.par_dataset['shape_image'], self.par_dataset['data_type'],
                                   self.par_dataset['name'],
                                   self.par_dataset['path_current_source_file'], self)
        self.loader.validateButton.clicked.connect(self._sig_add_image_to_archive)
        self.loader.show()

    def import_hdf5(self, path_hdf5_file, hdf5_path_image, ob_hdf5):
        """
        Initialize hdf5 sequence import 
        To Do: Move to a new import python file
        :param path_hdf5_file: Path to the hdf5 file
        :param hdf5_path_image: Internal path to the hdf5 image data
        :param ob_hdf5: Hdf5 file from H5py
        :return: 
        """
        self.par_dataset = {'name': os.path.basename(path_hdf5_file[0]), 'format': 'hdf5',
                            'path_current_source_file': path_hdf5_file[0], 'path_data': [hdf5_path_image],
                            'flag_streaming': True, 'shape_image': ob_hdf5[hdf5_path_image].shape,
                            'data_type': ob_hdf5[hdf5_path_image].dtype, 'local': False}
        self.loader = LoadingDataW(self.par_dataset['shape_image'], self.par_dataset['data_type'],
                                   self.par_dataset['name'], self.par_dataset['path_current_source_file'], self)
        self.loader.validateButton.clicked.connect(self._sig_add_image_to_archive)
        self.loader.show()

    def _sig_add_image_to_archive(self):
        """
        Fill up parameter dictionary with metadata and call archive image populate
        :return:
        """
        self.par_dataset['name'] = self.loader.nameImage
        self.par_dataset['axes'] = self.loader.returnAxesInfo()
        self.par_dataset['units'] = self.loader.returnUnitsInfo()
        self.par_dataset['pixel_size'] = self.loader.returnPixelsInfo()

        """Data Dictionary"""
        self.parent.start_up_archive.dataset.open_current_dataset()
        self.h5_archive = self.parent.start_up_archive.dataset
        self.h5_archive.generate_empty_image()
        self.h5_archive.populate_image(self.par_dataset)
        self.populate_table_image_selector()
        self.loader.close()

    def _sig_tab_changed(self):
        """
        Init Volume Rendering Widget when switch to the volume tab
        To Do: Not Fully Implemented
        :return:
        """
        """
        if tabIndex == 1:
            self.w_main_volume_viewer.ImagesList = self.Name_list
            self.w_main_volume_viewer.setImages()
            self.w_main_volume_viewer.DataList = self.Data_list
            self.w_main_volume_viewer.ItemLists = self.Items_list
        """
        pass
