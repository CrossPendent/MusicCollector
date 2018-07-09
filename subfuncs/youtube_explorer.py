# -*- coding: utf-8 -*-

#import music_collector as mc
import os
import subprocess
from bs4 import BeautifulSoup
import urllib.parse
from pytube import YouTube
from utils import http, debug, music_reporter
from subfuncs import chart_crawler as cc

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

def find_youtube_detailed(query):
  base_url = 'https://www.youtube.co.kr'
  req_url = base_url + '/results?search_query=' + urllib.parse.quote(query)
  response = http.getHTMLDocument(req_url)
  # debug.log(response)

  soup = BeautifulSoup(response, "html.parser")
  # debug.log(soup)
  watch_list = []
  for link in soup.find_all('h3', {'class':'yt-lockup-title'}):
    # debug.log(link)
    span_contents = link.find('span').contents
    if len(span_contents) > 0:
      length_info = span_contents[0]
      length_keyword = ' - Duration: '
      if length_info.find(length_keyword) >= 0:
        record = {'title':link.find('a').contents[0],
                  'length':length_info.replace(length_keyword, ''),
                  'url':base_url + link.find('a').attrs['href']}
        watch_list.append(record)
  return watch_list

def find_youtube(query):
  base_url = 'https://www.youtube.co.kr'
  req_url = base_url + '/results?search_query=' + urllib.parse.quote(query)
  debug.log(req_url)
  response = http.getHTMLDocument(req_url)
  # debug.log(response)

  soup = BeautifulSoup(response, "html.parser")
  # debug.log(soup)
  watch_urls = []
  for link in soup.find_all('h3', {'class':'yt-lockup-title'}):
    watch_urls.append(base_url + link.find('a').attrs['href'])
  # if len(watch_urls) < 1:
  #   debug.log(soup)

  return watch_urls

def download_audio_from_youtube(url, output_dir, strQuery, music_reporter):
  debug.log('\'{}\' is downloading from \'{}\'...'.format(strQuery, url))
  if music_reporter != None:
    music_reporter.updateMusic(strQuery, url)
  yt = YouTube(url)
  filename = convertQueryToFilename(strQuery)
  audio_list = yt.streams.filter(only_audio=True).all()
  if audio_list == []:
    audio_list = yt.streams.filter().all()
  for stream in audio_list:
    # print(stream)
    if stream.mime_type.find('mp4') >= 0:
      stream.download(output_dir, filename)
      break;
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

def convertMP3(baseDIR, old_filename, new_filename):
  mp3_path = os.path.join(baseDIR, new_filename)
  old_path = os.path.join(baseDIR, old_filename)
  if not os.path.exists(mp3_path):
    ret = subprocess.call(['ffmpeg', '-i', old_path, mp3_path])
    if ret == 0:
      os.remove(old_path)

def getSongFromYouTube(artist, title, songID, lyric, albumID, baseMusicDir, baseImageDir,
                       isOverwriteMode=False, music_reporter=None):
  audio_name = '{}-{}'.format(artist, title)
  query = '{} audio'.format(audio_name)
  # check whether mp3 file already exists.
  if not os.path.exists(baseMusicDir):
    os.mkdir(baseMusicDir)
  filename = convertQueryToFilename(audio_name)
  mp3_parent = os.path.join(baseMusicDir, convertQueryToFilename(artist))
  if not os.path.exists(mp3_parent):
    os.mkdir(mp3_parent)
  mp3_dir = os.path.join(convertQueryToFilename(artist), albumID)
  if not os.path.exists(os.path.join(baseMusicDir, mp3_dir)):
    os.mkdir(os.path.join(baseMusicDir, mp3_dir))
  mp3_filename = filename + '.mp3'
  mp3_path = os.path.join(mp3_dir, mp3_filename)

  isSkip = False
  if os.path.exists(os.path.join(baseMusicDir, mp3_path)):
    if isOverwriteMode:
      debug.log('{} is already exist. it will be overwritten.'.format(mp3_path))
      os.remove(os.path.join(baseMusicDir, mp3_path))
    else:
      debug.log('{} is already exist. Downloading will be skipped.'.format(mp3_path))
      isSkip = True
  if not isSkip:
    debug.log('Looking for youtube by the query \'{}\'...'.format(query))
    list = find_youtube(query)
    retry = 0
    while len(list) <= 1 and retry < 5:
      debug.log('Youtube list couldn\'t be gotten. retry...')
      list = find_youtube(query)
      retry += 1
    debug.log('trying to download \'' + query + '\'...')

    file_name = download_audio_from_youtube(list[0], baseMusicDir, audio_name, music_reporter)
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
  print(find_youtube('볼빨간사춘기-여행 audio'))
  # print(download_audio_from_youtube('https://www.youtube.co.kr/watch?v=a7Kl_A6Hce8', './', '볼빨간사춘기-여행', None))
  lyric = u'''
  abc
  deb
  ddd
  '''
#  getSongFromYouTube('BIGBANG', '꽃 길', '30948698', lyric)
