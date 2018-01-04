#!/usr/bin/python3
# -*- coding: utf-8 -*-

from spider import *

#url = 'old%20testament/27dan/27index.htm'
#get_volume()
#url = 'http://source:8888/old%20testament/02exo/02圣经译本/02at37.htm'
#url = 'http://source:8888/old%20testament/01gen/01圣经译本/01at19.htm'
#abc = get_bible_translation_detail(url)
#for each in abc:
#	print(each)
#url = 'http://source:8888/old%20testament/32jonah/32index.htm'
#abc = get_list_to_chapter(url)
#for each in abc:
#	print(each)
#url = 'http://source:8888/old%20testament/02exo/02圣经背景注释/02bt38.htm'
#url = 'http://source:8888/new%20testament/66rev/66index.htm'
#abc = get_list_to_chapter(url)
#for each in abc:
#	print(each)
url = 'http://source:8888/topics/76union/76index.htm'
url = 'http://source:8888/topics/76union/76at07.htm'
abc = get_page_total_detail(url)
print(abc)
