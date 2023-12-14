

import importQt as qt

class ProgressBar(qt.QProgressBar):
    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.changeTxt('')

    def changeTxt(self,txt):

        self.setValue(100)
        self.setFormat(txt)
        self.setAlignment(qt.Qt.AlignCenter)




