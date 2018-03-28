#-*- coding:utf-8 -*-

import chart_crawler as cc
import youtube_explorer as ye
from playlist import PlayListCreater

import debug

_TEST_MODE_ON_WINDOWS_ = False

if _TEST_MODE_ON_WINDOWS_:
  IMAGE_DIR = 'cover_img'
  MUSIC_FILE_DIR = 'music_files'
  PLAYLISTS_DIR = MUSIC_FILE_DIR
  MAX_RANK = 20
else:
  IMAGE_DIR = 'temp/melon_cover_img'
  MUSIC_FILE_DIR = '/volume1/music/melon_chart'
  PLAYLISTS_DIR = '/volume1/music/playlists'
  MAX_RANK = 50

def main():
  debug.log('Collecting the chart information from Melon...')
  chart_name, chart = cc.getMelonChart(MAX_RANK)
  #  debug.log(chart)
  try:
    playList = PlayListCreater(PLAYLISTS_DIR, chart_name)
  except FileExistsError as e:
    debug.log('Chart file(\'{}.m3u\') already exsits.'.format(chart_name))
  else:
    debug.log('\nMaking the MP3 files...')
    for song in chart:
      debug.log(song)
      audio_file_path = ye.getSongFromYouTube(
        song['artist'], song['title'], song['songID'], song['lyric'], song['albumID'], MUSIC_FILE_DIR, IMAGE_DIR)
      playList.storePlayList(MUSIC_FILE_DIR, audio_file_path)
    del playList
    debug.log('\nMusic Collecting and Creating chart are done.')

if __name__ == '__main__':
  main()