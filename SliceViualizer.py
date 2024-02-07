# -*- coding: utf-8 -*-


import importQt as qt
import numpy as np

from CustomToolBar import CustomToolBar
from SliderAndLabel import SliderAndLabel
from CustomGraphicsView import CustomGraphicsView
import time


class SliceVisualizer(qt.QWidget):
    def __init__(self, planeSection, parent=None):
        qt.QWidget.__init__(self, parent)
        self.parent = parent
        self.currentPlaneSection = planeSection

        self.scene = qt.QGraphicsScene()
        self.view = CustomGraphicsView(self.scene, self)

        self.sliceSlider = SliderAndLabel(self)
        self.sliceSlider._setRange(0,0)
        self.sliceSlider.slider.valueChanged.connect(self._changeSlice)

        layout = qt.QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(self.sliceSlider)
        self.setLayout(layout)

    def _changeSlice(self):

        self.scene.clear()
        if (self.currentPlaneSection == 0):
            self.slice = np.copy(self.dataVolume[self.sliceSlider.value(), :, :])

        elif (self.currentPlaneSection == 1):
            self.slice = np.copy(self.dataVolume[:, self.sliceSlider.value(), :])

        elif (self.currentPlaneSection == 2):
            self.slice = np.copy(self.dataVolume[:, :, self.sliceSlider.value()])

        self.slice.squeeze()

        self.maximumValue = self.slice.max()
        self.minimumValue = self.slice.min()

        self.data = 255.0*((self.slice - self.minimumValue) / (self.maximumValue - self.minimumValue))

        self.data[self.data >= 255] = 255
        self.data[self.data <= 0] = 0
        self.data = np.array(self.data, dtype=np.uint8)
        self.display_image()


    def _setDataVolume(self, h5Prj,index, flagOpen ):

        self.h5Prj = h5Prj
        if flagOpen:
            self.h5Prj.openCurrentArchiveRead()

        if h5Prj.archH5[index].attrs["flag_streaming"]:
            self.dataVolume = self.h5Prj.archH5[f'{index}/data']
            self.maximumValue = -1
            self.minimumValue = -1
        else:
            self.dataVolume = self.h5Prj.dataRam[f'{index}']
            self.maximumValue = self.dataVolume.max()
            self.minimumValue = self.dataVolume.min()

        self.dataShape = self.dataVolume.shape

        if (self.currentPlaneSection == 0):
            self.sliceSlider._setRange(0, self.dataShape[0] - 1)
        elif (self.currentPlaneSection == 1):
            self.sliceSlider._setRange(0, self.dataShape[1] - 1)
        elif (self.currentPlaneSection == 2):
            self.sliceSlider._setRange(0, self.dataShape[2] - 1)

        self._changeSlice()
        self.scene.update

    def display_image(self):
        self.image = qt.QImage(self.data, self.data.shape[1], self.data.shape[0], self.data.shape[1],
                               qt.QImage.Format_Indexed8)

        pixMap = qt.QPixmap.fromImage(self.image)
        pixItem = qt.QGraphicsPixmapItem(pixMap)
        pixItem.setZValue(-1)
        self.scene.addItem(pixItem)
        self.scene.setSceneRect(0, 0, self.image.width(), self.image.height())
        self.scene.update


class Interactor3D(qt.QWidget):
    CustomGraphicsViewEvent = qt.pyqtSignal()
    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)

        self.dataH5 = None
        self.dataRam = None

        self.toolBar = CustomToolBar(self)
        self.axialWidget = SliceVisualizer(0,self)
        self.coronalWidget = SliceVisualizer(1,self)
        self.sagittalWidget = SliceVisualizer(2,self)
        self.timeSlider = SliderAndLabel(self)
        self.timeSlider._setRange(0,0)

        layoutTop = qt.QHBoxLayout()
        layoutTop.addWidget(self.toolBar)

        layout = qt.QVBoxLayout()
        layout.addLayout(layoutTop)

        splitterVertical = qt.QSplitter(self)
        splitterAxialCoronal = qt.QSplitter(0, self)

        splitterVertical.addWidget(self.axialWidget)
        splitterAxialCoronal.addWidget(self.sagittalWidget)
        splitterAxialCoronal.addWidget(self.coronalWidget)
        splitterVertical.addWidget(splitterAxialCoronal)
        layout.addWidget(splitterVertical,1)
        layout.addWidget(self.timeSlider)
        self.setLayout(layout)

    def newDisplay(self,h5Prj,index):

        self.h5Prj = h5Prj
        self.index = f'{int(index):05}'
        self.axialWidget._setDataVolume(self.h5Prj, self.index,1)
        self.coronalWidget._setDataVolume(self.h5Prj, self.index,0)
        self.sagittalWidget._setDataVolume(self.h5Prj, self.index,0)
