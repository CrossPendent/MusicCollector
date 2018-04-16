#-*- coding:utf-8 -*-

import datetime as dt

def log(msg=''):
    out = '[{}] {}'.format(dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), str(msg))
    try:
        print(out)
    except UnicodeEncodeError as e:
        print(out.encode('utf-8'))
