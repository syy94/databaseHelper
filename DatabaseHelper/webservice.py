from flask import Flask
from flask import render_template, request
import json
import database
app = Flask(__name__)

BASE_URL = '/_ah/api/'
SUCCESS = 'success'
ERROR = 'error'

@app.route(BASE_URL)
def main():
    return render_template('serviceList.html')

@app.route(BASE_URL+'list', methods=['POST'])
def list_courses():
    result = {}
    
    length = request.form.get('length', type=int, default=10)
    offset = request.form.get('offset', type=int, default=0)
    #order for now not supported
    #order = request.form.get('order', type=str).split(':')
    
    course_list = [course.to_dict() for course in database.get_course_list(length, offset)]
    
    result['courses'] = course_list
    result[SUCCESS] = True
    
    return json.dumps(result)

@app.route(BASE_URL+'course', methods=['POST'])
def get_course():
    result = {SUCCESS:True}
    
    course_id = request.form.get('course_id')
    
    course = database.get_course_by_id(course_id)
    
    if course is not None:
        result['course'] = course.to_dict()

    return json.dumps(result)
    

@app.errorhandler(500)
def server_error(e):
    result = {SUCCESS:False, ERROR:str(e)}
    return json.dumps(result)

if __name__ == '__main__':
    app.run()