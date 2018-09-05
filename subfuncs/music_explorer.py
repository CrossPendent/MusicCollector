import urllib
import os
from bs4 import BeautifulSoup

from utils import http, music_reporter, debug
from subfuncs import chart_crawler as cc
from subfuncs import youtube_explorer as ye

def getSongInfoFromMelonOfSearch(music_record):
  soupArtist = music_record.find('div', {'id':'artistName'})
  soupTitle = music_record.find('a', {'class':'fc_gray'})
  soupSongInfo = music_record.find('a', {'class':'btn btn_icon_detail'})
  soupAlbumInfo = music_record.find('div', {'style':'max-width:90%'})

  # print('=========')
  # print('soupArtist')
  artist = ''
  print(soupArtist)
  artistCount = 0
  for art in soupArtist.find('span', {'class':'checkEllipsisSongsongList'}).find_all('a'):
    if artistCount > 0:
      artist += ','
    artist += art.contents[0]
    artistCount += 1
  if artistCount == 0:
    artist = 'Various Artists'
  # print(artist)
  # print('soupTitle')
  # print(soupTitle)
  title = soupTitle.contents[0]
  # print(title)
  # print('soupSongInfo')
  # print(soupSongInfo)
  songID = soupSongInfo['href'].split('goSongDetail(\'')[-1].replace('\');', '')
  # print(songID)

  albumInfo = soupAlbumInfo.find('a').contents[0]

  return artist, title, songID, albumInfo

def getSearchList(artist, title):
  query = 'q={}+-+{}'.format(urllib.parse.quote(artist), urllib.parse.quote(title))
  url = 'http://www.melon.com/search/total/index.htm?{}'.format(query)
  debug.log("send the request to melon: [{}]".format(url))
  content = http.getHTMLDocument(url)
  soup = BeautifulSoup(content, "html.parser")

  if soup.find('div', {'class':'section_no_data'}) == None:
    song_table = soup.find_all('div', {'class':'tb_list d_song_list songTypeOne'})[-1]
    song_list = song_table.find_all('tr')
    music_list = []
    for song_record in song_list:
      soupTitle = song_record.find('a', {'class':'fc_gray'})
      if soupTitle != None:
        artist, title, songID, albumInfo = getSongInfoFromMelonOfSearch(song_record)
        music_list.append({'artist':artist, 'title':title, 'songID':songID, 'albumInfo':albumInfo})
        # print('{}. artist: {} | title: {} | album: {}'.format(count, artist, title, albumInfo))

    count = 0
    for item in music_list:
      count += 1
      print('[{}] artist: {} | title: {} | album: {}'.format(count, item['artist'], item['title'], item['albumInfo']))
    selected_num = -1
    while selected_num < 0 or selected_num > count:
      try:
        selected_num = int(input(
          "Please choose the number(1<=NUM<={}) of music to download (input '0' if you want to exit): ".format(
            count)))
      except ValueError:
        selected_num = -1
        continue

      if selected_num == 0:
        return
      if selected_num < 0 or selected_num > count:
        print('Input number is out of range (0<=NUM<={}). Try to input again.'.format(count))

      print("\n[{}]({}-{}<{}>) is selected.".format(selected_num,
                                                    music_list[selected_num - 1]['artist'],
                                                    music_list[selected_num - 1]['title'],
                                                    music_list[selected_num - 1]['albumInfo']))

      return music_list[selected_num - 1]['songID']
  else:
    print('There is no data ({}-{} couldn\'t be found in Melon.)'.format(artist, title))
    return None

def downloadSingleMusic(songID, baseMusicDir, baseImageDir):
  lyric, artist, title, albumID, imgURL = cc.getSongInfobySongIDOfMelon(songID)
  coverImgFile = cc.downloadImageFromMelon(imgURL, songID)

  mr = music_reporter.MusicReporter('logs', 'report.log')

  audio_file_path = ye.getSongFromYouTube(
    artist, title, songID, lyric, albumID, baseMusicDir, baseImageDir, isOverwriteMode=False, music_reporter=mr)
  del mr

if __name__ == '__main__':
  # getSearchList('붹', '퀙')   # no data test
  # getSearchList('싸이', '아버지')
  getSearchList('싸이', '낙원')
  # getSearchList('김하온,이병재', '바코드')
