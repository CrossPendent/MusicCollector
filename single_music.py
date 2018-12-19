import argparse
import sys

from subfuncs import music_explorer as me

FLAGS = None

_TEST_MODE_ON_WINDOWS_ = (sys.platform != 'linux')

if _TEST_MODE_ON_WINDOWS_:
  IMAGE_DIR = 'cover_img'
  MUSIC_FILE_DIR = 'music_files'
else:
  IMAGE_DIR = 'temp/melon_cover_img'
  MUSIC_FILE_DIR = '/volume1/music/melon_chart'

def main():
  f = open("youtube_api_key.txt", "r")
  youtube_api_key = f.readline()
  print(youtube_api_key)
  f.close()

  if FLAGS.singer == None:
    artist = input('please input singer name: ')
  else:
    artist = FLAGS.singer
  if FLAGS.title == None:
    title = input('please input title of music: ')
  else:
    title = FLAGS.title

  songID = me.getSearchList(artist, title)

  if songID != None:
    me.downloadSingleMusic(songID, MUSIC_FILE_DIR, IMAGE_DIR, youtube_api_key)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-s', '--singer', type=str,
                      help='The singer you want to find')
  parser.add_argument('-t', '--title', type=str,
                      help='The title your want to find')
  FLAGS = parser.parse_args()
  print('excution parameters: ', FLAGS)
  main()