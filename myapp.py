#!/usr/bin/python3
# -*- coding: utf-8 -*-

from spider import *
import time
import MySQLdb

#url = 'old%20testament/27dan/27index.htm'
#get_volume()
#url = 'http://source:8888/old%20testament/02exo/02圣经译本/02at37.htm'
#get_bible_translation_detail(url)

host='http://source:8888/'
volumes = get_volume()
start_time=int(time.time())
db = MySQLdb.connect(host='appdb',user='homestead',passwd='secret',db='homestead',charset="utf8")
for volume in volumes:
	if not re.match('^\d+',volume['name']):
		continue
	volume_sqs = volume['name'][:2]
	volume_name = volume['name'][2:]
	volume_href = volume['href']
	volume_id = get_volume_id(volume_name,db)
	if volume_id == -1:
		volume_insert_sql = 'insert into volume (name,href) values("'+volume_name+'","'+volume_href+'")'
		execute_sql(volume_insert_sql)#insert into volume
		volume_id = get_volume_id(volume_name,db)
	#if int(volume_sqs) >= 66:
	#只分析圣经
	if int(volume_sqs) > 66 and int(volume_sqs) <= 99:
	#只包含查经资料
		list_url = host+volume_href
		lists = get_list_to_chapter(list_url)
		for item in lists:
			list_name = item['list_name'].strip()[2:].replace('《','').replace('》','').replace('、','')
			list_id = get_list_id(list_name,db)
			if list_id == -1:
				list_name_sql = 'insert into list (name) values("'+list_name+'")'
				execute_sql(list_name_sql)
				list_id = get_list_id(list_name,db)
			if not list_name.endswith(u'圣经译本') and not list_name.endswith(u'基督徒文摘解经系列'):
				for chapter in item['list_content']:
					cur_chapter = get_page_total_detail(host+chapter['chapter_url'])

					if not cur_chapter:
						continue
					detail_id = get_resource_detail_id(volume_id,list_id,chapter['chapter_name'],db)
					if detail_id != -1:
						sql = 'delete from detail where id='+str(detail_id)
						execute_sql(sql)
					#if detail_id == -1:
					content_insert_sql = 'insert into resource (volume_id,list_id,chapter,content) values('+str(volume_id)+','+str(list_id)+',"'+chapter['chapter_name']+'","'+cur_chapter+'")'
					execute_sql(content_insert_sql)
						

#			if list_name.endswith('圣经译本'):
#			#今天只分析译本
#				for chapter in item['list_content']:
#					cur_chapter = get_bible_translation_detail(host+chapter['chapter_url'])
#					for detail in cur_chapter:
#						if not detail['content']:
#							continue
#						detail_id = get_bible_section_id(volume_id,detail,db)
#						if detail_id == -1:
#							content_insert_sql = 'insert into bible (volume_id,chapter,chapter_num,section_num,version,content) values("'+str(volume_id)+'","'+chapter['chapter_name']+'","'+str(detail['chapter'])+'","'+str(detail['section'])+'","'+detail['version']+'","'+detail['content']+'")'
#							execute_sql(content_insert_sql)
#						else:
#							my_log('volume_id:'+str(volume_id)+' list_id:'+str(list_id)+'chapter:'+str(detail['chapter'])+' section:'+str(detail['section'])+' version:'+detail['version']+' already exist')

db.close()
end_time=int(time.time())
release = end_time - start_time
my_log('run '+str(release)+' second')
