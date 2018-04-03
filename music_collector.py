#-*- coding:utf-8 -*-

from subfuncs import youtube_explorer as ye, chart_crawler as cc
from subfuncs.playlist import PlayListCreater
import argparse
import sys

from utils import debug, music_reporter

FLAGS = None

_TEST_MODE_ON_WINDOWS_ = (sys.platform != 'linux')

if _TEST_MODE_ON_WINDOWS_:
  IMAGE_DIR = 'cover_img'
  MUSIC_FILE_DIR = 'music_files'
  PLAYLISTS_DIR = MUSIC_FILE_DIR
  MAX_RANK = 10
else:
  IMAGE_DIR = 'temp/melon_cover_img'
  MUSIC_FILE_DIR = '/volume1/music/melon_chart'
  PLAYLISTS_DIR = '/volume1/music/playlists'
  MAX_RANK = 50

def main():
  debug.log('Collecting the chart information from Melon...')
  chart_name, chart = cc.getMelonChart(maxRank=FLAGS.rank, period_type=FLAGS.period, str_target_date=FLAGS.date)
  #  debug.log(chart)
  try:
    playList = PlayListCreater(PLAYLISTS_DIR, chart_name, FLAGS.refresh_list)
  except FileExistsError as e:
    debug.log('Chart file(\'{}.m3u\') already exsits.'.format(chart_name))
  else:
    debug.log('\nMaking the MP3 files...')
    mr = music_reporter.MusicReporter('logs', 'report.log')
    for song in chart:
      debug.log(
        'rank:{:02}, artist:{}, title:{}, songID:{}, albumID:{}'.format(
          song['rank'], song['artist'], song['title'], song['songID'], song['albumID']))
      audio_file_path = ye.getSongFromYouTube(
        song['artist'], song['title'], song['songID'], song['lyric'], song['albumID'], MUSIC_FILE_DIR, IMAGE_DIR,
        FLAGS.overwrite_songs, music_reporter=mr)
      playList.storePlayList(MUSIC_FILE_DIR, audio_file_path)
    del playList
    del mr
    debug.log('\nMusic Collecting and Creating chart are done.')

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-p', '--period', type=str, choices=['weekly', 'monthly'], default='weekly',
                      help='chart period (default={})'.format('weekly'))
  parser.add_argument('-d', '--date', type=str, default='',
                      help='directs the target date which you want to get chart. (YYYYMMDD)')
  parser.add_argument('-r', '--rank', type=int, default=MAX_RANK,
                      help='maximum rank as you want to get from chart (1<=RANK<=50) (default={})'.format(MAX_RANK))
  parser.add_argument('-l', '--refresh-list', action='store_true',
                      help='overwrites the playlist when the same list is found.')
  parser.add_argument('-o', '--overwrite-songs', action='store_true',
                      help='overwrites the audio file when the same file is found.')
  FLAGS = parser.parse_args()
  print('excution parameters: ', FLAGS)
  main()