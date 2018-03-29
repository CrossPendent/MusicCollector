#-*- coding:utf-8 -*-

import os
import argparse

from subfuncs import youtube_explorer as ye
from utils import debug

from mutagen.mp3 import MP3
from mutagen.id3 import ID3

FLAGS = None

def getID3Tag(mp3_path):
  audio_file = MP3(mp3_path, ID3=ID3)
  encoding=3   # 3 is for utf-8
  return audio_file.tags

def getAudioNameFromID3(id3_tag):
  return '{}-{}'.format(id3_tag['TPE1'].text[0], id3_tag['TIT2'].text[0])

def redown_music():
  # check whether the target file exists and the file condision is satisfied.
  if not os.path.exists(FLAGS.path):
    print('There is no target file.')
    return
  if not (os.path.isfile(FLAGS.path) or FLAGS.path.split('.')[-1] == 'mp3'):
    print('It is not MP3 file.')
    return

  # get ID3 tag and query
  id3_tag = getID3Tag(FLAGS.path)
  audio_name = getAudioNameFromID3(id3_tag)

  # search for youtube
  query =  '{} audio'.format(audio_name)
  debug.log('Looking for youtube by the query \'{}\''.format(query))
  list = ye.find_youtube_detailed(query)

  debug.log('\'' + query + '\' is downloading.')



def main():
  redown_music()

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('path', type=str, help="the file's path you want to re-download and replace")
  FLAGS = parser.parse_args()
  print(FLAGS)
  main()