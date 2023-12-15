import importQt as qt
import xmltodict
from pathlib import Path
import glob
import psutil
import importlib.util
import ast



from LabelEditAndButton import LabelEditAndButton

class SettingWidget(qt.QMainWindow):

    def __init__(self, parent=None,):
        super(SettingWidget, self).__init__(parent)
        self.parent = parent
        self.setWindowTitle('Settings')
        """Attributs"""
        self.path_xml = Path('./config.xml')

        """ Tabs Widgets Init"""
        self.tabWidget = qt.QTabWidget()
        self.pythonLibrary = qt.QWidget()
        self.mainSettings = qt.QWidget()
        """Tabs Layout Init"""
        self.layoutMainSettings = qt.QGridLayout()
        self.layoutPythonLibrary = qt.QGridLayout()
        """Main Settings Widgets Init"""

        self.PathTmpFilesSave = LabelEditAndButton(boolLabel = True, textLabel = "Path Temporary Collection",
                                                   booltextEdit = True, textEdit = "",
                                                   boolButton = True, textButton="Browse")

        self.PathTmpFilesSave.lineEdit.setFixedWidth(500)
        self.labelInfo = qt.QLabel()
        self.saveButton = qt.QPushButton('Save')

        self.tableLibrary = qt.QTableWidget()

        """Signals"""
        self.PathTmpFilesSave.button.clicked.connect(self._chooseHomeDirectory)
        self.PathTmpFilesSave.lineEdit.textChanged.connect(self._checkFolder)
        self.saveButton.clicked.connect(self._saveParameters)

        """Widget/Layout Builder"""
        self.layoutMainSettings.addWidget(self.PathTmpFilesSave)
        self.layoutMainSettings.addWidget(self.labelInfo)
        self.layoutMainSettings.addWidget(self.saveButton)
        self.mainSettings.setLayout(self.layoutMainSettings)

        self.layoutPythonLibrary.addWidget(self.tableLibrary)
        self.pythonLibrary.setLayout(self.layoutPythonLibrary)
        self.tabWidget.addTab(self.mainSettings, "Settings")
        self.tabWidget.addTab(self.pythonLibrary, "Python Library")
        self.setCentralWidget(self.tabWidget)

        "Init Methods"
        self._loadConfigFile()

        self.pathArchiveInit = str(Path(self.parameter['pini_parameters']['home_collection']['path']))

        self._updateWidget()
        self._checkFolder()
        self._buildTable()

    def _buildTable(self):
        self.tableLibrary.setColumnCount(2)
        self.tableLibrary.verticalHeader().setVisible(False)
        self.tableLibrary.horizontalHeader().setVisible(False)

        list_library = self.parameter['pini_parameters']['library']['names']
        res = list(map(str, list_library[1:-1].split(',')))
        list_library = res

        list_Install = self.parameter['pini_parameters']['library']['install']
        res = list(map(int, list_Install[1:-1].split(',')))
        list_Install = res

        self.tableLibrary.setRowCount(len(list_library))
        for i, lib in enumerate(list_library):
            self.tableLibrary.setItem(i, 0, qt.QTableWidgetItem(lib))
            test_lib = importlib.util.find_spec(lib)
            if test_lib == None:
                self.tableLibrary.setItem(i , 1, qt.QTableWidgetItem("Not Installed"))
                list_Install[i] = 0
            else:
                self.tableLibrary.setItem(i , 1, qt.QTableWidgetItem("Installed"))
                list_Install[i] = 1

        self.parameter['pini_parameters']['library']['install'] = str(list_Install)


    def _checkFolder(self):
        path = Path(self.PathTmpFilesSave.valueLineEdit())
        if path.exists():

            hdd = psutil.disk_usage(str(path))
            free_space = hdd.free // (2 ** 30)
            pc_free_space = round((hdd.used  // (2 ** 30))/(hdd.total // (2 ** 30)) * 100.0)

            if (hdd.free // (2 ** 30)) > 1000:
                string_space = '{}/{} TiB ( {} % )'.format(free_space/1000,hdd.total // ((2 ** 30)*1000), pc_free_space)

            else:
                string_space = '{}/{} GiB ( {} % )'.format(free_space, hdd.total // ((2 ** 30)), pc_free_space)
                
            self.stringFreeSpace = string_space

            path_file = str(Path(path, '*.h5'))
            list_h5 = glob.glob(path_file)

            if len(list_h5) == 0:
                self.labelInfo.setText('No Data Archived {}'.format(string_space))
            else:
                if len(list_h5) == 1:
                    string = 'Found 1 data File {}'.format(string_space)
                else:
                    string = 'Found {} data file {}'.format(len(list_h5),string_space)

                self.labelInfo.setText(string)
        else:
            self.labelInfo.setText('Warning: Directory does not exist!')

    def _chooseHomeDirectory(self):
        filePath = qt.QFileDialog.getExistingDirectory(self,'Select Folder')
        self.PathTmpFilesSave.changeLineEdit(str(Path(filePath)))

    def _saveParameters(self):
        path = self.PathTmpFilesSave.valueLineEdit()
        self.parameter['pini_parameters']['home_collection']['path'] = str(Path(path))
        with open(self.path_xml, 'w') as result_file:
            result_file.write(xmltodict.unparse(self.parameter))

        self.parent.startUpArchive._testFolderWriteable()

        if (self.pathArchiveInit != self.PathTmpFilesSave.textEdit) or (not self.parent.startUpArchive.flag_writeable):
            self.parent.startUpArchive._startUpMessageBox()
        elif self.parent.startUpArchive.flag_writeable:
            self.close()



    def _loadConfigFile(self):
        with open(self.path_xml) as fd:
            doc = xmltodict.parse(fd.read())
        self.parameter = doc

    def _updateWidget(self):
        self.PathTmpFilesSave.changeLineEdit(str(Path(self.parameter['pini_parameters']['home_collection']['path'])))