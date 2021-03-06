import unittest
from subfuncs import chart_crawler as cc
from bs4 import BeautifulSoup
import test.test_variables as testvar

class ChartCrawlerTest(unittest.TestCase):
  '''
  def testGetAlbumInfoFromMelon(self):
    albumInfo = cc.getAlbumInfoFromMelon('10147314')
    self.assertIsNotNone(albumInfo)
    print(albumInfo)
    albumInfo = cc.getAlbumInfoFromMelon('10145303')
    self.assertIsNotNone(albumInfo)
    print(albumInfo)
  '''
  def testGetSongInfoOfMelon(self):
    soup = BeautifulSoup(testvar.html_rank_page, 'html.parser')
    table = soup.find(style='width:100%')
    count = 0
    for music in table.find_all('tr'):
      songInfo = cc.getSongInfoOfMelon(music)
      if count == 0:
        self.assertIsNone(songInfo)
      else:
        self.assertIsNotNone(songInfo)
#      print(songInfo)
      count += 1

  def testGetSongInfobySongIDOfMelon(self):
    print(cc.getSongInfobySongIDOfMelon('30230986'))
    print(cc.getSongInfobySongIDOfMelon('30403595'))

  def testGetMelonChart(self):
    # listChart = cc.getMelonChart(maxRank=10, period_type='weekly', str_target_date='20170201')
    listChart = cc.getMelonChart(maxRank=10, period_type='monthly')
    for song in listChart:
      print(song)

if __name__ == '__main__':
  unittest.main()
