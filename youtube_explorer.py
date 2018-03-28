# -*- coding: utf-8 -*-

#import music_collector as mc
import os
import subprocess
from bs4 import BeautifulSoup
import requests
import urllib.parse
from pytube import YouTube
from netutils import http
import chart_crawler as cc

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
  response = http.getHTMLDocument(req_url)
  #print(response)

  soup = BeautifulSoup(response, "html.parser")
  #print(soup)
  watch_urls = []
  for link in soup.find_all('h3', {'class':'yt-lockup-title'}):
    watch_urls.append(base_url + link.find('a').attrs['href'])
  return watch_urls

def download_audio_from_youtube(url, output_dir, strQuery):
  print('\'{}\' will be downloaded from \'{}\''.format(strQuery, url))
  yt = YouTube(url)
  audio_list = yt.streams.filter(only_audio=True).all()
  filename = convertQueryToFilename(strQuery)
  audio_list[0].download(output_dir, filename)
  return (filename + '.mp4')

def setID3(baseDIR, filename, artist, title, lyric, albumID, cover_img_path):
  file_path = os.path.join(baseDIR, filename)
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
  albumInfo = cc.getAlbumInfoFromMelon(albumID)
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

def convertMP3(baseDIR, old_filename):
  mp3_name = old_filename.replace('.mp4', '.mp3')
  mp3_path = os.path.join(baseDIR, mp3_name)
  old_path = os.path.join(baseDIR,old_filename)
  if not os.path.exists(mp3_path):
    subprocess.call(['ffmpeg', '-i', old_path, mp3_path])
    os.remove(old_path)
  return mp3_name

def getSongFromYouTube(artist, title, songID, lyric, albumID, baseDIR):
  audio_name = '{}-{}'.format(artist, title)
  query = '{} audio'.format(audio_name)
  print('Looking for youtube by the query \'{}\''.format(query))
  list = find_youtube(query)
  print('\'' + query + '\' is downloading.')

  if not os.path.exists(baseDIR):
    os.mkdir(baseDIR)
  filename = convertQueryToFilename(audio_name)

  mp3_filename = filename+'.mp3'
  if os.path.exists(os.path.join(baseDIR, mp3_filename)):
    print('{} is already exist. Downloading will be skipped.'.format(filename+'.mp3'))
    new_filename = mp3_filename
  else:
    file_name = download_audio_from_youtube(list[0], baseDIR, audio_name)
    print('\'' + file_name + '\' was downloaded.')
    print('\'' + file_name + '\' is converting...')
    new_filename = convertMP3(baseDIR, file_name)
    print('\'' + new_filename + '\' was converted.')
    setID3(baseDIR, new_filename, artist, title, lyric, albumID, os.path.join(baseDIR, songID+'.jpg'))
    print('Song Information was recorded on \'' + new_filename + '\'')

  return new_filename

if __name__ == '__main__':
  lyric = u'''
  abc
  deb
  ddd
  '''
#  getSongFromYouTube('BIGBANG', '꽃 길', '30948698', lyric)
