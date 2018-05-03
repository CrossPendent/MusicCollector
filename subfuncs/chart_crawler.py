#-*- coding:utf-8 -*-

import music_collector as mc
from utils import http, debug
from datetime import date, timedelta

import urllib.request
import os
from bs4 import BeautifulSoup

def downloadImageFromMelon(url, songID):
  image_dir = mc.IMAGE_DIR
  if not os.path.exists(image_dir):
    os.mkdir(image_dir)
  file_name = songID + '.jpg'
  urllib.request.urlretrieve(url, os.path.join(image_dir, file_name))
  return file_name

def getSongInfobySongIDOfMelon(melon_songID):
  base_url = 'http://www.melon.com/song/detail.htm?songId='
  url = base_url + melon_songID;

  content = http.getHTMLDocument(url)

  soup = BeautifulSoup(content, "html.parser")

  # parse lyric
  lyric_soup = soup.find('div', {'class':'lyric'})
  lyric = ''
  if lyric_soup != None:
    raw_lyric = lyric_soup.contents[1:]
    raw_lyric[0] = raw_lyric[0].replace('\r\n\t\t\t\t\t\t\t\t', '')
    for line in raw_lyric:
      if str(line) == '<br/>':
        lyric = lyric + '\r\n'
      else:
        lyric = lyric + str(line)

  # parse other information
  title = soup.find('div', {'class':'song_name'}).contents[-1].replace('\r\n', '').replace('\t', '')

  artist = ''
  artistCount = 0
  for art in soup.find('div', {'class': 'artist'}).find_all('a'):
    if artistCount > 0:
      artist += ','
    artist += art.find('span').contents[0]
    artistCount += 1

  albumID = soup.find('dl', {'class':'list'}).find('a')['href'].split('\'')[1]

  imageUrl = soup.find('a', {'class':'image_typeAll'}).find('img')['src'].split('?')[0]

  return lyric, artist, title, albumID, imageUrl

def getLyricFromMelon(melon_songID):
  lyric, _, _, _, _  = getSongInfobySongIDOfMelon(melon_songID)
  return lyric

def getAlbumInfoFromMelon(melon_albumID):
  if melon_albumID == None:
    return None
  base_url = 'http://www.melon.com/album/detail.htm?albumId='
  url = base_url + melon_albumID

  content = http.getHTMLDocument(url)

  soup = BeautifulSoup(content, "html.parser")
  soupAlbumName = soup.find('div', {'class':'song_name'})
  albumName = soupAlbumName.contents[-1].replace('\r\n\t\t\t\t\t\t\t\t\t', '').replace('\t', '')
  debug.log('Getting album information of \'{}\'(id:{})'.format(albumName, melon_albumID))

  info = soup.find('dl', {'class':'list'})
  if info == None:
    return None
  dd_list = info.find_all('dd')

  pub_date = dd_list[0].contents[0]
  genre = dd_list[1].contents[0]
  publisher = dd_list[2].contents[0]
  copyright = dd_list[3].contents[0]
  return {'album_name':albumName, 'pub_date':pub_date, 'genre':genre, 'publisher':publisher, 'copyright':copyright}

def getSongInfoOfMelon(music_record):
  soupArtist = music_record.find('div', {'class':'ellipsis rank02'})
  soupTitle = music_record.find('div', {'class':'ellipsis rank01'})
  soupSongInfo = music_record.find('a', {'class':'btn btn_icon_detail'})
  soupAlbumInfo = music_record.find('div', {'class':'ellipsis rank03'})

  # debug.log('=========')
  # debug.log('soupArtist')
  artist = ''
  # debug.log(soupArtist)
  artistCount = 0
  for art in soupArtist.find('span', {'class':'checkEllipsis'}).find_all('a'):
    if artistCount > 0:
      artist += ','
    artist += art.contents[0]
    artistCount += 1
  # debug.log(artist)
  # debug.log('soupTitle')
  # debug.log(soupTitle)
  if soupTitle.find('a') == None:
    title = soupTitle.find('span', {'class':'fc_lgray'}).contents[0]
  else:
    title = soupTitle.find('a').contents[0]
  # debug.log(title)
  # debug.log('soupSongInfo')
  # debug.log(soupSongInfo)
  songID = soupSongInfo['href'].replace('javascript:melon.link.goSongDetail(\'', '').replace('\');', '')
  # debug.log(songID)
  # debug.log('soupAlbumInfo')
  # debug.log(soupAlbumInfo)
  albumID = soupAlbumInfo.find('a')['href'].replace('javascript:melon.link.goAlbumDetail(\'', '').replace('\');', '')
  # debug.log(albumID)
  debug.log('parsed the music detail (artist: {}, title: {}, songID: {}, albumID: {})'.format(artist, title, songID, albumID))
  '''
  links = music_record.find_all('a')
  if len(links) < 4:
    return None
  artist = links[3].contents[0]
  title = links[2].contents[0]
  songID = links[1]['href'].replace('javascript:melon.link.goSongDetail(\'', '').replace('\');', '')
  albumID = links[5]['href'].replace('javascript:melon.link.goAlbumDetail(\'', '').replace('\');', '')
  if len(albumID) > 10:
    for link in links:
      debug.log(link)
  debug.log(albumID)
  '''
  image = music_record.find('img')
  coverImageURL = image['src'].split('.jpg')[0] + '.jpg'
  coverImgFile = downloadImageFromMelon(coverImageURL, songID)
  lyric = getLyricFromMelon(songID)

  return artist, title, songID, coverImgFile, lyric, albumID

