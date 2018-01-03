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
name='圣经译本'
print(get_list_id(name,''))
name='ksdjf'
print(get_list_id(name,''))
volume=1
list_id=1
detail={'chapter':0,'section':0,'version':'和合本'} 
print(get_detail_id(volume,list_id,detail,''))
url = 'http://source:8888/old%20testament/01gen/01圣经译本/01at01.htm'
abc = get_bible_translation_detail(url)
for each in abc:
	print(each)
