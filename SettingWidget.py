import importQt as Qt
import xmltodict
from pathlib import Path
import glob
import psutil
import importlib.util
import ast

from LabelEditAndButton import LabelEditAndButton

class SettingWidget(Qt.QMainWindow):
    """
    QMain Window to display all setting of Pini for now only needed libraries are integrated
    """

    def __init__(self, parent=None,):
        super(SettingWidget, self).__init__(parent)
        self.parent = parent
        self.setWindowTitle('Settings')
        """Attributs"""
        self.path_xml = Path('./config.xml')

        """ Tabs Widgets Init"""
        self.tabWidget = Qt.QtabWidget()
        self.pythonLibrary = Qt.QWidget()
        self.mainSettings = Qt.QWidget()
        """Tabs Layout Init"""
        self.layoutMainSettings = Qt.QGridLayout()
        self.layoutPythonLibrary = Qt.QGridLayout()
        """Main Settings Widgets Init"""

        self.PathTmpFilesSave = LabelEditAndButton(boolLabel = True, textLabel = "Path Temporary Collection",
                                                   booltextEdit = True, textEdit = "",
                                                   boolButton = True, textButton="Browse")

        self.PathTmpFilesSave.lineEdit.setFixedWidth(500)
        self.labelInfo = Qt.QLabel()
        self.saveButton = Qt.QPushButton('Save')

        self.tableLibrary = Qt.QtableWidget()

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
        """
        Method to build the table of all libraries required
        :return:
        """
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
            self.tableLibrary.setItem(i, 0, Qt.QtableWidgetItem(lib))
            test_lib = importlib.util.find_spec(lib)
            if test_lib == None:
                self.tableLibrary.setItem(i , 1, Qt.QtableWidgetItem("Not Installed"))
                list_Install[i] = 0
            else:
                self.tableLibrary.setItem(i , 1, Qt.QtableWidgetItem("Installed"))
                list_Install[i] = 1

        self.parameter['pini_parameters']['library']['install'] = str(list_Install)


    def _checkFolder(self):
        """
        Method to check available space in the current project folder
        :return:
        """
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
        """
        Setting to change the path of the projects directories
        :return:
        """
        filePath = Qt.QFileDialog.getExistingDirectory(self,'Select Folder')
        self.PathTmpFilesSave.changeLineEdit(str(Path(filePath)))

    def _saveParameters(self):
        """
        Method call on save button pressed save the parameters into the xml parameters files
        :return:
        """
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
        """
        import xml into a python dictionary
        :return:
        """
        with open(self.path_xml) as fd:
            doc = xmltodict.parse(fd.read())
        self.parameter = doc

    def _updateWidget(self):
        """
        Update string to current project directory
        :return:
        """
        self.PathTmpFilesSave.changeLineEdit(str(Path(self.parameter['pini_parameters']['home_collection']['path'])))