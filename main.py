"""
Created on Mon Jan 16 17:50:34 2023

@author: broche
"""

import importQt as qt
import sys

from MainWidget import MainWidget
from SettingWidget import SettingWidget
from lib import h5pyImport
from FileFormatArchive import StartUpArchive


class MainWindow(qt.QMainWindow):
    """
    Main PINI Window Define All functions from menus bar and import main widget
    """
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.test = 1
        self.w_setting = SettingWidget(self)
        self.start_up_archive = StartUpArchive(self)
        self.w_main = MainWidget(self)
        self.setCentralWidget(self.w_main)
        self.w_h5_importer = h5pyImport.HDF5Importer(self)
        self.setWindowTitle('Pini')
        self._buildMenu()

    def _buildMenu(self):
        """
        Builder for the menus bar
        :return:
        """
        menu_bar = self.menuBar()
        
        # File Menu Project Management Import Export of Data
        file_menu = menu_bar.addMenu('&File')
        project_menu = qt.QAction('&Open Project',self)
        project_menu.triggered.connect(self._launchProjectWin)
        file_menu.addAction(project_menu)


        import_menu = file_menu.addMenu('&Import Data')
        export_menu = file_menu.addMenu('&Export Data')

        # Import Data
        import_tiff = qt.QAction('Images &Sequence', self)
        import_tiff.triggered.connect(self._importSequenceImages)
        import_menu.addAction(import_tiff)

        import_h5 = qt.QAction('&HDF5', self)
        import_h5.triggered.connect(self._importHDF5)
        import_menu.addAction(import_h5)

        # Export Data Tiff
        export_tiff = qt.QAction('Images &Sequence', self)
        #TO DO 
        #export_tiff.triggered.connect(self.w_main._export_tiff) 
        export_menu.addAction(export_tiff)

        # Export Data NX
        export_nx = qt.QAction('&HDF5/NX', self)
        #TO DO 
        #export_tiff.triggered.connect(self.w_main._export_tiff)
        export_menu.addAction(export_nx)
        
        # Setting Parameters 
        parameters = qt.QAction('Settings', self)
        parameters.triggered.connect(self._parametersGUI)
        file_menu.addAction(parameters)

        # Processing Menu 
        processing_menu = menu_bar.addMenu('&Processing')
        filter_menu = processing_menu.addMenu('Filters')
        gaussian_filter = qt.QAction('Gaussian',self)
        gaussian_filter.triggered.connect(self._imageProcessing)
        filter_menu.addAction(gaussian_filter)


    def _launchProjectWin(self):
        """
         Launch Project Manager
        :return: 
        """
        self.start_up_archive._buildArchiveWidget()

    def _importSequenceImages(self):
        """
        Simple QFile Dialog for tiff import 
        TO DO : should be moved somewhere else
        :return: 
        """
        dialog = qt.QFileDialog()
        dialog.setWindowIcon(qt.QIcon('./Icones/transp.png'))
        dialog.setNameFilter("Images (*.tiff *.tif)")
        dialog.setViewMode(qt.QFileDialog.Detail)
        dialog.setFileMode(qt.QFileDialog.FileMode.ExistingFiles)
        dialog.setDirectory("")
        if dialog.exec():
            path_tiff_sequence = dialog.selectedFiles()
            self.w_main.import_tiff_sequence(path_tiff_sequence)

    def _importHDF5(self):
        """
        Launch hdf5 widget importer
        :return: 
        """
        self.w_h5_importer.show()

    def _parametersGUI(self):
        """
        Launch Setting Widget
        :return: 
        """
        self.w_setting.show()

    def display_flash_splash(self):
        """
        To Do: Change flash Splash to a non random image
        :return: 
        """
        self.splash = qt.QSplashScreen(qt.QPixmap("Icones/pini_splash.png"))
        self.splash.show()

        # Close SplashScreen after 2 seconds (2000 ms)
        screen = qt.QGuiApplication.primaryScreen()
        geo = screen.geometry()
        height = geo.height()
        width = geo.width()
        self.splash.move(int((width/4)-(541/2)),int((height/2)-(686/2)))
        qt.QTimer.singleShot(2000, self.splash.close)

    def _imageProcessing(self):
        print(gaussian_filter.objectName())


if __name__ == "__main__":
    app = qt.QApplication(["-display"])
    m = MainWindow()
    m.setWindowIcon(qt.QIcon("Icones/pini.png"))
    m.showMaximized()
    m.show()
    m.display_flash_splash()
    sys.exit(app.exec_())
