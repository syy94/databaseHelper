'''
Created on May 17, 2017

@author: Choony
'''
import csv
import urllib2

url = 'http://www.polytechnic.edu.sg/api/download/course?id=b434281c-efe6-69f6-9162-ff000003a8ed'
response = urllib2.urlopen(url)
cr = csv.reader(response)

for row in cr:
    print row