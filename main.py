"""
MIT License

Copyright (c) [2024] [Ludovic Broche]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import importQt as Qt
import sys

from MainWidget import MainWidget
from SettingWidget import SettingWidget
from lib import h5pyImport
from FileFormatArchive import StartUpArchive


class MainWindow(Qt.QMainWindow):
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
        project_menu = Qt.QAction('&Open Project',self)
        project_menu.triggered.connect(self._launchProjectWin)
        file_menu.addAction(project_menu)


        import_menu = file_menu.addMenu('&Import Data')
        export_menu = file_menu.addMenu('&Export Data')

        # Import Data
        import_tiff = Qt.QAction('Images &Sequence', self)
        import_tiff.triggered.connect(self._importSequenceImages)
        import_menu.addAction(import_tiff)

        import_h5 = Qt.QAction('&HDF5', self)
        import_h5.triggered.connect(self._importHDF5)
        import_menu.addAction(import_h5)

        # Export Data Tiff
        export_tiff = Qt.QAction('Images &Sequence', self)
        #TO DO 
        #export_tiff.triggered.connect(self.w_main._export_tiff) 
        export_menu.addAction(export_tiff)

        # Export Data NX
        export_nx = Qt.QAction('&HDF5/NX', self)
        #TO DO 
        #export_tiff.triggered.connect(self.w_main._export_tiff)
        export_menu.addAction(export_nx)
        
        # Setting Parameters 
        parameters = Qt.QAction('Settings', self)
        parameters.triggered.connect(self._parametersGUI)
        file_menu.addAction(parameters)

        # Processing Menu 
        processing_menu = menu_bar.addMenu('&Processing')
        filter_menu = processing_menu.addMenu('Filters')
        gaussian_filter = Qt.QAction('Gaussian',self)
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
        dialog = Qt.QFileDialog()
        dialog.setWindowIcon(Qt.QIcon('./Icones/transp.png'))
        dialog.setNameFilter("Images (*.tiff *.tif)")
        dialog.setViewMode(Qt.QFileDialog.Detail)
        dialog.setFileMode(Qt.QFileDialog.FileMode.ExistingFiles)
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
        self.splash = Qt.QSplashScreen(Qt.QPixmap("Icones/pini_splash.png"))
        self.splash.show()

        # Close SplashScreen after 2 seconds (2000 ms)
        screen = Qt.QGuiApplication.primaryScreen()
        geo = screen.geometry()
        height = geo.height()
        width = geo.width()
        self.splash.move(int((width/4)-(541/2)),int((height/2)-(686/2)))
        Qt.QTimer.singleShot(2000, self.splash.close)

    def _imageProcessing(self):
        print(gaussian_filter.objectName())


if __name__ == "__main__":
    app = Qt.QApplication(["-display"])
    m = MainWindow()
    m.setWindowIcon(Qt.QIcon("Icones/pini.png"))
    m.showMaximized()
    m.show()
    m.display_flash_splash()
    sys.exit(app.exec_())
