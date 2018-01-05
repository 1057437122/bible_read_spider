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
		volume_insert_sql = 'select 100;';
		if int(volume_sqs) <= 39:
			volume_insert_sql = 'insert into volume (name,href,category_id) values("'+volume_name+'","'+volume_href+'",1)'
		elif int(volume_sqs) >39 and int(volume_sqs) <=66:
			volume_insert_sql = 'insert into volume (name,href,category_id) values("'+volume_name+'","'+volume_href+'",2)'
		elif int(volume_sqs) >66 and int(volume_sqs) <=99:
			volume_insert_sql = 'insert into volume (name,href,category_id) values("'+volume_name+'","'+volume_href+'",3)'
		execute_sql(volume_insert_sql)#insert into volume
		volume_id = get_volume_id(volume_name,db)
	if int(volume_sqs) <= 99:
	#不包含经文汇总的圣经译本和查经资料
		list_url = host+volume_href
		lists = get_list_to_chapter(list_url)
		for item in lists:
			list_name = item['list_name'].strip()[2:].replace('《','').replace('》','').replace('、','')
			list_id = get_list_id(list_name,db)
			if list_id == -1:
				list_name_sql = 'insert into list (name) values("'+list_name+'")'
				execute_sql(list_name_sql)
				list_id = get_list_id(list_name,db)

			for chapter in item['list_content']:
				chapter_name = chapter['chapter_name']
				chapter_href = chapter['chapter_url']
				chapter_id = get_chapter_id(chapter_name,list_id,volume_id,db)
				if chapter_id == -1:
					chapter_insert_sql = 'insert into chapter (name,href,volume_id,list_id) values ("'+chapter_name+'","'+chapter_href+'",'+str(volume_id)+','+str(list_id)+') '
					execute_sql(chapter_insert_sql)
				chapter_id = get_chapter_id(chapter_name,list_id,volume_id,db)
				if list_name.endswith('圣经译本'):
					cur_chapter = get_bible_translation_detail(host+chapter['chapter_url'])
					for detail in cur_chapter:
						if not detail['content']:
							continue
						detail_id = get_bible_section_id(chapter_id,detail,db)
						if detail_id == -1:
							content_insert_sql = 'insert into detail (chapter_id,chapter_num,section_num,version,content) values('+str(chapter_id)+',"'+str(detail['chapter'])+'","'+str(detail['section'])+'","'+detail['version']+'","'+detail['content']+'")'
							execute_sql(content_insert_sql)
						else:
							my_log(list_name+':'+'chapter:'+str(detail['chapter'])+' section:'+str(detail['section'])+' version:'+detail['version']+' already exist')
				else:
					detail = get_page_total_detail(host+chapter_href)
					if not detail:
						continue
					detail_id = get_resource_detail_id(chapter_id,db)
					if detail_id != -1:
						sql = 'delete from detail where id='+str(detail_id)
						execute_sql(sql)
					#if detail_id == -1:
					content_insert_sql = 'insert into detail (chapter_id,content) values('+str(chapter_id)+',"'+detail+'")'
					execute_sql(content_insert_sql)

db.close()
end_time=int(time.time())
release = end_time - start_time
my_log('run '+str(release)+' second')
