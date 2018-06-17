#!/usr/bin/python
# -*- coding: UTF-8 -*-

from searcher import Searcher
import sys

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding("utf-8")
    sites = ['https://www.douban.com/group/zhufang/discussion']
    keywords = []
    exclude = []
    searcher = Searcher(sites, keywords, exclude)
    searcher.search()
