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
    def __init__(self, dataSet,axe,position,resolution,index,resoStatic,resoCurrent):
        super(H5Reader, self).__init__()
        self.dataSet = dataSet
        self.axe = axe
        self.position = position
        self.resolution = resolution
        self.resoStatic = resoStatic
        self.resoCurrent = resoCurrent
        self.flag_load = True
        self._data = None
        self.index = index
        self.pos_p1 = 0
        self.pos_p2 = 0
        self.deltaTimeLimit = 0.05
    def run(self):
        if self.flag_load:
            before = time.time()
            if self.axe == 0:
                slice11 = self.dataSet[self.position, 0:self.pos_p1:self.resolution, 0:self.pos_p2:self.resolution]
                slice22 = self.dataSet[self.position, self.pos_p1+1::self.resolution, self.pos_p2+1::self.resolution]
                slice12 = self.dataSet[self.position, 0:self.pos_p1:self.resolution, self.pos_p2+1::self.resolution]
                slice21 = self.dataSet[self.position, self.pos_p1+1::self.resolution, 0:self.pos_p2:self.resolution]

            elif self.axe == 1:

                slice11 = self.dataSet[0:self.pos_p1:self.resolution,self.position, 0:self.pos_p2:self.resolution]
                slice12 = self.dataSet[0:self.pos_p1:self.resolution,self.position,  self.pos_p2+1::self.resolution]
                slice21 = self.dataSet[self.pos_p1+1::self.resolution, self.position,  0:self.pos_p2:self.resolution]
                slice22 = self.dataSet[self.pos_p1+1::self.resolution,self.position,  self.pos_p2+1::self.resolution]

            elif self.axe == 2:
                slice11 = self.dataSet[0:self.pos_p1:self.resolution, 0:self.pos_p2:self.resolution,self.position,]
                slice12 = self.dataSet[0:self.pos_p1:self.resolution, self.pos_p2+1::self.resolution,self.position,]
                slice21 = self.dataSet[self.pos_p1+1::self.resolution,   0:self.pos_p2:self.resolution,self.position,]
                slice22 = self.dataSet[self.pos_p1+1::self.resolution, self.pos_p2+1::self.resolution,self.position,]

            slice1 = np.hstack([slice11,slice12])
            slice2 = np.hstack([slice21, slice22])
            self._data = np.vstack([slice1, slice2])
            deltaTime = time.time() - before
            print(deltaTime)
            if self.resolution != self.resoCurrent[-1]:
                if deltaTime < self.deltaTimeLimit:
                    range_reso = int(np.emath.logn(4,self.resolution))
                    self.resoCurrent = []
                    for i in range(range_reso+1):
                        self.resoCurrent.append(4**i)
        self.data_read.emit()


