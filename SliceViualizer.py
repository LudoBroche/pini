# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
#####------------------------------------
import time
import importQt as qt
import numpy as np

from CustomToolBar import CustomToolBar
from SliderAndLabel import SliderAndLabel
from CustomGraphicsView import CustomGraphicsView

from skimage.transform import resize
import threading


class H5Reader(qt.QObject):
    data_read = qt.pyqtSignal()
    def __init__(self, dataSet,axe,position,resolution,index):
        super(H5Reader, self).__init__()
        self.dataSet = dataSet
        self.axe = axe
        self.position = position
        self.resolution = resolution
        self.flag_load = True
        self._data = None
        self.index = index
    def run(self):
        if self.flag_load:
            if self.axe == 0:
                self._data = self.dataSet[self.position, ::self.resolution, ::self.resolution]
            elif self.axe == 1:
                self._data = self.dataSet[::self.resolution, self.position, ::self.resolution]
            elif self.axe == 2:
                self._data = self.dataSet[::self.resolution, ::self.resolution, self.position]
        self.data_read.emit()
class Timer(qt.QObject):
    progress = qt.pyqtSignal()
    finished = qt.pyqtSignal()
    def run(self):
        for i in range(0,50):
            print('Sleeping')
            time.sleep(0.1)
        print('Done Sleeping')
        self.finished.emit()



class SliceVisualizer(qt.QWidget):
    def __init__(self, planeSection, resolution,parent=None):
        qt.QWidget.__init__(self, parent)
        self.parent = parent
        self.currentPlaneSection = planeSection

        self.scene = qt.QGraphicsScene()
        self.view = CustomGraphicsView(self.scene, self)

        self.sliceSlider = SliderAndLabel(self)
        self.sliceSlider._setRange(0,0)
        self.sliceSlider.slider.valueChanged.connect(self._changeSlice)
        self.timerDisplay = -1

        self.resolution = resolution

        layout = qt.QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(self.sliceSlider)
        self.setLayout(layout)

    def displayImage(self,flag_thread=False,index=0):
        print('display ')
        if not flag_thread:
            if self.currentPlaneSection == 0:
                slice = self.dataVolume[self.sliceSlider.value(), ::self.resolution, ::self.resolution]
            elif self.currentPlaneSection == 1:
                slice = self.dataVolume[::self.resolution, self.sliceSlider.value(), ::self.resolution]
            elif self.currentPlaneSection == 2:
                slice = self.dataVolume[::self.resolution, ::self.resolution, self.sliceSlider.value()]
        else:

            slice = self.loadingWorkdersList[index]._data
            self.resolution = self.loadingWorkdersList[index].resolution
            print('Slice threads import',index,slice)

        if not slice is None:
            print('Starting Update Display')
            slice.squeeze()
            slice = resize(slice, (slice.shape[0] * self.resolution, slice.shape[1] * self.resolution),anti_aliasing=False)
            maximumValue = slice.max()
            minimumValue = slice.min()
            data = 255.0*((slice - minimumValue) / (maximumValue - minimumValue))
            data[data >= 255] = 255
            data[data <= 0] = 0
            data = np.array(data, dtype=np.uint8)

            image = qt.QImage(data, data.shape[1], data.shape[0],data.shape[1],qt.QImage.Format_Indexed8)

            pixMap = qt.QPixmap.fromImage(image)
            pixItem = qt.QGraphicsPixmapItem(pixMap)
            pixItem.setZValue(-1)
            self.scene.clear()
            self.scene.addItem(pixItem)
            self.scene.setSceneRect(0, 0, image.width(), image.height())
            self.scene.update

    def _changeSlice(self):

        if hasattr(self,'timerThread'):
            self.timerThread.quit()
            self.timerThread.start()
            print('After')

        if hasattr(self,'loadingThreadsList'):
            for th in self.loadingThreadsList:
                th.quit()
        self.displayImage(False,0)



    def _setDataVolume(self, h5Prj,index, flagOpen ):
        self.h5Prj = h5Prj
        if flagOpen:
            self.h5Prj.openCurrentArchiveRead()

        if self.h5Prj.archH5[index].attrs["flag_streaming"]:
            self.dataVolume = self.h5Prj.archH5[f'{index}/data']
        else:
            self.dataVolume = self.h5Prj.dataRam[f'{index}']

        dataShape = self.dataVolume.shape

        if (self.currentPlaneSection == 0):
            self.sliceSlider._setRange(0, dataShape[0] - 1)
        elif (self.currentPlaneSection == 1):
            self.sliceSlider._setRange(0, dataShape[1] - 1)
        elif (self.currentPlaneSection == 2):
            self.sliceSlider._setRange(0, dataShape[2] - 1)

        self.sliceSlider.slider.setValue(1)
        self.timerThread = qt.QThread()
        self.timer = Timer()
        self.timer.moveToThread(self.timerThread)
        self.timerThread.started.connect(self.timer.run)
        self.timer.finished.connect(self.timerThread.quit)
        self.timer.finished.connect(self.threadLoadNewResolution)

        self.loadingThreadsList = []
        self.loadingWorkdersList = []

        resolution = 64

        for i in range(7):
            worker = H5Reader(self.dataVolume,self.currentPlaneSection,0,resolution//(i+1),i)
            resolution *=2
            thread = qt.QThread()
            worker.moveToThread(thread)
            thread.started.connect(worker.run)
            worker.data_read.connect(thread.quit)
            worker.data_read.connect(self.displayNewResolution)
            self.loadingThreadsList.append(thread)
            self.loadingWorkdersList.append(worker)



        #self.timer.finished.connect(self.thread.deleteLater)
        #self.timerThread.finished.connect(self.thread.deleteLater)

    def displayNewResolution(self):
        self.displayImage(True,self.sender().index)

    def threadLoadNewResolution(self):
        resolution = 64
        for thread,worker in zip(self.loadingThreadsList,self.loadingWorkdersList):
            print('Starting Resolution thread')
            worker.position = self.sliceSlider.value()
            worker.resolution = resolution
            resolution //= 2
            thread.start()
            print('Done Threading')


class Interactor3D(qt.QWidget):
    CustomGraphicsViewEvent = qt.pyqtSignal()
    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)

        self.dataH5 = None
        self.dataRam = None

        self.toolBar = CustomToolBar(self)
        self.axialWidget = SliceVisualizer(0,128,self)
        self.coronalWidget = SliceVisualizer(1,128,self)
        self.sagittalWidget = SliceVisualizer(2,128,self)
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