def isWeekStartedFromSunday(target_date):
  result = False
  if date(2007, 7, 15) <= target_date < date(2012, 8, 13) or target_date < date(2004, 11, 22):
    result = True
  return result

def getMelonChart(maxRank = 50, period_type ='weekly', str_target_date=None):
  period_url = {'daily': 'day', 'weekly': 'week', 'monthly': 'month'}

  if maxRank < 1:
    maxRank = 1
  elif maxRank > 50:
    maxRank = 50
  if str_target_date == None or str_target_date == '':
    if period_type == 'weekly':
      str_target_date = (date.today() - timedelta(days=date.today().isoweekday())).strftime('%Y%m%d')
    else:
      str_target_date = (date.today() - timedelta(days=date.today().day)).strftime('%Y%m%d')

  debug.log(str_target_date)
  target_date = date(int(str_target_date[0:4]),
                     int(str_target_date[4:6]),
                     int(str_target_date[6:8]))

  if target_date < date(1990, 1, 7):
    target_date = date(1990, 1, 7)
  elif target_date > date.today():
    target_date = date.today()

  if period_type == 'weekly':
    strTimeFormat = '%Y%m%d'
    if isWeekStartedFromSunday(target_date):
      startDay = target_date - timedelta(days=target_date.isoweekday()%7)
    else:
      startDay = target_date - timedelta(days=target_date.weekday())
    endDay = startDay + timedelta(days=6)
    if not isWeekStartedFromSunday(startDay) and isWeekStartedFromSunday(endDay):
      endDay = endDay - timedelta(days=1)
    if isWeekStartedFromSunday(startDay) and not isWeekStartedFromSunday(endDay):
      target_date = target_date - timedelta(days=1)
      startDay = target_date - timedelta(days=target_date.isoweekday()%7)
      endDay = startDay + timedelta(days=6)
    if target_date.year < 2017:
      if target_date < date(2009, 11, 1):
        if target_date < date(2004, 11, 22):
          classCd = 'KPOP'
        else:
          classCd = 'CL0000'
      else:
        classCd = 'DP0000'
    else:
      classCd = 'GN0000'
    url_param = 'chartType=WE&classCd={}&startDay={}&endDay={}'.format(
      classCd, startDay.strftime(strTimeFormat), endDay.strftime(strTimeFormat)
    )
  else:
    strYearFormat = '%Y'
    strMonthFormat = '%m'
    rankYear = target_date.strftime(strYearFormat)
    rankMonth = target_date.strftime(strMonthFormat)
    url_param = 'chartType=MO&year={}&mon={}&classCd=DP0000'.format(rankYear, rankMonth)
  url = "http://www.melon.com/chart/search/list.htm?{}&moved=Y".format(url_param)
  debug.log("Request chart to melon by query < {} >".format(url))
  content = http.getHTMLDocument(url)
  # debug.log(content)

  soup = BeautifulSoup(content, "html.parser")
  # debug.log(soup)
  if(period_type == 'weekly'):
    period_str = '{}-{}'.format(startDay.strftime('%Y.%m.%d'), endDay.strftime('%Y.%m.%d'))
  else:
    period_str = '{}'.format(target_date.strftime('%Y.%m'))

  chart_name = 'melon_{}_'.format(period_type) + period_str
  debug.log(chart_name)

  table = soup.find('tbody', {'id':'chartListObj'})
  # debug.log(table)
  debug.log('')
  count = 1
  chart_list = []
  for music in table.find_all('tr', {'class':'lst50'}):
    if count > maxRank:
      break
    # image = music.find('img')
    links = music.find_all('a')
    if len(links) > 3:
      artist , title, songID, coverImgFile, lyric, albumID = getSongInfoOfMelon(music)
      debug.log('{:02}. {} - {} (id:{}, {})'.format(count, artist, title, songID, coverImgFile))
      chart_list.append({'rank':count, 'artist':artist, 'title':title,
                         'songID':songID, 'albumID':albumID, 'lyric':lyric})
      # debug.log(lyric)
      count += 1
  return chart_name, chart_list

if __name__ == '__main__':
  # lyric, artist, title, albumID, imgUrl = getSongInfobySongIDOfMelon('30989550')
  # print(lyric)
  # print(artist)
  # print(title)
  # print(albumID)
  # print(imgUrl)
  # chartlist = getMelonChart()
  # chartlist = getMelonChart(period_type='monthly', str_target_date='20150101')
  chartlist = getMelonChart(period_type='weekly', str_target_date='20041120')
  for song in chartlist:
    debug.log(song)
