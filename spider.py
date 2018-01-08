#!/usr/bin/python3
# -*- coding: utf-8 -*-
from lxml import etree
import requests
import MySQLdb
import re
from servertools import my_log
from urllib import parse

host='http://source:8888/'
def get_clear_html_selector(url):
	root_html = requests.get(url)
	selector = etree.HTML(root_html.content.decode('GBK','ignore'))
	return selector
def get_volume():
#生成一个列表结构为[{'name':'01创世记','href':'sdfsdf.htm'},{'name':'02出埃及记','href':'xc.htm'}]
	root_url = 'http://source:8888/index.htm'
	selector = get_clear_html_selector(root_url)
	ret = []
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
	ret = {}
	tmp_lists_content = []
	selector = get_clear_html_selector(url)
	chapter_name_list = selector.xpath('//div[@align="center"]//table')
	
	for each in chapter_name_list:
	#each 为所有的带着url的章列表 需要采集出对应的章名称和url 生成一个[{'chapter_name':'第一章','chapter_url':'abcdef.htm'},{'chapter_name':'第二章','chapter_url':'ahcsdf.htm'}...]
		cur_list = []
		lists = each.xpath('.//p//a')
		if lists:
			for each2 in lists:
				
				parent_path = parse.urlparse(url)[2]
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
def get_page_total_detail(url):
	#
	my_log('now to get page detail....'+url)
	selector = get_clear_html_selector(url)
	detail = selector.xpath('//body//p')
	ret = ''
	for item in detail:
		tmp = item.xpath('string(.)').replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
		#tmp = item.xpath('string(.)').replace('\r','').replace('\n','').replace('\t','').replace(' ','').replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
		if tmp and not tmp.startswith(u'返回') and not re.match('.*返回.*',tmp):
			ret+='&lt;br&gt;'+tmp
	return ret
def get_chapters_from_type_3(info):
	tp = re.match('^(\d+)\S(\d+)\S\S+$',info)
	ret = []
	chapter = tp.group(1)
	section = tp.group(2)
	versions = [u'和合本',u'修订本',u'新译本',u'吕振中',u'中译本',u'当代一',u'当代二',u'现代本',u'文理本',u'普通话',u'思高本',u'恢复本']
	count_versions = len(versions)
	i = 0
	for version in versions:
		i += 1
		if i == count_versions:
			next_version = False
		else:
			next_version = versions[i]
		content_start = info.find(version)+3
		if next_version:
			content = info[info.find(version)+4:info.find(next_version)-1]
		else:
			content = info[info.find(version)+4:]

		cur_chapter = {'chapter':chapter,'section':section,'version':version,'content':content}
		ret.append(cur_chapter)
	return ret


def get_bible_translation_detail(url):
	my_log('now to get bible detail....'+url)
	# get detail
	# return struct: [{'chapter':1,'section':23,'version':'sdfsdfd','content':'ksdjfksdjfksjdf'},...]
	selector = get_clear_html_selector(url)
	detail = selector.xpath('//body//p')
	last_node = selector.xpath('//body/span')
	last_line = "".join(str.xpath('string(.)').replace('\r','').replace('\n','').replace('\t','') for str in last_node)
	cur_chapter = 0
	cur_section = 0
	ret = []
	for item in detail:
		info = item.xpath('string(.)').replace('\xa0','').replace('\r','').replace('\n','').replace('\t','').replace('\u3000','').replace(' ','')
		if not info:
			continue
		if info.startswith(u'返回') or info.endswith(u'简介'):
			continue
		if not info.startswith(u'('):
			is_new_section_1 = re.match('^(\d+)\S(\d+)\S$',info)
			if is_new_section_1 :#is new section
				cur_chapter = is_new_section_1.group(1)
				cur_section = is_new_section_1.group(2)
			else:
				is_new_section_2 = re.match('^\S+(\d+):(\d+)\S$',info)
				if is_new_section_2:
					cur_chapter = is_new_section_2.group(1)
					cur_section = is_new_section_2.group(2)
				else:
					is_new_section_3 = re.match('^(\d+)\S(\d+)\S\S+$',info)
					if is_new_section_3:
						chapters = get_chapters_from_type_3(info)
						for eachchapter in chapters:
							ret.append(eachchapter)
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

def get_chapter_id(name,list_id,volume_id,db):
	sql = 'select id from chapter where name="'+name+'" and list_id='+str(list_id)+' and volume_id='+str(volume_id);
	return get_info(sql,id,db)
def get_resource_detail_id(chapter_id,db):
	#查经资料的一个chapter就只有一个detail
	sql = 'select id from detail where chapter_id='+str(chapter_id);
	return get_info(sql,id,db)
def get_bible_section_id(chapter_id,detail,db):
	#my_log('get detail_id:'+str(detail['chapter'])+':'+str(detail['section'])+':'+detail['version'])
	sql = 'select id from detail where chapter_id='+str(chapter_id)+' and content="'+detail['content']+'" and chapter_num='+str(detail['chapter'])+' and section_num='+str(detail['section'])+' and version="'+detail['version']+'"'
	return get_info(sql,id,db)
def get_chapter_and_section(url,is_print=False):
	selector = get_clear_html_selector(url)
	detail = selector.xpath('//body//p')
	ret = []
	for item in detail:
		info = item.xpath('string(.)').replace('\xa0','').replace('\r','').replace('\n','').replace('\t','').replace('\u3000','').replace(' ','')
		if not info:
			continue
		if info.startswith(u'返回') or info.endswith(u'简介'):
			continue
		if not info.startswith(u'('):
			if re.match('^(\d+)\S(\d+)\S$',info):
				pass
			elif re.match('^\S+\d+:\d+\S$',info):
				pass
			else:
				print(info)
def get_all_chapter_section_struct():
# 
	volumes = get_volume()
	for volume in volumes:
		if not re.match('^\d+',volume['name']):
			continue
		volume_sqs = volume['name'][:2]
		volume_name = volume['name'][2:]
		volume_href = volume['href']
		if int(volume_sqs) <= 66:
			list_url = host+volume_href
			lists = get_list_to_chapter(list_url)
			for item in lists:
				list_name = item['list_name'].strip()[2:].replace('《','').replace('》','').replace('、','')
				if list_name.endswith(u'圣经译本'):
					for chapter in item['list_content']:
						cur_chapter = get_chapter_and_section(host+chapter['chapter_url'],True)


