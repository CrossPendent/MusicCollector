import unittest
import subfuncs.youtube_explorer as ye

class YoutubeExplorerTest(unittest.TestCase):
  def test_download_audio_from_youtube(self):
    ye.download_audio_from_youtube('https://www.youtube.co.kr/watch?v=7HshY4J1thE', '.', 'PRODUCE 101-나야 나 (PICK ME)', None)
    # ye.download_audio_from_youtube('https://www.youtube.co.kr/watch?v=d07Mykz57so', '.', '블락비 (Block B)-YESTERDAY', None)

  def testFind_youtube(self):
    pass

if __name__ is '__main__':
  unittest.main()