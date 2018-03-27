import music_collector as mc

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

def getLyricFromMelon(melon_songID):
  base_url = 'http://www.melon.com/song/detail.htm?songId='
  url = base_url + melon_songID;
  opener = urllib.request.build_opener()
  opener.addheaders = [('User_agent', 'Mozilla/5.0')]
  html = opener.open(url)
  content = html.read()

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

  opener = urllib.request.build_opener()
  opener.addheaders = [('User_agent', 'Mozilla/5.0')]
  html = opener.open(url)
  content = html.read()

  soup = BeautifulSoup(content, "html.parser")
  info = soup.find('dl', {'class':'list'})
  if info == None:
    return None
  dd_list = info.find_all('dd')

  pub_date = dd_list[0].contents[0]
  genre = dd_list[1].contents[0]
  publisher = dd_list[2].contents[0]
  copyright = dd_list[3].contents[0]
  return {'pub_date':pub_date, 'genre':genre, 'publisher':publisher, 'copyright':copyright}

def getSongInfoOfMelon(music_record):
  links = music_record.find_all('a')
  if len(links) < 4:
    return None
  artist = links[3].contents[0]
  title = links[2].contents[0]
  songID = links[1]['href'].replace('javascript:melon.link.goSongDetail(\'','').replace('\');', '')
  albumID = links[4]['href'].replace('javascript:melon.link.goAlbumDetail(\'','').replace('\');', '')
  albumInfo = getAlbumInfoFromMelon(albumID)

  image = music_record.find('img')
  coverImageURL = image['src'].split('.jpg')[0] + '.jpg'
  coverImgFile = downloadImageFromMelon(coverImageURL, songID)
  lyric = getLyricFromMelon(songID)

  return artist, title, songID, coverImgFile, lyric, albumInfo

def getMelonChart():
  url = "http://www.melon.com/chart/week/"
  opener = urllib.request.build_opener()
  opener.addheaders = [('User_agent', 'Mozilla/5.0')]
  html = opener.open(url)
  content = html.read()
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
                         'songID':songID, 'lyric':lyric, 'albumInfo':albumInfo})
#      print(lyric)
      count += 1
      if count > 50:
        break
  return chart_list

if __name__ == '__main__':
  getMelonChart()
