import music_collector as mc

import urllib.request
import os
import time
from bs4 import BeautifulSoup

def getHTMLContents(url):
  listAgent = ['Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
               'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
               'Mozilla/5.0 (Windows NT 5.1; rv:6.0.2) Gecko/20100101 Firefox/6.0.2',
               'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
               ]
  retryDelay = [0.1, 0.5, 1, 2, 5, 10, 30, 60, 300]
  conLoop = True
  agentCount = 0
  delayCount = 0
  while(conLoop):
    opener = urllib.request.build_opener()
    opener.addheaders = [('Accept', 'text/html, application/xhtml+xml, */*'),
                         ('Accept-Language', 'ko-KR'),
                         ('User_agent', listAgent[agentCount]),
                         ('Host', 'www.melon.com'),
                         ('DNT', '1'),
                         ('Connection', 'Keep-Alive'),
                         ("Content-Type", "application/x-www-form-urlencoded;charset=utf-8")]
    try:
      html = opener.open(url)
    except ConnectionResetError as e:
      print('Connection denied from \'{}\''.format(url))
      print('Try again using another header after {}sec...'.format(retryDelay[delayCount]))
      agentCount = (agentCount+1) % len(listAgent)
      time.sleep(retryDelay[delayCount])
      delayCount = (delayCount+1) % len(retryDelay)
    else:
      conLoop = False
  return html.read()

def downloadImageFromMelon(url, songID):
  image_dir = mc.IMAGE_DIR
  if not os.path.exists(image_dir):
    os.mkdir(image_dir)
  file_name = songID + '.jpg'
  urllib.request.urlretrieve(url, os.path.join(image_dir, file_name))
  return file_name

def getLyricFromMelon(melon_songID):
  base_url = 'http://www.melon.com/song/detail.htm?songId='
  url = base_url + melon_songID;

  content = getHTMLContents(url)

  soup = BeautifulSoup(content, "html.parser")
  raw_lyric = soup.find('div', {'class':'lyric'}).contents[1:]
  raw_lyric[0] = raw_lyric[0].replace('\r\n\t\t\t\t\t\t\t\t', '')

  lyric = ''
  for line in raw_lyric:
    if str(line) == '<br/>':
      lyric = lyric + '\r\n'
    else:
      lyric = lyric + str(line)

  return lyric

def getAlbumInfoFromMelon(melon_albumID):
  if melon_albumID == None:
    return None
  base_url = 'http://www.melon.com/album/detail.htm?albumId='
  url = base_url + melon_albumID

  content = getHTMLContents(url)

  soup = BeautifulSoup(content, "html.parser")
  soupAlbumName = soup.find('div', {'class':'song_name'})
  albumName = soupAlbumName.contents[-1].replace('\r\n\t\t\t\t\t\t\t\t\t', '').replace('\t', '')
  print(albumName)

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
  soupSongInfo = music_record.find('a', {'class':'btn button_icons type03 song_info'})
  soupAlbumInfo = music_record.find('div', {'class':'ellipsis rank03'})

  print('=========')
  print('soupArtist')
  artist = ''
#  print(soupArtist)
  artistCount = 0
  for art in soupArtist.find('span', {'class':'checkEllipsis'}).find_all('a'):
    if artistCount > 0:
      artist += ','
    artist += art.contents[0]
    artistCount += 1
  print(artist)
  print('soupTitle')
#  print(soupTitle)
  title = soupTitle.find('a').contents[0]
  print(title)
  print('soupSongInfo')
#  print(soupSongInfo)
  songID = soupSongInfo['href'].replace('javascript:melon.link.goSongDetail(\'', '').replace('\');', '')
  print(songID)
  print('soupAlbumInfo')
#  print(soupAlbumInfo)
  albumID = soupAlbumInfo.find('a')['href'].replace('javascript:melon.link.goAlbumDetail(\'', '').replace('\');', '')
  print(albumID)
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
      print(link)
  print(albumID)
  '''
  albumInfo = getAlbumInfoFromMelon(albumID)

  image = music_record.find('img')
  coverImageURL = image['src'].split('.jpg')[0] + '.jpg'
  coverImgFile = downloadImageFromMelon(coverImageURL, songID)
  lyric = getLyricFromMelon(songID)

  return artist, title, songID, coverImgFile, lyric, albumInfo

def getMelonChart():
  url = "http://www.melon.com/chart/week/"
  content = getHTMLContents(url)
#  print(content)

  soup = BeautifulSoup(content, "html.parser")
#  print(soup)
  period = soup.find('div', {'class':'calendar_prid'})
  print(period.find('span').contents[0].replace('\r\n\t\t\t\t\t\t', '').replace('\t', ''))

  table = soup.find(style='width:100%')
#  print(table)
  print('')
  count = 1
  chart_list = []
  for music in table.find_all('tr'):
    image = music.find('img')
    links = music.find_all('a')
    if len(links) > 3:
      artist , title, songID, coverImgFile, lyric, albumInfo = getSongInfoOfMelon(music)
      print('{:02}. {} - {} (id:{}, {})'.format(count, artist, title, songID, coverImgFile))
      chart_list.append({'rank':count, 'artist':artist, 'title':title,
                         'songID':songID, 'albumInfo':albumInfo, 'lyric':lyric})
#      print(lyric)
      count += 1
      if count > 20:
        break
  return chart_list

if __name__ == '__main__':
  chartlist = getMelonChart()
  for song in chartlist:
    print(song)
