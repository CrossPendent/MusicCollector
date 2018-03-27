# -*- coding: utf-8 -*-

import music_collector as mc
import os
import subprocess
from bs4 import BeautifulSoup
import requests
import urllib.parse
from pytube import YouTube

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, USLT, TOPE, TIT1, TIT2, TPE1, TIPL, TPRO, TCON, TPUB, TDOR, TDRL, TALB

def convertQueryToFilename(strQuery):
  listTargetKeys = ['\"', '#', '$', '%', '\'', '*', ',', '.', '/', ':', '"',
                    ';', '<', '>', '?', '\\', '^', '|', '~', '\\\\',]
  '''
  listTargetKeys = ['~', '`', '!', '@', '#', '$', '%', '^', '&', '*', '+', '=', '|',
                    '\\', '"', '\'', ':', ';', '?', '/', '<', '>', ',', '.']
  '''
  strFileName = strQuery
  for letter in listTargetKeys:
    strFileName = strFileName.replace(letter, '')
  return strFileName

def find_youtube(query):
  base_url = 'https://www.youtube.co.kr'
  req_url = base_url + '/results?search_query=' + urllib.parse.quote(query)
  response = requests.get(req_url)
  #print(response)

  soup = BeautifulSoup(response.text, "html.parser")
  #print(soup)
  watch_urls = []
  for link in soup.find_all('h3', {'class':'yt-lockup-title'}):
    watch_urls.append(base_url + link.find('a').attrs['href'])
  return watch_urls

def download_audio_from_youtube(url, output_dir, strQuery):
  filename = convertQueryToFilename(strQuery)
  yt = YouTube(url)
  audio_list = yt.streams.filter(only_audio=True).all()
  if not os.path.exists(output_dir):
    os.mkdir(output_dir)
  if not os.path.exists(os.path.join(output_dir, filename+'.mp3')):
    audio_list[0].download(output_dir, filename)
  return os.path.join(output_dir, filename + '.mp4')

def setID3(file_path, artist, title, lyric, albumInfo, cover_img_path):
  audio_file = MP3(file_path, ID3=ID3)
  encoding=3   # 3 is for utf-8
  # add CoverPicture
  audio_file.tags.add(
    APIC(
      encoding=encoding,
      mime='image/jpg', # image/jpeg or image/png
      type=3, # 3 is for the cover image
      desc=u'Cover',
      data=open(cover_img_path, 'rb').read()
    )
  )
  audio_file.tags.add(
    USLT(
      encoding=encoding,
      desc=u'Lyric',
      text=lyric
    )
  )
  audio_file.tags.add(
    TOPE(
      encoding=encoding,
      text=artist
    )
  )
  audio_file.tags.add(
    TPE1(
      encoding=encoding,
      text=artist
    )
  )
  audio_file.tags.add(
    TIT1(
      encoding=encoding,
      text=title
    )
  )
  audio_file.tags.add(
    TIT2(
      encoding=encoding,
      text=title
    )
  )
  audio_file.tags.add(
    TIPL(
      encoding=encoding,
      text=[artist]
    )
  )
  if not albumInfo == None:
    audio_file.tags.add(
      TALB(
        encoding=encoding,
        text=[albumInfo['album_name']]
      )
    )
    audio_file.tags.add(
      TPRO(
        encoding=encoding,
        text=[albumInfo['copyright']]
      )
    )
    audio_file.tags.add(
      TCON(
        encoding=encoding,
        text=[albumInfo['genre']]
      )
    )
    audio_file.tags.add(
      TPUB(
        encoding=encoding,
        text=[albumInfo['publisher']]
      )
    )
    audio_file.tags.add(
      TDOR(
        encoding=encoding,
        text=[albumInfo['pub_date']]
      )
    )
    audio_file.tags.add(
      TDRL(
        encoding=encoding,
        text=[albumInfo['pub_date']]
      )
    )
  audio_file.save()

def convertMP3(old_file_path):
  mp3_path = old_file_path.replace('.mp4', '.mp3')
  if not os.path.exists(mp3_path):
    subprocess.call(['ffmpeg', '-i', old_file_path, mp3_path])
    os.remove(old_file_path)
  return mp3_path

def getSongFromYouTube(artist, title, songID, lyric, albumInfo):
  query = '{}-{}'.format(artist, title)
  list = find_youtube(query)
  print('\'' + query + '\' is downloading.')
  file_path = download_audio_from_youtube(list[0], mc.MUSIC_FILE_DIR, query)
  print('\'' + file_path + '\' was downloaded.')
  print('\'' + file_path + '\' is converting...')
  new_file_path = convertMP3(file_path)
  print('\'' + new_file_path + '\' was converted.')
  setID3(new_file_path, artist, title, lyric, albumInfo, os.path.join(mc.IMAGE_DIR, songID+'.jpg'))
  print('Song Information was recorded on \'' + new_file_path + '\'')

if __name__ == '__main__':
  lyric = u'''
  abc
  deb
  ddd
  '''
  getSongFromYouTube('BIGBANG', '꽃 길', '30948698', lyric)
