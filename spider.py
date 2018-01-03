#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lxml import etree
import requests
import MySQLdb
import re
from servertools import my_log
from urllib import parse
def get_volume():

#生成一个列表结构为[{'name':'01创世记','href':'sdfsdf.htm'},{'name':'02出埃及记','href':'xc.htm'}]

	root_url = 'http://source:8888/index.htm'

	root_html = requests.get(root_url)

	ret = []

	selector = etree.HTML(root_html.content)

	tmp = selector.xpath('//a')

	for each in tmp:

		link = each.xpath('@href')[0]
		name = each.xpath('string(.)').replace('\r','').replace('\n','').replace('\t','')
		ret.append({'href':link,'name':name})

	return ret
def get_list_to_chapter(url):

	my_log('get list_to chapter:'+url)
#'''
#生成一个字典结构为
# url 为不带scheme的
#{
#	[
#	'list_name':'A、《圣经译本》',
#	'list_content':[
#		{'chapter_name':'第一章','chapter_url':'abcdefff.htm'},
#		{'chapter_name':'第二章','chapter_url':'abcdefff.htm'},
#		...
#		],//end list_content
#	],//end list
#	[
#	'list_name':'B、《丁达尔解经》',
#	'list_content':[
#		{'chapter_name':'第一章','chapter_url':'abcdefff.htm'},
#		{'chapter_name':'第二章','chapter_url':'abcdefff.htm'},
#		...
#		],//end list_content
#	],//end list
#	...
#}
#'''
	index_url = url;

	index_html = requests.get(index_url)

	ret = {}

	tmp_lists_content = []

	selector = etree.HTML(index_html.content)

	chapter_name_list = selector.xpath('//div[@align="center"]//table')
	
	for each in chapter_name_list:

	#each 为所有的带着url的章列表 需要采集出对应的章名称和url 生成一个[{'chapter_name':'第一章','chapter_url':'abcdef.htm'},{'chapter_name':'第二章','chapter_url':'ahcsdf.htm'}...]

		cur_list = []

		lists = each.xpath('.//p//a')

		if lists:

			for each2 in lists:
				
				parent_path = parse.urlparse(index_url)[2]

				add_path = parent_path[1:parent_path.rfind('/')+1]
				
				cur_chapter_url = add_path+each2.xpath('@href')[0]

				cur_chapter_name = each2.xpath('string(.)').replace('\r','').replace('\n','').replace('\t','')

				cur_list.append({'chapter_name':cur_chapter_name,'chapter_url':cur_chapter_url})
		if cur_list:

			tmp_lists_content.append(cur_list)

	tmp_lists_name = []

	list_name = selector.xpath('//div[not(@align or @class)]//p')
	#list_name = selector.xpath('//div[@style="border-style: groove"]//p')

	for each in list_name:

		list_name = each.xpath('string(.)').replace('\r','').replace('\n','').replace('\t','')

		if list_name :
			
			if list_name.endswith(u'目录'):

				continue

			tmp_lists_name.append(list_name)

			#decoded_str = bytes.decode(category)

			#execute_sql('insert into test(test_string) values('+decoded_str+')')

			#ret.append({'category':category})

	lists_name_lenth = len(tmp_lists_name)

	chapter_name_list_lenth = len(tmp_lists_content)

	min_lenth = lists_name_lenth

	if min_lenth > chapter_name_list_lenth:
		
		min_lenth = chapter_name_list_lenth

	ret = []

	for i in range(0,min_lenth):

		cur_list = {'list_name':tmp_lists_name[i],'list_content':tmp_lists_content[i]}

		ret.append(cur_list)
	return ret

def get_bible_translation_detail(url):
	
	my_log('now to get bible detail....'+url)
	
	# get detail
	# return struct: [{'chapter':1,'section':23,'version':'sdfsdfd','content':'ksdjfksdjfksjdf'},...]

	root_html = requests.get(url)

	selector = etree.HTML(root_html.content.decode('GBK','ignore'))

	detail = selector.xpath('//body//p')

	last_node = selector.xpath('//body/span')

	last_line = "".join(str.xpath('string(.)').replace('\r','').replace('\n','').replace('\t','') for str in last_node)

	cur_chapter = 0

	cur_section = 0

	ret = []

	for item in detail:

		info = item.xpath('string(.)').replace('\xa0','').replace('\r','').replace('\n','').replace('\t','').replace('\u3000','')

		if not info:
			continue

		if info.startswith(u'返回') or info.endswith(u'简介'):
			continue

		if not info.startswith(u'('):
		
			is_new_section = re.match('^(\d+)\S(\d+)\S$',info.replace(' ',''))

			if is_new_section :#is new section

				cur_chapter = is_new_section.group(1)

				cur_section = is_new_section.group(2)

			continue

		cur_version = info[1:info.find(')')]

		cur_content = info[info.find(')')+1:]

		cur_info = {'chapter':cur_chapter,'section':cur_section,'version':cur_version,'content':cur_content}

		ret.append(cur_info)

	last_content = last_line[last_line.find(')')+1:]
	
	last_version = last_line[1:last_line.find(')')]

	ret.append({'chapter':cur_chapter,'section':cur_section,'version':last_version,'content':last_content})

	return ret

def execute_sql(sql,db=''):
	need_close = 0
	if not db:

		db = MySQLdb.connect(host='appdb',user='homestead',passwd='secret',db='homestead',charset="utf8")
		need_close = 1

	cursor = db.cursor()

	try:
		cursor.execute(sql)
		db.commit()
	except Exception as e:
		my_log('failt to execute:'+sql+' and error:'+str(e))
		db.rollback()

	finally:
		cursor.close()
	if need_close:
		db.close()
def get_info(sql,info,db=''):

	need_close = 0
	
	if not db:	
		db = MySQLdb.connect(host='appdb',user='homestead',passwd='secret',db='homestead',charset="utf8")
		need_close = 1

	ret = -1

	cursor = db.cursor()

	try:
		cursor.execute(sql)
		ret = cursor.fetchone()
		if ret:
			ret = ret[0]
		else:
			ret = -1

		db.commit()
	except Exception as e:
		my_log('failt to get info:'+sql+' and error:'+str(e))
		db.rollback()

	finally:
		cursor.close()

	if need_close:

		db.close()

	return ret
def get_volume_id(volume_name,db):
	my_log('get volume_id:'+volume_name)
	sql = 'select id from volume where name="'+volume_name+'"'
	return get_info(sql,id,db)

def get_list_id(list_name,db):
	my_log('get list_id:'+list_name)
	sql = 'select id from list where name="'+list_name+'"'
	return get_info(sql,id,db)
def get_detail_id(volume_id,list_id,detail,db):
	#my_log('get detail_id:'+str(detail['chapter'])+':'+str(detail['section'])+':'+detail['version'])
	sql = 'select id from detail where content="'+detail['content']+'" and volume_id='+str(volume_id)+' and list_id='+str(list_id)+' and chapter_num='+str(detail['chapter'])+' and section_num='+str(detail['section'])+' and version="'+detail['version']+'"'
	return get_info(sql,id,db)
