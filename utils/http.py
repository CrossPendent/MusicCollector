#-*- coding:utf-8 -*-

import urllib.request
import time

from utils import debug


def getHTMLDocument(url, autoRetry=True):
  listAgent = ['Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36']
  retryDelay = [0.1, 0.5, 1, 2, 5, 10, 30, 60, 180, 300]
  conLoop = True
  agentCount = 0
  delayCount = 0
  while(conLoop):
    opener = urllib.request.build_opener()
    opener.addheaders = [('Host', 'www.melon.com'),
                         ('Connection', 'Keep-Alive'),
                         ('Upgrade-Insecure-Requests', '1'),
                         ('User_agent', listAgent[agentCount]),
                         ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'),
                         ('Accept-Language', 'en-US,en;q=0.9,ko-KR;q=0.8,ko;q=0.7'),
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
