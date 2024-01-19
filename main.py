import importQt as qt
import sys

from MainWidget import MainWidget
from SettingWidget import SettingWidget
from lib import h5pyImport
from FileFormatArchive import StartUpArchive


class MainWindow(qt.QMainWindow) :
    """
    Main PINI Window Define All functions from menus bar and import main widget
    """
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.test = 1
        self.startUpArchive = StartUpArchive(self)
        self.mainWidget = MainWidget(self)
        self.setCentralWidget(self.mainWidget)
        self.setting = SettingWidget(self)
        self.h5Import = h5pyImport.HDF5Importer(self)
        self.setWindowTitle('Pini')
        self._buildMenu()



    def _buildMenu(self):
        """
        Builder for the menus bar
        :return:
        """
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu('&File')
        project_menu = qt.QAction('&Open Project',self)
        project_menu.triggered.connect(self._launchProjectWin)
        file_menu.addAction(project_menu)


        import_menu = file_menu.addMenu('&Import Data')
        export_menu = file_menu.addMenu('&Export Data')
        #parameter_menu = file_menu.addMenu('&Settings')

        # Import Data
        import_tiff = qt.QAction('Images &Sequence', self)
        import_tiff.triggered.connect(self._importSequenceImages)
        import_menu.addAction(import_tiff)

        import_h5 = qt.QAction('&HDF5', self)
        import_h5.triggered.connect(self._importHDF5)
        import_menu.addAction(import_h5)

        # Export Data
        export_tiff = qt.QAction('Images &Sequence', self)
        #export_tiff.triggered.connect(self.mainWidget._export_tiff)
        export_menu.addAction(export_tiff)

        export_nx = qt.QAction('&HDF5/NX', self)
        #export_tiff.triggered.connect(self.mainWidget._export_tiff)
        export_menu.addAction(export_nx)

        parameters = qt.QAction('Settings',self)
        parameters.triggered.connect(self._parametersGUI)
        file_menu.addAction(parameters)

    def _launchProjectWin(self):
        self.startUpArchive._buildArchiveWidget()

    def _importSequenceImages(self):
        dialog = qt.QFileDialog()
        dialog.setWindowIcon(qt.QIcon('./Icones/transp.png'))
        dialog.setNameFilter("Images (*.tiff *.tif)")
        dialog.setViewMode(qt.QFileDialog.Detail)
        dialog.setFileMode(qt.QFileDialog.FileMode.ExistingFiles)
        dialog.setDirectory("")
        if dialog.exec():
            filenames = dialog.selectedFiles()
            self.mainWidget.loadImageSequence(filenames)

    def _importHDF5(self):
        self.h5Import.show()



    def _parametersGUI(self):
        self.setting.show()


    def flashSplash(self):
        self.splash = qt.QSplashScreen(qt.QPixmap("Icones/pini_splash.png"))
        self.splash.show()

        # Close SplashScreen after 2 seconds (2000 ms)
        screen = qt.QGuiApplication.primaryScreen()
        geo = screen.geometry()
        height = geo.height()
        width = geo.width()
        self.splash.move(int((width/4)-(541/2)),int((height/2)-(686/2)))



        qt.QTimer.singleShot(2000, self.splash.close)

if __name__ == "__main__":
    app = qt.QApplication(["-display"])
    m = MainWindow()
    m.setWindowIcon(qt.QIcon("Icones/pini.png"))
    m.showMaximized()
    m.show()
    m.flashSplash()
    sys.exit(app.exec_())
