import sys
import importQt as qt
import sys

class QCustomLabel (qt.QLabel):
    def __init__ (self, parent = None):
        super(QCustomLabel, self).__init__(parent)
        self.setMouseTracking(True)
        self.setTextLabelPosition(0, 0)
        self.setAlignment(qt.Qt.AlignCenter)

    def mouseMoveEvent (self, eventQMouseEvent):
        self.setTextLabelPosition(eventQMouseEvent.x(), eventQMouseEvent.y())
        QtGui.QWidget.mouseMoveEvent(self, eventQMouseEvent)

    def mousePressEvent (self, eventQMouseEvent):
        if eventQMouseEvent.button() == QtCore.Qt.LeftButton:
            QtGui.QMessageBox.information(self, 'Position', '( %d : %d )' % (self.x, self.y))
        QtGui.QWidget.mousePressEvent(self, eventQMouseEvent)

    def setTextLabelPosition (self, x, y):
        self.x, self.y = x, y
        self.setText('Please click on screen ( %d : %d )' % (self.x, self.y))

class QCustomWidget (qt.QWidget):
    def __init__ (self, parent = None):
        super(QCustomWidget, self).__init__(parent)
        self.setWindowOpacity(0.7)
        # Init QLabel
        self.positionQLabel = QCustomLabel(self)
        # Init QLayout
        layoutQHBoxLayout = qt.QHBoxLayout()
        layoutQHBoxLayout.addWidget(self.positionQLabel)
        layoutQHBoxLayout.setSpacing(0)
        self.setLayout(layoutQHBoxLayout)


myQApplication = qt.QApplication(sys.argv)
myQTestWidget = QCustomWidget()
myQTestWidget.show()
myQApplication.exec_()