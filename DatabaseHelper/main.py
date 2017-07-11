import database
import pickle
import pprint

from DataType.iPolyCourse import iPolyCourse
from flask import Flask, render_template
from database import entityListBuilder, bulkDeleter

app = Flask(__name__)

@app.route('/')   # URL '/' to be handled by main() route handler

def main():
    return render_template('index.html')
 
@app.route('/serviceList')
def serviceList():
    PolyList = []
    try:
        with open("./PolyData.pkl",'rb') as polyFile:
            while True:                          # loop indefinitely
                PolyList.append(pickle.load(polyFile))  # add each item from the file to a list
    except EOFError:  
        pass
    
    builder = entityListBuilder()
    for courseObj in PolyList:
        builder.add_entity(courseObj.courseID
                           , courseObj.polytechnic
                           , courseObj.score
                           , courseObj.name
                           , courseObj.url 
                           , courseObj.url2 
                           , courseObj.description
                           , courseObj.year
                           , courseObj.structure
                           , courseObj.cluster
                           , courseObj.intake
                           )
    builder.add_to_database()
    
    return 'refreshed database'
    
 
@app.errorhandler(500)
def server_error(e):
    return str(e)
 
if __name__ == '__main__':  # Script executed directly?
    app.run()  # Launch built-in web server and run this Flask webapp
    