class SliceVisualizer(qt.QWidget):
    def __init__(self, planeSection,parent=None):
        qt.QWidget.__init__(self, parent)
        self.parent = parent
        self.currentPlaneSection = planeSection

        self.scene = qt.QGraphicsScene()
        self.view = CustomGraphicsView(self.scene, self)

        self.sliceSlider = SliderAndLabel(self)
        self.sliceSlider._setRange(0,0)
        self.sliceSlider.slider.valueChanged.connect(self._changeSlice)
        self.sliceSlider.slider.sliderPressed.connect(self._stopAllThreads)
        self.sliceSlider.slider.sliderReleased.connect(self._startAllThreads)

        self.timerDisplay = -1

        layout = qt.QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(self.sliceSlider)
        self.setLayout(layout)

    def displayImage(self,flag_thread=False,index=0):

        if not flag_thread:
            if hasattr(self, 'fastResolution'):
                if self.currentPlaneSection == 0:
                    pos_p1 = self.parent.coronalWidget.sliceSlider.value()
                    pos_p2 = self.parent.sagittalWidget.sliceSlider.value()
                    slice11 = self.dataVolume[self.sliceSlider.value(), 0:pos_p1:self.fastResolution, 0:pos_p2:self.fastResolution]
                    slice12 = self.dataVolume[self.sliceSlider.value(), 0:pos_p1:self.fastResolution, pos_p2+1::self.fastResolution]
                    slice21 = self.dataVolume[self.sliceSlider.value(), pos_p1+1::self.fastResolution, 0:pos_p2:self.fastResolution]
                    slice22 = self.dataVolume[self.sliceSlider.value(), pos_p1+1::self.fastResolution, pos_p2+1::self.fastResolution]

                elif self.currentPlaneSection == 1:
                    pos_p1 = self.parent.axialWidget.sliceSlider.value()
                    pos_p2 = self.parent.sagittalWidget.sliceSlider.value()
                    slice11 = self.dataVolume[0:pos_p1:self.fastResolution,self.sliceSlider.value(), 0:pos_p2:self.fastResolution]
                    slice12 = self.dataVolume[0:pos_p1:self.fastResolution,self.sliceSlider.value(),  pos_p2+1::self.fastResolution]
                    slice21 = self.dataVolume[pos_p1+1::self.fastResolution, self.sliceSlider.value(),  0:pos_p2:self.fastResolution]
                    slice22 = self.dataVolume[pos_p1+1::self.fastResolution,self.sliceSlider.value(),  pos_p2+1::self.fastResolution]

                elif self.currentPlaneSection == 2:
                    pos_p1 = self.parent.axialWidget.sliceSlider.value()
                    pos_p2 = self.parent.coronalWidget.sliceSlider.value()
                    slice11 = self.dataVolume[ 0:pos_p1:self.fastResolution, 0:pos_p2:self.fastResolution,self.sliceSlider.value()]
                    slice12 = self.dataVolume[ 0:pos_p1:self.fastResolution, pos_p2+1::self.fastResolution,self.sliceSlider.value()]
                    slice21 = self.dataVolume[pos_p1+1::self.fastResolution, 0:pos_p2:self.fastResolution,self.sliceSlider.value()]
                    slice22 = self.dataVolume[pos_p1+1::self.fastResolution, pos_p2+1::self.fastResolution,self.sliceSlider.value()]
                slice1 = np.hstack([slice11,slice12])
                slice2 = np.hstack([slice21, slice22])
                slice = np.vstack([slice1, slice2])
            else:
                slice = None
        else:
            res = self.loadingWorkdersList[index].resolution
            if len(self.currentRes) > len(self.loadingWorkdersList[index].resoCurrent):
                self.currentRes = self.loadingWorkdersList[index].resoCurrent
            self.fastResolution = self.currentRes[-1]



            if self.resolution > res:
                slice = self.loadingWorkdersList[index]._data
                self.resolution = res
            else:
                slice  = None

        if (not slice is None):
            slice.squeeze()
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
            self.view.fitInView(self.scene.sceneRect(), qt.Qt.KeepAspectRatio)
            self.scene.update

    def _startAllThreads(self):

        self.resolution = self.currentRes[-1]
        self.threadLoadNewResolution()

        if self.currentPlaneSection == 0:
            if self.parent.coronalWidget.resolution !=1:
                self.parent.coronalWidget.threadLoadNewResolution()
            if self.parent.sagittalWidget.resolution !=1:
                self.parent.sagittalWidget.threadLoadNewResolution()

        if self.currentPlaneSection == 1:
            if self.parent.axialWidget.resolution !=1:
                self.parent.axialWidget.threadLoadNewResolution()
            if self.parent.sagittalWidget.resolution !=1:
                self.parent.sagittalWidget.threadLoadNewResolution()

        if self.currentPlaneSection == 2:
            if self.parent.axialWidget.resolution !=1:
                self.parent.axialWidget.threadLoadNewResolution()
            if self.parent.coronalWidget.resolution !=1:
                self.parent.coronalWidget.threadLoadNewResolution()



    def _stopAllThreads(self):

        if hasattr(self,'loadingThreadsList'):
            for th in self.loadingThreadsList:
                th.quit()

        if self.currentPlaneSection == 0:
            if hasattr(self.parent.coronalWidget,'loadingThreadsList'):
                for th in self.parent.coronalWidget.loadingThreadsList:
                    th.quit()
            if hasattr(self.parent.sagittalWidget,'loadingThreadsList'):
                for th in self.parent.sagittalWidget.loadingThreadsList:
                    th.quit()
        elif self.currentPlaneSection == 1 :
            if hasattr(self.parent.axialWidget,'loadingThreadsList'):
                for th in self.parent.axialWidget.loadingThreadsList:
                    th.quit()
            if hasattr(self.parent.sagittalWidget,'loadingThreadsList'):
                for th in self.parent.sagittalWidget.loadingThreadsList:
                    th.quit()

        elif self.currentPlaneSection == 2 :
            if hasattr(self.parent.axialWidget,'loadingThreadsList'):
                for th in self.parent.axialWidget.loadingThreadsList:
                    th.quit()
            if hasattr(self.parent.coronalWidget,'loadingThreadsList'):
                for th in self.parent.coronalWidget.loadingThreadsList:
                    th.quit()

    def _changeSlice(self):
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

        i=1
        test = 10
        self.staticRes = [1]

        while(test >= 1):
            i *= 4
            test = dataShape[self.currentPlaneSection]//i
            self.staticRes.append(i)

        self.staticRes = self.staticRes[:-2]
        self.currentRes = np.copy(self.staticRes)
        self.fastResolution = self.staticRes[-1]
        self.resolution = self.staticRes[-1]

        self.loadingThreadsList = []
        self.loadingWorkdersList = []

        for i,res in enumerate(self.staticRes):
            worker = H5Reader(self.dataVolume,self.currentPlaneSection,0,res,i,self.staticRes,self.currentRes)
            thread = qt.QThread()
            worker.moveToThread(thread)
            thread.started.connect(worker.run)
            worker.data_read.connect(thread.quit)
            worker.data_read.connect(self.displayNewResolution)
            self.loadingThreadsList.append(thread)
            self.loadingWorkdersList.append(worker)


    def displayNewResolution(self):
        self.displayImage(True,self.sender().index)

    def threadLoadNewResolution(self):


        if not (self.fastResolution == 1) :
            for i,res  in enumerate(self.currentRes):

                thread = self.loadingThreadsList[i]
                worker = self.loadingWorkdersList[i]

                worker.position = self.sliceSlider.value()
                worker.resolution = res
                worker.resoCurrent = self.currentRes
                worker.resoStatic = self.staticRes
                if self.currentPlaneSection == 0:
                    worker.pos_p1 = self.parent.coronalWidget.sliceSlider.value()
                    worker.pos_p2 = self.parent.sagittalWidget.sliceSlider.value()
                elif self.currentPlaneSection == 1:
                    worker.pos_p1 = self.parent.axialWidget.sliceSlider.value()
                    worker.pos_p2 = self.parent.sagittalWidget.sliceSlider.value()
                elif self.currentPlaneSection == 2:
                    worker.pos_p1 = self.parent.axialWidget.sliceSlider.value()
                    worker.pos_p2 = self.parent.coronalWidget.sliceSlider.value()

                thread.start()



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
        self.axialWidget.threadLoadNewResolution()
        self.coronalWidget.threadLoadNewResolution()
        self.sagittalWidget.threadLoadNewResolution()
