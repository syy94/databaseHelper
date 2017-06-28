import csv
import urllib2
from database import entityListBuilder 

url = 'http://www.polytechnic.edu.sg/api/download/course?id=b434281c-efe6-69f6-9162-ff000003a8ed'
response = urllib2.urlopen(url)
cr = csv.reader(response)

index = 0

builder = entityListBuilder()
for row in cr:
    if(index is not 0):
        builder.add_entity(row[2]  # Course ID
                       , row[1]  # Poly Acronym
                       , int(row[5])  # O'lv Score
                       , row[3]  # Course Name
                       , row[7]  # URL
                       , 'N/A'  # Additional Info
                       , row[4]  # Course Type
                       , row[6]  # Year
                       )
    index += 1
builder.add_to_database()
