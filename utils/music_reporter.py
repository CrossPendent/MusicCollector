#-*- coding:utf-8 -*-

import os
import datetime as dt

class MusicReporter():
  def __init__(self, output_dir, filename):
    if not os.path.exists(output_dir):
      os.mkdir(output_dir)
    file_path = os.path.join(output_dir, filename)
    self._report_file_ = open(file_path, mode='a+', encoding='utf-8')

  def __del__(self):
    if not self._report_file_ == None:
      self._report_file_.close()

  def updateMusic(self, title, link):
    self._report_file_.write('[{}] {} {}\r\n'.format(dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), title, link))
    self._report_file_.flush()

def generateReportFromDebugLog(target_dir, srclog_filename, report_filename):
  source_path = os.path.join(target_dir, srclog_filename)
  src_file = open(source_path, mode='r', encoding='utf-8')
  mr = MusicReporter(target_dir, report_filename)

  for rdBuf in src_file:
    if rdBuf.find('www.youtube.co.kr/watch') >= 0:
      parsed = rdBuf.split('\'')
      title, link = parsed[1], parsed[3]
      mr.updateMusic(title, link)

  del mr
  src_file.close()

if __name__ == '__main__':
  # mr = MusicReporter('.', 'test.log')
  # mr.updateMusic('abd', 'http://adb.com')
  # mr.updateMusic('bra', 'http://adb.com')
  # del mr
  # mr = MusicReporter('.', 'test.log')
  # mr.updateMusic('abd', 'http://adb.com')
  # del mr
  generateReportFromDebugLog('..\logs', 'debuglog.log', 'report.log')