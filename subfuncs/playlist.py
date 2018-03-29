#-*- coding:utf-8 -*-

import os

class PlayListCreater():
  def __init__(self, basePath, listFileName, isOverwriteMode=False):
    wholeFilename = listFileName + '.m3u'
    filepath = os.path.join(basePath, wholeFilename)
    if not os.path.exists(basePath):
      os.mkdir(basePath)
    if os.path.exists(filepath):
      if isOverwriteMode:
        os.remove(filepath)
      else:
        self._listFile_ = None
        raise FileExistsError
    self._listFile_ = open(filepath, mode='w')
    self._writeList_('#EXTM3U')

  def __del__(self):
    if not self._listFile_ == None:
      self._listFile_.close()

  def _writeList_(self, str):
    self._listFile_.write(str + '\r\n')
    self._listFile_.flush()

  def storePlayList(self, baseDir, musicFilePath):
    self._writeList_(os.path.join(baseDir, musicFilePath))