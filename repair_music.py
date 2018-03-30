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
  return audio_file.tags

def setID3Tag(mp3_path, id3Tag):
  audio_file = MP3(mp3_path, ID3=ID3)
  audio_file.tags = id3Tag
  audio_file.save()

def getAudioNameFromID3(id3_tag):
  return '{}-{}'.format(id3_tag['TPE1'].text[0], id3_tag['TIT2'].text[0])

def repair_music():
  filename = FLAGS.path.split(os.sep)[-1]
  target_dir = FLAGS.path.replace(os.sep+filename, '')

  # check whether the target file exists and the file condision is satisfied.
  if not os.path.exists(FLAGS.path):
    debug.log('There is no target file.')
    return
  if not (os.path.isfile(FLAGS.path) or FLAGS.path.split('.')[-1] == 'mp3'):
    debug.log('It is not MP3 file.')
    return

  # get ID3 tag and query
  id3_tag = getID3Tag(FLAGS.path)
  if id3_tag == None:
    debug.log('There is no ID3 Tag in the target mp3 file. Please check the file information')
    return
  audio_name = getAudioNameFromID3(id3_tag)

  # search for youtube
  query =  '{} audio'.format(audio_name)
  debug.log('Looking for youtube by the query \'{}\''.format(query))
  list = ye.find_youtube_detailed(query)

  count = 1
  for link in list:
    debug.log("[{}] title:'{}', length:{}, link:< {} >".format(count, link['title'], link['length'], link['url']))
    count += 1

  selected_num = -1

  while selected_num < 0 or selected_num > count:
    try:
      selected_num = int(input("Please choose the link number(1<=NUM<={}) of music to repair (input '0' if you want to exit): ".format(count)))
    except ValueError:
      selected_num = -1
      continue

    if selected_num == 0:
      return
    if selected_num < 0 or selected_num > count:
      debug.log('Input number is out of range (0<=NUM<={}). Try to input again.'.count())

  debug.log("\n[{}]({}<{}>) is selected.".format(selected_num, list[selected_num-1]['title'], list[selected_num-1]['url']))
  old_filename = "{}_old.mp3".format(audio_name)
  old_file_path = os.path.join(target_dir, old_filename)
  if os.path.exists(old_file_path):
    os.remove(old_file_path)
    debug.log('Previous old mp3 file is removed.')
  os.rename(FLAGS.path, old_file_path)
  debug.log("The name of previous file is changed to '{}'".format(old_filename))

  output_filename = ye.download_audio_from_youtube(list[selected_num-1]['url'], output_dir=target_dir, strQuery=audio_name)
  debug.log('\'' + output_filename + '\' was downloaded.')
  debug.log('\'' + output_filename + '\' is converting...')
  ye.convertMP3(target_dir, output_filename, audio_name+'.mp3')
  debug.log('\'' + FLAGS.path + '\' was converted.')
  setID3Tag(FLAGS.path, id3_tag)
  debug.log('Song Information was recorded on \'' + FLAGS.path + '\'')


def main():
  repair_music()

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('path', type=str, help="the file's path you want to re-download and replace")
  FLAGS = parser.parse_args()
  print(FLAGS)
  main()