#-*- coding:utf-8 -*-

def log(str=''):
    try:
        print(str)
    except UnicodeEncodeError as e:
        print(str.encode('utf-8'))
