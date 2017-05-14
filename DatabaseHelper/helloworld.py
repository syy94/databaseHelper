from flask import Flask
import database

from database import model_jae

app = Flask(__name__)

from google.appengine.ext import ndb
guestbook_key = ndb.Key('Guestbook', 'default_guestbook')

@app.route('/')   # URL '/' to be handled by main() route handler
def main():
    for i in range(10):
        database.insertCourse('c123'+str(i), 'NMA', 'A', 'difasd', 'dip in curry', '', 'asdasdasdasd')
        database.insertCourse('c123'+str(i+1), 'NMA', 'B', 'difasd', 'dip in ketchup', '', 'asdasdasdasd')
    
    
    qry = model_jae.query()

    return str(qry.fetch())
 
@app.errorhandler(500)
def server_error(e):
    return str(e)
 
if __name__ == '__main__':  # Script executed directly?
    app.run()  # Launch built-in web server and run this Flask webapp
    
