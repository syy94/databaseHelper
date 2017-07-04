from flask import Flask
from flask import render_template, request
import json
import database
from flask.wrappers import Response

app = Flask(__name__)

BASE_URL = '/_ah/api/'
SUCCESS = 'success'
ERROR = 'error'

@app.route(BASE_URL)
def main():
    return render_template('serviceList.html')

@app.route(BASE_URL + 'favs', methods=['POST'])
def get_favs():
    requestJson = request.get_json(force=True)
    
    result = database.get_favs(requestJson)
    
    result = json.dumps(result)
    
    return Response(result, mimetype='application/json')

@app.route(BASE_URL + 'search', methods=['POST'])
def search_courses():
    requestJson = request.get_json(force=True)
    
    result = json.dumps(database.find(requestJson['query'], requestJson['offset']))
    
    return Response(result, mimetype='application/json')
    

@app.route(BASE_URL + 'list', methods=['POST'])
def list_courses():
    requestJson = request.get_json(force=True)
    
    course_list = database.get_course_list(requestJson)
    
    if len(course_list) is not 0:
        return json.dumps(course_list)
    else:
        return "", 204

@app.route(BASE_URL + 'course', methods=['POST'])
def get_course():
    requestJson = request.get_json(force=True);
    
    course = database.get_course_by_id(requestJson['id'])
    
    if course is not None:
        return json.dumps(course.to_dict())
    else:
        return "", 204
    

@app.errorhandler(500)
def server_error(e):
    return json.dumps(str(e))

if __name__ == '__main__':
    app.run()
