#-*- coding:utf-8 -*-

import urllib.request
import time

import debug

def getHTMLDocument(url, autoRetry=True):
  listAgent = ['Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
               'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
               'Mozilla/5.0 (Windows NT 5.1; rv:6.0.2) Gecko/20100101 Firefox/6.0.2',
               'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
               ]
  retryDelay = [0.1, 0.5, 1, 2, 5, 10, 30, 60, 180, 300]
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
      if autoRetry:
        debug.log('Connection denied from \'{}\''.format(url))
        debug.log('Try again using another header after {}sec...'.format(retryDelay[delayCount]))
        agentCount = (agentCount+1) % len(listAgent)
        time.sleep(retryDelay[delayCount])
        delayCount = (delayCount+1) % len(retryDelay)
      else:
        debug.log('Document couldn\'t be get from {}'.format(url))
        return None
    else:
      conLoop = False
  return html.read()
