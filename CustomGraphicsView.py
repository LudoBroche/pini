import importQt as qt


class CustomGraphicsView(qt.QGraphicsView):

    CustomGraphicsViewEvent = qt.pyqtSignal(dict)

    def __init__(self, scene, parent):
        
        '''
        Constructor
        '''
        self.scene = scene
        qt.QGraphicsView.__init__(self, scene, parent)
        self.setMouseTracking(True)
        self.setBackgroundBrush(qt.Qt.black);
        self.setAcceptDrops(True)
        #self.setRenderHints(qt.QPainter.Antialiasing | qt.QPainter.SmoothPixmapTransform);
        self.zoomScale = 1
        self.FlagWheellEvent = True

    def mousePressEvent(self, event):

        ddict = {}

        if (event.button() == qt.Qt.LeftButton):
            dx = event.pos().x()
            dy = event.pos().y()
            clickPosition = self.mapToScene(dx, dy)
 

            ddict['event'] = "MousePressed"
            ddict['x'] = clickPosition.x()
            ddict['y'] = clickPosition.y()

        if (event.button() == qt.Qt.RightButton):
            dx = event.pos().x()
            dy = event.pos().y()

            clickPosition = self.mapToScene(dx, dy)
            ddict['event'] = "RMousePressed"
            ddict['x'] = clickPosition.x()
            ddict['y'] = clickPosition.y()


        self.CustomGraphicsViewEvent.emit(ddict)
        #self.emit(qt.SIGNAL("CustomGraphicsViewEvent"), ddict)

        return qt.QGraphicsView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if (event.button() == qt.Qt.NoButton):
            dx = event.pos().x()
            dy = event.pos().y()

            clickPosition = self.mapToScene(dx, dy)
            ddict = {}
            ddict['event'] = "MouseMoved"
            ddict['x'] = clickPosition.x()
            ddict['y'] = clickPosition.y()

            #self.emit(qt.SIGNAL("CustomGraphicsViewEvent"), ddict)
            self.CustomGraphicsViewEvent.emit(ddict)

        return qt.QGraphicsView.mouseMoveEvent(self, event) # <-- added this line.


    def mouseReleaseEvent(self, event):

        if (event.button() == qt.Qt.LeftButton):
            dx = event.pos().x()
            dy = event.pos().y()

            clickPosition = self.mapToScene(dx, dy)
            ddict = {}
            ddict['event'] = "MouseReleased"
            ddict['x'] = clickPosition.x()
            ddict['y'] = clickPosition.y()
            self.CustomGraphicsViewEvent.emit(ddict)
            #self.emit(qt.SIGNAL("CustomGraphicsViewEvent"), ddict)

        return qt.QGraphicsView.mouseReleaseEvent(self, event)

    def wheelEvent(self, event):

        factor =float(event.angleDelta().y()) / 100.0

        if factor < 0:
            factor = -factor
            factor = 1.0/factor

        self.zoomScale *= factor
        self.setTransformationAnchor(qt.QGraphicsView.AnchorUnderMouse)
        self.scale(factor, factor)

    def autofit(self):
        self.zoomScale = 1
        self.fitInView(self.scene.sceneRect(), qt.Qt.KeepAspectRatio)
