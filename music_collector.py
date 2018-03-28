import chart_crawler as cc
import youtube_explorer as ye
from playlist import PlayListCreater

_TEST_MODE_ON_WINDOWS_ = True

if _TEST_MODE_ON_WINDOWS_:
  IMAGE_DIR = 'cover_img'
  MUSIC_FILE_DIR = 'music_files'
  MAX_RANK = 20
else:
  IMAGE_DIR = 'temp/melon_cover_img'
  MUSIC_FILE_DIR = '/volume1/music/melon_chart'
  MAX_RANK = 50

def main():
  print('Collecting the chart information from Melon...')
  chart_name, chart = cc.getMelonChart(MAX_RANK)
  #  print(chart)
  try:
    playList = PlayListCreater(MUSIC_FILE_DIR, chart_name)
  except FileExistsError as e:
    print('Chart file(\'{}.m3u\') already exsits.'.format(chart_name))
  else:
    print('\nMaking the MP3 files...')
    for song in chart:
      print(song)
      audio_file_path = ye.getSongFromYouTube(
        song['artist'], song['title'], song['songID'], song['lyric'], song['albumID'], MUSIC_FILE_DIR, IMAGE_DIR)
      playList.storePlayList(audio_file_path)
    del playList
    print('\nMusic Collecting and Creating chart are done.')

if __name__ == '__main__':
  main()