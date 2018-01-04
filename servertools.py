#!/usr/bin/python
# -*- coding: utf8 -*-
import time

def my_log(log_str,log_file='my_log_file.log',print_out=False):
	with open(log_file,'a+') as fp:
		fp.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
		fp.write(':'+str(log_str))
		#fp.write(':'+str(log_str).decode('utf-8'))
		if(print_out):
			print(str(log_str))
		fp.write('\n')
