# -*- coding: utf-8 -*-

__author__ = 'dj@ixinyou.com'
__version__= 'v1'
__copyright__ = '2014@xinyou Corp'

"""
@since: 2014-07-20
@summary: 
	execute shell script command via creating subprocess.
 	python script filter STDOUT text,and split key-word that u provided to get return value.
"""

import subprocess
import sys

__BUFSIZE__ = 1024

# stdout without return value
# cmdArgsList : shell name and cmd args
#               cmdArgsList=['ping','google.com','-c','10']
def subprocess_stdout(cmdArgsList):
    try:
		sp = subprocess.Popen(cmdArgsList,bufsize=__BUFSIZE__,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
		spid = sp.pid
		while True:
			nextLine = sp.stdout.readline()
	    if( nextLine == '' and sp.poll() != None):
   			break
        sys.stdout.write(nextLine)
    except Exception, e:
	    print e

# return value via stdout PIPE filter.
# cmdArgsList : shell name and cmd args
#               cmdArgsList=['ping','google.com','-c','10']
# rvKeyword : set rvKeyword=key, 'subprocess_returnvalue' will filter text line like 'key=value',
#             when 'key=value' appeared, subprocess will be terminated, and 'value' be returned.
def subprocess_returnvalue(cmdArgsList,rvKeyword):
    try:
        sp = subprocess.Popen(cmdArgsList,bufsize=__BUFSIZE__,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
        spid = sp.pid
        while True:
            nextLine = sp.stdout.readline()
            if( nextLine == '' and sp.poll() != None):
                break
            resultArray = nextLine.split('%s='%rvKeyword)
            if len(resultArray) == 2:
                sp.terminate()
				return resultArray[1]
    except Exception, e:
        print e

if __name__ == '__main__':
    cmdList=['ping','baidu.com','-c','100']
    print subprocess_returnvalue(cmdList,'time')
