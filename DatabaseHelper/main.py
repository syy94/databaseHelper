import database
import csv
import urllib2

from flask import Flask, render_template
from database import entityListBuilder, bulkDeleter

app = Flask(__name__)

@app.route('/')   # URL '/' to be handled by main() route handler

def main():
    return render_template('index.html')
 
@app.route('/serviceList')
def serviceList():
    url = 'http://www.polytechnic.edu.sg/api/download/course?id=b434281c-efe6-69f6-9162-ff000003a8ed'
    response = urllib2.urlopen(url)
    cr = csv.reader(response)

    builder = entityListBuilder()
    for row in cr:
        builder.add_entity(row[2] # Course ID
                           , row[1] # Poly Acronym
                           , row[5] # O'lv Score
                           , row[3] # Course Name
                           , row[7] # URL
                           , 'N/A' # Additional Info
                           , row[4] # Course Type
                           , row[6] # Year
                           )
    builder.add_to_database()
    
    return 'refreshed database'
    
 
@app.errorhandler(500)
def server_error(e):
    return str(e)
 
if __name__ == '__main__':  # Script executed directly?
    app.run()  # Launch built-in web server and run this Flask webapp
    
