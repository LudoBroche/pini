import os

import h5py
from pathlib import Path
import xmltodict
from datetime import datetime
import glob
import importQt as qt

class StartUpArchive(qt.QMainWindow):

    def __init__(self, parent=None ):
        super(StartUpArchive, self).__init__(parent)
        self.path_xml = Path('./config.xml')
        self._check4Archive()

    def _check4Archive(self):
        test







class ArchiveHdf5:
    def __init__(self):
        self.path_xml = Path('./config.xml')
        self.pathArchive = ''
        self.archH5 = None
        self._loadConfigFile()

    def _loadConfigFile(self):
        with open(self.path_xml) as fd:
            doc = xmltodict.parse(fd.read())
        self.parameter = doc
        self.pathFolderArchive = Path(self.parameter['pini_parameters']['home_collection']['path'])

    def createNewArchive(self):
        current_date = datetime.now()
        current_date = str(current_date).split('.')[0]
        current_date = '_'.join(current_date.split(' '))
        current_date = ''.join(current_date.split(':'))
        nameArchive = 'pini_'+current_date+'.h5'
        self.pathArchive = Path(self.pathFolderArchive,nameArchive)
        self.archH5 = h5py.File(self.pathArchive,'a')


        self.archH5.close()

    def openArchive(self,archivePath):
        self.pathArchive = Path(archivePath)
        self.archH5 = h5py.File(self.pathArchive,'a')

    def _closeArchive(self):
        self.archH5.close()

    def cleanUpAllArchive(self):
        if self.archH5 != None:
            self._closeArchive()

        list_h5 = glob.glob(str(self.pathFolderArchive)+'/*.h5')
        for h5files in list_h5:
            os.remove(h5files)

    def createEmptyImage(self):
        index_list = [int(k) for k in list(self.archH5.keys())]
        if len(index_list) == 0 :
            index = '0'.zfill(5)
        else:
            index = max(index_list)+1
            index = str(index).zfill(5)

        dt = h5py.special_dtype(vlen=str)
        self.archH5.create_group(index)
        self.archH5[index].attrs["name"] = h5py.Empty(dt)
        self.archH5[index].attrs["path_source"] = h5py.Empty(dt)
        self.archH5[index].create_dataset("pixel_size",(3,),dtype="f")
        self.archH5[index].create_dataset("data", dtype="f")
        self.archH5[index].create_dataset("roi",dtype="uint")
        self.archH5[index].create_group("pipeline")

        print(self.archH5.keys())
        self._closeArchive()

    def populateImage(self,dicPar):
        print(dicPar)

    def _StartUpArchive(self):



if __name__ == "__main__":

    archive = ArchiveHdf5()
    archive.openArchive('./pini_2023-12-14_113830.h5')
    archive.createNewImage()



        