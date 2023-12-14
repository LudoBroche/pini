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
        self.mainWidget = MainWidget(self)
        self.setCentralWidget(self.mainWidget)
        self.setting = SettingWidget(self)
        self.h5Import = h5pyImport.HDF5Importer(self)
        self.setWindowTitle('Pini')
        self._buildMenu()
        self.startUpArchive = StartUpArchive()

    def _buildMenu(self):
        """
        Builder for the menus bar
        :return:
        """
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu('&File')
        import_menu = file_menu.addMenu('&Import Data')
        export_menu = file_menu.addMenu('&Export Data')
        #parameter_menu = file_menu.addMenu('&Settings')

        # Import Data
        import_tiff = qt.QAction('Images &Sequence', self)
        #import_tiff.triggered.connect(self.mainWidget._importTiff)
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