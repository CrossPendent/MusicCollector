#-*- coding:utf-8 -*-

def log(msg=''):
    out = str(msg)
    try:
        print(out)
    except UnicodeEncodeError as e:
        print(out.encode('utf-8'))
