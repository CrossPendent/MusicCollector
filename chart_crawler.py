import urllib.request
from bs4 import BeautifulSoup

def getMelonChart():
  url = "http://www.melon.com/chart/week/"
#  url = "http://www.google.com"
  opener = urllib.request.build_opener()
  opener.addheaders = [('User_agent', 'Mozilla/5.0')]
  html = opener.open(url)
  content = html.read()

  soup = BeautifulSoup(content, "html5lib")
  table = soup.find(style='width:100%')
  print(table)

if __name__ == '__main__':
  getMelonChart()