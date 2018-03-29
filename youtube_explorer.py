# -*- coding: utf-8 -*-

#import music_collector as mc
import os
import subprocess
from bs4 import BeautifulSoup
import urllib.parse
from pytube import YouTube
from netutils import http
import chart_crawler as cc

import debug

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, USLT, TOPE, TIT1, TIT2, TPE1, TIPL, TPRO, TCON, TPUB, TDOR, TDRL, TALB

def convertQueryToFilename(strQuery):
  listTargetKeys = ['\"', '#', '$', '%', '\'', '*', ',', '.', '/', ':', '"',
                    ';', '<', '>', '?', '\\', '^', '|', '~', '\\\\']
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
  #debug.log(response)

  soup = BeautifulSoup(response, "html.parser")
  #debug.log(soup)
  watch_urls = []
  for link in soup.find_all('h3', {'class':'yt-lockup-title'}):
    watch_urls.append(base_url + link.find('a').attrs['href'])
  return watch_urls

def download_audio_from_youtube(url, output_dir, strQuery):
  debug.log('\'{}\' will be downloaded from \'{}\''.format(strQuery, url))
  yt = YouTube(url)
  audio_list = yt.streams.filter(only_audio=True).all()
  if audio_list == []:
    audio_list = yt.streams.filter().all()
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

def convertMP3(baseDIR, old_filename, new_file_path):
  mp3_path = os.path.join(baseDIR, new_file_path)
  old_path = os.path.join(baseDIR,old_filename)
  if not os.path.exists(mp3_path):
    subprocess.call(['ffmpeg', '-i', old_path, mp3_path])
    os.remove(old_path)

def getSongFromYouTube(artist, title, songID, lyric, albumID, baseMusicDir, baseImageDir):
  audio_name = '{}-{}'.format(artist, title)
  query = '{} audio'.format(audio_name)
  debug.log('Looking for youtube by the query \'{}\''.format(query))
  list = find_youtube(query)
  debug.log('\'' + query + '\' is downloading.')

  if not os.path.exists(baseMusicDir):
    os.mkdir(baseMusicDir)
  filename = convertQueryToFilename(audio_name)
  mp3_parent = os.path.join(baseMusicDir, convertQueryToFilename(artist))
  if not os.path.exists(mp3_parent):
    os.mkdir(mp3_parent)
  mp3_dir = os.path.join(convertQueryToFilename(artist), albumID)
  if not os.path.exists(os.path.join(baseMusicDir, mp3_dir)):
    os.mkdir(os.path.join(baseMusicDir, mp3_dir))
  mp3_filename = filename+'.mp3'
  mp3_path = os.path.join(mp3_dir, mp3_filename)
  if os.path.exists(os.path.join(baseMusicDir, mp3_path)):
    debug.log('{} is already exist. Downloading will be skipped.'.format(mp3_path))
  else:
    file_name = download_audio_from_youtube(list[0], baseMusicDir, audio_name)
    debug.log('\'' + file_name + '\' was downloaded.')
    debug.log('\'' + file_name + '\' is converting...')
    convertMP3(baseMusicDir, file_name, mp3_path)
    debug.log('\'' + mp3_path + '\' was converted.')
    img_path = os.path.join(baseImageDir, songID + '.jpg')
    setID3(baseMusicDir, mp3_path, artist, title, lyric, albumID, img_path)
    os.remove(img_path)
    debug.log('Song Information was recorded on \'' + mp3_path + '\'')

  return mp3_path

if __name__ == '__main__':
  lyric = u'''
  abc
  deb
  ddd
  '''
#  getSongFromYouTube('BIGBANG', '꽃 길', '30948698', lyric)
